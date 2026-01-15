import sys
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame, QAbstractItemView, QListView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QCursor

# 导入配置模块
import powerShellManager
from translations import TRANSLATIONS
from themes import THEMES
from styles import generate_stylesheet


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
        t = TRANSLATIONS[self.lang]
        self.log(f"{t['log_lang_changed']} {self.lang.upper()}")

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
        """应用主题样式"""
        theme_colors = THEMES[theme_name]
        stylesheet = generate_stylesheet(theme_colors, theme_name)
        self.setStyleSheet(stylesheet)

    def log(self, text):
        now = time.strftime("%H:%M:%S")
        self.log_view.append(f"<span style='color:gray;'>[{now}]</span> {text}")
        # 自动滚动到底部
        self.log_view.ensureCursorVisible()

    # --- 逻辑处理 ---
    def on_start(self):
        t = TRANSLATIONS[self.lang]
        self.log(f"<b>{t['log_start']}</b>")
        powerShellManager.start_app()
        QTimer.singleShot(1000, lambda: self.log(t['log_ready']))

    def on_clear(self):
        t = TRANSLATIONS[self.lang]
        self.log(t['log_clean'])
        powerShellManager.clear_cache()
        QTimer.singleShot(800, lambda: self.log(f"<span style='color:green;'>{t['log_success']}</span>"))

    def on_login(self):
        t = TRANSLATIONS[self.lang]
        accounts = powerShellManager.load_accounts()
        acc_len = len(accounts)
        acc = accounts[self.current_acc_idx]
        if self.current_acc_idx >= acc_len:
          print("当前账号已达到最大值")
          return
        powerShellManager.go_login(acc)
        self.current_acc_idx = (self.current_acc_idx + 1) % acc_len
        self.log(f"{t['log_login']} <b style='color:#f1c40f;'>{acc['username']}</b>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())