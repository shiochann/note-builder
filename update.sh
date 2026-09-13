#!/bin/bash
# vault の配布スキルをこのリポジトリに同期して zip を作り直す
set -e
cd "$(dirname "$0")"
SRC="/Users/shio_chan/Library/Mobile Documents/iCloud~md~obsidian/Documents/しおちゃん/02_自分のコンテンツ/note/配布スキル/note-builder"
rm -rf skill note-builder.zip
mkdir -p skill
cp -R "$SRC"/. skill/
find skill -name .DS_Store -delete
# zip の中身は note-builder/ フォルダ1つ（解凍してそのまま置ける）
TMP=$(mktemp -d)
cp -R skill "$TMP/note-builder"
(cd "$TMP" && zip -qr "$OLDPWD/note-builder.zip" note-builder -x '*.DS_Store')
rm -rf "$TMP"
echo "zip: $(du -h note-builder.zip | cut -f1)"
echo "次: git add -A && git commit -m 'Update skill' && git push"
