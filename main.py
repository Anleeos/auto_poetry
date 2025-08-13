import sys
from PyQt5.QtWidgets import QApplication
from tray import PoetryTray
from poem_manager import PoemManager
from daily_trigger import DailyTrigger
from ui_main import PoemWindow


def main():
    app = QApplication(sys.argv)

    manager = PoemManager()
    win = PoemWindow()

    tray = PoetryTray(
        show_today_callback=lambda: win.show_poem(manager.get_today_poem()),
        show_next_callback=lambda: win.show_poem(manager.get_random_poem()),
        quit_callback=lambda: sys.exit(),
        app=app
    )

    def show_poem():
        poem = manager.get_today_poem()
        win.show_poem(poem)

    def show_random_poem():
        poem = manager.get_random_poem()
        win.show_poem(poem)

    win.next_callback = show_random_poem

    win.show_poem(manager.get_today_poem())

    DailyTrigger(manager, show_poem, trigger_time="09:00")  # 每天 9 点触发

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
