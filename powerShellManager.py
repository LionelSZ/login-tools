import subprocess
import os
import json
APP_NAME = "39674HytoGame.TexasHoldemOnline"


class PowerShellSession:
    def __init__(self):
        self.ps = subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

    def run(self, script: str):
        self.ps.stdin.write(script + "\n")
        self.ps.stdin.write("Write-Output '__END__'\n")
        self.ps.stdin.flush()

        output = []
        while True:
            line = self.ps.stdout.readline()
            if "__END__" in line:
                break
            output.append(line)
        return "".join(output)

    def close(self):
        self.ps.stdin.write("exit\n")
        self.ps.stdin.flush()
ps = PowerShellSession()

def run_ps(script: str):
    # subprocess.run(
    #     ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
    #     check=False
    # )
    return ps.run(script)


def login_str(email: str):
    return f'''
$email = "{email}"

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Windows.Forms

# ================= 鼠标工具 =================
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Mouse {{
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, IntPtr dwExtraInfo);
    public const uint LEFTDOWN = 0x0002;
    public const uint LEFTUP   = 0x0004;
}}
"@

# ================= 前台窗口 =================
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {{
  [DllImport("user32.dll")]
  public static extern bool SetForegroundWindow(IntPtr hWnd);
}}
"@

# ================= 稳定点击函数 =================
function Click-ByText {{
    param([string]$Text)

    $element = $window.FindFirst(
        [System.Windows.Automation.TreeScope]::Subtree,
        (New-Object System.Windows.Automation.PropertyCondition(
            [System.Windows.Automation.AutomationElement]::NameProperty,
            $Text
        ))
    )

    if (-not $element) {{
        throw "未找到文本：$Text"
    }}

    function Get-Point($el) {{
        try {{
            $pt = $el.GetClickablePoint()
            return @{{
                X = [int]$pt.X
                Y = [int]$pt.Y
            }}
        }} catch {{
            $rect = $el.Current.BoundingRectangle
            if ($rect.Width -gt 0 -and $rect.Height -gt 0) {{
                return @{{
                    X = [int](($rect.Left + $rect.Right) / 2)
                    Y = [int](($rect.Top + $rect.Bottom) / 2)
                }}
            }}
        }}
        return $null
    }}

    # 1️⃣ 自己
    $pt = Get-Point $element

    # 2️⃣ 向上找父节点
    if (-not $pt) {{
        $parent = $element
        for ($i = 0; $i -lt 6; $i++) {{
            $parent = [System.Windows.Automation.TreeWalker]::ControlViewWalker.GetParent($parent)
            if (-not $parent) {{ break }}
            $pt = Get-Point $parent
            if ($pt) {{ break }}
        }}
    }}

    if (-not $pt) {{
        throw "无法点击：$Text"
    }}

    [Mouse]::SetCursorPos($pt.X, $pt.Y)
    Start-Sleep -Milliseconds 80
    [Mouse]::mouse_event([Mouse]::LEFTDOWN,0,0,0,[IntPtr]::Zero)
    Start-Sleep -Milliseconds 80
    [Mouse]::mouse_event([Mouse]::LEFTUP,0,0,0,[IntPtr]::Zero)
}}

# ================= 找窗口 =================
$desktop = [System.Windows.Automation.AutomationElement]::RootElement
$window = $desktop.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        "Texas Holdem Poker!"
    ))
)

if (-not $window) {{
    Write-Error "未找到 Texas Holdem Poker! 窗口"
    return
}}

# 前台
[Win32]::SetForegroundWindow([IntPtr]$window.Current.NativeWindowHandle)
Start-Sleep -Milliseconds 500

# ================= 找 Edit 输入框 =================
$edits = $window.FindAll(
    [System.Windows.Automation.TreeScope]::Subtree,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit
    ))
)

$inputs = $edits | Where-Object {{
    $_.TryGetCurrentPattern(
        [System.Windows.Automation.ValuePattern]::Pattern,
        [ref]$null
    ) -and
    $_.GetCurrentPattern(
        [System.Windows.Automation.ValuePattern]::Pattern
    ).Current.IsReadOnly -eq $false
}}

if ($inputs.Count -lt 2) {{
    throw "未找到足够输入框"
}}

# ================= 输入邮箱 =================
$inputs[0].SetFocus()
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("^a")
[System.Windows.Forms.SendKeys]::SendWait("{{BACKSPACE}}")
[System.Windows.Forms.SendKeys]::SendWait($email)

# ================= 输入密码 =================
Start-Sleep -Milliseconds 300
$inputs[1].SetFocus()
[System.Windows.Forms.SendKeys]::SendWait("^a")
[System.Windows.Forms.SendKeys]::SendWait("{{BACKSPACE}}")
[System.Windows.Forms.SendKeys]::SendWait("a123456")

# ================= 点击登录 =================
Start-Sleep -Milliseconds 600
Click-ByText "用户登录"
'''




