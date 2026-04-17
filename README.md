# 四川农业大学校园网自动登录 + 热点保活

川农校园网自动登录程序，支持热点保活功能。

## 功能特点

- 自动检测校园网连接状态
- 登录成功后自动重连
- 热点保活功能（可选）
- 配置文件保存账号密码
- 开机自启支持

## 文件说明

- `campus_login.py` - 主程序（带热点保活）
- `open_hotspot.ps1` - 打开热点脚本
- `close_hotspot.ps1` - 关闭热点脚本
- `campus_net.conf` - 配置文件（自动生成）
- `启动校园网.bat` - 一键启动批处理文件

## 首次使用

1. 安装依赖：`pip install requests`
2. 启动程序（二选一）：
   - 双击 `启动校园网.bat`
   - 命令行运行 `python campus_login.py`
3. 输入校园网账号密码
4. 选择是否开启热点保活（Y/N）

## 热点保活

开启后，当网络断开重连时会自动打开热点，确保其他设备能正常联网。

运行时输入 `y` 开启热点保活，输入 `n` 关闭热点保活。

## 环境要求

- Python 3.x（[下载地址](https://www.python.org/downloads/)）
- Windows 系统
- 已连接校园网 WiFi
- Python 依赖库：`requests`（安装命令：`pip install requests`）
