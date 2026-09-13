#!/usr/bin/env python3
"""10_本編.md（と任意で12_セールスレター.md）を、noteやBrainのエディタに貼れるHTMLに変換する。

使い方:
  python3 md_to_html.py <ノートフォルダ> [--with-letter] [--platform note|brain]

出力:
  <ノートフォルダ>/20_貼り付け用/全文.html      … 全体（手動で貼るとき用）
  <ノートフォルダ>/20_貼り付け用/NN_章名.html   … 章ごと（Chromeから流し込むとき用）
  <ノートフォルダ>/20_貼り付け用/summary.json  … 見出し数・図解の目印・有料ラインの位置

依存ライブラリなし。見出しは # → h2（大見出し）、## → h3（小見出し）、### → 太字段落。
表・脚注・HTMLは扱わない（記法ルールで使わないことになっている）。
"""
import html, json, re, sys
from pathlib import Path

PAID = "=====ここから有料====="
FIG = re.compile(r"^【図解\d+｜[^】]*】")

def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s

def convert(md: str):
    out, info = [], {"h2": 0, "h3": 0, "figures": [], "paid_after": None}
    lines = md.splitlines()
    i, para, lst, quote, code = 0, [], None, [], None
    want_paid = False

    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + "<br>".join(inline(x) for x in para) + "</p>")
            para = []
    def flush_list():
        nonlocal lst
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            lst = None
    def flush_quote():
        nonlocal quote
        if quote:
            out.append("<blockquote><p>" + "<br>".join(inline(x) for x in quote) + "</p></blockquote>")
            quote = []
    def flush_all():
        flush_para(); flush_list(); flush_quote()

    while i < len(lines):
        ln = lines[i]; i += 1
        if code is not None:
            if ln.strip().startswith("```"):
                out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>"); code = None
            else:
                code.append(ln)
            continue
        if ln.strip().startswith("```"):
            flush_all(); code = []; continue
        if ln.strip() == PAID:
            flush_all(); want_paid = True; continue
        if not ln.strip():
            flush_all(); continue
        m = re.match(r"^(#{1,3})\s+(.*)", ln)
        if m:
            flush_all()
            level, text = len(m.group(1)), m.group(2).strip()
            if want_paid and info["paid_after"] is None:
                info["paid_after"] = text
            if level == 1:
                out.append(f"<h2>{inline(text)}</h2>"); info["h2"] += 1
            elif level == 2:
                out.append(f"<h3>{inline(text)}</h3>"); info["h3"] += 1
            else:
                out.append(f"<p><strong>{inline(text)}</strong></p>")
            continue
        if FIG.match(ln.strip()):
            flush_all(); info["figures"].append(ln.strip())
            out.append(f"<p>{inline(ln.strip())}</p>"); continue
        m = re.match(r"^\s*[-・]\s+(.*)", ln)
        if m:
            flush_para(); flush_quote()
            if not lst or lst[0] != "ul": flush_list(); lst = ("ul", [])
            lst[1].append(m.group(1)); continue
        m = re.match(r"^\s*\d+[.．]\s+(.*)", ln)
        if m:
            flush_para(); flush_quote()
            if not lst or lst[0] != "ol": flush_list(); lst = ("ol", [])
            lst[1].append(m.group(1)); continue
        if ln.startswith(">"):
            flush_para(); flush_list(); quote.append(ln.lstrip("> ").rstrip()); continue
        if ln.strip() == "---":
            flush_all(); continue
        flush_list(); flush_quote(); para.append(ln.rstrip())
    flush_all()
    return out, info

def split_chapters(blocks):
    """h2（章）ごとに分ける。最初のh2より前は 00_冒頭 にまとめる。"""
    chapters, cur, name = [], [], "冒頭"
    for b in blocks:
        if b.startswith("<h2>") and cur:
            chapters.append((name, cur)); cur = []
        if b.startswith("<h2>"):
            name = re.sub(r"<.*?>", "", b)
        cur.append(b)
    if cur: chapters.append((name, cur))
    return chapters

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    folder = Path(sys.argv[1]); with_letter = "--with-letter" in sys.argv
    body = (folder / "10_本編.md").read_text(encoding="utf-8")
    md = body
    if with_letter:
        letter = (folder / "12_セールスレター.md").read_text(encoding="utf-8")
        letter = re.split(r"^## 制作メモ.*$", letter, flags=re.M)[0]  # 制作メモ以降は貼らない
        letter = re.sub(r"^# .*\n", "", letter, count=1)              # ファイル先頭の # タイトル行は貼らない
        md = letter.rstrip() + "\n\n" + body
    blocks, info = convert(md)
    outdir = folder / "20_貼り付け用"; outdir.mkdir(exist_ok=True)
    for f in outdir.glob("*.html"): f.unlink()
    (outdir / "全文.html").write_text(
        "<!doctype html><meta charset='utf-8'><body>" + "\n".join(blocks) + "</body>", encoding="utf-8")
    files = []
    for n, (name, bl) in enumerate(split_chapters(blocks)):
        safe = re.sub(r"[\\/:*?\"<>|\s]+", "_", name)[:30]
        fn = f"{n:02d}_{safe}.html"
        (outdir / fn).write_text("\n".join(bl), encoding="utf-8"); files.append(fn)
    info.update({"chapters": files, "with_letter": with_letter, "chars": len(md)})
    (outdir / "summary.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(info, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
