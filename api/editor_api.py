import os
import pyperclip
import sys

proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_root not in sys.path:
    sys.path.append(proj_root)
from kernel.global_var import GlabalVar as GB

class EditorAPI:
    def __init__(self, app_instance, get_app):
        self.app = app_instance
        self.get_app = get_app

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
        GB.EDITING_PATH = path

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
        self.get_app.layout.focus(self.app.cmd_line)

    def focus_edit(self):
        self.get_app.layout.focus(self.app.editor)

    def quit(self):
        self.get_app.exit()

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

    def clear(self):
        """エディタの内容をすべてクリアする"""
        self.app.editor.text = ""
        self.app.log("Editor cleared.")

    def jump(self, line_num=1):
        """指定した行にカーソルを移動する"""
        buffer = self.app.editor.buffer
        line_num = int(line_num)
        if line_num < 1:
            self.app.log("Error: Line number must be greater than 0.")
            return
        lines = self.app.editor.text.split('\n')
        if line_num > len(lines):
            self.app.log(f"Error: Line number {line_num} exceeds total lines {len(lines)}.")
            return
        target_position = sum(len(l) + 1 for l in lines[:line_num - 1])
        buffer.cursor_position = target_position

    def stash(self, revert=False):
        """現在のエディタの内容を一時的に保存する"""
        if revert:
            if GB.CACHE_EDITOR is not None:
                self.app.editor.text = GB.CACHE_EDITOR
                GB.EDITING_PATH = GB.STASHED_PATH
                GB.STASHED_PATH = None
                self.app.log("Editor content restored from stash.")
            else:
                self.app.log("No stashed content to restore.")
        else:
            GB.CACHE_EDITOR = self.app.editor.text
            GB.STASHED_PATH = GB.EDITING_PATH
            GB.EDITING_PATH = None
            self.app.log("Editor content stashed.")
            self.app.editor.text = ""

    