#requires -Version 5.1
param([ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9._:-]*$')][string]$Serial)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$adb = Join-Path $root 'tools/adb.exe'
$apk = Join-Path $root 'assets/root/Magisk-v31.1.apk'
$manager = 'com.topjohnwu.magisk'
$expectedVersion = 31100
$expectedHash = '89cefac0a318afa39fb3880c45c87b036c05bc1ebf02a7a715b7f8d7c26ac6e7'

function Invoke-Adb([string[]]$AdbArguments) {
    $output = & $adb @AdbArguments
    if ($LASTEXITCODE -ne 0) { throw "ADB 操作失败，退出码 $LASTEXITCODE。" }
    $output
}

if (!(Test-Path -LiteralPath $adb -PathType Leaf) -or !(Test-Path -LiteralPath $apk -PathType Leaf)) {
    throw '请从已完整解压的 ROM 目录运行安装入口。'
}
if ((Get-FileHash -LiteralPath $apk -Algorithm SHA256).Hash -ne $expectedHash) {
    throw 'Magisk 官方 APK 的 SHA-256 校验失败。'
}

$devices = @(Invoke-Adb @('devices') | ForEach-Object {
    if ($_ -match '^([a-zA-Z0-9][a-zA-Z0-9._:-]*)\s+device\s*$') { $Matches[1] }
})
if (!$Serial) {
    if ($devices.Count -ne 1) { throw '请只连接一台已授权 USB 调试的平板。' }
    $Serial = $devices[0]
}
if ($devices -notcontains $Serial) { throw '指定平板未连接或尚未授权调试。' }
$target = @(Invoke-Adb @('-s', $Serial, 'shell', 'getprop ro.product.board; getprop sys.boot_completed'))
if (($target -join '|') -ne 'spinel|1') { throw '仅支持已完成启动的 TB371FC。' }

$systemPackages = @(Invoke-Adb @('-s', $Serial, 'shell', 'pm', 'list', 'packages', '-s', '-u', $manager))
if ($systemPackages -contains "package:$manager") { throw '系统分区仍含 Magisk 管理器，请先换用 R2 或更新的 ROM。' }
$before = (Invoke-Adb @('-s', $Serial, 'shell', 'dumpsys', 'package', $manager)) -join "`n"
if ($before -match '\bversionCode=(\d+)\b' -and [long]$Matches[1] -gt $expectedVersion) {
    throw '平板已安装更高版本的 Magisk，保留当前版本。'
}

Write-Host '请留意平板上的 ColorOS 安装确认。若出现安全验证，请在平板上完成后继续。'
$result = @(Invoke-Adb @('-s', $Serial, 'install', '-r', '--user', '0', $apk))
if ($result -notcontains 'Success') { throw 'Android 未确认安装成功。' }
$path = Invoke-Adb @('-s', $Serial, 'shell', 'pm', 'path', '--user', '0', $manager)
$after = (Invoke-Adb @('-s', $Serial, 'shell', 'dumpsys', 'package', $manager)) -join "`n"
if ($path -notmatch '^package:/data/app/.+/base\.apk$' -or
    $after -notmatch "\bversionCode=$expectedVersion\b" -or $after -match '\bpkgFlags=\[[^\r\n\]]*\bSYSTEM\b') {
    throw '无法确认 Magisk 31.1 已安装为普通用户应用。'
}
Write-Host 'Magisk 31.1 已安装为普通用户应用。请在平板上打开 Magisk。'
