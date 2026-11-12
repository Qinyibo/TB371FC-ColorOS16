Option Explicit
On Error Resume Next
Dim fso, shell, folder, python, command, stopFile
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
folder = fso.GetParentFolderName(WScript.ScriptFullName)
python = "C:\Users\Administrator\AppData\Local\Programs\DeepSeek Harness\resources\runtime\primary-runtime\dependencies\python\pythonw.exe"
stopFile = "D:\TB371FC-wake-logs\stop.request"
If fso.FileExists(stopFile) Then fso.DeleteFile stopFile, True
command = Chr(34) & python & Chr(34) & " " & Chr(34) & folder & "\wake_logger.py" & Chr(34) & " --config " & Chr(34) & folder & "\config.json" & Chr(34)
shell.RegWrite "HKCU\Software\Microsoft\Windows\CurrentVersion\Run\TB371FCWakeLogger", command, "REG_SZ"
shell.Run command, 0, False
