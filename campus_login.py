import sys
import subprocess

try:
    import requests
except ImportError:
    print("错误：缺少 requests 模块")
    print("请运行以下命令安装：")
    print("pip install requests")
    sys.exit(1)

import configparser
import os
import time
import socket
import threading
from datetime import datetime
# 禁用SSL警告（校园网证书可能不规范）
try:
    requests.packages.urllib3.disable_warnings()
except:
    pass

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campus_net.conf")


class CampusNetAutoLogin:
    def __init__(self):
        # 初始化配置
        self.count = 0
        self.config = configparser.ConfigParser()
        self.load_config()

        # 热点保活开关（从配置文件读取或首次运行时设置）
        self.auth_url = "https://portal.sicau.edu.cn/webauth.do"
        self.base_params = {
            "wlanuserip": "",  # 会自动获取
            "wlanacname": "YA-XX-Bras01-ME60-X8A",
            "nasip": "5.5.5.13",
            "pageid": "201",
            "templatetype": "1",
            "isRemind": "1",
            "loginType": "",
            "auth_type": "0",
            "isBindMac1": "0",
            "listqqauth": "",
            "listwbauth": "",
            "listwxauth": "0",
            "listtwiceauth": "0",
            "listbindmac": "0",
            "recordmac": "0",
            "listgetpass": "0",
            "areaId": "0",
            "logoutflag": "2",
            "scheme": "https",
            "serverIp": "portal.sicau.edu.cn:443",
            "hostIp": "http://127.0.0.1:8446/",
            "distoken": "86e8c6548e872544104b898383b5d67d"
        }
        
        # 启动输入监听线程
        self.start_input_listener()

    def load_config(self):
        """加载配置文件（账号密码）"""
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE, encoding="utf-8")
            self.username = self.config.get("USER_INFO", "username", fallback="")
            self.password = self.config.get("USER_INFO", "password", fallback="")
            self.hotspot_keepalive = self.config.get("USER_INFO", "hotspot_keepalive", fallback="N").upper() == "Y"
        else:
            # 首次运行，提示输入账号密码并保存
            self.username = input("请输入校园网账号：")
            self.password = input("请输入校园网密码：")
            hotspot_choice = input("是否开启热点保活？(Y/N)：").strip().upper()
            self.hotspot_keepalive = (hotspot_choice == "Y")
            self.config["USER_INFO"] = {
                "username": self.username,
                "password": self.password,
                "hotspot_keepalive": "Y" if self.hotspot_keepalive else "N"
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                self.config.write(f)
            print(f"账号密码已保存至：{CONFIG_FILE}")

    def get_local_ip(self):
        """获取本机内网IP（对应wlanuserip参数）"""
        try:
            # 创建UDP连接获取本机IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            print(f"获取本机IP失败：{e}")
            return "10.23.167.52"  # 使用默认IP

    def check_network(self):
        """检测网络是否已认证（访问外网判断）"""
        test_urls = ["https://www.jetbrains.com","https://www.bilibili.com"] #"https://www.bilibili.com"
        timeout = 3 
        for url in test_urls:
            try:
                response = requests.head(url, timeout=timeout, verify=False)
                if response.status_code == 200:
                    return True  # 网络已认证
            except requests.exceptions.Timeout:
                print(f"网络检测超时：{url}")
                continue
            except requests.exceptions.ConnectionError:
                print(f"网络连接失败：{url}")
                continue
            except Exception as e:
                print(f"网络检测异常：{url} - {str(e)}")
                continue
        return False  # 未认证/网络异常

    def login(self):
        """执行校园网登录"""
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始登录流程...")
            
            # 更新动态参数
            self.base_params["wlanuserip"] = self.get_local_ip()
            print(f"获取到本地IP：{self.base_params['wlanuserip']}")
            
            # 构造登录表单数据
            login_data = {
                **self.base_params,
                "userId": self.username,
                "passwd": self.password,
                "act": "login"
            }

            # 发送登录请求
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://portal.sicau.edu.cn/",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            print("正在发送登录请求...")
            response = requests.post(
                self.auth_url,
                data=login_data,
                headers=headers,
                verify=False,
                timeout=10
            )
            print(f"服务器响应状态码：{response.status_code}")

            # 验证登录结果
            print("正在验证登录状态...")
            if self.check_network():
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 登录成功！")
                return True
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 登录失败")
                print(f"服务器响应内容：{response.text[:500]}")
                return False

        except requests.exceptions.Timeout:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  登录请求超时")
            return False
        except requests.exceptions.ConnectionError:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️  网络连接错误")
            return False
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 登录异常：{str(e)}")
            return False

    def run_monitor(self, interval=30, fail_retry=3):
        """运行监控程序，定时检测并登录"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 校园网自动登录程序已启动，监控间隔：{interval}秒")
        print(f"当前账号：{self.username}")
        print("按 Ctrl+C 可以停止程序")
        print("输入 y 开启热点保活，输入 n 关闭热点保活")
        print("-" * 50)

        try:
            while True:
                
                print(f"\r[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 检测网络:",end=' ',flush=True)
                if not self.check_network():
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🌐 检测到网络未认证，准备登录...")
                    # 网络断开时，关闭热点
                    status = self.check_hotspot_status()
                    if status:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📶 网络断开，正在关闭热点...")
                        self.close_hotspot()
                    success = self.login()
                    if not success:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 💤 等待{fail_retry}秒后重试...")
                        time.sleep(fail_retry)
                    print()  # 空行分隔
                else:
                    print(f"✅已认证；",end='',flush=True)
                    # 检查并保持热点开启
                    self.check_and_keep_hotspot()
                    print(f"💤等待{interval}秒...",end='',flush=True)
                    time.sleep(interval)
                    self.update_count(interval)
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 程序已手动停止")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 程序异常终止：{str(e)}")

    def start_input_listener(self):
        """启动输入监听线程"""
        def listen_for_input():
            while True:
                try:
                    user_input = input().strip().lower()
                    if user_input == 'y':
                        self.hotspot_keepalive = True
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 热点保活已开启")
                    elif user_input == 'n':
                        self.hotspot_keepalive = False
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 热点保活已关闭")
                        # 调用一次close_hotspot.ps1关闭热点
                        self.close_hotspot()
                except:
                    pass
        
        input_thread = threading.Thread(target=listen_for_input, daemon=True)
        input_thread.start()
    
    def check_hotspot_status(self):
        """检查热点状态"""
        try:
            # 执行PowerShell命令直接检查热点状态
            cmd = "$connectionProfile = [Windows.Networking.Connectivity.NetworkInformation,Windows.Networking.Connectivity,ContentType=WindowsRuntime]::GetInternetConnectionProfile(); $tetheringManager = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime]::CreateFromConnectionProfile($connectionProfile); $tetheringManager.TetheringOperationalState"
            result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True, check=True)
            # 状态值1或"On"表示已开启，0或"Off"表示已关闭
            status_output = result.stdout.strip()
            return "1" in status_output or "On" in status_output
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检查热点状态时出错: {e}")
            return False
    
    def open_hotspot(self):
        """打开热点"""
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "open_hotspot.ps1")
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 打开热点时出错: {e}")
            return False
    
    def close_hotspot(self):
        """关闭热点"""
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "close_hotspot.ps1")
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 关闭热点时出错: {e}")
            return False
    
    def check_and_keep_hotspot(self):
        """检查并保持热点开启"""
        # 每次执行都打印热点状态
        status = self.check_hotspot_status()
        print(f"📶 热点: {'✅' if status else '❌'}；",end='',flush=True)
        
        if self.hotspot_keepalive:
            if not status:
                print("热点未开启，正在尝试打开...",flush=True)
                success = self.open_hotspot()
                if success:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 热点已成功打开✅！")
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 打开热点失败，请检查脚本权限或网络设置。")
    
    def update_count(self, interval=30):
        if self.count >= 240*24*7:
            self.count = 0
            os.system('cls')
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 控制台输出已清空，监控间隔：{interval}秒")
            print(f"当前账号：{self.username}")
            print("按 Ctrl+C 可以停止程序")
            print("输入 y 开启热点保活，输入 n 关闭热点保活")
            print("-" * 50)
            return
        self.count += 1



if __name__ == "__main__":
    # 创建登录实例
    auto_login = CampusNetAutoLogin()

    # 运行监控程序（间隔15秒检测一次）
    auto_login.run_monitor(interval=15)