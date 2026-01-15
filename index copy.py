import sys
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame, QAbstractItemView,QListView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QCursor

# ===== 1. 国际化数据 =====
TRANSLATIONS = {
    "zh": {
        "window_title": "自动化控制台 v4.0",
        "panel_title": "控制中心",
        "theme_label": "界面主题",
        "lang_label": "语言设置",
        "btn_start": "🚀 启动程序",
        "btn_clear": "🧹 清理缓存",
        "btn_login": "🔑 一键登录",
        "btn_clear_log": "清空日志",
        "log_start": "▶ 引擎启动中...",
        "log_ready": "🚀 系统就绪",
        "log_clean": "🧹 正在清理...",
        "log_success": "✅ 操作完成",
        "log_login": "🔑 正在登录: "
    },
    "en": {
        "window_title": "Automation Console v4.0",
        "panel_title": "CONTROL CENTER",
        "theme_label": "THEME",
        "lang_label": "LANGUAGE",
        "btn_start": "🚀 START SYSTEM",
        "btn_clear": "🧹 CLEAN CACHE",
        "btn_login": "🔑 AUTO LOGIN",
        "btn_clear_log": "CLEAR",
        "log_start": "▶ Starting engine...",
        "log_ready": "🚀 System Ready",
        "log_clean": "🧹 Cleaning...",
        "log_success": "✅ Task Finished",
        "log_login": "🔑 Logging in: "
    }
}

