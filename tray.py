from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon


class PoetryTray(QSystemTrayIcon):
    def __init__(self, show_today_callback, show_next_callback, quit_callback, app):
        super().__init__(QIcon("icon.png"), app)
        self.menu = QMenu()

        self.menu.addAction("显示今日诗词", show_today_callback)
        self.menu.addAction("下一首", show_next_callback)
        self.menu.addSeparator()
        self.menu.addAction("退出", quit_callback)

        self.setContextMenu(self.menu)
        self.setToolTip("每日诗词")
        self.show()
