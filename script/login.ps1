# ================== 引用程序集 ==================
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName System.Windows.Forms

# ================== 鼠标点击工具 ==================
Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Mouse {
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);

    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, IntPtr dwExtraInfo);

    public const uint LEFTDOWN = 0x0002;
    public const uint LEFTUP   = 0x0004;
}
"@

# ================== 窗口前台工具 ==================
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
  [DllImport("user32.dll")]
  public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@

# ================== 通用：点击 Text ==================
function Click-ByText {
    param(
        [Parameter(Mandatory)]
        [string]$Text
    )

    $element = $window.FindFirst(
        [System.Windows.Automation.TreeScope]::Subtree,
        (New-Object System.Windows.Automation.AndCondition(
            (New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::NameProperty,
                $Text
            )),
            (New-Object System.Windows.Automation.PropertyCondition(
                [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
                [System.Windows.Automation.ControlType]::Text
            ))
        ))
    )

    if (-not $element) {
        throw "未找到文本：$Text"
    }

    try {
        $pt = $element.GetClickablePoint()
        $x = [int]$pt.X
        $y = [int]$pt.Y
    }
    catch {
        $rect = $element.Current.BoundingRectangle
        if ($rect.Width -le 0 -or $rect.Height -le 0) {
            throw "无法点击文本：$Text"
        }
        $x = [int](($rect.Left + $rect.Right) / 2)
        $y = [int](($rect.Top + $rect.Bottom) / 2)
    }

    [Mouse]::SetCursorPos($x, $y)
    Start-Sleep -Milliseconds 60
    [Mouse]::mouse_event([Mouse]::LEFTDOWN, 0, 0, 0, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 60
    [Mouse]::mouse_event([Mouse]::LEFTUP, 0, 0, 0, [IntPtr]::Zero)
}

# ================== 1. 找窗口 ==================
$desktop = [System.Windows.Automation.AutomationElement]::RootElement

$window = $desktop.FindFirst(
    [System.Windows.Automation.TreeScope]::Children,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::NameProperty,
        "Texas Holdem Poker!"
    ))
)

# if (-not $window) {
#     throw "未找到 Texas Holdem Poker! 窗口"
#     # 不往下执行
#     Exit
# }
if (-not $window) {
    Write-Error "未找到 Texas Holdem Poker! 窗口"
    Read-Host "按回车键退出"
    return
}


# ================== 2. 强制前台 ==================
$hwnd = $window.Current.NativeWindowHandle
[Win32]::SetForegroundWindow([IntPtr]$hwnd)
Start-Sleep -Milliseconds 400

# ================== 3. 找所有 Edit ==================
$edits = $window.FindAll(
    [System.Windows.Automation.TreeScope]::Subtree,
    (New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit
    ))
)

# 可写 Edit
$writeableEdits = $edits | Where-Object {
    $_.TryGetCurrentPattern(
        [System.Windows.Automation.ValuePattern]::Pattern,
        [ref]$null
    ) -and
    $_.GetCurrentPattern(
        [System.Windows.Automation.ValuePattern]::Pattern
    ).Current.IsReadOnly -eq $false
}

if ($writeableEdits.Count -lt 2) {
    throw "未找到足够的输入框"
}

# ================== 4. 输入邮箱 ==================
$edit1 = $writeableEdits[0]
$edit1.SetFocus()
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("^a")
[System.Windows.Forms.SendKeys]::SendWait("{BACKSPACE}")
[System.Windows.Forms.SendKeys]::SendWait("lionels@gmail.com")

# ================== 5. 输入密码 ==================
Start-Sleep -Milliseconds 300
$edit2 = $writeableEdits[1]
$edit2.SetFocus()
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("^a")
[System.Windows.Forms.SendKeys]::SendWait("{BACKSPACE}")
[System.Windows.Forms.SendKeys]::SendWait("a123456")

# ================== 6. 点击【用户登录】 ==================
Start-Sleep -Milliseconds 500
Click-ByText "用户登录"
