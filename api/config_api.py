import json
import os
import sys

proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_root not in sys.path:
    sys.path.append(proj_root)
from kernel.global_var import GlabalVar as GB

class ConfigAPI:
    """ユーザーがコマンドやショートカットから叩く Python API"""
    def __init__(self, app_instance):
        self.app = app_instance

    def set_editor_config(self, item, value):
        """エディタの設定を動的に変更する"""
        setattr(self.app.editor, item, value)
        if "editor" not in self.app.config:
            self.app.config["editor"] = {}
        self.app.config["editor"][item] = value
        with open(os.path.join(GB.BASE_DIR, "config.json"), 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log(f"Editor config updated: {item} : {value}")

    def set_editor_theme(self, theme_dict, overwrite=False):
        """エディタのテーマを動的に変更する"""
        if "theme" not in self.app.config:
            self.app.config["theme"] = {}
        if overwrite:
            self.app.config["theme"] = theme_dict
        else:
            for k, v in theme_dict.items():
                self.app.config["theme"][k] = v
        with open(os.path.join(GB.BASE_DIR, "config.json"), 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log("Editor theme updated.")

    def set_alias(self, alias, command):
        """コマンドエイリアスを追加・更新する"""
        if "aliases" not in self.app.config:
            self.app.config["aliases"] = {}
        self.app.config["aliases"][alias] = command
        with open(os.path.join(GB.BASE_DIR, "config.json"), 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log(f"Alias set: {alias} : {command}")

    def set_keybind(self, key_combo, command):
        """キーバインドを追加・更新する"""
        if "shortcuts" not in self.app.config:
            self.app.config["shortcuts"] = {}
        self.app.config["shortcuts"][key_combo] = command
        with open(os.path.join(GB.BASE_DIR, "config.json"), 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log(f"Keybind set: {key_combo} : {command}")