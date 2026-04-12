import subprocess
import tempfile
import os
import sys
import shutil
from pathlib import Path

from prompt_toolkit.application import get_app

class TerminalAPI:
    def __init__(self, app_instance):
        self.app = app_instance

    def shell(self, editor=False, command=None, clear_console=True, open_console=True):
        if editor:
            command = self.app.editor.text
        if command:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if not self.app.is_console_mode:
                    if clear_console:
                        self.app.console.text = ""
                    if open_console:
                        self.console()
                self.app.console.text += f"\n$ {command}\n{result.stdout}"
                self.app.log("Shell command executed")
            except Exception as e:
                self.app.log(f"Shell error: {e}")
        else:
            self.app.log("No shell command provided.")

    def console(self):
        """エディタとコンソールの表示を切り替える (内容は保持される)"""
        self.app.is_console_mode = not self.app.is_console_mode
        if self.app.is_console_mode:
            get_app().layout.focus(self.app.console)
            self.app.log("Console Mode")
        else:
            get_app().layout.focus(self.app.editor)
            self.app.log("Editor Mode")

    def clear(self):
        """コンソールの内容をクリアする"""
        self.app.console.text = ""
        self.app.log("Console cleared.")

    def run_py(self, clear_console=True, open_console=True, interpreter=None, venv=None):
        """
        現在エディタにあるコードを一時ファイルとして保存し、
        実行結果をコンソール出力に表示する。
        """
        if not self.app.is_console_mode:
            if clear_console:
                self.app.console.text = ""
            if open_console:
                self.console()
        code = self.app.editor.text
        self.app.console.text += f"\n--- Running Code ---\n"
        
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as tf:
            tf.write(code)
            temp_name = tf.name

        venv = venv if venv else self.app.config.get("run_env", {}).get("venv", None)
        if venv:
            if sys.platform == "win32":
                intepreter_used = os.path.join(venv, "Scripts", "python.exe")
            else:
                intepreter_used = os.path.join(venv, "bin", "python3")
        else:
            intepreter_used = interpreter if interpreter else sys.executable

        try:
            result = subprocess.run(
                [intepreter_used, temp_name],
                capture_output=True,
                text=True,
                timeout=self.app.config.get("timeout", 30)
            )
            output = result.stdout
            error = result.stderr
            
            if output:
                self.app.console.text += output
            if error:
                self.app.console.text += f"\n[STDERR]\n{error}"
            if not output and not error:
                self.app.console.text += "(No output)"
        except subprocess.TimeoutExpired:
            self.app.console.text += "\nError: Process timed out (30s)"
        except Exception as e:
            self.app.console.text += f"\nExecution Error: {e}"
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

        #self.app.console.buffer.cursor_position = len(self.app.console.text)
        self.app.console.text += "\n--- Code Execution Finished ---\n"
        self.app.log("Code executed.")

    def venv(self, dir, interpreter=None, remove=False):
        if not remove:
            interpreter_used = interpreter if interpreter else sys.executable
            subprocess.run([interpreter_used, "-m", "venv", dir])
            self.app.log(f"Virtual environment created at: {dir}")
        else:
            dangerous_dirs = ["/", "C:\\", "C:/"] + self.app.config.get("editor", {}).get("dangerous_dirs", [])
            if dir in dangerous_dirs: #dangerous check
                self.app.log("Error: Cannot remove dangerous directories.")
                return
            if os.path.exists(dir):
                shutil.rmtree(dir)
                self.app.log(f"Virtual environment removed: {dir}")
            else:
                self.app.log(f"Directory not found: {dir}")

    def package(self, name, venv=None, force=False, version=None, install=True, upgrade=False, pip3=False):
        name = f"{name}=={version}" if version else name
        package_manager = "pip3" if pip3 else "pip"
        if not self.app.is_console_mode:
            self.console()
            self.app.console.text += f"\n--- Package: {name} ---\n"

        if venv:
            if not os.path.exists(venv):
                if force:
                    self.venv(venv)
                self.app.log(f"Error: Virtual environment not found at {venv}")
                return
            if sys.platform == "win32":
                package_manager = os.path.join(venv, "Scripts", "pip.exe")
            else:
                package_manager = os.path.join(venv, "bin", "pip3")
            if not os.path.exists(package_manager):
                self.app.log(f"Error: {package_manager} not found in the specified virtual environment.")
                return
        if install:
            command = [package_manager, "install", name]
            if upgrade:
                command.insert(2, "--upgrade")
        else:
            command = [package_manager, "uninstall", name, "-y"]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.stdout:
                self.app.console.text += f"\n{result.stdout}"
            if result.stderr:
                self.app.console.text += f"\n[STDERR]\n{result.stderr}"
        except Exception as e:
            self.app.log(f"Package management error: {e}")