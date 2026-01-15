# ===== QSS 样式生成器 =====

def generate_stylesheet(theme_colors, theme_name):
    """
    根据主题颜色生成完整的 QSS 样式表

    Args:
        theme_colors: 主题颜色字典，包含 bg, panel, text, accent, border 等键
        theme_name: 主题名称，用于判断是否为深色主题

    Returns:
        完整的 QSS 样式字符串
    """
    c = theme_colors
    is_dark = theme_name != "森林护眼 (Eco Green)"
    text_color = c['text']
    accent = c['accent']

    return f"""
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
    """
