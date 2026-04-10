# Oriana

> A minimal, Python-first CLI code editor. Every operation is a Python command.

---

## 哲学

Oriana はすべての操作が Python 関数として定義された CLI エディタです。  
保存・git 操作・シェル実行・設定変更、すべてがコマンドラインから呼べる Python 関数のショートカットに過ぎません。  
`config.json` 一枚でどの PC でも同じ環境を再現できます。

---

## インストール

```bash
git clone https://github.com/yourname/oriana.git
cd oriana
pip install -r requirements.txt
```

### 依存ライブラリ

```
prompt_toolkit
pygments
jedi
pyperclip
gitpython
```

---

## 起動

```bash
python oriana.py
```

コマンドラインから以下のプレフィックスで各APIを呼び出します。

| プレフィックス | クラス | 役割 |
|--------------|--------|------|
| `ope` | `EditorAPI` | エディタ本体の操作 |
| `cfg` | `ConfigAPI` | 設定・テーマ・エイリアス管理 |
| `git` | `GitAPI` | git操作 |
| `term` | `TerminalAPI` | シェル・コンソール・コード実行 |

---
## APIリファレンス
---

## EditorAPI (`ope`)

エディタのバッファ・カーソル・ファイルを操作するAPIです。

---

### `ope.create(path)`

新しいファイルを作成して開きます。指定パスにファイルが既に存在する場合はログに通知したうえでそのまま開きます。

```
:ope.create("new_script.py")
```

---

### `ope.open(path)`

指定したファイルをエディタに読み込みます。存在しないパスを指定した場合は新規ファイルとして扱います。`GB.EDITING_PATH`（グローバル状態）も同時に更新されます。

```
:ope.open("main.py")
```

---

### `ope.save(path=None)`

現在のエディタ内容をファイルに保存します。`path` を指定すると保存先を変更します（名前をつけて保存）。ファイルが未指定の場合はログにエラーを表示します。

```
:ope.save()
:ope.save("output.py")
```

---

### `ope.focus_cmd()`

フォーカスをコマンドラインに移します。

```
:ope.focus_cmd()
```

---

### `ope.focus_edit()`

フォーカスをエディタに移します。

```
:ope.focus_edit()
```

---

### `ope.quit(force=False)`

エディタを終了します。
`force=False`（デフォルト）では、編集中の内容が保存されていない場合は保存を促すメッセージを表示して終了を中断します。`force=True` で強制終了します。

```
:ope.quit()
```

---

### `ope.copy(line_num=None)`

クリップボードにコピーします。`line_num` を指定するとその行をコピーします。省略時は選択範囲、選択がなければ現在行をコピーします。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `line_num` | `None` | コピーする行番号（1始まり） |

```
:ope.copy()      # 現在行 or 選択範囲
:ope.copy(10)    # 10行目
```

---

### `ope.paste(line_num=None)`

クリップボードの内容を貼り付けます。`line_num` を指定するとその行の内容を置き換えます。省略時はカーソル位置に挿入します。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `line_num` | `None` | 貼り付け先の行番号（1始まり） |

```
:ope.paste()     # カーソル位置に挿入
:ope.paste(10)   # 10行目を置き換え
```

---

### `ope.delete(line_num=None)`

内容を削除します。`line_num` を指定するとその行を削除します。省略時は選択範囲、選択がなければ現在行を削除します。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `line_num` | `None` | 削除する行番号（1始まり） |

```
:ope.delete()    # 現在行 or 選択範囲
:ope.delete(5)   # 5行目を削除
```

---

### `ope.undo()`

直前の操作を取り消します。

```
:ope.undo()
```

---

### `ope.redo()`

取り消した操作をやり直します。

```
:ope.redo()
```

---

### `ope.clear()`

エディタの内容をすべてクリアします。

```
:ope.clear()
```

---

### `ope.jump(line_num=1)`

指定した行番号にカーソルを移動します。範囲外の行番号はログにエラーを表示します。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `line_num` | `1` | ジャンプ先の行番号（1始まり） |

```
:ope.jump(42)
```

---

### `ope.stash(revert=False)`

エディタの内容をグローバル変数（`GB.CACHE_EDITOR`）に一時退避します。`revert=True` で退避した内容を復元します。退避中はエディタがクリアされ、`GB.EDITING_PATH` も退避されます。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `revert` | `False` | `True` で退避内容を復元 |

```
:ope.stash()             # 退避（エディタがクリアされる）
:ope.stash(revert=True)  # 復元
```

---

## ConfigAPI (`cfg`)

`config.json` への読み書きを担うAPIです。変更は即座にファイルに保存されます。

---

### `cfg.set_editor_config(item, value)`

エディタの属性を動的に変更し、`config.json` の `"editor"` セクションに保存します。

```
:cfg.set_editor_config("is_complete_while_typing", False)
```

