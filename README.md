# 校园网自动登录与热点管理工具

一款自动化的校园网登录和热点管理工具，支持Windows系统，能够自动检测网络状态、登录校园网、管理WiFi热点。

## 功能特性

### 🎯 核心功能

- **自动登录校园网**: 监控网络状态，自动登录portal.sicau.edu.cn
- **热点自动管理**: 
  - 网络断开时自动关闭热点
  - 网络恢复时自动开启热点
  - 支持手动控制热点开关
- **真实IP获取**: 在虚拟网卡环境下自动获取真实的物理网卡IP地址
- **日志记录**: 完整的日志记录功能，便于故障排查

### ⚙️ 智能特性

- **热点保活开关**: 通过y/n输入实时控制热点保活功能
- **虚拟网卡识别**: 自动识别并排除虚拟网卡，获取真实IP
- **多级回退机制**: IP获取失败时自动尝试多种方案
- **实时状态显示**: 命令行界面显示网络状态、热点状态等信息

## 系统要求

- Windows 10/11
- Python 3.8+
- PowerShell 5.1+
- 网络连接（校园网）

## 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd PythonProject
```

### 2. 安装Python依赖

```bash
pip install requests
```

### 3. 配置执行策略（PowerShell）

```powershell
# 推荐使用RemoteSigned策略
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. 首次运行配置

首次运行时，程序会提示输入校园网账号和密码：

```bash
python campus_login.py
```

输入后会自动保存到 `campus_net.conf` 文件中。

## 使用方法

### 基本使用

```bash
python campus_login.py
```

### 程序界面

运行程序后会显示以下界面：

```
[2026-05-15 21:59:31] 校园网自动登录程序已启动，监控间隔：15秒
当前账号：202502163
按 Ctrl+C 可以停止程序
输入 y 开启热点保活，输入 n 关闭热点保活
--------------------------------------------------
[2026-05-15 21:59:31] 🔍 检测网络: ✅已认证；📶 热点: ✅；💤等待15秒...
```

### 热点保活控制

- 输入 `y` - 开启热点保活（程序会自动检测并恢复热点）
- 输入 `n` - 关闭热点保活（程序会关闭热点，不再自动管理）

### 日志查看

日志文件位于 `campus_login.log`，包含详细的调试信息。

## 项目文件

```
PythonProject/
├── campus_login.py          # 主程序
├── campus_net.conf          # 配置文件（账号密码）
├── campus_login.log         # 日志文件
├── open_hotspot.ps1        # 开启热点脚本
├── close_hotspot.ps1       # 关闭热点脚本
└── get_real_ip.ps1         # 获取真实IP脚本
```

## 工作流程

### 网络检测流程

1. 程序每隔15秒检测网络连接状态
2. 访问目标网站判断是否需要登录
3. 如果需要登录，自动执行登录流程
4. 登录成功后继续监控

### 热点管理流程

1. **网络断开时**:
   - 检测到目标网址无法访问
   - 自动关闭热点（如果开启）
   - 尝试登录校园网
   - 登录失败则等待后重试

2. **网络恢复时**:
   - 检测到网络已认证
   - 如果开启热点保活，自动开启热点
   - 如果关闭热点保活，只显示状态不操作

3. **手动控制**:
   - 输入 `y` 开启热点保活
   - 输入 `n` 关闭热点保活

### 真实IP获取流程

1. 通过socket获取当前IP
2. 检测是否为代理/VPN虚拟IP
3. 如果是，调用PowerShell脚本获取真实IP
4. 排除虚拟网卡，返回物理网卡IP
5. 所有方法失败时使用默认IP

## 故障排查

### 常见问题

#### 1. 登录失败

**症状**: 程序反复提示登录失败

**解决方法**:
- 检查账号密码是否正确
- 检查网络连接是否正常
- 查看日志文件 `campus_login.log` 获取详细信息

#### 2. 无法获取真实IP

**症状**: 在使用VPN或虚拟网卡时，获取到的IP不正确

**解决方法**:
- 确保 `get_real_ip.ps1` 脚本可以正常运行
- 检查PowerShell执行策略配置
- 手动运行脚本测试：`powershell -ExecutionPolicy Bypass -File get_real_ip.ps1`

#### 3. 热点无法开启

**症状**: 程序提示热点开启失败

**解决方法**:
- 确保以管理员权限运行程序
- 检查 `open_hotspot.ps1` 脚本是否存在
- 检查Windows热点功能是否可用

#### 4. 热点状态检测不准确

**症状**: 热点状态显示不正确

**解决方法**:
- 检查网络适配器是否正常工作
- 查看日志中的详细状态信息
- 重启网络适配器

### 调试模式

查看详细日志：

```bash
# 实时查看日志
Get-Content campus_login.log -Wait -Tail 50
```

测试PowerShell脚本：

```powershell
# 测试获取IP脚本
powershell -ExecutionPolicy Bypass -File get_real_ip.ps1

# 测试开启热点脚本
powershell -ExecutionPolicy Bypass -File open_hotspot.ps1

# 测试关闭热点脚本
powershell -ExecutionPolicy Bypass -File close_hotspot.ps1
```

## 技术细节

### IP获取策略

1. **主策略**: socket方法（最快）
2. **备选策略**: PowerShell脚本（最准确）
3. **回退策略**: NetIPAddress命令
4. **默认策略**: 硬编码IP

### 虚拟网卡识别

排除以下类型的网卡：
- Virtual*
- VMware*
- VirtualBox*
- Hyper-V*
- vEthernet*
- WSL*
- Loopback

### 日志级别

- DEBUG: 详细信息（IP获取过程）
- INFO: 正常运行信息
- WARNING: 警告信息（代理IP检测）
- ERROR: 错误信息（登录失败）

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 作者

Your Name

## 更新日志

### v2.0.0 (2026-05-15)

- ✨ 新增真实IP获取功能（虚拟网卡环境下）
- 🔧 优化热点状态检测机制
- 📝 完善日志记录功能
- 🎨 改进命令行界面显示

### v1.0.0 (2026-04-11)

- 🎉 初始版本发布
- ✅ 实现校园网自动登录
- ✅ 实现热点自动管理
- ✅ 实现手动热点开关控制

## 联系方式

- GitHub Issues: [项目地址](<repository-url>)

## 致谢

- [requests库](https://docs.python-requests.org/) - Python HTTP库
- [PowerShell](https://docs.microsoft.com/powershell/) - Windows自动化工具
