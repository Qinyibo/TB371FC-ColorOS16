#requires -Version 5.1
[CmdletBinding()]
param([switch]$Execute,[switch]$Clean,[switch]$Reboot,[switch]$CheckDevice,
      [string]$FastbootPath='', [string]$Serial='')
$ErrorActionPreference='Stop'
$PSNativeCommandUseErrorActionPreference=$false
if(![Environment]::Is64BitOperatingSystem -or $env:PROCESSOR_ARCHITECTURE -eq 'ARM64'){throw '本包配套工具要求 Windows 10/11 x64。'}
$packetRoot=Split-Path -Parent $PSScriptRoot
$manifest=Get-Content -LiteralPath (Join-Path $packetRoot 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$wipeUserdata = ($true -eq $manifest.wipe_userdata)
if($manifest.state -notin @('OFFLINE_VERIFIED_DEVICE_PENDING','DEVICE_VERIFIED')) {throw 'ROM 未完成离线核验。'}
if(!$FastbootPath){$FastbootPath=Join-Path $packetRoot 'tools/fastboot.exe'}
$logFolder=Join-Path $packetRoot ('attempt-logs/'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $logFolder -Force | Out-Null
$script:logPath=Join-Path $logFolder 'fastboot.txt'
function Write-Record([string]$Message) {
    ((Get-Date -Format 'o')+' '+$Message) | Out-File -LiteralPath $script:logPath -Append -Encoding utf8
    Write-Host $Message
}
function Get-Sha256([string]$Path) {
    $hash=[Security.Cryptography.SHA256]::Create()
    $stream=[IO.File]::OpenRead($Path)
    try { return ([BitConverter]::ToString($hash.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
    finally { $stream.Dispose(); $hash.Dispose() }
}
$script:completedCommands=New-Object 'System.Collections.Generic.List[string]'
function Write-StepState([string]$State,[string[]]$Command,[string]$Detail='') {
    [ordered]@{state=$State;time=(Get-Date -Format o);serial=$Serial;command=@($Command);detail=$Detail;
        completed_commands=@($script:completedCommands.ToArray());android_boot_verified=$false} |
        ConvertTo-Json -Depth 5 | Out-File -LiteralPath (Join-Path $logFolder 'attempt-status.json') -Encoding utf8
}
function Invoke-CheckedFastboot {
    param([string[]]$Arguments,[switch]$AllowUnsupportedBatteryQuery,[switch]$AllowUnsupportedModeQuery,[switch]$Enumeration)
    if($AllowUnsupportedBatteryQuery -and ($Arguments.Count -ne 2 -or $Arguments[0] -ne 'getvar' -or $Arguments[1] -ne 'battery-soc-ok')) {
        throw '仅允许识别 battery-soc-ok 查询的不支持返回。'
    }
    if($AllowUnsupportedModeQuery -and ($Arguments.Count -ne 2 -or $Arguments[0] -ne 'getvar' -or $Arguments[1] -ne 'is-userspace')) {
        throw '仅允许识别 is-userspace 查询的明确不支持返回。'
    }
    if($AllowUnsupportedModeQuery -and $AllowUnsupportedBatteryQuery){throw '不允许组合可选查询。'}
    if($Enumeration -and ($Arguments.Count -ne 1 -or $Arguments[0] -ne 'devices')){throw '枚举只允许 devices。'}
    Write-Record ('开始 '+($Arguments -join ' '))
    Write-StepState 'running' $Arguments
    $allArguments=if($Enumeration){@('devices')}else{@('-s',$Serial)+$Arguments}
    # Execute directly, with quoted Windows argv (no command shell). Stream both
    # channels and stop on disconnect/hang instead of waiting forever.
    $quoted=@($allArguments | ForEach-Object {
        if($_.Contains('"')){throw '参数包含不支持的引号。'}
        '"'+($_ -replace '(\\+)$','$1$1')+'"'
    })
    $info=New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName=$FastbootPath; $info.Arguments=$quoted -join ' '
    $info.UseShellExecute=$false; $info.CreateNoWindow=$true
    $info.RedirectStandardOutput=$true; $info.RedirectStandardError=$true
    $proc=New-Object System.Diagnostics.Process
    $proc.StartInfo=$info
    $lines=New-Object 'System.Collections.Generic.List[string]'
    $timeout=if($Enumeration){15}elseif($Arguments[0] -eq 'flash'){900}else{60}
    $watch=[Diagnostics.Stopwatch]::StartNew()
    try {
        if(!$proc.Start()){throw 'fastboot 启动失败。'}
        $stdout=$proc.StandardOutput.ReadLineAsync(); $stderr=$proc.StandardError.ReadLineAsync()
        while($null -ne $stdout -or $null -ne $stderr){
            if($watch.Elapsed.TotalSeconds -gt $timeout){
                if(!$proc.HasExited){$proc.Kill()}
                throw 'USB 命令超时，停止后续写入。保留日志，检查连接后处理，脚本不会自动重试。'
            }
            foreach($streamName in @('stdout','stderr')){
                $task=Get-Variable -Name $streamName -ValueOnly
                if($null -ne $task -and $task.IsCompleted){
                    $line=$task.GetAwaiter().GetResult()
                    if($null -eq $line){Set-Variable -Name $streamName -Value $null}
                    else {
                        $lines.Add($line); Write-Record $line
                        $reader=if($streamName -eq 'stdout'){$proc.StandardOutput}else{$proc.StandardError}
                        Set-Variable -Name $streamName -Value ($reader.ReadLineAsync())
                    }
                }
            }
            Start-Sleep -Milliseconds 30
        }
        if(!$proc.WaitForExit(5000)){ $proc.Kill(); throw 'fastboot 未正常退出。' }
        $code=$proc.ExitCode
    } catch {
        $failureDetail=$_.Exception.Message
        try {if(!$proc.HasExited){$proc.Kill()}} catch {}
        Write-StepState 'command_failed' $Arguments $failureDetail
        throw
    } finally { $proc.Dispose() }
    $output=$lines -join "`n"
    Write-Record ("结束 exit=$code")
    if($AllowUnsupportedBatteryQuery -or $AllowUnsupportedModeQuery) {
        # Only this exact remote response is optional. Transport errors, extra
        # diagnostics, malformed values, and actual flash failures stay fatal.
        $diagnosticLines=@($lines | Where-Object { $_.Trim() -ne '' -and $_ -notmatch '^Finished\. Total time: [0-9.]+s\s*$' })
        $optionalName=if($AllowUnsupportedBatteryQuery){'battery-soc-ok'}else{'is-userspace'}
        $unsupportedPattern='(?i)^\s*(?:getvar:'+ [regex]::Escape($optionalName) +'\s+)?FAILED\s+\(remote:\s*[''"]unknown command[''"]\)\s*$' 
        if($code -in @(0,1) -and $diagnosticLines.Count -eq 1 -and $diagnosticLines[0] -match $unsupportedPattern) {
            if($AllowUnsupportedBatteryQuery){Write-Record '设备不支持 battery-soc-ok；未验证实际电量。正式刷入前必须人工确认。'}
            else{Write-Record '设备明确返回不支持 is-userspace；仍须通过型号、解锁、槽位、容量等检查。'}
            Write-StepState 'optional_query_unsupported' $Arguments
            return $null
        }
    }
    if($code -ne 0 -or $output -match '(?im)\bFAILED\b|error:|volume is full') {
        Write-StepState 'command_failed' $Arguments $output
        throw '命令失败，停止后续操作；详见 attempt-status.json，未自动重试或补刷。'
    }
    $script:completedCommands.Add(($Arguments -join ' '))
    Write-StepState 'command_ok' $Arguments
    return $output
}
function Read-Var([string]$Name) {
    $output=Invoke-CheckedFastboot @('getvar',$Name)
    $match=[regex]::Match($output,'(?im)^\s*(?:\(bootloader\)\s*)?'+[regex]::Escape($Name)+':\s*(\S+)')
    if(!$match.Success){throw "设备变量读取失败：$Name"}
    return $match.Groups[1].Value.ToLowerInvariant()
}
function Read-VarSafe([string]$Name) {
    if($Name -ne 'is-userspace'){throw '模式查询名称异常。'}
    $output=Invoke-CheckedFastboot -Arguments @('getvar',$Name) -AllowUnsupportedModeQuery
    if([string]::IsNullOrEmpty($output)){return ''}
    $match=[regex]::Match($output,'(?im)^\s*(?:\(bootloader\)\s*)?is-userspace:\s*(\S+)')
    if(!$match.Success -or $match.Groups[1].Value.ToLowerInvariant() -notin @('yes','no')){throw '模式查询返回异常，停止。'}
    return $match.Groups[1].Value.ToLowerInvariant()
}
function Require-Size([string]$Name,[long]$Expected) {
    $v=Read-Var "partition-size:$Name"
    $size=if($v.StartsWith('0x')){[Convert]::ToInt64($v.Substring(2),16)}else{[long]$v}
    if($size -ne $Expected){throw "$Name 容量不符：$size"}
}
$verified=@{}
foreach($image in $manifest.images){
    if($image.packaged -eq 'parts-only'){
        if($image.name -ne 'super'){throw 'parts-only 打包方式仅允许用于 super。'}
        Write-Record 'super 按 385 分块打包，整镜像文件不在包内；完整性由逐分块哈希和 source_sha256 绑定保证。'
        continue
    }
    $path=Join-Path $packetRoot $image.path
    if(!(Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Item -LiteralPath $path).Length -ne $image.bytes){throw "镜像缺失或大小不符：$($image.name)"}
    if((Get-Sha256 $path) -ne $image.sha256){throw "镜像哈希不符：$($image.name)"}
    $verified[$image.name]=$path; Write-Record "镜像核验通过：$($image.name)"
}
foreach($tool in @($manifest.tools)+@($manifest.accessories)){
    if($null -eq $tool){continue}
    $path=Join-Path $packetRoot $tool.path
    if(!(Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Sha256 $path) -ne $tool.sha256){throw "配套工具核验失败：$($tool.path)"}
}
foreach($n in @('boot','vbmeta','vbmeta_system')){if(!$verified.ContainsKey($n)){throw "清单缺少 $n"}}
if(!(@($manifest.images | Where-Object { $_.name -eq 'super' }).Count)){throw '清单缺少 super 定义'}
if(!$Execute -and !$CheckDevice){Write-Record '文件核验完成，未连接或修改平板。';return}
if($Execute -and $wipeUserdata -and !$Clean){throw '清单要求清空 userdata；执行必须明确指定 -Clean。'}
if($Execute -and !$wipeUserdata){Write-Record '清单 wipe_userdata=false：完整刷入 super/boot/vbmeta，不清 userdata/metadata。'}
if($Execute -and $wipeUserdata -and $Clean){Write-Record '清单 wipe_userdata=true 且已指定 -Clean：将 erase userdata/metadata。'}
if(!(Test-Path -LiteralPath $FastbootPath -PathType Leaf)){throw 'fastboot 工具不存在。'}
$attached=@((Invoke-CheckedFastboot -Arguments @('devices') -Enumeration) -split "`n")
$targets=@($attached | ForEach-Object {
    if($_ -match '^\s*(\S+)\s+fastboot\s*$'){$Matches[1]}
})
if($targets.Count -eq 0){throw '没有发现 fastboot 设备。先运行连接检查，确认引导模式、数据线及 WinUSB 驱动。'}
if(!$Serial){
    if($targets.Count -ne 1){throw '同时连接了多台设备，请仅保留目标平板。'}
    $Serial=$targets[0]
}
if($Serial -notmatch '^[A-Za-z0-9._-]+$' -or $Serial -notin $targets){throw '指定序列号未在 fastboot 设备列表中找到。'}
Write-Record "已选择当前连接设备：$Serial"
$userspace=Read-VarSafe 'is-userspace'
if($userspace -eq 'yes'){throw '当前为 fastbootd。请进入 bootloader fastboot 后再运行。'}
if($userspace -eq ''){Write-Record 'is-userspace 未提供模式信息；继续执行其余必需检查，任何失败都停止。'}
if((Read-Var 'product') -ne 'spinel'){throw '设备型号不符。'}
if((Read-Var 'unlocked') -ne 'yes'){throw '设备未解锁。'}
if((Read-Var 'current-slot') -ne 'a'){throw '当前不是 A 槽，停止。'}
$batteryNeedsConfirmation=$false
$batteryOutput=Invoke-CheckedFastboot -Arguments @('getvar','battery-soc-ok') -AllowUnsupportedBatteryQuery
if([string]::IsNullOrEmpty($batteryOutput)) {
    $batteryNeedsConfirmation=$true
} else {
    $batteryMatch=[regex]::Match($batteryOutput,'(?im)^\s*(?:\(bootloader\)\s*)?battery-soc-ok:\s*(\S+)')
    if(!$batteryMatch.Success){throw '电量查询返回异常，停止。'}
    if($batteryMatch.Groups[1].Value.ToLowerInvariant() -ne 'yes'){throw '引导程序未报告电量充足，停止。'}
}
Require-Size 'super' 12884901888
Require-Size 'boot_a' 100663296
Require-Size 'vbmeta_a' 65536
Require-Size 'vbmeta_system_a' 65536
Require-Size 'metadata' 16777216
$downloadText=Read-Var 'max-download-size'
$downloadMax=0L
try {
    if($downloadText -match '^0x[0-9a-f]+$'){$downloadMax=[Convert]::ToInt64($downloadText.Substring(2),16)}
    elseif($downloadText -match '^[0-9]+$'){$downloadMax=[long]$downloadText}
    else{throw '格式错误'}
} catch {throw '下载缓冲区上限返回异常，停止。'}
if($downloadMax -lt 2097152){throw '下载缓冲区上限缺失或过小，停止。'}
Write-Record ('设备报告下载缓冲区 '+$downloadMax+' 字节；采用已预拆分的 32 MiB 稀疏镜像。')
$userdata=Read-Var 'partition-size:userdata' 
if($userdata -notmatch '^(?:0x[0-9a-f]+|[0-9]+)$'){throw 'userdata 容量异常。'}
if(!$Execute){
    if($batteryNeedsConfirmation){Write-Record '文件、连接、型号、解锁状态、槽位和容量检查通过；本机不支持电量查询，电量未验证。请先确认电量至少50%，正式刷入时需输入 CHARGED。未刷写或清空数据。'}
    else{Write-Record '文件、连接、型号、解锁状态、槽位、容量和电量检查通过。未刷写或清空数据。'}
    return
}
if($batteryNeedsConfirmation){
    $batteryConfirm=Read-Host '请先在系统或可靠电量显示中确认本机至少50%电量；确认后输入 CHARGED，无法确认则直接回车退出'
    if($batteryConfirm -cne 'CHARGED'){throw '未确认实际电量，停止，未开始刷写。'}
    Write-Record '用户输入 CHARGED，确认实际电量至少50%；引导程序无法提供电量核验。'
}
Write-Record '已核对指定平板、容量、槽位及电量，开始完整 ROM 刷入（按清单决定是否清 userdata）。'
$partsDir=Join-Path $packetRoot 'super-parts-32m'
$partsManifest=Get-Content -LiteralPath (Join-Path $partsDir 'manifest.json') -Raw | ConvertFrom-Json
$superEntry=@($manifest.images | Where-Object { $_.name -eq 'super' })[0]
if($partsManifest.format -ne 'android-sparse-contiguous-exact-v1' -or $partsManifest.source_sha256 -ne $superEntry.sha256 -or [long]$partsManifest.expanded_size -ne [long]$superEntry.bytes){throw 'Prepared super parts do not match the verified ROM.'}
$parts=@($partsManifest.parts)
$cursor=0L
for($i=0; $i -lt $parts.Count; $i++){
    $part=$parts[$i]
    if($part.file -ne ('super.part{0:D4}.sparse.img' -f $i) -or [long]$part.start -ne $cursor -or [long]$part.raw_bytes -le 0 -or [long]$part.size -gt 33554432 -or [long]$part.size -gt $downloadMax){throw "Invalid super part manifest entry $i."}
    $cursor += [long]$part.raw_bytes
}
if($cursor -ne [long]$superEntry.bytes){throw 'Super parts do not cover the complete partition.'}
$checkpoint=Join-Path $packetRoot 'super-parts-progress.json'
$next=0
if(Test-Path -LiteralPath $checkpoint){
    $saved=Get-Content -LiteralPath $checkpoint -Raw | ConvertFrom-Json
    if($saved.serial -ne $Serial -or $saved.source_sha256 -ne $superEntry.sha256 -or [int]$saved.next_index -lt 0 -or [int]$saved.next_index -gt $parts.Count){throw 'Super checkpoint does not match this device and ROM.'}
    $next=[int]$saved.next_index
    Write-Record ("从已确认的分块断点恢复：下一块 {0}，总数 {1}。期间若另行刷过 super，应先移走断点记录。" -f ($next+1),$parts.Count)
}
for($i=$next; $i -lt $parts.Count; $i++){
    $part=$parts[$i]
    $path=Join-Path $partsDir $part.file
    if((Get-Item -LiteralPath $path).Length -ne [long]$part.size -or (Get-Sha256 $path) -ne $part.sha256){throw "Super part verification failed at index $i."}
    Write-Record ("super part {0}/{1}" -f ($i+1),$parts.Count)
    $result=Invoke-CheckedFastboot @('flash','super',$path)
    if($result -notmatch "(?im)^\s*Writing 'super'.*OKAY"){throw "Super 写入未确认，停在分块 $i。"}
    $tmp=$checkpoint+'.tmp'
    @{serial=$Serial;source_sha256=$superEntry.sha256;next_index=$i+1} | ConvertTo-Json -Compress | Set-Content -LiteralPath $tmp -Encoding UTF8
    Move-Item -LiteralPath $tmp -Destination $checkpoint -Force
}
Write-Record 'ALL_SUPER_PARTS_FLASHED_OK'
Invoke-CheckedFastboot @('flash','vbmeta_a',$verified['vbmeta']) | Out-Null
Invoke-CheckedFastboot @('flash','vbmeta_system_a',$verified['vbmeta_system']) | Out-Null
Invoke-CheckedFastboot @('flash','boot_a',$verified['boot']) | Out-Null
if($wipeUserdata){
    Invoke-CheckedFastboot @('erase','userdata') | Out-Null
    Invoke-CheckedFastboot @('erase','metadata') | Out-Null
} else {
    Write-Record '跳过 erase userdata/metadata（wipe_userdata=false）'
}
Invoke-CheckedFastboot @('set_active','a') | Out-Null
if((Read-Var 'current-slot') -ne 'a'){throw 'A 槽激活失败。'}
if((Read-Var 'slot-unbootable:a') -ne 'no'){throw 'A 槽仍不可启动。'}
$retry=Read-Var 'slot-retry-count:a'
if($retry -notmatch '^[0-9]+$' -or [long]$retry -le 0){throw 'A 槽启动重试次数异常。'}
Write-StepState 'images_and_wipe_complete_slot_verified' @()
Write-Record "镜像、数据清除和 A 槽检查完成，剩余启动重试次数：$retry；Android 启动尚未验收。"
Move-Item -LiteralPath $checkpoint -Destination (Join-Path $logFolder 'super-parts-complete.json')
if($Reboot){Invoke-CheckedFastboot @('reboot') | Out-Null; Write-StepState 'reboot_sent_android_pending' @('reboot'); Write-Record '已发送重启，等待首次开机引导；实际开机结果需另行验收。'}
else{Write-StepState 'complete_no_reboot_android_pending' @(); Write-Record '保持 fastboot，尚未重启。'}
