import subprocess
import tempfile
import os
import sys
from pathlib import Path

class TerminalAPI:
    def __init__(self, app_instance, get_app):
        self.app = app_instance
        self.get_app = get_app

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
            self.get_app.layout.focus(self.app.console)
            self.app.log("Console Mode")
        else:
            self.get_app.layout.focus(self.app.editor)
            self.app.log("Editor Mode")

    def clear_console(self):
        """コンソールの内容をクリアする"""
        self.app.console.text = ""
        self.app.log("Console cleared.")

    def run_code(self, clear_console=True, open_console=True):
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