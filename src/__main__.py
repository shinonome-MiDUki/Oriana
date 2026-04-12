import os
import sys

from kernel.global_var import GlabalVar as GB
from kernel.editor_core import EditorCore
from api.editor_api import EditorAPI

GB.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GB.BIN_DIR = os.path.join(GB.BASE_DIR, "bin")
os.environ["PATH"] = GB.BIN_DIR + os.pathsep + os.environ.get("PATH", "")

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        editor = EditorCore(open_path=file_path)
    else:
        editor = EditorCore()

    editor.run()

if __name__ == "__main__":
    main()
