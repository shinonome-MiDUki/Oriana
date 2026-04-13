import sys
import os

class GlabalVar:
    BASE_DIR = None
    DATA_DIR = None
    PLUGIN_DIR = None
    BIN_DIR = None
    EDITING_PATH = None
    STASHED_PATH = None
    CACHE_EDITOR = None

class GlobalConst:
    if sys.platform == "win32":
        APP_DATA = os.getenv("APPDATA")
    else:
        APP_DATA = os.path.expanduser("~/.config")