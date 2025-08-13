import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QComboBox, QTextEdit,
                             QVBoxLayout, QWidget, QSystemTrayIcon, QMenu, QAction, QLabel, QGraphicsDropShadowEffect,
                             QHBoxLayout)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import QTimer, Qt

import utils
from config import ICON_PATH, POPUP_TIME
from utils import is_past_time
from data_manager import DataManager

CONFIG_FILE = "config.json"


class MainWindow(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self._drag_pos = None
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
        self.resize(600, 350)

        # 主容器，半透明背景，圆角
        self.container = QWidget(self)
        self.container.setStyleSheet("""
                    background-color: rgba(0, 0, 0, 180);
                    border-radius: 12px;
                """)
        self.setCentralWidget(self.container)

        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.combo_category = QComboBox()
        self.combo_category.addItem("全部")
        cats = sorted(self.data_manager.poems.keys())
        self.combo_category.addItems(cats)
        self.combo_category.setStyleSheet("""
                           QComboBox {
                               background: transparent;
                               border: 1px solid rgba(255,255,255,0.6);
                               border-radius: 5px;
                               padding: 5px 10px;
                               color: rgba(255,255,255,0.9);
                               font-weight: bold;
                               font-size: 14px;
                           }
                           QComboBox::drop-down {
                               border: none;
                           }
                           QComboBox QAbstractItemView {
                               background-color: rgba(0, 0, 0, 220);
                               color: white;
                               selection-background-color: rgba(255, 255, 255, 50);
                           }
                       """)

        self.poem_text = QLabel(self)
        self.poem_text.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.poem_text.setAlignment(Qt.AlignCenter)

        self.label = self.poem_text
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setColor(QColor(0, 0, 0, 160))  # 半透明黑色阴影
        shadow.setOffset(1, 1)
        self.label.setGraphicsEffect(shadow)

        self.btn_today = QPushButton("今日诗词")
        self.btn_next = QPushButton("下一首")

        # 按钮样式，透明底，白字带阴影
        for btn in (self.btn_today, self.btn_next):
            btn.setStyleSheet("""
                        QPushButton {
                            background-color: rgba(255, 255, 255, 50);
                            border: none;
                            color: white;
                            font-weight: bold;
                            font-size: 16px;
                            padding: 8px 20px;
                            border-radius: 6px;
                        }
                        QPushButton:hover {
                            background-color: rgba(255, 255, 255, 100);
                        }
                    """)
            # 按钮描边阴影
            b_shadow = QGraphicsDropShadowEffect()
            b_shadow.setBlurRadius(1)
            b_shadow.setColor(QColor(0, 0, 0, 160))
            b_shadow.setOffset(0, 0)
            btn.setGraphicsEffect(b_shadow)

        self.btn_today.clicked.connect(self.show_today_poem)
        self.btn_next.clicked.connect(self.show_next_poem)
        self.combo_category.currentTextChanged.connect(self.category_changed)

        # 关闭按钮
        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(28, 28)
        self.btn_close.setStyleSheet("""
                   QPushButton {
                       background: transparent;
                       color: white;
                       font-weight: bold;
                       font-size: 20px;
                       border: none;
                   }
                   QPushButton:hover {
                       color: red;
                   }
               """)
        # 给关闭按钮加描边（阴影）模拟
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(0)
        shadow.setColor(QColor(0, 0, 0, 255))
        shadow.setOffset(0, 0)
        self.btn_close.setGraphicsEffect(shadow)
        self.btn_close.clicked.connect(self.hide)

        top_bar.addWidget(self.combo_category)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_close)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.label, stretch=1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.addWidget(self.btn_today)
        btn_layout.addWidget(self.btn_next)
        main_layout.addLayout(btn_layout)

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
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 记录点击时，鼠标相对于窗口左上角的位置
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            # 根据鼠标当前位置减去偏移计算窗口新的左上角位置，实现拖动
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            event.accept()
    
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
