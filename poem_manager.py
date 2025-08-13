import os
import json
import random
import re
import datetime
import zipfile
import io
import requests

class PoemManager:
    def __init__(self):
        self.base_path = os.path.join("data", "chinese-poetry-master")
        self.history_file = "history.log"
        self.ensure_data()
        self.poems = []
        self.load_all_poems()

    def ensure_data(self):
        if not os.path.exists(self.base_path):
            print("未检测到数据文件夹，正在下载 chinese-poetry 数据...")
            url = "https://github.com/chinese-poetry/chinese-poetry/archive/refs/heads/master.zip"
            r = requests.get(url)
            r.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                z.extractall("data")

            print("数据下载完成！")

    def load_all_poems(self):
        # 只加载符合诗词文件命名规范的json，排除作者等文件
        pattern = re.compile(r'^(ci|poetry|song|tang|yuan|ming|qing)\..*\.json$', re.I)
        poems = []

        for root, _, files in os.walk(self.base_path):
            for file in files:
                if pattern.match(file):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                for item in data:
                                    if "paragraphs" in item and isinstance(item["paragraphs"], list):
                                        title = item.get("title") or item.get("rhythmic") or ""
                                        author = item.get("author", "")
                                        paragraphs = item["paragraphs"]
                                        poems.append({
                                            "title": title,
                                            "author": author,
                                            "paragraphs": paragraphs,
                                            "file_path": file_path
                                        })
                    except Exception as e:
                        print(f"读取文件失败: {file_path}，错误: {e}")

        self.poems = poems
        print(f"共加载诗词条目：{len(self.poems)}")

    def get_random_poem(self, genre_filter=None):
        filtered = self.poems
        if genre_filter:
            # 简单用文件路径中包含关键词过滤
            filtered = [p for p in self.poems if genre_filter.lower() in p["file_path"].lower()]
            if not filtered:
                filtered = self.poems  # 过滤后空则使用全部

        if not filtered:
            return None

        poem = random.choice(filtered)
        if poem:
            self.save_history(poem)
        return poem

    def save_history(self, poem):
        if not poem:
            return
        first_line = poem["paragraphs"][0] if poem["paragraphs"] else ""
        line = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t{poem.get('file_path','')}\t{poem.get('title','')}\t{poem.get('author','')}\t{first_line}\n"
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(line)

    def get_today_poem(self, genre_filter=None):
        poem = self.get_random_poem(genre_filter)
        return poem
