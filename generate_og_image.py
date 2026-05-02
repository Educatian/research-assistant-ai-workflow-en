"""
generate_og_image.py — render a 1200x630 social-preview image (og.png) by
designing it as HTML+CSS and screenshotting via Playwright. Real web fonts
(Inter + Source Serif from CDN), CSS gradients, shadows, proper kerning.

Usage: python generate_og_image.py
Writes: ./og.png and ./og.jpg  (1200x630)

Requires: pip install playwright pillow && playwright install chromium
"""
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "og.png"

OG_HTML = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;0,8..60,800&family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #fbfaf6;
    --bg-soft: #f4f1e8;
    --ink: #2a2418;
    --ink-2: #5a5140;
    --ink-3: #8a7f68;
    --teal: #2d7d6e;
    --orange: #d88a3a;
    --rust: #c4593f;
    --purple: #9b7eb7;
    --green: #4a7c59;
    --serif: "Source Serif 4", "Playfair Display", Georgia, serif;
    --sans: "Inter", -apple-system, sans-serif;
    --mono: "JetBrains Mono", monospace;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { width: 1200px; height: 630px; overflow: hidden; }
  body {
    font-family: var(--sans);
    color: var(--ink);
    background:
      radial-gradient(ellipse at 90% 10%, rgba(216,138,58,0.18), transparent 50%),
      radial-gradient(ellipse at 10% 90%, rgba(45,125,110,0.12), transparent 50%),
      var(--bg);
    position: relative;
    -webkit-font-smoothing: antialiased;
  }

  .corner {
    position: absolute;
    top: 36px;
    right: 48px;
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.18em;
    color: var(--orange);
    text-transform: uppercase;
  }
  .corner::before { content: "✦  "; color: var(--teal); }

  .grid {
    display: grid;
    grid-template-columns: 690px 1fr;
    gap: 60px;
    padding: 88px 60px 0 72px;
    height: 100%;
  }

  .left { display: flex; flex-direction: column; justify-content: flex-start; }
  .kicker {
    font-family: var(--mono);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.2em;
    color: var(--ink-3);
    text-transform: uppercase;
    margin-bottom: 22px;
  }
  .kicker .badge {
    background: var(--teal);
    color: #fff;
    padding: 3px 10px;
    border-radius: 3px;
    margin-right: 10px;
  }
  h1 {
    font-family: var(--serif);
    font-weight: 800;
    font-size: 68px;
    line-height: 1.05;
    letter-spacing: -0.025em;
    color: var(--ink);
    margin-bottom: 6px;
  }
  .h1-second {
    font-family: var(--serif);
    font-weight: 800;
    font-size: 68px;
    line-height: 1.05;
    letter-spacing: -0.025em;
    color: var(--ink);
    margin-bottom: 16px;
  }
  .sub {
    font-family: var(--serif);
    font-weight: 600;
    font-style: italic;
    font-size: 26px;
    line-height: 1.2;
    color: var(--teal);
    margin-bottom: 18px;
    letter-spacing: -0.005em;
  }
  .accent-bar {
    width: 96px;
    height: 4px;
    background: linear-gradient(90deg, var(--teal), var(--orange));
    border-radius: 2px;
    margin-bottom: 24px;
  }
  .deck {
    font-family: var(--sans);
    font-size: 17px;
    font-weight: 400;
    line-height: 1.55;
    color: var(--ink-2);
    max-width: 560px;
  }
  .deck strong { color: var(--ink); font-weight: 700; }

  .stats {
    display: flex;
    gap: 0;
    margin-top: 30px;
    border-top: 1px solid #d8cfb8;
    border-bottom: 1px solid #d8cfb8;
    padding: 16px 0;
    max-width: 600px;
  }
  .stat {
    flex: 1;
    border-right: 1px dashed #d8cfb8;
    padding: 0 18px;
  }
  .stat:first-child { padding-left: 0; }
  .stat:last-child { border-right: none; }
  .stat .label {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-3);
    font-weight: 700;
    margin-bottom: 4px;
  }
  .stat .value {
    font-family: var(--serif);
    font-size: 26px;
    font-weight: 700;
    color: var(--teal);
  }

  .author {
    position: absolute;
    bottom: 36px;
    left: 72px;
    right: 60px;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 13px;
    color: var(--ink-2);
  }
  .author .by-label {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--ink-3);
    font-weight: 700;
    margin-right: 10px;
  }
  .author .name {
    font-family: var(--serif);
    font-weight: 700;
    font-size: 18px;
    color: var(--ink);
    margin-right: 12px;
  }
  .author .aff {
    font-style: italic;
    color: var(--ink-2);
  }
  .author .url {
    font-family: var(--mono);
    font-size: 12px;
    color: var(--orange);
    font-weight: 500;
  }

  .right { position: relative; padding-top: 28px; }
  .right-label {
    position: absolute;
    top: 0;
    right: 0;
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.2em;
    color: var(--ink-3);
    text-transform: uppercase;
  }
  .right-label::before { content: "↘ "; color: var(--orange); margin-right: 4px; }

  .days {
    display: flex;
    flex-direction: column;
    gap: 9px;
    margin-top: 50px;
  }
  .day {
    display: grid;
    grid-template-columns: 56px 1fr;
    gap: 14px;
    align-items: center;
    padding: 7px 14px;
    background: #fff;
    border-radius: 10px;
    border: 1px solid rgba(60,45,20,.08);
    box-shadow: 0 4px 14px rgba(60,45,20,.04);
  }
  .day .num {
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: #fff;
    background: var(--teal);
    padding: 6px 10px;
    border-radius: 6px;
    text-align: center;
  }
  .day:nth-child(2) .num { background: var(--orange); }
  .day:nth-child(3) .num { background: var(--purple); }
  .day:nth-child(4) .num { background: var(--ink); }
  .day:nth-child(5) .num { background: var(--green); }
  .day:nth-child(6) .num { background: var(--rust); }
  .day:nth-child(7) .num { background: #e8a770; }
  .day .name {
    font-family: var(--serif);
    font-size: 18px;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: -0.01em;
  }
  .day .name .desc {
    font-family: var(--sans);
    font-size: 12px;
    font-weight: 400;
    color: var(--ink-3);
    margin-left: 8px;
  }
</style>
</head>
<body>

<div class="corner">VOL.01 · 2026 SPRING</div>

<div class="grid">
  <div class="left">
    <div class="kicker"><span class="badge">FIELD GUIDE</span>OBSIDIAN × CLAUDE CODE</div>
    <h1>A Research Assistant</h1>
    <div class="h1-second">System for PhDs</div>
    <div class="sub">7-Day setup · for researchers</div>
    <div class="accent-bar"></div>
    <div class="deck">Spend 1-2 hours/day for a week and your vault has a working system. <strong>Local-first</strong>, <strong>~$1-2/month</strong>, <strong>BYOK</strong>. Step-by-step, with diagrams.</div>

    <div class="stats">
      <div class="stat"><div class="label">Length</div><div class="value">7 days</div></div>
      <div class="stat"><div class="label">Per day</div><div class="value">1-2h</div></div>
      <div class="stat"><div class="label">Monthly</div><div class="value">$1-2</div></div>
      <div class="stat"><div class="label">Format</div><div class="value">local</div></div>
    </div>
  </div>

  <div class="right">
    <div class="right-label">JOURNEY</div>
    <div class="days">
      <div class="day"><div class="num">D1</div><div class="name">Vault<span class="desc">first entity</span></div></div>
      <div class="day"><div class="num">D2</div><div class="name">Today.md<span class="desc">entry point</span></div></div>
      <div class="day"><div class="num">D3</div><div class="name">Hook<span class="desc">auto-record</span></div></div>
      <div class="day"><div class="num">D4</div><div class="name">Tracker<span class="desc">every 2h</span></div></div>
      <div class="day"><div class="num">D5</div><div class="name">Ontology<span class="desc">knowledge graph</span></div></div>
      <div class="day"><div class="num">D6</div><div class="name">Watcher<span class="desc">change detection</span></div></div>
      <div class="day"><div class="num">D7</div><div class="name">/slides<span class="desc">deck generation</span></div></div>
    </div>
  </div>
</div>

<div class="author">
  <div>
    <span class="by-label">BY</span>
    <span class="name">Jewoong Moon</span>
    <span class="aff">The University of Alabama · jmoon19@ua.edu</span>
  </div>
  <div class="url">educatian.github.io/research-assistant-ai-workflow-en</div>
</div>

</body></html>
"""


def main() -> None:
    from playwright.sync_api import sync_playwright
    template = HERE / ".og_template.html"
    template.write_text(OG_HTML, encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        page = ctx.new_page()
        page.goto(template.as_uri(), wait_until="networkidle")
        page.wait_for_timeout(1200)
        jpg_out = OUT.with_suffix(".jpg")
        page.screenshot(path=str(jpg_out), type="jpeg", quality=90,
                        clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        browser.close()
    try:
        from PIL import Image
        Image.open(jpg_out).save(OUT, "PNG", optimize=True)
    except Exception:
        pass
    template.unlink(missing_ok=True)
    print(f"[done] {jpg_out}  ({jpg_out.stat().st_size // 1024} KB)")
    if OUT.exists():
        print(f"[done] {OUT}    ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
