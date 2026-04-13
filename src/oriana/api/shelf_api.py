import json
import os
from pathlib import Path

from oriana.kernel.global_var import GlabalVar as GB
from oriana.kernel.memory_operation import MemoryOperation

class ShelfAPI:
    def __init__(self, app_instance):
        self.app = app_instance

    def shelf(self, name):
        cache_path = Path(GB.DATA_DIR) / ".shelf_cache" / (name + ".pkl")
        MemoryOperation.swap_out(self.app.editor.text, cache_path)
        self.app.editor.text = ""
        with open(Path(GB.DATA_DIR) / ".shelf_cache" / "shelf.json", 'r', encoding='utf-8') as f:
            shelf_data = json.load(f)
        shelf_data[name] = {
            "cache_path": str(cache_path),
            "editing_path": GB.EDITING_PATH,
            "cache_name": name
        }
        with open(Path(GB.DATA_DIR) / ".shelf_cache" / "shelf.json", 'w', encoding='utf-8') as f:
            json.dump(shelf_data, f, indent=4)
        GB.EDITING_PATH = None
        GB.WORKING_SHELF = None
        self.app.log("Current content shelved.")

    def switch_shelf(self, name, discard_current=False):
        with open(Path(GB.DATA_DIR) / ".shelf_cache" / "shelf.json", 'r', encoding='utf-8') as f:
            shelf_data = json.load(f)
        if name in shelf_data:
            if GB.WORKING_SHELF and not discard_current:
                self.shelf(name=GB.WORKING_SHELF)
            data = MemoryOperation.swap_in(shelf_data[name]["cache_path"])
            self.app.editor.text = data
            GB.WORKING_SHELF = name
            GB.EDITING_PATH = shelf_data[name]["editing_path"]
            self.app.log(f"Switched to shelf: {name}")
        else:
            self.app.log(f"Shelf not found: {name}")

    def unshelf(self, name, auto_save=True):
        with open(Path(GB.DATA_DIR) / ".shelf_cache" / "shelf.json", 'r', encoding='utf-8') as f:
            shelf_data = json.load(f)
        if name in shelf_data:
            cache_file = shelf_data[name]["cache_path"]
            if auto_save:
                saved_file = shelf_data[name]["editing_path"]
                if saved_file is None:
                    self.app.log("No editing path associated with this shelf. Please save the shelved content before unshelving.")
                    return
                data = MemoryOperation.swap_in(cache_file)
                with open(saved_file, 'w', encoding='utf-8') as f:
                    f.write(data)
                self.app.log(f"Shelved content saved to: {saved_file}")
            if os.path.exists(cache_file):
                os.unlink(cache_file)
            del shelf_data[name]
            with open(Path(GB.DATA_DIR) / ".shelf_cache" / "shelf.json", 'w', encoding='utf-8') as f:
                json.dump(shelf_data, f, indent=4)
            if GB.WORKING_SHELF == name:
                self.app.editor.text = ""
                GB.WORKING_SHELF = None
                GB.EDITING_PATH = None
            self.app.log(f"Unshelved: {name}")
        else:
            self.app.log(f"Shelf not found: {name}")

    def clear_shelves(self):
        cache_dir = Path(GB.DATA_DIR) / ".shelf_cache"
        for file in cache_dir.glob("*.pkl"):
            file.unlink()
        with open(cache_dir / "shelf.json", 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4)