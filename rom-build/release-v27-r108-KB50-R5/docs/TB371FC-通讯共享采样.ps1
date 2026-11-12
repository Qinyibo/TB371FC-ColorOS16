[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Adb,
    [Parameter(Mandatory)][ValidateSet('wifi-connected','wifi-disconnected','wifi-off')][string]$Stage,
    [string]$Serial
)

$ErrorActionPreference = 'Stop'
$Adb = (Resolve-Path -LiteralPath $Adb).Path
$devices = @(& $Adb devices)
if ($LASTEXITCODE -ne 0) { throw 'adb devices failed' }
$attached = @($devices | ForEach-Object { if ($_ -match '^([A-Za-z0-9._:-]+)\s+device\s*$') { $Matches[1] } })
if (!$Serial -and $attached.Count -eq 1) { $Serial = $attached[0] }
if (!$Serial -or $Serial -notin $attached) { throw 'Connect one authorized tablet, or specify -Serial.' }

function Read-Device([string]$Command) {
    $lines = @(& $Adb -s $Serial shell $Command)
    if ($LASTEXITCODE -ne 0) { throw "ADB read failed: $Command" }
    return $lines
}

$wifi = (Read-Device 'cmd wifi status') -join "`n"
$system = (Read-Device 'getprop ro.build.display.id; getprop init.svc.r94-commcenterd; getprop init.svc.r94-virtual-ril-0; settings get global VCOMM_SHARE_NETWORK; cat /proc/uptime')
if ($system.Count -ne 5) { throw 'Incomplete ROM/service status' }
$links = Read-Device 'for n in ovnet0 ovnet1 ovnet2; do if [ ! -d /sys/class/net/$n ]; then echo "$n missing"; continue; fi; state=$(cat /sys/class/net/$n/operstate 2>/dev/null); echo "$n state=${state:-unknown}"; if addrs=$(ip -o addr show dev "$n" scope global 2>/dev/null); then printf "%s\n" "$addrs" | awk -v n="$n" ''$3=="inet" {v4++} $3=="inet6" {v6++} END {printf "%s global_ipv4=%d global_ipv6=%d\n", n, v4, v6}''; else echo "$n global_addresses=unknown"; fi; for c in tx_packets rx_packets tx_dropped; do v=$(cat /sys/class/net/$n/statistics/$c 2>/dev/null); echo "$n $c=${v:-unknown}"; done; done'
$connectivity = Read-Device 'dumpsys -t 4 connectivity'
$default = [regex]::Match(($connectivity -join "`n"), '(?m)^\s*Active default network:\s*(\d+)\s*$')
$agents = @($connectivity | Where-Object { $_ -match 'NetworkAgentInfo\{network\{\d+\}' })
$ovnetAgents = @($agents | ForEach-Object {
    if ($_ -match 'InterfaceName:\s*(ovnet[0-2])\b') {
        [pscustomobject]@{ interface = $Matches[1]; validated = ($_ -match '\bVALIDATED\b') }
    }
})
$defaultInterface = 'unknown'
$validated = $null
if ($default.Success) {
    $id = $default.Groups[1].Value
    $row = $agents | Where-Object { $_ -match "NetworkAgentInfo\{network\{$id\}" } | Select-Object -First 1
    if ($row -match 'InterfaceName:\s*([A-Za-z0-9_.-]+)') { $defaultInterface = $Matches[1] }
    if ($row) { $validated = $row -match '\bVALIDATED\b' }
} elseif (($connectivity -join "`n") -match '(?m)^\s*Active default network:\s*(none|null|<none>)\s*$') {
    $defaultInterface = 'none'
}

[pscustomobject]@{
    stage = $Stage
    time = (Get-Date).ToString('o')
    build = $system[0]
    uptime_seconds = ($system[4] -split '\s+')[0]
    wifi_enabled = if ($wifi -match '(?m)^Wifi is enabled') { $true } elseif ($wifi -match '(?m)^Wifi is disabled') { $false } else { $null }
    wifi_associated = if ($wifi -match '(?m)^Wifi is connected') { $true } elseif ($wifi -match '(?m)^Wifi is (not connected|disconnected|disabled)') { $false } else { $null }
    commcenterd = $system[1]
    virtual_ril = $system[2]
    share_network = $system[3]
    default_interface = $defaultInterface
    default_validated = $validated
    ovnet_network_agents = $ovnetAgents
    ovnet = @($links | Where-Object { $_ -match '^ovnet[0-2] (missing|state=\w+|global_ipv4=\d+ global_ipv6=\d+|global_addresses=unknown|(tx_packets|rx_packets|tx_dropped)=(\d+|unknown))\s*$' })
} | ConvertTo-Json -Depth 3
