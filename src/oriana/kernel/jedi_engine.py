import jedi
from prompt_toolkit.completion import Completer, Completion

class JediCompleter(Completer):
    """
    jedi ライブラリを直接使用するカスタム補完クラス
    """
    def __init__(self, interpreter_env=None):
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