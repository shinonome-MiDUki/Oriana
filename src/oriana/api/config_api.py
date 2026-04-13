import json
import os
import sys

from oriana.kernel.global_var import GlabalVar as GB

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
        with open(os.path.join(GB.DATA_DIR, "config.json"), 'w') as f:
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
        with open(os.path.join(GB.DATA_DIR, "config.json"), 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log("Editor theme updated.")

    def set_alias(self, alias, command):
        """コマンドエイリアスを追加・更新する"""
        if "aliases" not in self.app.config:
            self.app.config["aliases"] = {}
        self.app.config["aliases"][alias] = command
        with open(os.path.join(GB.DATA_DIR, "config.json"), 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log(f"Alias set: {alias} : {command}")

    def set_keybind(self, key_combo, command):
        """キーバインドを追加・更新する"""
        if "shortcuts" not in self.app.config:
            self.app.config["shortcuts"] = {}
        self.app.config["shortcuts"][key_combo] = command
        with open(os.path.join(GB.DATA_DIR, "config.json"), 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log(f"Keybind set: {key_combo} : {command}")

    def open_config(self):
        """設定ファイルをエディタで開く"""
        config_path = os.path.join(GB.DATA_DIR, "config.json")
        self.app.editor_api.open(config_path)

    def clear_log(self, clear_lines=100):
        """エディタのログをクリアする"""
        log_path = os.path.join(GB.DATA_DIR, "editor.log")
        if os.path.exists(log_path):
            if clear_lines == 0:
                self.app.log("Clear nothing")
                return
            if clear_lines < 0:
                os.unlink(log_path)
                self.app.log("Clear all log")
                return
            with open(log_path, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
            if len(log_lines) > clear_lines:
                remain_since = len(log_lines) - clear_lines
                log_lines = log_lines[-remain_since:]   
            with open(log_path, 'w', encoding='utf-8') as f:
                f.writelines(log_lines)
            self.app.log("Editor log cleared.")
        else:
            self.app.log("No log file found to clear.")

    def reset_config(self, confirm=False):
        if not confirm:
            self.app.log("Please confirm config reset by passing confirm=True.")
            return
        config_path = os.path.join(GB.DATA_DIR, "config.json")
        if os.path.exists(config_path):
            os.unlink(config_path)
        self.app.log("Please restart the editor to apply default config.")