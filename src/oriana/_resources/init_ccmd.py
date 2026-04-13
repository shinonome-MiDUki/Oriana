from functools import wraps

from prompt_toolkit.application import get_app

from oriana.api.editor_api import EditorAPI 
from oriana.api.config_api import ConfigAPI 
from oriana.api.terminal_api import TerminalAPI 
from oriana.api.git_api import GitAPI 
from oriana.api.plugin_api import PluginAPI 
from oriana.kernel.editor_core import EditorCore

def useapi(*api_to_use):
    """コマンド関数にAPIを注入するデコレーター"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for api_name in api_to_use:
                api_available = ["ope", "cfg", "git", "shr", "plg"]
                if api_name in api_available:
                    kwargs[api_name] = getattr(self, api_name, None)
                else:
                    raise ValueError(f"API '{api_name}' is not available.")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

class CustomCommands:
    def __init__(self, app_instance):
        self.app = app_instance
        self._editor_api = None
        self._config_api = None
        self._terminal_api = None
        self._git_api = None
        self._plugin_api = None

    @property
    def ope(self):
        if self._editor_api is None:
            self._editor_api = EditorAPI(self.app)
        return self._editor_api
    
    @property
    def cfg(self):
        if self._config_api is None:
            self._config_api = ConfigAPI(self.app)
        return self._config_api
    
    @property
    def shr(self):
        if self._terminal_api is None:
            self._terminal_api = TerminalAPI(self.app)
        return self._terminal_api

    @property
    def git(self):
        if self._git_api is None:
            self._git_api = GitAPI(self.app)
        return self._git_api

    @property
    def plg(self):
        if self._plugin_api is None:
            self._plugin_api = PluginAPI(self.app)
        return self._plugin_api
