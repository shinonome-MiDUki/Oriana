import pickle
import json
from pathlib import Path

from oriana.kernel.global_var import GlabalVar as GB

class MemoryOperation:
    @classmethod
    def swap_out(cls, data, cache_path):
        """データをファイルに保存してメモリから削除する"""
        with open(cache_path, "wb") as f:
            pickle.dump(data, f)
        del data

    @classmethod
    def swap_in(cls, cache_path):
        """ファイルからデータを読み込んでメモリに戻す"""
        with open(cache_path, "rb") as f:
            data = pickle.load(f)
        return data
    
    @classmethod
    def clear_cache(cls):
        cache_dir = Path(GB.DATA_DIR) / ".shelf_cache"
        for file in cache_dir.glob("*.pkl"):
            file.unlink()
        with open(cache_dir / "shelf.json", 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)