# ===============================
# 清除 UWP 缓存 + 关闭进程
# ===============================
def clear_cache():
    ps_script = f'''
    $AppName = "{APP_NAME}"

    # 获取包
    $pkg = Get-AppxPackage | Where-Object {{ $_.Name -eq $AppName }}
    if (-not $pkg) {{
        Write-Host "未找到应用：$AppName"
        exit
    }}

    $family = $pkg.PackageFamilyName
    $DataPath = "$env:LOCALAPPDATA\\Packages\\$family"

    # ===============================
    # 1. 强力关闭相关 UWP 进程
    # ===============================
    Get-Process | Where-Object {{
        $_.Name -match "Texas|Unity|ApplicationFrameHost|RuntimeBroker"
    }} | Stop-Process -Force -ErrorAction SilentlyContinue

    # 再兜底 taskkill（比 Stop-Process 狠）
    taskkill /F /IM TexasHoldem* /T 2>$null
    taskkill /F /IM Unity* /T 2>$null

    # 等待系统释放句柄
    Start-Sleep -Seconds 2

    # ===============================
    # 2. 重试清除数据目录
    # ===============================
    for ($i = 0; $i -lt 5; $i++) {{
        if (Test-Path $DataPath) {{
            try {{
                Remove-Item $DataPath -Recurse -Force
                Write-Host "数据清除成功"
                break
            }} catch {{
                Start-Sleep -Milliseconds 800
            }}
        }}
    }}

'''
    print(ps_script)
    run_ps(ps_script)
# def clear_cache():
    # ps_script = f'''
    # $AppName = "{APP_NAME}"

    # $pkg = Get-AppxPackage | Where-Object {{ $_.Name -eq $AppName }}
    # if (-not $pkg) {{
    #     Write-Host "未找到应用：$AppName"
    #     exit
    # }}

    # # 关闭进程
    # Get-Process | Where-Object {{
    #     $_.Path -like "*$($pkg.PackageFamilyName)*"
    # }} | Stop-Process -Force -ErrorAction SilentlyContinue

    # Start-Sleep -Seconds 1

    # # 清除数据
    # $DataPath = "$env:LOCALAPPDATA\\Packages\\$($pkg.PackageFamilyName)"
    # if (Test-Path $DataPath) {{
    #     Remove-Item $DataPath -Recurse -Force
    # }}
    # '''
    # run_ps(ps_script)


# ===============================
# 启动 UWP 应用
# ===============================
def start_app():
    ps_script = f'''
    $AppName = "{APP_NAME}"

    $pkg = Get-AppxPackage | Where-Object {{ $_.Name -eq $AppName }}
    if ($pkg) {{
        Start-Process "shell:AppsFolder\\$($pkg.PackageFamilyName)!App"
    }}
    '''
    run_ps(ps_script)


# ===============================
# 
# ===============================
def load_accounts():
  # 加载accounts文件夹中的所有JSON文件
  accounts = []
  for file in os.listdir("accounts"):
    if file.endswith(".json"):
        with open(f"accounts/{file}", encoding="utf-8") as f:
            jsons = json.load(f)
        for acc in jsons:
            accounts.append(acc)
  return accounts

def go_login(account: dict):
  print("正在登陆账户：", account["email"])
  ps_script = login_str(account["email"])
  # print(ps_script)
  run_ps(ps_script)
  print("登陆成功")




if __name__ == "__main__":
  accounts = load_accounts()
#   acc_len = len(accounts)
#   acc_index = 0
#   print(accounts[acc_index])
#   start_app()
#   go_login(accounts[acc_index])
#   clear_cache()
  