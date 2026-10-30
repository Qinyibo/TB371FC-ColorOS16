#requires -Version 5.1
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$out=Join-Path $root ('attempt-logs/connection-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $out -Force | Out-Null
function Inspect-Tool([string]$Name) {
    $path=Join-Path $root ('tools/'+$Name+'.exe')
    $psi=New-Object Diagnostics.ProcessStartInfo
    $psi.FileName=$path; $psi.Arguments='devices -l'; $psi.UseShellExecute=$false; $psi.CreateNoWindow=$true
    $psi.RedirectStandardOutput=$true; $psi.RedirectStandardError=$true
    $p=New-Object Diagnostics.Process; $p.StartInfo=$psi
    try {
        if(!$p.Start()){throw ('无法启动 '+$Name)}
        $a=$p.StandardOutput.ReadToEndAsync();$b=$p.StandardError.ReadToEndAsync()
        if(!$p.WaitForExit(15000)){
            $p.Kill();$p.WaitForExit(2000)|Out-Null
            throw ($Name+' 枚举超过15秒，已停止该进程；本检查不会刷写。')
        }
        $text=$a.GetAwaiter().GetResult()+$b.GetAwaiter().GetResult()
        $text | Out-File -LiteralPath (Join-Path $out ($Name+'.txt')) -Encoding utf8
        Write-Host $text
        if($p.ExitCode -ne 0 -or $text -match '(?im)\bFAILED\b|error:'){throw ($Name+' 枚举失败。')}
    } catch {
        $_ | Out-String | Out-File -LiteralPath (Join-Path $out ($Name+'-error.txt')) -Encoding utf8
        Write-Host $_ -ForegroundColor Red
        $script:toolFailure=$true
    } finally {$p.Dispose()}
}
Write-Host '只读连接检查：不重启、不刷写、不修改驱动或注册表。每个工具限15秒。'
$script:toolFailure=$false
Inspect-Tool fastboot
Inspect-Tool adb
$androidGuid='{F72FE0D4-CBCB-407D-8814-9ED673D0DD6B}'
$inventory=@()
Get-PnpDevice -PresentOnly | Where-Object {$_.InstanceId -match '^USB\\VID_(17EF|18D1|05C6|22D9)(?=&|\\|$)'} | ForEach-Object {
    $node=$_
    $properties=@(Get-PnpDeviceProperty -InstanceId $node.InstanceId -KeyName 'DEVPKEY_Device_HardwareIds','DEVPKEY_Device_Service','DEVPKEY_Device_DriverInfPath' -ErrorAction SilentlyContinue | Select-Object KeyName,Data)
    $key='Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\'+$node.InstanceId+'\Device Parameters'
    $guids=@();$readable=$true
    try {$guids=@((Get-ItemProperty -LiteralPath $key -Name DeviceInterfaceGUIDs -ErrorAction Stop).DeviceInterfaceGUIDs)} catch {$readable=$false}
    $record=[ordered]@{instance_id=$node.InstanceId;status=[string]$node.Status;name=$node.FriendlyName;properties=$properties;
        interface_guids_readable=$readable;interface_guids=$guids;android_guid_present=$(if($readable){$guids -contains $androidGuid}else{$null})}
    $inventory+=$record
    $record | ConvertTo-Json -Depth 5 | Write-Host
}
ConvertTo-Json -InputObject @($inventory) -Depth 7 | Out-File -LiteralPath (Join-Path $out 'usb-interface-inventory.json') -Encoding utf8
Write-Host ('匹配的USB节点数：'+$inventory.Count+'；枚举无错误不代表设备已连接。')
Write-Host ('记录位置：'+$out)
Write-Host '有USB设备但fastboot列表为空时，核对目标接口的WinUSB绑定和Android接口GUID；读取不到GUID不等于缺失。不要改ClassGUID或批量卸载驱动。'
Write-Host 'USB3下查询/传输不稳，可用可靠USB2数据链路对照。连接检查不代替完整刷前检查。'
if($script:toolFailure){exit 1}
