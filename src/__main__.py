import os
import sys

from kernel.global_var import GlabalVar as GB
from kernel.global_var import GlobalConst as GC
from kernel.editor_core import EditorCore
from kernel.make_config import MakeConfig

GB.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GB.DATA_DIR = os.path.join(GC.APP_DATA, "oriana")
GB.BIN_DIR = os.path.join(GB.BASE_DIR, "bin")
#os.environ["PATH"] = GB.BIN_DIR + os.pathsep + os.environ.get("PATH", "")

def main():
    if os.path.exists(GC.APP_DATA):
        if not os.path.exists(GB.DATA_DIR):
            os.mkdir(GB.DATA_DIR)
            config_path = os.path.join(GB.DATA_DIR, "config.json")
            if not os.path.exists(config_path):
                MakeConfig(config_path).create_default_config()
    else:
        print(f"Error: Cannot access app data directory at {GC.APP_DATA}")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        editor = EditorCore(open_path=file_path)
    else:
        editor = EditorCore()

    editor.run()

if __name__ == "__main__":
    main()
