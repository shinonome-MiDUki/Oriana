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
pip install oriana==2026.1.1
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
| `shr` | `TerminalAPI` | シェル・コンソール・コード実行 |
| `shelf` | `ShelfAPI` | シェルフ・バッファ管理 |
| `plug` | `PluginAPI` | プラグイン・カスタムコマンド管理 |

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

### `ope.quit(force=False, clear_cache=True)`

エディタを終了します。`force=False`（デフォルト）では、編集中のファイルを自動保存してから終了します。ファイルが未指定の場合は終了を中断しログに通知します。`force=True` で強制終了します。`clear_cache=True`（デフォルト）では終了時にシェルフキャッシュをクリアします。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `force` | `False` | `True` で強制終了（未保存内容は破棄） |
| `clear_cache` | `True` | `True` で終了時にシェルフキャッシュをクリア |

```
:ope.quit()
:ope.quit(force=True)
:ope.quit(force=True, clear_cache=False)
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

### `cfg.open_config()`

`config.json` をエディタで直接開きます。

```
:cfg.open_config()
```

---

### `cfg.clear_log(clear_lines=100)`

`editor.log` の末尾から指定行数を残して古いログを削除します。`clear_lines=0` で何もしません。`clear_lines=-1` でログファイルを完全に削除します。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `clear_lines` | `100` | 残す行数。`0` で何もしない、`-1` でファイルごと削除 |

```
:cfg.clear_log()        # 末尾100行を残して削除
:cfg.clear_log(50)      # 末尾50行を残して削除
:cfg.clear_log(-1)      # ログファイルを完全削除
:cfg.clear_log(0)       # 何もしない
```

---

### `cfg.reset_config(confirm=False)`

`config.json` を削除します。次回起動時にデフォルト設定で再生成されます。誤操作防止のため `confirm=True` を明示的に渡す必要があります。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `confirm` | `False` | `True` を渡さないと実行されない |

```
:cfg.reset_config(confirm=True)
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

シェルコマンドの実行・コンソールの制御・コードの実行・パッケージ管理を担うAPIです。

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

現在のエディタ内容を一時ファイル（`.py`）として保存し、Pythonインタプリタで実行します。結果・エラーはコンソールに表示されます。タイムアウトは `config.json` の `"timeout"` で設定できます（デフォルト30秒）。`venv` を指定した場合はそのvenv内のインタプリタを直接使用します。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `clear_console` | `True` | 実行前にコンソールをクリア |
| `open_console` | `True` | 実行後にコンソールを自動で開く |
| `interpreter` | `None` | 使用するPythonインタプリタのパス。`None` でデフォルトインタプリタ |
| `venv` | `None` | 使用する仮想環境のパス。`None` でデフォルト環境 |

```
:shr.run_py()
:shr.run_py(clear_console=False, open_console=False)
:shr.run_py(venv=".venv")
:shr.run_py(interpreter="/usr/bin/python3")
```

---

### `shr.venv(dir, interpreter=None, remove=False)`

