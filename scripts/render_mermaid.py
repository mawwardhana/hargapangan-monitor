#!/usr/bin/env python3
"""Bungkus sumber Mermaid menjadi .mermaid + .html (render via CDN, screenshot manual)."""
import sys
from pathlib import Path

TPL = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>body{{font-family:system-ui;margin:24px;background:#fff}}
#d{{border:1px solid #ddd;border-radius:8px;padding:16px}}</style></head>
<body><h2>{title}</h2><div id="d" class="mermaid">
{body}
</div><script>mermaid.initialize({{startOnLoad:true}});</script></body></html>"""


def main():
    if len(sys.argv) < 3:
        print("pakai: render_mermaid.py <sumber.mermaid> <judul> [keluaran]"); return
    src, title = Path(sys.argv[1]), sys.argv[2]
    base = Path(sys.argv[3]) if len(sys.argv) > 3 else src.with_suffix("")
    body = src.read_text(encoding="utf-8")
    Path(f"{base}.mermaid").write_text(body, encoding="utf-8")
    Path(f"{base}.html").write_text(TPL.format(title=title, body=body), encoding="utf-8")
    print(f"dibuat: {base}.mermaid + {base}.html")


if __name__ == "__main__":
    main()