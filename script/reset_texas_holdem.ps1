# ===============================
# TexasHoldemOnline 一键清数据 + 重启
# ===============================

$AppName = "39674HytoGame.TexasHoldemOnline"

Write-Host "? 正在查找应用包..."

$pkg = Get-AppxPackage | Where-Object { $_.Name -eq $AppName }

if (-not $pkg) {
    Write-Host "? 未找到应用：$AppName"
    exit 1
}

# -------------------------------
# 1. 关闭正在运行的进程
# -------------------------------
Write-Host "? 关闭应用进程..."

Get-Process | Where-Object {
    $_.Path -like "*$($pkg.PackageFamilyName)*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 1

# -------------------------------
# 2. 清除 UWP 本地数据
# -------------------------------
$DataPath = "$env:LOCALAPPDATA\Packages\$($pkg.PackageFamilyName)"

if (Test-Path $DataPath) {
    Write-Host "? 清除数据目录：$DataPath"
    Remove-Item $DataPath -Recurse -Force
} else {
    Write-Host "? 未发现数据目录，可能已被清理"
}

# -------------------------------
# 3. 重新启动 UWP 应用
# -------------------------------
Write-Host "? 重新启动应用..."

Start-Process "shell:AppsFolder\$($pkg.PackageFamilyName)!App"

Write-Host "? 完成"
