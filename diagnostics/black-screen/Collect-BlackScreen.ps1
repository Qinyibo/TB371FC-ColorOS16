# Run only during a naturally occurring black screen. No wake/reboot or device writes.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$Serial,
    [string]$AdbPath='C:/android-sdk/platform-tools/adb.exe',
    [string]$OutputDirectory=''
)
$ErrorActionPreference='Stop'
if($Serial -notmatch '^[A-Za-z0-9._:-]+$'){throw 'Invalid device serial or existing paired wireless endpoint.'}
if(!(Test-Path -LiteralPath $AdbPath -PathType Leaf)){throw 'ADB not found; specify -AdbPath.'}
if(!$OutputDirectory){$OutputDirectory=Join-Path $PSScriptRoot ('captures/'+(Get-Date -Format 'yyyyMMdd-HHmmss'))}
if(Test-Path -LiteralPath $OutputDirectory){throw 'Output directory already exists; preserve the previous capture.'}
New-Item -ItemType Directory -Path $OutputDirectory | Out-Null
$encoding=New-Object System.Text.UTF8Encoding($false)
$results=New-Object 'System.Collections.Generic.List[object]'

function Read-RootSnapshot([string]$Name,[string]$Script,[int]$TimeoutSeconds=20) {
    $info=New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName=$AdbPath
    $info.Arguments='-s "'+$Serial+'" shell "su -mm -c sh"'
    $info.UseShellExecute=$false
    $info.CreateNoWindow=$true
    $info.RedirectStandardInput=$true
    $info.RedirectStandardOutput=$true
    $info.RedirectStandardError=$true
    $proc=New-Object System.Diagnostics.Process
    $proc.StartInfo=$info
    try {
        if(!$proc.Start()){throw 'Could not start ADB.'}
        $stdout=$proc.StandardOutput.ReadToEndAsync()
        $stderr=$proc.StandardError.ReadToEndAsync()
        # Send through stdin: no remote temporary script and no host variable expansion.
        $proc.StandardInput.Write($Script.Replace("`r`n","`n")+"`n")
        $proc.StandardInput.Close()
        $timedOut=!$proc.WaitForExit($TimeoutSeconds*1000)
        if($timedOut){$proc.Kill();$proc.WaitForExit()}
        $output=$stdout.GetAwaiter().GetResult()
        $errorText=$stderr.GetAwaiter().GetResult()
        [IO.File]::WriteAllText((Join-Path $OutputDirectory ($Name+'.txt')),$output,$encoding)
        [IO.File]::WriteAllText((Join-Path $OutputDirectory ($Name+'.stderr.txt')),$errorText,$encoding)
        $results.Add([ordered]@{name=$Name;exit_code=$proc.ExitCode;timed_out=$timedOut;characters=$output.Length})
        return $output
    } finally {$proc.Dispose()}
}

$record=[ordered]@{
    started=(Get-Date -Format o);endpoint=$Serial;device_state_modified=$false
    natural_incident_required=$true;wake_injected=$false;reboot_requested=$false
    filter_absence_proves_no_recovery=$false;marker_proves_physical_power_cycle=$false
    steps=@();capture_complete=$false
}
try {
    # Preserve the full ring first. Filtering only on the computer retains surrounding context.
    $kernel=Read-RootSnapshot 'black-dmesg-full' 'dmesg'
    $pattern='R97_DIAG|R104_PANEL_DEAD|R107_|PANEL_DEAD|esd check failed|R94_PREPARE|R94_PREPANEL|R94_DISPLAY_PREPARED|R94_PANEL_POST|R94_NATIVE_COMPLETE|R94_REAL_READY|R94_FW_HW_RESET|R94_BRIDGE|R96_ENABLE|nvt_check_fw_reset_state|crc_done|ilm:|dlm:|0x9D|0xA0'
    $filtered=($kernel -split "`n" | Where-Object {$_ -match $pattern}) -join "`n"
    [IO.File]::WriteAllText((Join-Path $OutputDirectory 'black-dmesg-filter.txt'),$filtered,$encoding)
    $sysfs=@'
echo '== identity'
date
getprop ro.serialno
cat /proc/sys/kernel/random/boot_id /proc/uptime /proc/version
echo '== touch wake state'
if [ -r /sys/module/nt36xxx/parameters/r94_wake_state ]; then
    cat /sys/module/nt36xxx/parameters/r94_wake_state
else
    echo 'TOUCH_STATE_UNAVAILABLE'
fi
echo '== DRM connectors'
for d in /sys/class/drm/card0-*; do
    [ -d "$d" ] || continue
    echo "==$d"
    for f in status enabled dpms; do
        if [ -r "$d/$f" ]; then echo "$f"; cat "$d/$f"; fi
    done
done
echo '== backlight state'
for d in /sys/class/backlight/*; do
    [ -d "$d" ] || continue
    echo "==$d"
    for f in bl_power brightness actual_brightness; do
        if [ -r "$d/$f" ]; then echo "$f"; cat "$d/$f"; fi
    done
done
echo '== regulators'
for r in /sys/class/regulator/regulator.*; do
    [ -d "$r" ] || continue
    echo "==$r"
    for f in name state num_users microvolts; do
        if [ -r "$r/$f" ]; then echo "$f"; cat "$r/$f"; fi
    done
done
echo '== GPIO line metadata (not voltage or pin level)'
if command -v gpioinfo >/dev/null 2>&1; then
    gpioinfo gpiochip0
else
    echo 'GPIOINFO_UNAVAILABLE'
fi
echo '== SNAPSHOT_END'
'@
    $snapshot=Read-RootSnapshot 'black-sysfs' $sysfs
    $record['snapshot_end_seen']=$snapshot.Contains('== SNAPSHOT_END')
    $record['marker_counts']=[ordered]@{
        R97_DIAG=([regex]::Matches($kernel,'R97_DIAG')).Count
        R104_POWER_ON=([regex]::Matches($kernel,'R104_PANEL_DEAD_POWER_ON')).Count
        R104_POWER_OFF=([regex]::Matches($kernel,'R104_PANEL_DEAD_POWER_OFF')).Count
        PANEL_DEAD=([regex]::Matches($kernel,'PANEL_DEAD')).Count
        INIT_9D=([regex]::Matches($kernel,'0x9D')).Count
        REK_FAILED=([regex]::Matches($kernel,'R94_NATIVE_COMPLETE_REK_FAILED')).Count
        R107_UNBLANK_FAILED=([regex]::Matches($kernel,'R107_NATIVE_UNBLANK_FAILED')).Count
    }
    $record['capture_complete']=($results.Count -eq 2 -and
        @($results | Where-Object {$_.timed_out -or $_.exit_code -ne 0}).Count -eq 0 -and
        $kernel.Length -gt 0 -and $record['snapshot_end_seen'])
} catch {
    $record['error']=$_.Exception.Message
    throw
} finally {
    $record['steps']=@($results.ToArray())
    $record['finished']=Get-Date -Format o
    [IO.File]::WriteAllText((Join-Path $OutputDirectory 'capture.json'),($record | ConvertTo-Json -Depth 6),$encoding)
    Write-Host ('Capture saved: '+$OutputDirectory)
    Write-Host 'Incomplete/failed captures and missing markers are not a hardware diagnosis.'
}
