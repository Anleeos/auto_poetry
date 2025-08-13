import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QComboBox, QTextEdit,
                             QVBoxLayout, QWidget, QSystemTrayIcon, QMenu, QAction, QLabel)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt

import utils
from config import ICON_PATH, POPUP_TIME
from utils import is_past_time
from data_manager import DataManager

CONFIG_FILE = "config.json"


class MainWindow(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.today_shown = False
        self.init_ui()
        self.init_tray()
        self.check_popup_timer = QTimer()
        self.check_popup_timer.timeout.connect(self.check_popup)
        self.check_popup_timer.start(60000)  # 每分钟检查一次

        # 恢复体裁选择
        config = utils.load_config(CONFIG_FILE)
        saved_cat = config.get("last_category", "全部")
        index = self.combo_category.findText(saved_cat)
        if index >= 0:
            self.combo_category.setCurrentIndex(index)

        # 程序启动时尝试加载并显示今日诗词（确保有内容）
        self.show_today_poem()
        self.today_shown = True

    def init_ui(self):
        self.setWindowTitle("每日古诗词")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(600, 400)

        self.combo_category = QComboBox()
        self.combo_category.addItem("全部")
        cats = sorted(self.data_manager.poems.keys())
        self.combo_category.addItems(cats)

        self.poem_text = QLabel(self)
        self.poem_text.setStyleSheet("""
                    color: rgba(255, 255, 255, 200);
                    font-size: 24px;
                    font-weight: bold;
                """)
        self.poem_text.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.poem_text)

        self.btn_today = QPushButton("今日诗词")
        self.btn_next = QPushButton("下一首")

        self.btn_today.clicked.connect(self.show_today_poem)
        self.btn_next.clicked.connect(self.show_next_poem)
        self.combo_category.currentTextChanged.connect(self.category_changed)

        layout = QVBoxLayout()
        layout.addWidget(self.combo_category)
        layout.addWidget(self.poem_text)
        layout.addWidget(self.btn_today)
        layout.addWidget(self.btn_next)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_tray(self):
        if not QIcon.hasThemeIcon(ICON_PATH):
            self.tray_icon = QSystemTrayIcon(QIcon(ICON_PATH if QIcon(ICON_PATH).availableSizes() else QIcon()), self)
        else:
            self.tray_icon = QSystemTrayIcon(QIcon(ICON_PATH), self)
        self.tray_icon.setToolTip("每日古诗词")

        menu = QMenu()
        today_action = QAction("今日诗词", self)
        next_action = QAction("下一首", self)
        exit_action = QAction("退出", self)

        today_action.triggered.connect(self.show_today_poem)
        next_action.triggered.connect(self.show_next_poem)
        exit_action.triggered.connect(self.exit_app)

        menu.addAction(today_action)
        menu.addAction(next_action)
        menu.addSeparator()
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def current_category(self):
        cat = self.combo_category.currentText()
        return cat if cat != "全部" else "all"

    def show_today_poem(self):
        poem = self.data_manager.get_today_poem(self.current_category())
        self.display_poem(poem)
        self.show()
        self.raise_()
        self.activateWindow()

    def show_next_poem(self):
        poem = self.data_manager.get_random_poem(self.current_category())
        self.display_poem(poem)
        self.show()
        self.raise_()
        self.activateWindow()

    def category_changed(self, _):
        self.show_today_poem()

    def display_poem(self, poem):
        if not poem:
            self.poem_text.setText("暂无诗词数据")
            return
        title = poem.get("title") or poem.get("rhythmic") or "未知"
        author = poem.get("author", "未知")
        paragraphs = poem.get("paragraphs", [])
        content = "\n".join(paragraphs)
        text = f"【{title}】  —— {author}\n\n{content}"
        self.poem_text.setText(text)

    def check_popup(self):
        if not self.today_shown and is_past_time(POPUP_TIME):
            if not self.isVisible():
                self.show_today_poem()
                self.today_shown = True

    def exit_app(self):
        self.tray_icon.hide()
        QApplication.quit()
