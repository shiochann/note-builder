# フェーズ7｜Chromeで note / Brain に流し込む

**下書き保存まで。公開ボタンは押さない。** 公開・価格設定・有料ラインの確定は人間がやる。

## 前提（満たしていなければ、ここで止めてユーザーに伝える）

- Claude in Chrome（Chrome拡張）が入っていて、Claude Code から `mcp__claude-in-chrome__*` のツールが使えること
  - ツールが「deferred」なら ToolSearch で一括ロードする：
    `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__find,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__javascript_tool`
- そのChromeで note（または Brain）に **ログイン済み** であること。ログインはユーザーがやる。Claude はID・パスワードを入力しない
- 対話セッションで動かすこと（`claude -p` などのヘッドレスでは Chrome を触れない）

## 手順

### 1. HTMLに変換する

```bash
python3 <スキルの場所>/scripts/md_to_html.py "<ノートフォルダ>" --with-letter
```

- `--with-letter` はセールスレターを冒頭（無料部分）に含める。含めるかどうかは先にユーザーに聞く
- `20_貼り付け用/` に 全文.html・章ごとのHTML・summary.json ができる
- summary.json の `paid_after` が有料ラインの直後の見出し。`figures` が画像に差し替える目印の一覧

### 2. エディタを開く

- note：新しいタブで `https://note.com/notes/new` を開く。ログイン画面にリダイレクトされたら、ユーザーにログインしてもらってから続ける
- Brain：ログイン後のマイページから「コンテンツを作成（出品）」に進む。エディタのURLが分からなければ、ユーザーに「エディタを開いた状態にしてください」と頼み、開いたタブで続ける

### 3. タイトルを入れる

`find` で「記事タイトル」「タイトル」のプレースホルダを持つ欄を探し、`02_企画書.md` のノート名を `form_input` または `type` で入れる。

### 4. 本文を章ごとに流し込む

本文の編集領域（note は `.ProseMirror`、なければ `[contenteditable="true"]`）を探し、**章ごとのHTMLを順番に** 合成pasteで入れる。1章ずつ入れるのは、途中で崩れたときに戻れるようにするため。

`javascript_tool` で実行するコード（`HTML_HERE` と `TEXT_HERE` を章のHTMLとプレーンテキストに置き換える）：

```js
const el = document.querySelector('.ProseMirror') || document.querySelector('[contenteditable="true"]');
if (!el) throw new Error('editor not found');
el.focus();
// カーソルを末尾へ
const sel = window.getSelection(); const r = document.createRange();
r.selectNodeContents(el); r.collapse(false); sel.removeAllRanges(); sel.addRange(r);
const dt = new DataTransfer();
dt.setData('text/html', HTML_HERE);
dt.setData('text/plain', TEXT_HERE);
el.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
({h2: el.querySelectorAll('h2').length, h3: el.querySelectorAll('h3').length, chars: el.innerText.length});
```

1章入れるごとに、返ってきた見出し数が増えているかを確認する。**増えていなければ次の章に進まず**、フォールバックへ。

### フォールバック（合成pasteが効かないとき）

1. `document.execCommand('insertHTML', false, HTML_HERE)` を試す
2. それでもダメなら、ユーザーに手動で貼ってもらう：
   - `20_貼り付け用/全文.html` を Chrome で開く（ファイルをダブルクリック）
   - 表示されたページで全選択（⌘A）→コピー（⌘C）→ エディタに貼り付け（⌘V）
   - リッチテキストとしてコピーされるので、見出し・太字・箇条書きは保たれる
   - 貼れたらユーザーに「貼れました」と言ってもらい、手順5へ

### 5. 確認する

`javascript_tool` でエディタ内の h2 / h3 の数を取り、summary.json の h2 / h3 と一致するかを見る。
`【図解` を含む段落の数が `figures` の数と一致するかも見る。
ずれていたら、どの章でずれたかを特定して、その章だけ消して入れ直す（エディタ内で該当h2から次のh2までを選択して削除）。

### 6. 下書き保存する

- note：`find` で「下書き保存」ボタンを探して押す。押した後、画面に「保存しました」等が出るのを確認する
- Brain：「下書き保存」「保存」に相当するボタンを探して押す。見つからなければユーザーに聞く
- **「公開に進む」「公開設定」「投稿する」「出品する」は押さない**

### 7. ユーザーに報告する

以下を伝えて終わる：

- 下書きのURL（タブのURL）
- 有料ラインを置く位置：`paid_after` の見出しの直前
- 画像に差し替える目印の一覧（`figures`）と、指示書の場所（`03_図解計画.md`）
- 価格と有料ラインの設定、公開ボタンはユーザーが行うこと

## やってはいけないこと

- ログイン情報を入力する
- 公開・出品・投稿のボタンを押す
- 価格を設定する
- 貼り付け結果を確認せずに終わる
- 見出し数がずれているのに「貼れました」と報告する
