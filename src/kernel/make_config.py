import json
from pathlib import Path

from .global_var import GlabalVar as GB

class MakeConfig:
    def __init__(self, config_path):
        self.config_path = config_path

    def create_default_config(self):
        default_config = {
            "editor": {
                "is_splash": True,
                "is_record_to_log": True,
                "language": "python",
                "is_complete_while_typing": True,
                "cmd_prompt": "pycmd:>",
                "dangerous_dirs": [
                    "/",
                    "/home",
                    "/root",
                    "C:\\",
                    "C:\\Windows",
                    "C:\\Program Files",
                    "C:\\Program Files (x86)"
                ]
            },
            "theme": {
                "editor": "bg:#000000 #ffffff",
                "editor.cursor": "bg:#ffffff",
                "console": "bg:#000000 #ffffff",
                "status": "reverse #00ffff",
                "command": "bg:#222222 #ffffff",
                "line-number": "#444444",
                "pygments.text": "#ffffff",
                "pygments.keyword": "#ff79c6 bold",
                "pygments.name.function": "#50fa7b",
                "pygments.name.class": "#8be9fd italic",
                "pygments.string": "#f1fa8c",
                "pygments.comment": "#6272a4 italic",
                "pygments.number": "#bd93f9",
                "pygments.operator": "#ff79c6",
                "pygments.punctuation": "#f8f8f2",
                "pygments.name.builtin": "#8be9fd",
                "pygments.name.variable": "#f8f8f2",
                "completion-menu": "bg:#333333 #ffffff",
                "completion-menu.completion.current": "bg:#44475a #50fa7b",
                "completion-menu.completion": "bg:#282a36 #f8f8f2"
            },
            "completer": {
                "python": "jedi"
            },
            "run_env": {
                "timeout": 30
            },
            "shortcuts": {

            },
            "aliases": {

            },
            "plugin":
                {
                    "plugin_dir": str(Path.home() / "Documents/oriana"),
                    "package": ["package"]
                }
        }
        custom_dir = str(input("Enter plugin directory (default /home/Documents/oriana): ")).strip()
        custom_dir = Path(custom_dir) if custom_dir else Path.home() / "Documents/oriana"
        default_config["plugin"]["plugin_dir"] = str(custom_dir)
        if not custom_dir.exists():
            custom_dir.mkdir(parents=True, exist_ok=True)
            default_pkg = custom_dir / "package"
            if not default_pkg.exists():
                default_pkg.mkdir() 
            with open(default_pkg / "__init__.py", "w", encoding="utf-8") as f:
                f.write("")
            custom_cmd = custom_dir / "ccmd"
            if not custom_cmd.exists():
                custom_cmd.mkdir()
            with open(custom_cmd / "__init__.py", "w", encoding="utf-8") as f:
                f.write("")
            with open(GB.BASE_DIR / "_resources" / "init_ccmd.py", "r", encoding="utf-8") as f:
                init_ccmd_code = f.read()
            with open(custom_cmd / "ccmd.py", "w", encoding="utf-8") as f:
                f.write(init_ccmd_code)
            
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)