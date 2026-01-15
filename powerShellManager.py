# v1.1 - Fixed input fields and arguments
import os
import json
import time
import shutil
import psutil
from pywinauto import Desktop, Application
from pywinauto.keyboard import send_keys

APP_NAME = "39674HytoGame.TexasHoldemOnline"

def start_app():
    """启动 UWP 应用"""
    print(f"正在启动应用: {APP_NAME}")
    # UWP 协议启动方式: shell:AppsFolder\PackageFamilyName!App
    # 这里我们通过 powershell 获取一下完整的 PackageFamilyName (仅用于启动，不作为常驻 session)
    try:
        # 获取 PackageFamilyName
        cmd = f'powershell -Command "(Get-AppxPackage -Name {APP_NAME}).PackageFamilyName"'
        family_name = os.popen(cmd).read().strip()
        if family_name:
            os.startfile(f"shell:AppsFolder\\{family_name}!App")
            print("启动指令已发送")
        else:
            print(f"找不到应用: {APP_NAME}")
    except Exception as e:
        print(f"启动失败: {e}")

def clear_cache():
    """清除 UWP 缓存并关闭相关进程"""
    print("正在清理缓存和进程...")
    
    # 1. 关闭相关进程
    target_process_names = ["TexasHoldem", "Unity", "ApplicationFrameHost", "RuntimeBroker"]
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if any(target in name for target in target_process_names):
                print(f"正在关闭进程: {name}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # 2. 清理数据目录
    try:
        cmd = f'powershell -Command "(Get-AppxPackage -Name {APP_NAME}).PackageFamilyName"'
        family_name = os.popen(cmd).read().strip()
        if family_name:
            local_app_data = os.environ.get('LOCALAPPDATA')
            data_path = os.path.join(local_app_data, "Packages", family_name)
            
            if os.path.exists(data_path):
                # 重试机制，防止文件被占用
                for i in range(5):
                    try:
                        shutil.rmtree(data_path)
                        print("数据清理成功")
                        break
                    except Exception:
                        time.sleep(0.8)
            else:
                print(f"路径不存在: {data_path}")
    except Exception as e:
        print(f"清理缓存失败: {e}")

def load_accounts():
    """加载 accounts 文件夹中的所有 JSON 文件"""
    accounts = []
    if not os.path.exists("accounts"):
        return accounts
    for file in os.listdir("accounts"):
        if file.endswith(".json"):
            with open(os.path.join("accounts", file), "r", encoding="utf-8") as f:
                try:
                    jsons = json.load(f)
                    if isinstance(jsons, list):
                        accounts.extend(jsons)
                    else:
                        accounts.append(jsons)
                except json.JSONDecodeError:
                    print(f"无法解析文件: {file}")
    return accounts

def go_login(account: dict):
    """使用 pywinauto 执行登录逻辑"""
    email = account.get("email")
    password = "a123456" # 默认密码
    print(f"正在登录账户: {email}")

    try:
        # 在线程中初始化 COM 
        import pythoncom
        pythoncom.CoInitialize()
        
        # 连接桌面
        desktop = Desktop(backend="uia")
        
        # 等待窗口出现 (最多等待30秒)
        timeout = 30
        start_time = time.time()
        window = None
        
        while time.time() - start_time < timeout:
            try:
                # 使用 title 而不是 name
                window = desktop.window(title="Texas Holdem Poker!")
                if window.exists():
                    break
            except Exception:
                pass
            time.sleep(1)
            
        if not window or not window.exists():
            print("找不到游戏窗口: Texas Holdem Poker!")
            return

        # 置顶窗口
        window.set_focus()
        time.sleep(1)

        # 查找输入框
        all_edits = window.descendants(control_type="Edit")
        # 过滤并排序：按屏幕上的纵轴位置（Top）从上到下排序
        # 根据日志，主输入框宽度约为 560，中间混入了一个 234 的干扰项，所以将阈值调高到 400
        active_edits = [e for e in all_edits if e.is_visible() and e.rectangle().width() > 400]
        edits = sorted(active_edits, key=lambda x: x.rectangle().top)
        
        print(f"找到 {len(all_edits)} 个 Edit 控件，其中有效控件 {len(edits)} 个")
        for i, e in enumerate(edits):
            print(f"  控件 {i}: Top={e.rectangle().top}, Width={e.rectangle().width()}")

        if len(edits) < 2:
            print(f"未找到足够且有效的输入框，当前找到: {len(edits)}")
            return

        # 获取具体的控件对象
        email_field = edits[0]
        pwd_field = edits[1]

        # 输入邮箱
        print(f"步骤 1/2: 正在输入邮箱... (Top: {email_field.rectangle().top})")
        email_field.click_input()
        time.sleep(0.5)
        email_field.type_keys("^a{BACKSPACE}") # 先全选删除
        email_field.type_keys(email, with_spaces=True)
        time.sleep(0.5)

        # 输入密码
        print(f"步骤 2/2: 正在输入密码... (Top: {pwd_field.rectangle().top})")
        pwd_field.click_input()
        time.sleep(0.5)
        pwd_field.type_keys("^a{BACKSPACE}") # 先全选删除
        pwd_field.type_keys(password)
        time.sleep(0.5)

        # 查找并点击登录按钮
        # 使用 title 而名字
        login_btn = window.child_window(title="用户登录", control_type="Button")
        if not login_btn.exists():
            # 尝试直接通过 title 查找
            login_btn = window.child_window(title="用户登录")
            
        if login_btn.exists():
            # 点击登录前再加一个小延迟确保万无一失
            time.sleep(0.1)
            login_btn.click_input()
            print(f"账户 {email} 登录指令已发送")
        else:
            print("未找到'用户登录'按钮")
            
    except Exception as e:
        print(f"登录执行出错: {e}")
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

if __name__ == "__main__":
    # 测试代码
    # accounts = load_accounts()
    # if accounts:
    #     clear_cache()
    #     start_app()
    #     time.sleep(10) # 等待启动
    #     go_login(accounts[0])
    pass
  