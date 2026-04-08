import os

from kernel.global_var import GlabalVar as GB
from kernel.editor_core import EditorCore

GB.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GB.BIN_DIR = os.path.join(GB.BASE_DIR, "bin")
os.environ["PATH"] = GB.BIN_DIR + os.pathsep + os.environ.get("PATH", "")

if __name__ == "__main__":
    EditorCore().run()
