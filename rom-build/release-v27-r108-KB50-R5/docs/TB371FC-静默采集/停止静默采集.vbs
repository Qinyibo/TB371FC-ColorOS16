Option Explicit
On Error Resume Next
Dim fso, shell, file
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
shell.RegDelete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run\TB371FCWakeLogger"
If Not fso.FolderExists("D:\TB371FC-wake-logs") Then fso.CreateFolder "D:\TB371FC-wake-logs"
Set file = fso.CreateTextFile("D:\TB371FC-wake-logs\stop.request", True)
file.WriteLine "stop"
file.Close
