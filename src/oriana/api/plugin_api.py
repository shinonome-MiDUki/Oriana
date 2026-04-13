from pathlib import Path
import shutil
import json
import re 

from oriana.kernel.global_var import GlabalVar as GB

class PluginAPI:
    def __init__(self, app_instance):
        self.app = app_instance

    def ccmd_template(self):
        GB.EDITING_PATH = None
        with open(Path(GB.BASE_DIR) / "_resources" / "ccmd_sample.py", "r", encoding="utf-8") as f:
            ccmd_template_code = f.read()
        self.app.editor.text = ccmd_template_code
        self.app.log("CCMD template loaded. Edit the code and run 'reg_ccmd' command to register.")

    def reg_ccmd(self):
        added_code = self.app.editor.text
        added_code_processed = added_code.split("\n")
        if added_code_processed[0].startswith("@"):
            used_api_search = re.search(r'\((.*?)\)', added_code_processed[0])
            if used_api_search:
                used_api = used_api_search.group(1)
                used_api_list = [re.sub(r'["\']', '', api) for api in used_api.split(",")]
            else:
                raise ValueError("Invalid CCMD format. The first line should specify used APIs in the format: @useapi(api1, api2, ...)")
        else:
            used_api_list = []
        parameter = ", ".join(used_api_list) if used_api_list else ""
        def_line = added_code_processed[1].replace("()", f"(self, {parameter})" if parameter else "(self)")
        added_code_processed = ["    " + line for line in added_code_processed]
        custom_ccmd_file = Path(GB.PLUGIN_DIR) / "oriana_client/ccmd/ccmd.py"
        with open(custom_ccmd_file, "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(added_code_processed))
        self.app.log("Custom command has been registered.")

    def set_plugin(self, name):
        with open(Path(GB.PLUGIN_DIR) / f"oriana_client/package/{name}.py", "w", encoding="utf-8") as f:
            f.write(self.app.editor.text)
        self.app.log(f"Plugin '{name}' has been set.")
    
    def set_ext_plugin(self, ext):
        if not Path(ext).exists():
            self.app.log(f"Plugin file not found: {ext}")
            return
        shutil.copy2(ext, Path(GB.PLUGIN_DIR) / "oriana_client/package")
        self.app.log(f"External plugin '{ext}' has been registered.")

    def set_pkg(self, ext):
        if not Path(ext).exists():
            self.app.log(f"Package diretory not found: {ext}")
            return
        shutil.copytree(ext, Path(GB.PLUGIN_DIR)/ "oriana_client")
        self.app.config["plugin"]["package"].append(Path(ext).stem)
        with open(Path(GB.DATA_DIR) / "config.json", 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log(f"External package '{ext}' has been registered.")