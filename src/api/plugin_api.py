from pathlib import Path
import shutil
import json

from kernel.global_var import GlabalVar as GB

class PluginAPI:
    def __init__(self, app_instance):
        self.app = app_instance

    def reg_ccmd(self):
        added_code = self.app.editor.text
        added_code_processed = added_code.split("\n")
        added_code_processed = ["    " + line for line in added_code_processed]
        custom_ccmd_file = Path(GB.PLUGIN_DIR) / "ccmd" / "ccmd.py"
        with open(custom_ccmd_file, "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(added_code_processed))

    def set_plugin(self, name):
        with open(Path(GB.PLUGIN_DIR) / f"package/{name}.py", "w", encoding="utf-8") as f:
            f.write(self.app.editor.text)
        self.app.log(f"Plugin '{name}' has been set.")
    
    def set_ext_plugin(self, ext):
        if not Path(ext).exists():
            self.app.log(f"Plugin file not found: {ext}")
            return
        shutil.copy2(ext, Path(GB.PLUGIN_DIR) / "package")
        self.app.log(f"External plugin '{ext}' has been registered.")

    def set_pkg(self, ext):
        if not Path(ext).exists():
            self.app.log(f"Package diretory not found: {ext}")
            return
        shutil.copytree(ext, Path(GB.PLUGIN_DIR))
        self.app.config["plugin"]["pachage"].append(Path(ext).stem)
        with open(Path(GB.DATA_DIR) / "config.json", 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log(f"External package '{ext}' has been registered.")