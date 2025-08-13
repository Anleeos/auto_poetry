import datetime
import os
import json


def get_today_str():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def is_past_time(time_str):
    now = datetime.datetime.now().time()
    h, m = map(int, time_str.split(":"))
    target = datetime.time(hour=h, minute=m)
    return now >= target


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def append_history(date, title, author, first_line):
    line = f"{date}|{title}|{author}|{first_line}\n"
    with open("history.txt", "a", encoding="utf-8") as f:
        f.write(line)


def save_config(data, filename="config.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def load_config(filename="config.json"):
    if not os.path.exists(filename):
        return {}
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
