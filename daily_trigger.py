from PyQt5.QtCore import QTimer, QTime, QDate
import os


class DailyTrigger:
    def __init__(self, manager, show_poem_callback, trigger_time="09:00"):
        self.manager = manager
        self.show_poem_callback = show_poem_callback
        self.trigger_time = QTime.fromString(trigger_time, "HH:mm")
        self.last_trigger_date = ""
        self.load_last_date()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_time)
        self.timer.start(1000)

    def load_last_date(self):
        if os.path.exists("last_trigger.txt"):
            with open("last_trigger.txt", "r", encoding="utf-8") as f:
                self.last_trigger_date = f.read().strip()

    def save_last_date(self, date_str):
        with open("last_trigger.txt", "w", encoding="utf-8") as f:
            f.write(date_str)
        self.last_trigger_date = date_str

    def check_time(self):
        now = QTime.currentTime()
        today = QDate.currentDate().toString("yyyy-MM-dd")

        if today != self.last_trigger_date and now >= self.trigger_time:
            self.show_poem_callback()
            self.save_last_date(today)
