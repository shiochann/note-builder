# note-builder

**ノートを、企画からセールスレターまで。質問に答えるだけで。**

note / Brain の有料ノートを、ヒアリング → 知識の整理 → 核となる主張 → 目次＋特典 → 本編（1章ずつ・図解の指示書つき） → セールスレター の順に作る Claude Code スキルです。
できあがった本編は1ファイルなので、開いてコピーして note に貼るだけです。

配布ページ → **https://shiochann.github.io/note-builder/**

---

## ダウンロード

- [note-builder.zip](note-builder.zip) — スキル一式
- [skill/](skill/) — 同じ中身をそのまま置いてあります（GitHub上で読めます）

## インストール

zip を解凍して、フォルダごとどちらかに置くだけです。

```
~/.claude/skills/note-builder/                # どのプロジェクトでも使う
<プロジェクト>/.claude/skills/note-builder/   # そのプロジェクトだけで使う
```

Claude Code を開き直して、こう打ちます。

```
/note-builder
```

途中でやめても `_state.md` に進捗が残るので、もう一度同じコマンドで続きから再開できます。

## 中身

```
note-builder/
├── SKILL.md                    本体。フェーズの流れと各フェーズのルール
├── README.md                   渡された人が最初に読む説明書
├── references/
│   ├── 01_interview.md         ヒアリングの質問票
│   ├── 02_claim-patterns.md    核となる主張の型
│   ├── 03_toc-patterns.md      目次の型と有料ラインの置き方
│   ├── 04_diagram-types.md     図解の種類と指示書の書き方
│   ├── 05_platform-rules.md    note / Brain で崩れない記法
│   └── 06_letter-structure.md  セールスレターの骨格と整合チェック
└── templates/
    ├── _state.md               進捗ファイルの雛形
    └── 企画書.md               主張・特典・目次の雛形
```

## できあがるもの（ノート1本 = 1フォルダ）

```
ノート名/
├── _state.md            進捗
├── 00_ヒアリング.md      答えの記録
├── 01_domain.md         まとめた知識
├── 02_企画書.md         主張・特典・目次
├── 03_図解計画.md       図解の指示書
├── 10_本編.md           本編。これをそのまま note に貼る
└── 11_セールスレター.md  販売ページ用
```

## 更新のしかた（管理者用）

vault 側の `02_自分のコンテンツ/note/配布スキル/note-builder/` を直してから:

```bash
bash update.sh && git add -A && git commit -m "Update skill" && git push
```
