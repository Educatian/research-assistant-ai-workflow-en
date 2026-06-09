"""render_fullguide.py — Build full-guide.html from full-guide.md.

Reuses the tutorial's visual system (BEGINNER_CSS, build_toc, callout +
wikilink processing) from the sibling render.py, but wraps the content in a
*reference*-flavored masthead instead of the "7-day beginner" one.

Usage (run from the repo dir so `import render` finds the local render.py):
    python render_fullguide.py --lang en
    python render_fullguide.py --lang ko   full-guide.md  full-guide.html
"""
from __future__ import annotations
import re, sys, io, html as htmllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import markdown
import render as base  # local render.py (also sets a utf-8 stdout wrapper on win32)

# ---- CLI ----
args = [a for a in sys.argv[1:]]
lang = "ko"
if "--lang" in args:
    i = args.index("--lang"); lang = args[i + 1]; del args[i:i + 2]
if len(args) == 1 and args[0].endswith(".html"):
    # one positional that is clearly the output -> keep default input
    GUIDE, OUT = Path("full-guide.md"), Path(args[0])
else:
    GUIDE = Path(args[0]) if len(args) > 0 else Path("full-guide.md")
    OUT   = Path(args[1]) if len(args) > 1 else Path("full-guide.html")

BASE = {
    "ko": "https://educatian.github.io/research-assistant-ai-workflow-ko",
    "en": "https://educatian.github.io/research-assistant-ai-workflow-en",
}[lang]

UI = {
    "ko": dict(
        kicker="레퍼런스 · 풀 가이드",
        deck_suffix=" — 14개 컴포넌트 전체 레퍼런스.",
        back="← 7일 튜토리얼로 돌아가기",
        toc="목차",
        kb_narrow="좁게", kb_dark="다크모드",
        tiles=[("유형", "레퍼런스"), ("분량", "16개 섹션"),
               ("레퍼런스", "17개 검증"), ("대상", "셋업 완료 후")],
        closing_mark="— 풀 레퍼런스 끝 —",
        closing_note='7일 셋업이 처음이라면 <a class="wikilink" href="index.html">초심자 튜토리얼</a>부터 보세요.',
        desc="Obsidian × Claude Code 연구보조 시스템 풀 레퍼런스 — 아키텍처·스크립트·온톨로지·프라이버시 전체.",
    ),
    "en": dict(
        kicker="REFERENCE · FULL GUIDE",
        deck_suffix=" — the complete 14-component reference.",
        back="← Back to the 7-day tutorial",
        toc="Contents",
        kb_narrow="narrow", kb_dark="dark mode",
        tiles=[("Type", "Reference"), ("Length", "16 sections"),
               ("References", "17 verified"), ("Audience", "After setup")],
        closing_mark="— End of full reference —",
        closing_note='New to the setup? Start with the <a class="wikilink" href="index.html">beginner tutorial</a>.',
        desc="The full reference for the Obsidian × Claude Code research-assistant system — architecture, scripts, ontology, privacy.",
    ),
}[lang]


def process_body(body_md: str) -> str:
    # Callouts (same emoji blockquote convention as render.py)
    for emoji, cls, label in [("💡", "tip", "💡 TIP"),
                              ("⚠️", "warn", "⚠ WATCH OUT"),
                              ("✅", "check", "✓ CHECK")]:
        body_md = re.sub(
            rf"^> {emoji} (\*\*[^*]+\*\*:?)?(.+?)(?=\n\n|\Z)",
            lambda m, cls=cls, label=label: f'<div class="callout callout-{cls}"><span class="cb">{label}</span> {(m.group(1) or "")}{m.group(2).strip()}</div>',
            body_md, flags=re.MULTILINE | re.DOTALL,
        )
    # Wikilinks → non-clickable chips (markdown [text](url) links pass through untouched)
    body_md = re.sub(r"\[\[([^\]|]+?)(\|[^\]]+)?\]\]",
                     lambda m: f'<span class="wikilink">{htmllib.escape(m.group(1).strip())}</span>',
                     body_md)
    md = markdown.Markdown(extensions=["extra", "fenced_code", "tables", "sane_lists"])
    html = md.convert(body_md)
    return html


def main() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    body_md, fm = base.strip_frontmatter(text)
    title = fm.get("title", "Research Assistant System Guide")
    subtitle = fm.get("subtitle", "Obsidian × Claude Code — the full reference")

    body_html = process_body(body_md)
    body_html, toc_html = base.build_toc(body_html)

    tiles = "".join(f"<div><span>{htmllib.escape(a)}</span><strong>{htmllib.escape(b)}</strong></div>"
                    for a, b in UI["tiles"])

    html_doc = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{htmllib.escape(title)}</title>
<meta name="description" content="{htmllib.escape(UI['desc'])}">
<link rel="canonical" href="{BASE}/full-guide.html">
<meta property="og:type" content="article">
<meta property="og:title" content="{htmllib.escape(title)}">
<meta property="og:description" content="{htmllib.escape(UI['desc'])}">
<meta property="og:url" content="{BASE}/full-guide.html">
<meta property="og:image" content="{BASE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="theme-color" content="#2d7d6e">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,800;1,500&family=Hahmlet:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.css">
<style>{base.BEGINNER_CSS}</style>
<style>
.backbar {{ max-width: 1180px; margin: 0 auto; padding: 18px 5vw 0; }}
.backbar a {{ font-family: "JetBrains Mono", monospace; font-size: 13px; color: var(--accent);
  text-decoration: none; border-bottom: 1px solid transparent; }}
.backbar a:hover {{ border-bottom-color: var(--accent); }}
a.wikilink {{ text-decoration: none; cursor: pointer; }}
a.wikilink:hover {{ filter: brightness(1.08); }}
</style>
</head>
<body>

<div class="backbar"><a href="index.html">{htmllib.escape(UI['back'])}</a></div>

<header class="masthead">
  <div class="mast-inner">
    <div class="mast-kicker">{htmllib.escape(UI['kicker'])}</div>
    <h1 class="mast-title">{htmllib.escape(title)}</h1>
    <p class="mast-deck">{htmllib.escape(subtitle)}{htmllib.escape(UI['deck_suffix'])}</p>
    <div class="mast-meta">{tiles}</div>
  </div>
</header>

<div class="layout">
  <aside class="toc">
    <div class="toc-label">{htmllib.escape(UI['toc'])}</div>
    <ol>{toc_html}</ol>
    <div class="toc-foot">
      <p><kbd>F</kbd> {htmllib.escape(UI['kb_narrow'])} · <kbd>D</kbd> {htmllib.escape(UI['kb_dark'])}</p>
    </div>
  </aside>
  <article class="prose">
    {body_html}
    <div class="closing">
      <div class="closing-mark">{htmllib.escape(UI['closing_mark'])}</div>
      <div class="closing-note">{UI['closing_note']}</div>
    </div>
  </article>
</div>

<script>
document.addEventListener('keydown', function(e) {{
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  if (e.key === 'f' || e.key === 'F') document.body.classList.toggle('narrow');
  if (e.key === 'd' || e.key === 'D') document.body.classList.toggle('dark');
}});
</script>
</body>
</html>"""
    OUT.write_text(html_doc, encoding="utf-8")
    print(f"[done] {OUT}  ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