# ===== 2. 主题色彩库 =====
THEMES = {
    "极客深蓝 (Geek Blue)": {
        "bg": "#0f172a", "panel": "#1e293b", "text": "#f8fafc", "accent": "#38bdf8",
        "border": "#334155", "item_hover": "#334155"
    },
    "魅惑紫色 (Cyber Purple)": {
        "bg": "#130f40", "panel": "#30336b", "text": "#ffffff", "accent": "#be2edd",
        "border": "#4834d4", "item_hover": "#4834d4"
    },
    "森林护眼 (Eco Green)": {
        "bg": "#f0f2f0", "panel": "#ffffff", "text": "#2d3436", "accent": "#218c74",
        "border": "#dcdde1", "item_hover": "#f1f2f6"
    }
}

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = "zh"
        self.current_theme = "极客深蓝 (Geek Blue)"
        
        # 初始数据
        self.accounts = [{"username": f"User_{i:02d}"} for i in range(1, 5)]
        self.current_acc_idx = 0
        
        self.init_ui()
        self.update_ui_text()
        self.change_theme(self.current_theme)

    def init_ui(self):
        self.resize(1000, 620)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- 左侧侧边栏 ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(15, 25, 15, 25)
        side_layout.setSpacing(12)

        self.label_title = QLabel()
        self.label_title.setFont(QFont("Arial", 18, QFont.Bold))
        self.label_title.setAlignment(Qt.AlignCenter)

        # 下拉框公用设置
        def setup_combo(combo):
            combo.setCursor(Qt.PointingHandCursor)
            # 使用 QListView 代替 QAbstractItemView
            combo.setView(QListView()) 
            return combo

        # 语言切换
        self.label_lang = QLabel()
        self.combo_lang = setup_combo(QComboBox())
        self.combo_lang.addItems(["简体中文", "English"])
        self.combo_lang.currentIndexChanged.connect(self.switch_language)

        # 主题切换
        self.label_theme = QLabel()
        self.combo_theme = setup_combo(QComboBox())
        self.combo_theme.addItems(THEMES.keys())
        self.combo_theme.currentTextChanged.connect(self.change_theme)

        # 功能按钮
        self.btn_start = QPushButton()
        self.btn_clear = QPushButton()
        self.btn_login = QPushButton()

        for btn in [self.btn_start, self.btn_clear, self.btn_login]:
            btn.setCursor(Qt.PointingHandCursor)

        self.btn_start.clicked.connect(self.on_start)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_login.clicked.connect(self.on_login)

        side_layout.addWidget(self.label_title)
        side_layout.addSpacing(20)
        side_layout.addWidget(self.label_lang)
        side_layout.addWidget(self.combo_lang)
        side_layout.addWidget(self.label_theme)
        side_layout.addWidget(self.combo_theme)
        side_layout.addSpacing(20)
        side_layout.addWidget(self.btn_start)
        side_layout.addWidget(self.btn_clear)
        side_layout.addWidget(self.btn_login)
        side_layout.addStretch()

        # --- 右侧日志区 ---
        right_layout = QVBoxLayout()
        log_bar = QHBoxLayout()
        self.label_log = QLabel("LOGS")
        self.btn_clear_log = QPushButton()
        self.btn_clear_log.setCursor(Qt.PointingHandCursor)
        self.btn_clear_log.setFixedWidth(80)
        self.btn_clear_log.clicked.connect(lambda: self.log_view.clear())
        
        log_bar.addWidget(self.label_log)
        log_bar.addStretch()
        log_bar.addWidget(self.btn_clear_log)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        right_layout.addLayout(log_bar)
        right_layout.addWidget(self.log_view)

        main_layout.addWidget(self.sidebar, 1)
        main_layout.addLayout(right_layout, 3)

    def switch_language(self, index):
        self.lang = "zh" if index == 0 else "en"
        self.update_ui_text()
        self.log(f"Language changed to: {self.lang.upper()}")

    def update_ui_text(self):
        """刷新界面所有文字"""
        t = TRANSLATIONS[self.lang]
        self.setWindowTitle(t["window_title"])
        self.label_title.setText(t["panel_title"])
        self.label_lang.setText(t["lang_label"])
        self.label_theme.setText(t["theme_label"])
        self.btn_start.setText(t["btn_start"])
        self.btn_clear.setText(t["btn_clear"])
        self.btn_login.setText(t["btn_login"])
        self.btn_clear_log.setText(t["btn_clear_log"])

    def change_theme(self, theme_name):
        c = THEMES[theme_name]
        is_dark = theme_name != "森林护眼 (Eco Green)"
        text_color = c['text']
        accent = c['accent']
        
        # 核心 QSS 优化
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg']};
                color: {text_color};
                font-family: "Segoe UI", "Microsoft YaHei";
            }}
            QFrame#sidebar {{
                background-color: {c['panel']};
                border-radius: 15px;
                border: 1px solid {c['border']};
            }}
            /* 自定义下拉框样式 */
            QComboBox {{
                background-color: {c['bg']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 6em;
            }}
            QComboBox:hover {{
                border-color: {accent};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {accent}; /* 自定义箭头 */
                margin-right: 10px;
            }}
            /* 下拉列表视图样式 */
            QComboBox QAbstractItemView {{
                background-color: {c['panel']};
                border: 1px solid {c['border']};
                selection-background-color: {accent};
                selection-color: {c['bg'] if is_dark else '#ffffff'};
                outline: none;
                border-radius: 6px;
                padding: 5px;
            }}
            
            QPushButton {{
                background-color: {c['panel']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }}
            /* 在 change_theme 方法的 QSS 中添加 */
            QPushButton:pressed {{
                background-color: {c['border']};
                padding-top: 14px; /* 向下挤压 2px 模拟点击感 */
                padding-bottom: 10px;
            }}
            QPushButton:hover {{
                background-color: {accent};
                color: {c['bg'] if is_dark else '#ffffff'};
            }}
            QTextEdit {{
                background-color: {c['panel'] if is_dark else '#ffffff'};
                border: 1px solid {c['border']};
                border-radius: 10px;
                font-family: 'Consolas';
                font-size: 13px;
                padding: 10px;
            }}
            QLabel {{
                background: transparent;
                color: {accent};
            }}

            /* 垂直滚动条整体设置 */
            QScrollBar:vertical {{
                border: none;
                background-color: transparent; /* 背景透明，保持简洁 */
                width: 10px;
                margin: 0px 2px 0px 2px;
            }}

            /* 滚动条滑块（手柄） */
            QScrollBar::handle:vertical {{
                background-color: {c['border']}; /* 初始使用边框色 */
                min-height: 30px;
                border-radius: 4px;
            }}

            /* 鼠标悬停在滑块上时加亮 */
            QScrollBar::handle:vertical:hover {{
                background-color: {accent}; /* 悬停时变为主题强调色 */
            }}

            /* 隐藏滚动条顶部的箭头按钮 */
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            /* 隐藏滚动条底部的箭头按钮 */
            QScrollBar::add-line:vertical {{
                height: 0px;
            }}

            /* 滚动条滑块上下的槽部分（背景） */
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

    # def log(self, text):
    #     now = time.strftime("%H:%M:%S")
    #     self.log_view.append(f"<span style='color:gray;'>[{now}]</span> {text}")

    def log(self, text):
        now = time.strftime("%H:%M:%S")
        self.log_view.append(f"<span style='color:gray;'>[{now}]</span> {text}")
        # 自动滚动到底部
        self.log_view.ensureCursorVisible()

    # --- 逻辑处理 ---
    def on_start(self):
        t = TRANSLATIONS[self.lang]
        self.log(f"<b>{t['log_start']}</b>")
        QTimer.singleShot(1000, lambda: self.log(t['log_ready']))

    def on_clear(self):
        t = TRANSLATIONS[self.lang]
        self.log(t['log_clean'])
        QTimer.singleShot(800, lambda: self.log(f"<span style='color:green;'>{t['log_success']}</span>"))

    def on_login(self):
        t = TRANSLATIONS[self.lang]
        acc = self.accounts[self.current_acc_idx]
        self.log(f"{t['log_login']} <b style='color:#f1c40f;'>{acc['username']}</b>")
        self.current_acc_idx = (self.current_acc_idx + 1) % len(self.accounts)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())