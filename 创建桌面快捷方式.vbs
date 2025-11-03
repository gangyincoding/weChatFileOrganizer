' 创建桌面快捷方式的VBScript脚本
Set WshShell = CreateObject("WScript.Shell")
Set oShortcut = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") & "\微信文件整理器.lnk")

' 设置快捷方式属性
oShortcut.TargetPath = WshShell.CurrentDirectory & "\微信文件整理器.bat"
oShortcut.WorkingDirectory = WshShell.CurrentDirectory
oShortcut.Description = "微信文件整理器 - 自动整理微信文件"
oShortcut.IconLocation = "%windir%\System32\shell32.dll,171"  ' 使用文件夹图标

' 保存快捷方式
oShortcut.Save

MsgBox "桌面快捷方式已创建成功！" & vbCrLf & vbCrLf & "请在桌面查找 '微信文件整理器' 快捷方式", vbInformation, "创建完成"