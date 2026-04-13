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
    