from prompt_toolkit.application import get_app

from api.editor_api import EditorAPI as ope
from api.config_api import ConfigAPI as cfg
from api.terminal_api import TerminalAPI as shr
from api.git_api import GitAPI as git
from api.plugin_api import PluginAPI as plg

class CustomCommands:
    def __init__(self, app_instance):
        self.app = app_instance
    
    def added_method(self, x):
        print(f"Added method called with {x}")
        return x * 2
    