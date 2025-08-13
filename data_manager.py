import os
import json
import random
import shutil
import zipfile
import requests
from config import DATA_DIR, GITHUB_ZIP_URL, TODAY_CACHE_FILE
from utils import get_today_str, save_json, load_json, append_history


class DataManager:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.base_dir = os.path.join(self.data_dir, "chinese-poetry-master")
        self.poems = {}  # 体裁名 -> list of poems
        self.today_date = None
        self.today_poem = None
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.base_dir) or not os.listdir(self.base_dir):
            self.download_and_extract_data()
        self.load_all_poems()
        self.load_today_cache()

    def download_and_extract_data(self):
        print("Downloading poetry data...")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        r = requests.get(GITHUB_ZIP_URL)
        zip_path = os.path.join(self.data_dir, "poetry.zip")
        with open(zip_path, "wb") as f:
            f.write(r.content)
        print("Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.data_dir)
        os.remove(zip_path)
        print("Download and extraction finished.")

    def load_all_poems(self):
        # 只加载中文目录（排除纯英文目录）
        for d in os.listdir(self.base_dir):
            if all(ord(c) < 128 for c in d):  # 纯英文文件夹跳过
                continue
            dir_path = os.path.join(self.base_dir, d)
            if not os.path.isdir(dir_path):
                continue
            poems_list = []
            for fname in os.listdir(dir_path):
                if fname.endswith(".json") and not fname.startswith("authors"):
                    fpath = os.path.join(dir_path, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            poems_list.extend(data)
                    except Exception as e:
                        print(f"加载文件{fpath}出错：{e}")
            self.poems[d] = poems_list
        if not self.poems:
            print("警告：未加载到任何诗词数据！")

    def get_random_poem(self, category="all"):
        if category == "all":
            all_poems = []
            for poems in self.poems.values():
                all_poems.extend(poems)
        else:
            all_poems = self.poems.get(category, [])
        if not all_poems:
            return None
        return random.choice(all_poems)

    def get_today_poem(self, category="all"):
        today = get_today_str()
        if self.today_date == today and self.today_poem and self.today_poem.get("category") == category:
            return self.today_poem.get("poem")
        poem = self.get_random_poem(category)
        self.today_poem = {"date": today, "poem": poem, "category": category}
        self.today_date = today
        self.save_today_cache()
        if poem:
            title = poem.get("title") or poem.get("rhythmic") or "未知"
            author = poem.get("author", "未知")
            first_line = poem.get("paragraphs", [""])[0]
            append_history(today, title, author, first_line)
        return poem

    def save_today_cache(self):
        try:
            save_json(os.path.join(self.data_dir, TODAY_CACHE_FILE), self.today_poem)
        except Exception as e:
            print(f"保存今日诗词缓存失败: {e}")

    def load_today_cache(self):
        data = load_json(os.path.join(self.data_dir, TODAY_CACHE_FILE))
        if data and data.get("date") == get_today_str():
            self.today_poem = data
            self.today_date = data.get("date")
        else:
            self.today_poem = None
            self.today_date = None
