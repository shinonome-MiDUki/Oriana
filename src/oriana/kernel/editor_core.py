import os
import json
import datetime
import re
import sys
import importlib
from pathlib import Path

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, FloatContainer, Float, ConditionalContainer
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.styles import Style
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import PythonLexer

from oriana.kernel.jedi_engine import JediCompleter
from oriana.kernel.global_var import GlabalVar as GB
from oriana.api.editor_api import EditorAPI
from oriana.api.config_api import ConfigAPI
from oriana.api.terminal_api import TerminalAPI
from oriana.api.git_api import GitAPI
from oriana.api.plugin_api import PluginAPI
from oriana.api.shelf_api import ShelfAPI

class EditorCore:
    def __init__(self, open_path=None):
        #self.current_file = None
        self.config = self.load_config()
        self.is_console_mode = False
        self.reject_log_set = set(self.config.get("editor", {}).get("reject_log", []))
        GB.PLUGIN_DIR = self.config.get("plugin", {}).get("plugin_dir", str(Path.home() / "Documents/oriana/plugins"))
        if GB.PLUGIN_DIR not in sys.path:
            sys.path.append(GB.PLUGIN_DIR)
        pkg_list = self.config.get("plugin", {}).get("package", ["oriana_package"])
        try:
            for pkg in pkg_list:
                importlib.import_module(f"oriana_client.{pkg}")
            from oriana_client.ccmd.ccmd import CustomCommands
        except Exception as e:
            self.log(f"Plugin load error: {e}")

        lang = self.config.get("editor", {}).get("language", "python")
        completer = self.config.get("completer", {}).get(lang, "jedi")
        if completer == "jedi":
            self.completer = JediCompleter()
        else:
            self.completer = None
        
        # UI: エディタ本体
        self.editor = TextArea(
            line_numbers=True, 
            multiline=True, 
            scrollbar=True,
            completer=self.completer,
            complete_while_typing=self.config.get("editor", {}).get("is_complete_while_typing", True),
            style='class:editor',
            lexer=PygmentsLexer(PythonLexer)
            )
        # UI: コンソール
        self.console = TextArea(
            multiline=True, 
            scrollbar=True,
            style='class:console',
            read_only=True
            )
        # UI: ステータスバー
        self.status_bar = TextArea(
            text="Welcome", 
            height=1, 
            style='class:status',
            read_only=True
            )
        
        # UI: コマンドライン
        cmd_prompt = self.config.get("editor", {}).get("cmd_prompt", "pycmd:>")
        self.cmd_line = TextArea(
            prompt=cmd_prompt if isinstance(cmd_prompt, str) else "pycmd:>",
            multiline=False, 
            style='class:command',
            accept_handler=self.handle_command
            )

        self.editor_api = EditorAPI(self)
        self.config_api = ConfigAPI(self)
        self.ogit_api = GitAPI(self)
        self.terminal_api = TerminalAPI(self)
        self.plugin_api = PluginAPI(self)
        self.shelf_api = ShelfAPI(self)
        self.custom_cmd = CustomCommands(self) 
        self.api_set = {
            "ope": self.editor_api,
            "cfg": self.config_api,
            "git": self.ogit_api,
            "shr": self.terminal_api,
            "plg": self.plugin_api,
            "shf": self.shelf_api,
            "ccmd": self.custom_cmd,
            "app": self
        }

        if open_path:
            self.editor_api.open(open_path)

        # レイアウト構築
        is_console = Condition(lambda: self.is_console_mode)
        is_editor = Condition(lambda: not self.is_console_mode)
        main_workspace = HSplit([
            ConditionalContainer(
                content=self.editor, 
                filter=is_editor
            ),
            ConditionalContainer(
                content=self.console,
                filter=is_console
            ),
        ])
        root = HSplit([
            main_workspace,
            self.status_bar,
            self.cmd_line
        ])
        root_container = FloatContainer(
            content=root,
            floats=[
                Float(content=CompletionsMenu(max_height=12),
                      xcursor=True, 
                      ycursor=True)
            ]
        )
        self.layout = Layout(root_container, focused_element=self.editor)
        
        # キーバインド登録
        self.kb = KeyBindings()
        self.setup_bindings()

        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            mouse_support=True,
            full_screen=True,
            style=Style.from_dict(self.config.get("theme", {}))
        )

        if self.config.get("editor", {}).get("is_splash", True) and open_path is None:
            with open(Path(GB.BASE_DIR) / "_resources" / "splash.txt", 'r', encoding='utf-8') as f:
                self.editor.text = f.read()
            self.config["editor"]["is_splash"] = False
            with open(Path(GB.DATA_DIR) / "config.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)

    def load_config(self):
        path = Path(GB.DATA_DIR) / "config.json"
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "editor" : {},
            "aliases": {"o": "api.open(arg)", "w": "api.save()", "q": "api.quit()"},
            "shortcuts": {"c-p": "api.focus_cmd()", "c-s": "api.save()"}
        }

    def setup_bindings(self):
        for key, cmd in self.config.get("shortcuts", {}).items():
            def _create_h(c):
                return lambda event: exec(c, self.api_set)
            try:
                self.kb.add(key)(_create_h(cmd))
            except: pass

        @self.kb.add('c-o')
        def _(event): 
            if get_app().layout.has_focus(self.editor):
                self.editor_api.focus_cmd()
            else:
                self.editor_api.focus_edit()

    def handle_command(self, buffer):
        raw = buffer.text.strip()
        if not raw: return

        exec_code = raw
        if "aliases" in self.config:
            for alias, replacement in self.config["aliases"].items():
                pattern = r'\b' + re.escape(alias) + r'\b'
                exec_code = re.sub(pattern, replacement, exec_code)
        try:
            exec(exec_code, self.api_set)
        except Exception as e:
            self.log(f"Error: {e}")

        self.editor_api.focus_edit()
        buffer.reset()

    def log(self, msg):
        self.status_bar.text = msg
        if (self.config.get("editor", {}).get("is_record_to_log", False) 
            and (not self.reject_log_set 
                 or sys._getframe(1).f_code.co_name not in self.reject_log_set)):
            maxlines = self.config["editor"].get("max_log_lines", 10000)
            log_path = Path(GB.DATA_DIR) / "editor.log"
            if not log_path.exists():
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write("")
            maxlines = -1 if maxlines <= 0 else maxlines
            if maxlines != -1:
                with open(log_path, 'r', encoding='utf-8') as f:
                    log_lines = f.readlines()
                if len(log_lines) > maxlines:
                    remain_since = len(log_lines) - maxlines
                    log_lines = log_lines[-remain_since:]   
                    with open(log_path, 'w', encoding='utf-8') as f:
                        f.writelines(log_lines)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + msg + "\n")

    def run(self):
        self.app.run()