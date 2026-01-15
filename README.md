# Texas Hold'em Online 登录辅助工具 (Login Tools)

这是一个基于 PySide6 开发的 Windows 桌面应用程序，用于辅助管理和登录 "39674HytoGame.TexasHoldemOnline" (UWP) 应用。

## 功能特性

- **一键启动**：快速启动德州扑克 UWP 应用。
- **清除数据**：一键清理应用缓存、重置状态并关闭相关进程。
- **自动登录**：支持从 `accounts` 目录加载多个账号，并自动填充邮箱、密码完成登录过程。
- **多语言支持**：内置中英文界面切换。
- **主题切换**：提供多种界面主题色方案（极客蓝、活力橙、典雅金等）。

## 环境要求

- Windows 10/11 (由于涉及 UWP 应用操作和 PowerShell 脚本)
- Python 3.8+
- [PySide6](https://pypi.org/project/PySide6/)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置账号

在项目根目录下创建 `accounts` 文件夹，并添加 `.json` 格式的账号文件：

```json
[
  {
    "username": "账号A",
    "email": "userA@example.com"
  },
  {
    "username": "账号B",
    "email": "userB@example.com"
  }
]
```

### 3. 运行程序

```bash
python index.py
```
或者直接运行：
```bash
./run.bat
```

## 项目结构

- `index.py`: 程序主入口，UI 逻辑。
- `powerShellManager.py`: 后台操作核心，封装了应用启动、清理和 UI 自动化登录逻辑。
- `translations.py`: 国际化翻译文件。
- `themes.py` & `styles.py`: 主题与 CSS 样式管理。
- `script/`: 存放底层的 PowerShell 脚本 (`.ps1`)。

## 打包为可执行文件 (.exe)

如果你想将程序打包为独立运行的 `.exe` 文件：

```bash
pyinstaller index.spec
```
或者直接运行：
```bash
./build.bat
```
打包完成后，生成的程序将位于 `dist/` 目录下。

## 注意事项

- 程序运行需要 PowerShell 脚本执行权限。
- 自动登录功能依赖于 UI Automation，请确保登录窗口在前台显示。