仮想環境を作成または削除します。`remove=True` の場合、安全チェックを行ったうえで指定ディレクトリを削除します。`/`・`C:\` 等の危険なパスは削除できません。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `dir` | — | 仮想環境のパス |
| `interpreter` | `None` | 使用するPythonインタプリタのパス。`None` でデフォルトインタプリタ |
| `remove` | `False` | `True` で仮想環境を削除 |

```
:shr.venv(".venv")                          # 作成
:shr.venv(".venv", interpreter="/usr/bin/python3.11")
:shr.venv(".venv", remove=True)             # 削除
```

---

### `shr.package(name, venv=None, force=False, version=None, install=True, upgrade=False, pip3=False)`

pip を使ってパッケージを管理します。`venv` を指定するとそのvenv内の pip を使用します。結果はコンソールに表示されます。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `name` | — | パッケージ名 |
| `venv` | `None` | 使用する仮想環境のパス |
| `force` | `False` | `True` でvenvが存在しない場合に自動作成 |
| `version` | `None` | インストールするバージョン（例: `"1.2.3"`） |
| `install` | `True` | `False` でアンインストール |
| `upgrade` | `False` | `True` で `--upgrade` オプションを付与 |
| `pip3` | `False` | `True` で `pip3` を使用 |

```
:shr.package("requests")
:shr.package("numpy", version="1.26.0")
:shr.package("requests", venv=".venv")
:shr.package("requests", install=False)     # アンインストール
:shr.package("pip", upgrade=True)           # pip自体をアップグレード
```

---

## ShelfAPI (`shelf`)

シェルフはエディタのバッファを名前付きで退避・復元する仕組みです。複数のファイルを切り替えながら作業する際に使用します。シェルフの状態はディスク上にキャッシュされ、`ope.quit()` 実行時に自動でクリアされます。

---

### `shelf.shelf(name)`

現在のエディタ内容を指定した名前でシェルフに退避します。退避後はエディタがクリアされ、`GB.EDITING_PATH` と `GB.WORKING_SHELF` がリセットされます。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `name` | — | シェルフの名前 |

```
:shelf.shelf("feature-work")
```

---

### `shelf.switch_shelf(name, discard_current=False)`

指定したシェルフに切り替えます。現在作業中のシェルフがある場合は自動で退避してから切り替えます。`discard_current=True` で現在の内容を退避せずに破棄して切り替えます。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `name` | — | 切り替え先シェルフの名前 |
| `discard_current` | `False` | `True` で現在の内容を破棄して切り替え |

```
:shelf.switch_shelf("feature-work")
:shelf.switch_shelf("hotfix", discard_current=True)
```

---

### `shelf.unshelf(name, auto_save=True)`

シェルフを解除します。`auto_save=True`（デフォルト）では、シェルフに紐付いたファイルパスに内容を自動保存してからキャッシュを削除します。ファイルパスが未設定の場合は保存できないためログに通知し処理を中断します。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `name` | — | 解除するシェルフの名前 |
| `auto_save` | `True` | `True` で自動保存してからキャッシュを削除 |

```
:shelf.unshelf("feature-work")
:shelf.unshelf("temp", auto_save=False)   # 保存せずに破棄
```

---

### `shelf.clear_shelves()`

全シェルフのキャッシュファイル（`.pkl`）を削除し、`shelf.json` を初期化します。`ope.quit()` 実行時に自動で呼ばれます。

```
:shelf.clear_shelves()
```

---

## PluginAPI (`plug`)

カスタムコマンド（CCMD）の登録・プラグインの管理を担うAPIです。

---

### `plug.ccmd_template()`

カスタムコマンドのテンプレートコードをエディタに読み込みます。テンプレートを編集後、`plug.reg_ccmd()` で登録します。実行後は `GB.EDITING_PATH` がリセットされます。

```
:plug.ccmd_template()
```

---

### `plug.reg_ccmd()`

現在のエディタ内容をカスタムコマンドとして登録します。コードの1行目に `@useapi(api1, api2, ...)` 形式でデコレータを記述することで、使用するAPIを宣言できます。登録されたコマンドは `ccmd.py` に追記されます。

```
:plug.reg_ccmd()
```

CCMDの記述例：

```python
@useapi("ope", "shr")
def my_command():
    ope.save()
    shr.run_py()
```

---

### `plug.set_plugin(name)`

現在のエディタ内容を指定した名前のプラグインファイルとして保存します。保存先は `PLUGIN_DIR/oriana_client/package/` です。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `name` | — | プラグインのファイル名（拡張子なし） |

```
:plug.set_plugin("my_plugin")
```

---

### `plug.set_ext_plugin(ext)`

外部のプラグインファイルを `PLUGIN_DIR/oriana_client/package/` にコピーして登録します。指定パスが存在しない場合はログにエラーを表示します。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `ext` | — | 登録する外部プラグインファイルのパス |

```
:plug.set_ext_plugin("/path/to/my_plugin.py")
```

---

### `plug.set_pkg(ext)`

外部のパッケージディレクトリを `PLUGIN_DIR/oriana_client/` にコピーし、`config.json` の `"plugin"."package"` リストに追加します。指定パスが存在しない場合はログにエラーを表示します。

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `ext` | — | 登録する外部パッケージディレクトリのパス |

```
:plug.set_pkg("/path/to/my_package")
```