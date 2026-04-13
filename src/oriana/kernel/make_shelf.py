import json
import os

class MakeShelf:
    def __init__(self, shelf_cache_dir):
        self.sheld_cache_dir = shelf_cache_dir

    def make_shelf(self):
        """キャッシュディレクトリ作成"""
        if not os.path.exists(self.sheld_cache_dir):
            os.mkdir(self.sheld_cache_dir)
        with open(os.path.join(self.sheld_cache_dir, "shelf.json"), 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)