import os
import json
import subprocess
import sys
import datetime
import tempfile
from pathlib import Path

import jedi
import pyperclip
from git import Repo, InvalidGitRepositoryError
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, FloatContainer, Float, ConditionalContainer
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.widgets import TextArea, Frame
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import get_app
from prompt_toolkit.filters import Condition
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import PythonLexer

# --- 1. Path Setup (同梱ツール用) ---
# エディタがあるディレクトリの 'bin' を PATH の最優先に追加する
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
EDITING_PATH = None
STASEHD_PATH = None
CACHE_EDITOR = None
os.environ["PATH"] = BIN_DIR + os.pathsep + os.environ.get("PATH", "")

# --- 2. API Definition ---
class EditorAPI:
    """ユーザーがコマンドやショートカットから叩く Python API"""
    def __init__(self, app_instance):
        self.app = app_instance

    def create(self, path):
        """新しいファイルを作成して開く"""
        if os.path.exists(path):
            self.app.log(f"File already exists: {path}")
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("")
            self.app.log(f"Created: {path}")
        self.open(path)

    def open(self, path):
        """ファイルを読み込み、現在のシェルフに展開する"""
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.app.editor.text = f.read()
            self.app.current_file = path
            self.app.log(f"Opened: {path}")
        else:
            self.app.log(f"New file: {path}")
            self.app.current_file = path
        global EDITING_PATH
        EDITING_PATH = path

    def save(self, path=None):
        """現在のファイルを保存"""
        if path:
            self.app.current_file = path
        if self.app.current_file:
            with open(self.app.current_file, 'w', encoding='utf-8') as f:
                f.write(self.app.editor.text)
            self.app.log(f"Saved: {self.app.current_file}")
        else:
            self.app.log("No file specified to save.")

    def focus_cmd(self):
        get_app().layout.focus(self.app.cmd_line)

    def focus_edit(self):
        get_app().layout.focus(self.app.editor)

    def quit(self):
        get_app().exit()

    def copy(self, line_num=None):
        """エディタの内容をクリップボードにコピー"""
        buffer = self.app.editor.buffer
        if line_num is not None:
            lines = self.app.editor.text.split('\n')
            line_to_copy = int(line_num) - 1
            if 0 <= line_to_copy < len(lines):
                pyperclip.copy(lines[line_to_copy])
            else:
                self.app.log(f"Error: Line {line_num} out of range.")
        else:
            selected_text = buffer.document.selection.text if buffer.document.selection else None
            if selected_text:
                pyperclip.copy(selected_text)
            else:
                pyperclip.copy(buffer.document.current_line)

    def paste(self, line_num=None):
        """クリップボードの内容をエディタにペースト"""
        buffer = self.app.editor.buffer
        paste_text = pyperclip.paste()
        if line_num is not None:
            lines = self.app.editor.text.split('\n')
            line_to_paste = int(line_num) - 1
            if 0 <= line_to_paste < len(lines):
                lines[line_to_paste] = paste_text
                self.app.editor.text = '\n'.join(lines)
            else:
                self.app.log(f"Error: Line {line_num} out of range.")
        else:
            buffer.insert_text(paste_text)

    def delete(self, line_num=None):
        """エディタの内容を削除"""
        if line_num is None:
            buffer = self.app.editor.buffer
            if buffer.selection_state:
                buffer.cut_selection()
            else:
                buffer.delete_before_cursor(len(buffer.document.current_line))
        else:
            lines = self.app.editor.text.split('\n')
            line_to_delete = int(line_num) - 1
            if 0 <= line_to_delete < len(lines):
                lines.pop(line_to_delete)
                self.app.editor.text = '\n'.join(lines)
            else:
                self.app.log(f"Error: Line {line_num} out of range.")

    def undo(self):
        """直前の操作を取り消す"""
        buffer = self.app.editor.buffer
        buffer.undo()
        self.app.log("Undo")

    def redo(self):
        """取り消した操作をやり直す"""
        buffer = self.app.editor.buffer
        buffer.redo()
        self.app.log("Redo")

    def set_editor_config(self, item, value):
        """エディタの設定を動的に変更する"""
        setattr(self.app.editor, item, value)
        if "editor" not in self.app.config:
            self.app.config["editor"] = {}
        self.app.config["editor"][item] = value
        with open(os.path.join(BASE_DIR, "config.json"), 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log(f"Editor config updated: {item} : {value}")

    def set_editor_theme(self, theme_dict, overwrite=False):
        """エディタのテーマを動的に変更する"""
        if "theme" not in self.app.config:
            self.app.config["theme"] = {}
        if overwrite:
            self.app.config["theme"] = theme_dict
        else:
            for k, v in theme_dict.items():
                self.app.config["theme"][k] = v
        with open(os.path.join(BASE_DIR, "config.json"), 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log("Editor theme updated.")

    def set_alias(self, alias, command):
        """コマンドエイリアスを追加・更新する"""
        if "aliases" not in self.app.config:
            self.app.config["aliases"] = {}
        self.app.config["aliases"][alias] = command
        with open(os.path.join(BASE_DIR, "config.json"), 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log(f"Alias set: {alias} : {command}")

    def set_keybind(self, key_combo, command):
        """キーバインドを追加・更新する"""
        if "shortcuts" not in self.app.config:
            self.app.config["shortcuts"] = {}
        self.app.config["shortcuts"][key_combo] = command
        with open(os.path.join(BASE_DIR, "config.json"), 'w') as f:
            json.dump(self.app.config, f, indent=4)
        self.app.log(f"Keybind set: {key_combo} : {command}")

    def shell(self, editor=False, command=None):
        if editor:
            command = self.app.editor.text
        if command:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if not self.app.is_console_mode:
                    self.app.console.text = ""
                    self.console()
                self.app.console.text += f"\n$ {command}\n{result.stdout}"
                self.app.log("Shell command executed")
            except Exception as e:
                self.app.log(f"Shell error: {e}")
        else:
            self.app.log("No shell command provided.")

    def stash(self, revert=False):
        """現在のエディタの内容を一時的に保存する"""
        global CACHE_EDITOR
        global EDITING_PATH
        global STASEHD_PATH
        if revert:
            if CACHE_EDITOR is not None:
                self.app.editor.text = CACHE_EDITOR
                EDITING_PATH = STASEHD_PATH
                STASEHD_PATH = None
                self.app.log("Editor content restored from stash.")
            else:
                self.app.log("No stashed content to restore.")
        else:
            CACHE_EDITOR = self.app.editor.text
            STASEHD_PATH = EDITING_PATH
            EDITING_PATH = None
            self.app.log("Editor content stashed.")
            self.app.editor.text = ""

    def console(self):
        """エディタとコンソールの表示を切り替える (内容は保持される)"""
        self.app.is_console_mode = not self.app.is_console_mode
        if self.app.is_console_mode:
            get_app().layout.focus(self.app.console)
            self.app.log("Console Mode")
        else:
            get_app().layout.focus(self.app.editor)
            self.app.log("Editor Mode")

    def run_code(self):
        """
        現在エディタにあるコードを一時ファイルとして保存し、
        実行結果をコンソール出力に表示する。
        """
        if not self.app.is_console_mode:
            self.app.console.text = ""
            self.console()
        code = self.app.editor.text
        self.app.console.text += f"\n--- Running Code ---\n"
        
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as tf:
            tf.write(code)
            temp_name = tf.name

        intepreter = self.app.config.get("run_env", {}).get("interpreter", sys.executable) 
        venv_dir = self.app.config.get("run_env", {}).get("venv_path", None)
        if venv_dir:
            if not Path(venv_dir).exists():
                subprocess.run([intepreter, "-m", "venv", venv_dir])
            if sys.platform == "win32":
                subprocess.run([os.path.join(venv_dir, "Scripts", "activate")])
            else:
                subprocess.run(["source", os.path.join(venv_dir, "bin", "activate")])

        try:
            result = subprocess.run(
                [intepreter, temp_name],
                capture_output=True,
                text=True,
                timeout=30 
            )
            output = result.stdout
            error = result.stderr
            
            if output:
                self.app.console.text += output
            if error:
                self.app.console.text += f"\n[STDERR]\n{error}"
            if not output and not error:
                self.app.console.text += "(No output)\n"
        except subprocess.TimeoutExpired:
            self.app.console.text += "\nError: Process timed out (30s)\n"
        except Exception as e:
            self.app.console.text += f"\nExecution Error: {e}\n"
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

        self.app.console.buffer.cursor_position = len(self.app.console.text)
        self.app.log("Code executed.")
        if venv_dir:
            if sys.platform == "win32":
                subprocess.run([os.path.join(venv_dir, "Scripts", "deactivate")])
            else:
                subprocess.run(["deactivate"])


class GitAPI:
    """git コマンドを実行する API"""
    def __init__(self, app_instance):
        self.app = app_instance
        if EDITING_PATH:
            abs_path = os.path.abspath(EDITING_PATH)
        else:
            self.git_repo = None
            return

        try:
            repo = Repo(abs_path, search_parent_directories=True)
            repo_root = repo.git_dir.replace('.git', '')
            relative_path = os.path.relpath(abs_path, repo.working_tree_dir)
            is_tracked = any(relative_path in item for item in repo.git.ls_files(relative_path).splitlines())
            if is_tracked:
                self.git_repo = Repo(repo.working_tree_dir, search_parent_directories=True)
            else:
                self.git_repo = None
        except InvalidGitRepositoryError:
            self.git_repo = None

    def add(self, is_all=False, path:list|None=None):
        """git add コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        if is_all:
            self.git_repo.git.add(A=True)
            self.app.log("Git: Added all changes.")
        else:
            target = path if path else [EDITING_PATH]
            self.git_repo.git.add(target)
            self.app.log(f"Git: Added {target}.")

    def commit(self, message="commit from Oriana"):
        """git commit コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        self.git_repo.index.commit(message)
        self.app.log(f"Git: Committed with message: {message}")

    def reset(self):
        """git reset コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        self.git_repo.git.reset()

    def checkout(self, branch, is_force=False):
        """git checkout コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        self.git_repo.git.checkout(branch, force=is_force)
        self.app.log(f"Git: Checked out to {branch}")

    def pull(self, remote="origin", branch="main"):
        """git pull コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        if remote not in [r.name for r in self.git_repo.remotes]:
            self.app.log(f"Error: Remote '{remote}' not found.")
            return
        origin = self.git_repo.remote(name=remote)
        origin.pull(branch)
        self.app.log(f"Git: Pulled from {remote}/{branch}")

    def push(self, remote="origin", branch="main"):
        """git push コマンドを実行"""
        if not self.git_repo:
            self.app.log("Error: Not a git repository.")
            return
        if remote not in [r.name for r in self.git_repo.remotes]:
            self.app.log(f"Error: Remote '{remote}' not found.")
            return
        origin = self.git_repo.remote(name=remote)
        origin.push(branch)
        self.app.log(f"Git: Pushed to {remote}/{branch}")

class JediCompleter(Completer):
    """
    jedi ライブラリを直接使用するカスタム補完クラス
    """
    def __init__(self, interpreter_env=None):
        # 同梱した Python 環境を指定する場合はここに jedi.create_environment() を渡す
        self.env = interpreter_env

    def get_completions(self, document, complete_event):
        """
        prompt_toolkit が補完候補を必要とした時に呼ばれるメインメソッド
        """
        code = document.text
        line = document.cursor_position_row + 1 
        column = document.cursor_position_col

        try:
            script = jedi.Script(code, environment=self.env)
            jedi_completions = script.complete(line, column)

            for jc in jedi_completions:
                yield Completion(
                    jc.name,        
                    start_position=-len(jc.name_prefix),
                    display=jc.name,            
                    display_meta=jc.type,       
                )
        except Exception:
            return

# --- 3. Main Application ---
class PortableEditor:
    def __init__(self):
        self.current_file = None
        self.config = self.load_config()
        self.is_console_mode = False

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
        self.cmd_line = TextArea(
            prompt=":", 
            multiline=False, 
            style='class:command',
            accept_handler=self.handle_command
            )

        self.api = EditorAPI(self)
        self.ogit = GitAPI(self)
        
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

    def load_config(self):
        path = os.path.join(BASE_DIR, "config.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {
            "editor" : {},
            "aliases": {"o": "api.open(arg)", "w": "api.save()", "q": "api.quit()"},
            "shortcuts": {"c-p": "api.focus_cmd()", "c-s": "api.save()"}
        }

    def setup_bindings(self):
        for key, cmd in self.config.get("shortcuts", {}).items():
            def _create_h(c):
                return lambda event: exec(c, {"api": self.api, "app": self})
            try:
                self.kb.add(key)(_create_h(cmd))
            except: pass

        @self.kb.add('c-o')
        def _(event): 
            if get_app().layout.has_focus(self.editor):
                self.api.focus_cmd()
            else:
                self.api.focus_edit()
            

    def handle_command(self, buffer):
        raw = buffer.text.strip()
        if not raw: return

        # エイリアス解決
        exec_code = raw
        if "aliases" in self.config:
            for alias in self.config["aliases"]:
                if alias in raw:
                    exec_code = exec_code.replace(alias, self.config["aliases"][alias])
        try:
            exec(exec_code, {"api": self.api, "git": self.ogit, "app": self})
        except Exception as e:
            self.log(f"Error: {e}")
        
        self.api.focus_edit()
        buffer.reset()

    def log(self, msg):
        self.status_bar.text = msg
        if "editor" in self.config:
            if self.config.get("is_record_to_log", False):
                if not os.path.exists(os.path.join(BASE_DIR, "editor.log")):
                    with open(os.path.join(BASE_DIR, "editor.log"), 'w', encoding='utf-8') as f:
                        f.write("")
                with open(os.path.join(BASE_DIR, "editor.log"), 'a', encoding='utf-8') as f:
                    f.write(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + msg + "\n")

    def run(self):
        self.app.run()

if __name__ == "__main__":
    PortableEditor().run()