---

### `cfg.set_editor_theme(theme_dict, overwrite=False)`

テーマを変更します。`overwrite=False`（デフォルト）では既存テーマにマージします。`overwrite=True` では既存テーマを完全に置き換えます。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `theme_dict` | — | 適用するテーマの辞書 |
| `overwrite` | `False` | `True` で既存テーマを完全置換 |

```
:cfg.set_editor_theme({"editor": "bg:#1e1e1e fg:#d4d4d4"})
:cfg.set_editor_theme({"editor": "bg:#000000"}, overwrite=True)
```

---

### `cfg.set_alias(alias, command)`

コマンドエイリアスを追加・更新し、`config.json` の `"aliases"` セクションに保存します。

```
:cfg.set_alias("w", "ope.save()")
:cfg.set_alias("o", "ope.open(arg)")
```

---

### `cfg.set_keybind(key_combo, command)`

キーバインドを追加・更新し、`config.json` の `"shortcuts"` セクションに保存します。`key_combo` は prompt_toolkit のキー表記に従います。

| 表記例 | 意味 |
|--------|------|
| `"c-s"` | Ctrl+S |
| `"c-q"` | Ctrl+Q |
| `"f5"` | F5キー |

```
:cfg.set_keybind("c-s", "ope.save()")
:cfg.set_keybind("c-q", "ope.quit()")
```

---

## GitAPI (`git`)

開いているファイルが git リポジトリ内にあり、かつ git の追跡対象である場合のみ有効です。それ以外の場合は各メソッドがログにエラーを表示して処理を中断します。

---

### `git.add(is_all=False, path=None)`

ファイルをステージングします。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `is_all` | `False` | `True` で全変更をステージング（`git add -A`） |
| `path` | `None` | 対象ファイルのリスト。省略時は現在開いているファイル |

```
:git.add()
:git.add(is_all=True)
:git.add(path=["main.py", "utils.py"])
```

---

### `git.commit(message="commit from Oriana")`

ステージされた変更をコミットします。

```
:git.commit("feat: 新機能を追加")
```

---

### `git.reset()`

ステージングを取り消します（`git reset`）。

```
:git.reset()
```

---

### `git.checkout(branch, is_force=False)`

指定ブランチに切り替えます。`is_force=True` で未コミットの変更を破棄して強制切り替えします。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `branch` | — | 切り替え先ブランチ名 |
| `is_force` | `False` | `True` で強制切り替え |

```
:git.checkout("main")
:git.checkout("feature/new", is_force=True)
```

---

### `git.pull(remote="origin", branch="main")`

リモートから変更を取得します。指定したリモートが存在しない場合はログにエラーを表示します。

```
:git.pull()
:git.pull(remote="upstream", branch="develop")
```

---

### `git.push(remote="origin", branch="main")`

リモートに変更を送信します。指定したリモートが存在しない場合はログにエラーを表示します。

```
:git.push()
:git.push(remote="origin", branch="feature/new")
```

---

## TerminalAPI (`shr`)

シェルコマンドの実行・コンソールの制御・コードの実行を担うAPIです。

---

### `shr.shell(editor=False, command=None, clear_console=True, open_console=True)`

シェルコマンドを実行し、結果をコンソールに表示します。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `editor` | `False` | `True` でエディタ内容をコマンドとして実行 |
| `command` | `None` | 実行するシェルコマンド文字列 |
| `clear_console` | `True` | 実行前にコンソールをクリア |
| `open_console` | `True` | 実行後にコンソールを自動で開く |

```
:shr.shell(command="ls -la")
:shr.shell(command="make build", clear_console=False)
:shr.shell(editor=True)   # エディタの内容をシェルで実行
```

---

### `shr.console()`

エディタとコンソールの表示をトグルします。どちらの内容も切り替え時に保持されます。

```
:shr.console()
```

---

### `shr.clear()`

コンソールの表示内容をクリアします。

```
:shr.clear()
```

---

### `shr.run_py(clear_console=True, open_console=True, interpreter=None, venv=None)`

現在のエディタ内容を一時ファイル（`.py`）として保存し、Pythonインタプリタで実行します。結果・エラーはコンソールに表示されます。タイムアウトは30秒です。`config.json` の `run_env` セクションでインタプリタとvenvパスを指定できます。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `clear_console` | `True` | 実行前にコンソールをクリア |
| `open_console` | `True` | 実行後にコンソールを自動で開く |
| `interpreter` | `None` | 使用するPythonインタプリタのパス。`None` でデフォルトインタプリタ |
| `venv` | `None` | 使用する仮想環境のパス。`None` でデフォルト環境 |


```
:shr.run_py()
:shr.run_py(clear_console=False, open_console=False)
:shr.run_py(interpreter="/usr/bin/python3", venv=".venv")
```