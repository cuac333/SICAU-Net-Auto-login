@echo off
chcp 65001 >nul
echo 正在设置开机自启...

:: 获取启动文件夹路径
set "startup_folder=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "bat_path=%~dp0启动校园网.bat"

:: 用 PowerShell 创建快捷方式
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%startup_folder%\校园网自动登录.lnk'); $sc.TargetPath = '%bat_path%'; $sc.WorkingDirectory = '%~dp0'; $sc.Save()"

if %errorlevel% equ 0 (
    echo 设置成功！开机将自动启动校园网登录程序。
    echo 快捷方式位置：%startup_folder%\校园网自动登录.lnk
) else (
    echo 设置失败，请尝试手动操作。
    echo 手动方法：按 Win+R，输入 shell:startup，将"启动校园网.bat"的快捷方式复制到打开的文件夹中。
)
pause
