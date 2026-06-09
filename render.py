"""
render.py — Build the static guide HTML from guide.md.

Renders a friendly, illustrated single-file HTML with hand-crafted inline SVG
diagrams, using open-design's html-ppt-course-module visual tokens (warm paper,
teal accent) adapted for long-form scrolling docs.

Usage:
    python render.py                          # reads ./guide.md → ./index.html
    python render.py custom.md output.html    # custom paths

Requires: pip install markdown
"""
from __future__ import annotations
import re, sys, io, html as htmllib
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import markdown

HERE  = Path(__file__).resolve().parent
GUIDE = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "guide.md"
OUT   = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "index.html"


# ---------- Diagrams (inline SVG) ----------------------------------------
DIAGRAMS = {}

DIAGRAMS["hero"] = """
<figure class="diagram diagram-hero">
<svg viewBox="0 0 800 240" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="7-day journey timeline" preserveAspectRatio="xMidYMid meet">
  <defs>
    <linearGradient id="hg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#2a2418"/>
      <stop offset="1" stop-color="#3a2f1c"/>
    </linearGradient>
    <radialGradient id="halo" cx="0.5" cy="0.5" r="0.7">
      <stop offset="0" stop-color="#d88a3a" stop-opacity="0.16"/>
      <stop offset="1" stop-color="#d88a3a" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="800" height="240" fill="url(#hg)"/>
  <ellipse cx="400" cy="125" rx="380" ry="110" fill="url(#halo)"/>

  <!-- top kicker -->
  <g fill="#f4f1e8">
    <text x="400" y="40" text-anchor="middle" font-size="11" font-family="JetBrains Mono, monospace" letter-spacing="4" opacity="0.5">✦ A 7-DAY JOURNEY ✦</text>
  </g>

  <!-- timeline base line -->
  <line x1="78" y1="125" x2="722" y2="125" stroke="#f4f1e8" stroke-width="1" stroke-opacity="0.18" stroke-dasharray="2 4"/>

  <!-- 7 milestone groups, evenly spaced cx = 78 + i * 107.33 -->
  <g font-family="Pretendard Variable, Pretendard, Inter, sans-serif" fill="#f4f1e8">

    <!-- Day 1: Vault (folder icon) -->
    <g transform="translate(78,125)">
      <circle r="26" fill="#2a2418" stroke="#2d7d6e" stroke-width="2"/>
      <path d="M -10,-6 L -2,-6 L 0,-3 L 10,-3 L 10,7 L -10,7 Z" fill="none" stroke="#2d7d6e" stroke-width="1.5" stroke-linejoin="round"/>
      <text x="0" y="-44" text-anchor="middle" font-size="10" font-family="JetBrains Mono, monospace" font-weight="700" letter-spacing="2" fill="#d88a3a">DAY 1</text>
      <text x="0" y="50" text-anchor="middle" font-size="14" font-weight="700">Vault</text>
      <text x="0" y="68" text-anchor="middle" font-size="11" opacity="0.7">First entity</text>
    </g>

    <!-- Day 2: Today (page icon) -->
    <g transform="translate(185,125)">
      <circle r="26" fill="#2a2418" stroke="#d88a3a" stroke-width="2"/>
      <rect x="-8" y="-9" width="16" height="18" fill="none" stroke="#d88a3a" stroke-width="1.5"/>
      <line x1="-5" y1="-4" x2="5" y2="-4" stroke="#d88a3a" stroke-width="1"/>
      <line x1="-5" y1="0" x2="5" y2="0" stroke="#d88a3a" stroke-width="1"/>
      <line x1="-5" y1="4" x2="2" y2="4" stroke="#d88a3a" stroke-width="1"/>
      <text x="0" y="-44" text-anchor="middle" font-size="10" font-family="JetBrains Mono, monospace" font-weight="700" letter-spacing="2" fill="#d88a3a">DAY 2</text>
      <text x="0" y="50" text-anchor="middle" font-size="14" font-weight="700">Today.md</text>
      <text x="0" y="68" text-anchor="middle" font-size="11" opacity="0.7">Entry point</text>
    </g>

    <!-- Day 3: Claude (chat icon) -->
    <g transform="translate(292,125)">
      <circle r="26" fill="#2a2418" stroke="#9b7eb7" stroke-width="2"/>
      <path d="M -9,-5 Q -9,-9 -5,-9 L 5,-9 Q 9,-9 9,-5 L 9,2 Q 9,6 5,6 L 0,6 L -3,9 L -3,6 L -5,6 Q -9,6 -9,2 Z" fill="none" stroke="#9b7eb7" stroke-width="1.5" stroke-linejoin="round"/>
      <text x="0" y="-44" text-anchor="middle" font-size="10" font-family="JetBrains Mono, monospace" font-weight="700" letter-spacing="2" fill="#d88a3a">DAY 3</text>
      <text x="0" y="50" text-anchor="middle" font-size="14" font-weight="700">Claude Code</text>
      <text x="0" y="68" text-anchor="middle" font-size="11" opacity="0.7">Stop hook</text>
    </g>

    <!-- Day 4: Tracker (clock icon) -->
    <g transform="translate(400,125)">
      <circle r="30" fill="#d88a3a" opacity="0.15"/>
      <circle r="26" fill="#2a2418" stroke="#d88a3a" stroke-width="2.5"/>
      <circle cx="0" cy="0" r="9" fill="none" stroke="#d88a3a" stroke-width="1.5"/>
      <line x1="0" y1="0" x2="0" y2="-6" stroke="#d88a3a" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="0" y1="0" x2="5" y2="2" stroke="#d88a3a" stroke-width="1.5" stroke-linecap="round"/>
      <text x="0" y="-44" text-anchor="middle" font-size="10" font-family="JetBrains Mono, monospace" font-weight="700" letter-spacing="2" fill="#d88a3a">DAY 4</text>
      <text x="0" y="50" text-anchor="middle" font-size="14" font-weight="700">Tracker</text>
      <text x="0" y="68" text-anchor="middle" font-size="11" opacity="0.7">every 2h auto</text>
    </g>

    <!-- Day 5: Ontology (graph icon) -->
    <g transform="translate(508,125)">
      <circle r="26" fill="#2a2418" stroke="#4ea893" stroke-width="2"/>
      <circle cx="-7" cy="-4" r="2.5" fill="#4ea893"/>
      <circle cx="7" cy="-4" r="2.5" fill="#4ea893"/>
      <circle cx="0" cy="6" r="2.5" fill="#4ea893"/>
      <line x1="-7" y1="-4" x2="7" y2="-4" stroke="#4ea893" stroke-width="1"/>
      <line x1="-7" y1="-4" x2="0" y2="6" stroke="#4ea893" stroke-width="1"/>
      <line x1="7" y1="-4" x2="0" y2="6" stroke="#4ea893" stroke-width="1"/>
      <text x="0" y="-44" text-anchor="middle" font-size="10" font-family="JetBrains Mono, monospace" font-weight="700" letter-spacing="2" fill="#d88a3a">DAY 5</text>
      <text x="0" y="50" text-anchor="middle" font-size="14" font-weight="700">Ontology</text>
      <text x="0" y="68" text-anchor="middle" font-size="11" opacity="0.7">Knowledge graph</text>
    </g>

    <!-- Day 6: Watch (eye icon) -->
    <g transform="translate(615,125)">
      <circle r="26" fill="#2a2418" stroke="#c4593f" stroke-width="2"/>
      <path d="M -10,0 Q 0,-7 10,0 Q 0,7 -10,0 Z" fill="none" stroke="#c4593f" stroke-width="1.5"/>
      <circle cx="0" cy="0" r="3" fill="#c4593f"/>
      <text x="0" y="-44" text-anchor="middle" font-size="10" font-family="JetBrains Mono, monospace" font-weight="700" letter-spacing="2" fill="#d88a3a">DAY 6</text>
      <text x="0" y="50" text-anchor="middle" font-size="14" font-weight="700">Situation</text>
      <text x="0" y="68" text-anchor="middle" font-size="11" opacity="0.7">Change detection</text>
    </g>

    <!-- Day 7: Slides (deck icon) -->
    <g transform="translate(722,125)">
      <circle r="26" fill="#2a2418" stroke="#e8a770" stroke-width="2"/>
      <rect x="-9" y="-3" width="14" height="9" fill="none" stroke="#e8a770" stroke-width="1.5"/>
      <rect x="-7" y="-6" width="14" height="9" fill="none" stroke="#e8a770" stroke-width="1.2" opacity="0.7"/>
      <rect x="-5" y="-9" width="14" height="9" fill="none" stroke="#e8a770" stroke-width="1" opacity="0.4"/>
      <text x="0" y="-44" text-anchor="middle" font-size="10" font-family="JetBrains Mono, monospace" font-weight="700" letter-spacing="2" fill="#d88a3a">DAY 7</text>
      <text x="0" y="50" text-anchor="middle" font-size="14" font-weight="700">/slides</text>
      <text x="0" y="68" text-anchor="middle" font-size="11" opacity="0.7">Slide gen</text>
    </g>
  </g>

  <!-- bottom subtitle -->
  <g fill="#f4f1e8">
    <text x="400" y="218" text-anchor="middle" font-size="11" font-family="JetBrains Mono, monospace" letter-spacing="3" opacity="0.45">1-2 hours/day · ~$2/month · local-first · BYOK</text>
  </g>
</svg>
</figure>
"""

DIAGRAMS["before-after"] = """
<figure class="diagram diagram-pair">
  <div class="pair-side pair-before">
    <div class="pair-label">BEFORE</div>
    <svg viewBox="0 0 280 200" xmlns="http://www.w3.org/2000/svg">
      <rect width="280" height="200" fill="#f1f3f5" stroke="#ccc"/>
      <!-- scattered files -->
      <g font-family="IBM Plex Mono, monospace" font-size="9" fill="#0a1f3d">
        <rect x="20" y="20" width="60" height="14" fill="#fff" stroke="#999"/><text x="22" y="31">draft_v3.docx</text>
        <rect x="120" y="35" width="55" height="14" fill="#fff" stroke="#999"/><text x="122" y="46">slides.pptx</text>
        <rect x="200" y="15" width="50" height="14" fill="#fff" stroke="#999"/><text x="202" y="26">notes.txt</text>
        <rect x="60" y="65" width="48" height="14" fill="#fff" stroke="#999"/><text x="62" y="76">draft_v4.docx</text>
        <rect x="160" y="80" width="60" height="14" fill="#fff" stroke="#999"/><text x="162" y="91">screenshot.png</text>
        <rect x="20" y="105" width="55" height="14" fill="#fff" stroke="#999"/><text x="22" y="116">grant.docx</text>
        <rect x="100" y="120" width="60" height="14" fill="#fff" stroke="#999"/><text x="102" y="131">data.csv</text>
        <rect x="200" y="105" width="50" height="14" fill="#fff" stroke="#999"/><text x="202" y="116">v5.docx</text>
        <rect x="40" y="150" width="60" height="14" fill="#fff" stroke="#999"/><text x="42" y="161">paper2.pdf</text>
        <rect x="140" y="155" width="55" height="14" fill="#fff" stroke="#999"/><text x="142" y="166">final.docx</text>
        <rect x="210" y="150" width="50" height="14" fill="#fff" stroke="#999"/><text x="212" y="161">edit.md</text>
        <rect x="20" y="175" width="50" height="14" fill="#fff" stroke="#999"/><text x="22" y="186">log.txt</text>
      </g>
      <text x="140" y="14" text-anchor="middle" font-family="Inter, sans" font-size="9" fill="#999">Desktop\\</text>
    </svg>
    <p class="pair-caption">Desktop = a graveyard you must search</p>
  </div>
  <div class="pair-arrow">→</div>
  <div class="pair-side pair-after">
    <div class="pair-label" style="background: var(--rust); color: var(--paper);">AFTER</div>
    <svg viewBox="0 0 280 200" xmlns="http://www.w3.org/2000/svg">
      <rect width="280" height="200" fill="#f1f3f5" stroke="#0a1f3d"/>
      <!-- structured -->
      <g font-family="Inter, sans" font-size="10" fill="#0a1f3d">
        <rect x="14" y="14" width="252" height="22" fill="#0a1f3d"/>
        <text x="22" y="29" fill="#f1f3f5" font-family="Playfair Display, serif" font-weight="700">Today.md</text>
        <text x="200" y="29" fill="#facc15" font-family="IBM Plex Mono, monospace" font-size="9">D-12</text>

        <rect x="14" y="44" width="120" height="50" fill="#fff" stroke="#0a1f3d"/>
        <text x="22" y="58" font-weight="600">entities/</text>
        <text x="22" y="72" font-size="9" fill="#666">Project A, B, C, …</text>
        <text x="22" y="84" font-size="9" fill="#666">12 active</text>

        <rect x="146" y="44" width="120" height="50" fill="#fff" stroke="#0a1f3d"/>
        <text x="154" y="58" font-weight="600">concepts/</text>
        <text x="154" y="72" font-size="9" fill="#666">methods, theory</text>
        <text x="154" y="84" font-size="9" fill="#666">methodology</text>

        <rect x="14" y="104" width="252" height="36" fill="#fff" stroke="#b5392a"/>
        <text x="22" y="118" font-weight="600">situation/2026-05-02.md</text>
        <text x="22" y="132" font-size="9" fill="#b5392a">[AUTO] Project A deadline → 2026-09-01</text>

        <rect x="14" y="150" width="252" height="38" fill="#fff" stroke="#0a1f3d"/>
        <text x="22" y="164" font-weight="600">_ontology.json + graph.html</text>
        <g stroke="#3b82f6" stroke-width="1" fill="none">
          <circle cx="40" cy="180" r="3" fill="#3b82f6"/>
          <circle cx="80" cy="180" r="3" fill="#f59e0b"/>
          <circle cx="120" cy="180" r="3" fill="#8b5cf6"/>
          <circle cx="160" cy="180" r="3" fill="#10b981"/>
          <line x1="43" y1="180" x2="77" y2="180"/>
          <line x1="83" y1="180" x2="117" y2="180"/>
          <line x1="123" y1="180" x2="157" y2="180"/>
        </g>
        <text x="180" y="183" font-size="9" fill="#666">queryable</text>
      </g>
    </svg>
    <p class="pair-caption">vault = one entry page, no search needed</p>
  </div>
</figure>
"""

DIAGRAMS["mental-model"] = """
<figure class="diagram">
<svg viewBox="0 0 720 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Three-layer mental model">
  <!-- layer 1: project knowledge -->
  <g>
    <rect x="60" y="20" width="640" height="70" rx="8" fill="#2d7d6e" opacity="0.08" stroke="#2d7d6e" stroke-width="1.5"/>
    <text x="80" y="44" font-family="Playfair Display, serif" font-weight="700" font-size="17" fill="#2a2418">Layer 1 · Project knowledge</text>
    <text x="80" y="62" font-family="Inter, sans" font-size="11.5" fill="#5a5140">Notes you write yourself. Permanent asset.</text>
    <g font-family="JetBrains Mono, monospace" font-size="10" fill="#2a2418">
      <rect x="320" y="48" width="110" height="26" rx="4" fill="#fff" stroke="#2d7d6e"/>
      <text x="330" y="65">wiki/entities/</text>
      <rect x="440" y="48" width="110" height="26" rx="4" fill="#fff" stroke="#2d7d6e"/>
      <text x="450" y="65">wiki/concepts/</text>
      <rect x="560" y="48" width="120" height="26" rx="4" fill="#fff" stroke="#2d7d6e"/>
      <text x="570" y="65">wiki/sources/</text>
    </g>
  </g>
  <!-- layer 2: activity -->
  <g>
    <rect x="60" y="105" width="640" height="70" rx="8" fill="#d88a3a" opacity="0.1" stroke="#d88a3a" stroke-width="1.5"/>
    <text x="80" y="129" font-family="Playfair Display, serif" font-weight="700" font-size="17" fill="#2a2418">Layer 2 · Activity log (auto)</text>
    <text x="80" y="147" font-family="Inter, sans" font-size="11.5" fill="#5a5140">Computer fills every 2h. Answers "what did I do?"</text>
    <g font-family="JetBrains Mono, monospace" font-size="10" fill="#2a2418">
      <rect x="320" y="133" width="110" height="26" rx="4" fill="#fff" stroke="#d88a3a"/>
      <text x="330" y="150">activity/...</text>
      <rect x="440" y="133" width="110" height="26" rx="4" fill="#fff" stroke="#d88a3a"/>
      <text x="450" y="150">situation/...</text>
      <rect x="560" y="133" width="120" height="26" rx="4" fill="#fff" stroke="#d88a3a"/>
      <text x="570" y="150">Sessions/...</text>
    </g>
  </g>
  <!-- layer 3: memory -->
  <g>
    <rect x="60" y="190" width="640" height="70" rx="8" fill="#9b7eb7" opacity="0.1" stroke="#9b7eb7" stroke-width="1.5"/>
    <text x="80" y="214" font-family="Playfair Display, serif" font-weight="700" font-size="17" fill="#2a2418">Layer 3 · AI memory</text>
    <text x="80" y="232" font-family="Inter, sans" font-size="11.5" fill="#5a5140">Auto-loaded by Claude at session start. No re-explaining.</text>
    <g font-family="JetBrains Mono, monospace" font-size="9.5" fill="#2a2418">
      <rect x="320" y="218" width="360" height="26" rx="4" fill="#fff" stroke="#9b7eb7"/>
      <text x="330" y="235">~/.claude/projects/&lt;machine&gt;/memory/MEMORY.md</text>
    </g>
  </g>
  <!-- left labels -->
  <g font-family="JetBrains Mono, monospace" font-size="10" font-weight="700" fill="#8a7f68" letter-spacing="1.5">
    <text x="22" y="56" transform="rotate(-90 22 56)">I write</text>
    <text x="22" y="142" transform="rotate(-90 22 142)">Auto</text>
    <text x="22" y="228" transform="rotate(-90 22 228)">AI reads</text>
  </g>
</svg>
<figcaption>Three layers — Layer 1 you write, Layer 2 is automatic, Layer 3 the AI reads.</figcaption>
</figure>
"""

DIAGRAMS["tracker-flow"] = """
<figure class="diagram">
<svg viewBox="0 0 760 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Tracker flow every 2 hours">
  <!-- inputs -->
  <g font-family="Inter, sans" font-size="11.5" fill="#2a2418">
    <text x="20" y="22" font-family="JetBrains Mono, monospace" font-size="10" font-weight="700" letter-spacing="2" fill="#8a7f68">INPUTS</text>
    <rect x="20" y="35"  width="140" height="28" rx="6" fill="#fff" stroke="#2d7d6e" stroke-width="1.2"/><text x="34" y="53">📝 new/modified notes</text>
    <rect x="20" y="71"  width="140" height="28" rx="6" fill="#fff" stroke="#2d7d6e" stroke-width="1.2"/><text x="34" y="89">⌨ Git commits</text>
    <rect x="20" y="107" width="140" height="28" rx="6" fill="#fff" stroke="#2d7d6e" stroke-width="1.2"/><text x="34" y="125">⚡ GitHub PRs/issues</text>
    <rect x="20" y="143" width="140" height="28" rx="6" fill="#fff" stroke="#2d7d6e" stroke-width="1.2"/><text x="34" y="161">📅 calendar</text>
    <rect x="20" y="179" width="140" height="28" rx="6" fill="#fff" stroke="#2d7d6e" stroke-width="1.2"/><text x="34" y="197">📋 sticky notes</text>
  </g>
  <!-- arrows in -->
  <g stroke="#5a5140" stroke-width="1" fill="none" marker-end="url(#arr2)" stroke-opacity="0.6">
    <line x1="160" y1="49"  x2="288" y2="118"/>
    <line x1="160" y1="85"  x2="288" y2="125"/>
    <line x1="160" y1="121" x2="288" y2="130"/>
    <line x1="160" y1="157" x2="288" y2="135"/>
    <line x1="160" y1="193" x2="288" y2="142"/>
  </g>

  <!-- tracker box -->
  <g>
    <rect x="288" y="80" width="184" height="104" rx="10" fill="#2a2418"/>
    <text x="380" y="108" font-family="Playfair Display, serif" font-weight="800" font-size="18" fill="#d88a3a" text-anchor="middle">tracker.ps1</text>
    <text x="380" y="128" font-family="JetBrains Mono, monospace" font-size="11" fill="#f4f1e8" text-anchor="middle">every 2h</text>
    <text x="380" y="146" font-family="JetBrains Mono, monospace" font-size="10" fill="#c2b89f" text-anchor="middle">00:00, 02:00, ..., 22:00</text>
    <circle cx="380" cy="166" r="9" fill="#c4593f"/>
    <text x="380" y="170" font-family="JetBrains Mono, monospace" font-size="9" font-weight="700" fill="#fff" text-anchor="middle">12×</text>
  </g>

  <!-- arrows out -->
  <g stroke="#d88a3a" stroke-width="1" fill="none" marker-end="url(#arr3)" stroke-opacity="0.7">
    <line x1="472" y1="100" x2="598" y2="50"/>
    <line x1="472" y1="118" x2="598" y2="86"/>
    <line x1="472" y1="132" x2="598" y2="121"/>
    <line x1="472" y1="146" x2="598" y2="157"/>
    <line x1="472" y1="160" x2="598" y2="193"/>
  </g>
  <!-- outputs -->
  <g font-family="Inter, sans" font-size="11.5" fill="#2a2418">
    <text x="600" y="22" font-family="JetBrains Mono, monospace" font-size="10" font-weight="700" letter-spacing="2" fill="#8a7f68">OUTPUTS</text>
    <rect x="600" y="35"  width="150" height="28" rx="6" fill="#fff" stroke="#d88a3a" stroke-width="1.2"/><text x="614" y="53">Today.md refresh</text>
    <rect x="600" y="71"  width="150" height="28" rx="6" fill="#fff" stroke="#d88a3a" stroke-width="1.2"/><text x="614" y="89">_ontology.json</text>
    <rect x="600" y="107" width="150" height="28" rx="6" fill="#fff" stroke="#d88a3a" stroke-width="1.2"/><text x="614" y="125">activity/&lt;date&gt;</text>
    <rect x="600" y="143" width="150" height="28" rx="6" fill="#fff" stroke="#d88a3a" stroke-width="1.2"/><text x="614" y="161">situation/&lt;date&gt;</text>
    <rect x="600" y="179" width="150" height="28" rx="6" fill="#fff" stroke="#d88a3a" stroke-width="1.2"/><text x="614" y="197">graph.html</text>
  </g>

  <!-- bottom note -->
  <g font-family="JetBrains Mono, monospace" font-size="11" fill="#5a5140">
    <text x="380" y="232" text-anchor="middle">LLM only invoked when judging changes · ~$0.02-0.05/day</text>
    <text x="380" y="250" text-anchor="middle" fill="#8a7f68">Everything else: plain PowerShell + Python</text>
  </g>

  <defs>
    <marker id="arr2" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><polygon points="0 0, 6 3, 0 6" fill="#5a5140"/></marker>
    <marker id="arr3" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><polygon points="0 0, 6 3, 0 6" fill="#d88a3a"/></marker>
  </defs>
</svg>
<figcaption>Every-2-hours flow — 5 inputs become 5 outputs through one tracker.</figcaption>
</figure>
"""

DIAGRAMS["checklist"] = """
<figure class="diagram diagram-checklist">
<svg viewBox="0 0 720 200" xmlns="http://www.w3.org/2000/svg">
  <g font-family="Inter, sans" font-size="12" fill="#0a1f3d">
    <text x="20" y="22" font-family="IBM Plex Mono, monospace" font-size="11" letter-spacing="2" opacity="0.55">PHASE 1 · DAYS 1-3</text>
    <rect x="20" y="35"  width="320" height="32" fill="#fff" stroke="#0a1f3d"/>
    <text x="34" y="56">☐ Obsidian (vault UI)</text>
    <text x="240" y="56" font-family="IBM Plex Mono, monospace" font-size="10" opacity="0.55">free</text>
    <rect x="20" y="73"  width="320" height="32" fill="#fff" stroke="#0a1f3d"/>
    <text x="34" y="94">☐ Claude Code (AI agent)</text>
    <text x="240" y="94" font-family="IBM Plex Mono, monospace" font-size="10" opacity="0.55">subscription</text>
    <rect x="20" y="111" width="320" height="32" fill="#fff" stroke="#0a1f3d"/>
    <text x="34" y="132">☐ Python 3.11+</text>
    <text x="240" y="132" font-family="IBM Plex Mono, monospace" font-size="10" opacity="0.55">free</text>
    <rect x="20" y="149" width="320" height="32" fill="#fff" stroke="#0a1f3d"/>
    <text x="34" y="170">☐ Basic terminal skills</text>

    <text x="380" y="22" font-family="IBM Plex Mono, monospace" font-size="11" letter-spacing="2" opacity="0.55">PHASE 2 · DAYS 4-7</text>
    <rect x="380" y="35" width="320" height="32" fill="#fff" stroke="#b5392a"/>
    <text x="394" y="56">☐ OpenRouter API key</text>
    <text x="600" y="56" font-family="IBM Plex Mono, monospace" font-size="10" opacity="0.55">$5 top-up</text>
    <rect x="380" y="73" width="320" height="32" fill="#fff" stroke="#b5392a"/>
    <text x="394" y="94">☐ gh CLI (optional)</text>
    <text x="600" y="94" font-family="IBM Plex Mono, monospace" font-size="10" opacity="0.55">free</text>
    <rect x="380" y="111" width="320" height="32" fill="#fff" stroke="#b5392a"/>
    <text x="394" y="132">☐ pdfplumber, python-docx (pip)</text>
    <text x="600" y="132" font-family="IBM Plex Mono, monospace" font-size="10" opacity="0.55">free</text>
    <rect x="380" y="149" width="320" height="32" fill="#fff" stroke="#b5392a"/>
    <text x="394" y="170">☐ Windows scheduled task perms</text>
  </g>
</svg>
<figcaption>Days 1-3 free tools only. Day 4+ uses LLM key ($1-2/month).</figcaption>
</figure>
"""

DIAGRAMS["scenarios"] = """
<figure class="diagram">
<svg viewBox="0 0 760 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="5 use scenarios">
  <text x="20" y="22" font-family="JetBrains Mono, monospace" font-size="10" font-weight="700" letter-spacing="2" fill="#8a7f68">USE CASES · daily research life</text>

  <!-- 5 scenario cards in 2 rows -->
  <g font-family="Pretendard Variable, Inter, sans-serif">

    <!-- Card 1: Dissertation chapter -->
    <g>
      <rect x="20" y="40" width="230" height="130" rx="10" fill="#fff" stroke="#2d7d6e" stroke-width="2"/>
      <circle cx="50" cy="68" r="12" fill="#2d7d6e"/>
      <text x="50" y="73" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">1</text>
      <text x="74" y="72" font-size="14" font-weight="700" fill="#2a2418">Dissertation chapter</text>
      <text x="36" y="98" font-size="11.5" fill="#5a5140">Recover advisor decision</text>
      <text x="36" y="115" font-size="11.5" fill="#5a5140">from 6 months ago in 5 min</text>
      <rect x="36" y="128" width="200" height="28" rx="4" fill="#f6f3ea"/>
      <text x="46" y="146" font-family="JetBrains Mono, monospace" font-size="10" fill="#2d7d6e">grep Sessions*.md "Method A"</text>
    </g>

    <!-- Card 2: Grant deadline -->
    <g>
      <rect x="265" y="40" width="230" height="130" rx="10" fill="#fff" stroke="#d88a3a" stroke-width="2"/>
      <circle cx="295" cy="68" r="12" fill="#d88a3a"/>
      <text x="295" y="73" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">2</text>
      <text x="319" y="72" font-size="14" font-weight="700" fill="#2a2418">Grant D-7 panic</text>
      <text x="281" y="98" font-size="11.5" fill="#5a5140">9 docx auto-consistency</text>
      <text x="281" y="115" font-size="11.5" fill="#5a5140">+ deadline D-counter</text>
      <rect x="281" y="128" width="200" height="28" rx="4" fill="#fff8ed"/>
      <text x="291" y="146" font-family="JetBrains Mono, monospace" font-size="10" fill="#d88a3a">situation_watch [AUTO]</text>
    </g>

    <!-- Card 3: New advisee -->
    <g>
      <rect x="510" y="40" width="230" height="130" rx="10" fill="#fff" stroke="#9b7eb7" stroke-width="2"/>
      <circle cx="540" cy="68" r="12" fill="#9b7eb7"/>
      <text x="540" y="73" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">3</text>
      <text x="564" y="72" font-size="14" font-weight="700" fill="#2a2418">New advisee onboarding</text>
      <text x="526" y="98" font-size="11.5" fill="#5a5140">Portfolio at-a-glance</text>
      <text x="526" y="115" font-size="11.5" fill="#5a5140">auto-built in 5 min</text>
      <rect x="526" y="128" width="200" height="28" rx="4" fill="color-mix(in srgb, #9b7eb7 8%, #fff)"/>
      <text x="536" y="146" font-family="JetBrains Mono, monospace" font-size="10" fill="#9b7eb7">/slides my portfolio</text>
    </g>

    <!-- Card 4: Reviewer 2 -->
    <g>
      <rect x="20" y="190" width="230" height="130" rx="10" fill="#fff" stroke="#c4593f" stroke-width="2"/>
      <circle cx="50" cy="218" r="12" fill="#c4593f"/>
      <text x="50" y="223" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">4</text>
      <text x="74" y="222" font-size="14" font-weight="700" fill="#2a2418">Reviewer 2 reply</text>
      <text x="36" y="248" font-size="11.5" fill="#5a5140">"Why not X?" answered</text>
      <text x="36" y="265" font-size="11.5" fill="#5a5140">from past key_decisions</text>
      <rect x="36" y="278" width="200" height="28" rx="4" fill="#fdf2ee"/>
      <text x="46" y="296" font-family="JetBrains Mono, monospace" font-size="10" fill="#c4593f">key_decisions grep</text>
    </g>

    <!-- Card 5: Comp exam -->
    <g>
      <rect x="265" y="190" width="230" height="130" rx="10" fill="#fff" stroke="#4a7c59" stroke-width="2"/>
      <circle cx="295" cy="218" r="12" fill="#4a7c59"/>
      <text x="295" y="223" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">5</text>
      <text x="319" y="222" font-size="14" font-weight="700" fill="#2a2418">Comp exam prep</text>
      <text x="281" y="248" font-size="11.5" fill="#5a5140">80-paper citation network</text>
      <text x="281" y="265" font-size="11.5" fill="#5a5140">auto-graphed</text>
      <rect x="281" y="278" width="200" height="28" rx="4" fill="color-mix(in srgb, #4a7c59 8%, #fff)"/>
      <text x="291" y="296" font-family="JetBrains Mono, monospace" font-size="10" fill="#4a7c59">--predicate cites</text>
    </g>

    <!-- Pattern card (right bottom) -->
    <g>
      <rect x="510" y="190" width="230" height="130" rx="10" fill="#2a2418" stroke="#d88a3a" stroke-width="2"/>
      <text x="530" y="222" font-size="14" font-weight="800" fill="#d88a3a">Common pattern</text>
      <text x="530" y="242" font-size="11.5" fill="#f4f1e8">Notes in vault while working</text>
      <text x="530" y="259" font-size="11.5" fill="#f4f1e8">+ Stop hook auto-record</text>
      <text x="530" y="276" font-size="11.5" fill="#f4f1e8">+ ontology auto-extracts</text>
      <text x="530" y="298" font-size="11" fill="#d88a3a" font-style="italic">→ future-you retrieves instantly</text>
    </g>
  </g>

  <!-- bottom note -->
  <g font-family="Pretendard Variable, Inter, sans-serif" font-size="11.5" fill="#8a7f68">
    <text x="380" y="346" text-anchor="middle">The system adds *no extra burden* — it accumulates material for future-you from the traces of your normal work.</text>
  </g>
</svg>
<figcaption>5 daily scenarios — each card shows *setup / outcome / key command*. Bottom-right is the common pattern.</figcaption>
</figure>
"""


DIAGRAMS["agents"] = """
<figure class="diagram">
<svg viewBox="0 0 760 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Claude Code vs Codex roles">
  <text x="20" y="22" font-family="JetBrains Mono, monospace" font-size="10" font-weight="700" letter-spacing="2" fill="#8a7f68">AI AGENTS · role split</text>

  <!-- Claude Code column -->
  <g>
    <rect x="20" y="40" width="350" height="160" rx="12" fill="#fff" stroke="#2d7d6e" stroke-width="2"/>
    <text x="40" y="68" font-family="Pretendard Variable, Inter, sans-serif" font-size="18" font-weight="800" fill="#2d7d6e">Claude Code</text>
    <text x="40" y="86" font-family="JetBrains Mono, monospace" font-size="10" font-weight="700" letter-spacing="1.5" fill="#8a7f68">PRIMARY · Anthropic</text>

    <g font-family="Pretendard Variable, Inter, sans-serif" font-size="12" fill="#2a2418">
      <text x="40" y="112">✓ Stop hook auto (session digest)</text>
      <text x="40" y="132">✓ Slash commands (/slides /recall)</text>
      <text x="40" y="152">✓ MEMORY.md auto-load</text>
      <text x="40" y="172">✓ CLAUDE.md parent-walked</text>
      <text x="40" y="192">✓ 200K-1M context</text>
    </g>
  </g>

  <!-- Codex column -->
  <g>
    <rect x="390" y="40" width="350" height="160" rx="12" fill="#fff" stroke="#d88a3a" stroke-width="2"/>
    <text x="410" y="68" font-family="Pretendard Variable, Inter, sans-serif" font-size="18" font-weight="800" fill="#d88a3a">Codex</text>
    <text x="410" y="86" font-family="JetBrains Mono, monospace" font-size="10" font-weight="700" letter-spacing="1.5" fill="#8a7f68">SECONDARY · OpenAI</text>

    <g font-family="Pretendard Variable, Inter, sans-serif" font-size="12" fill="#2a2418">
      <text x="410" y="112">○ No hooks (manual codex_digest.ps1)</text>
      <text x="410" y="132">○ AGENTS.md auto-load</text>
      <text x="410" y="152">○ Sessions = ~/.codex/sessions/</text>
      <text x="410" y="172">✓ Image gen / reasoning mode</text>
      <text x="410" y="192">✓ VS Code IDE integration</text>
    </g>
  </g>

  <!-- Connection to vault -->
  <g stroke="#5a5140" stroke-width="1.2" fill="none" stroke-opacity="0.6">
    <path d="M 195,200 Q 195,260 380,290" marker-end="url(#arrA)"/>
    <path d="M 565,200 Q 565,260 380,290" marker-end="url(#arrA)"/>
  </g>

  <!-- Vault circle (center bottom) -->
  <g>
    <circle cx="380" cy="320" r="48" fill="#2a2418"/>
    <text x="380" y="318" text-anchor="middle" font-family="Playfair Display, serif" font-size="20" font-weight="800" fill="#d88a3a">vault</text>
    <text x="380" y="335" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="10" fill="#f4f1e8" opacity="0.7">wiki/*.md</text>
  </g>

  <!-- Side labels: CLI vs Desktop -->
  <g font-family="JetBrains Mono, monospace" font-size="11" font-weight="700" letter-spacing="1.5">
    <rect x="20" y="220" width="170" height="32" rx="6" fill="#fff8ed" stroke="#d88a3a"/>
    <text x="105" y="241" text-anchor="middle" fill="#d88a3a">CLI · full features</text>
    <rect x="200" y="220" width="170" height="32" rx="6" fill="color-mix(in srgb, #2d7d6e 6%, #fff)" stroke="#2d7d6e"/>
    <text x="285" y="241" text-anchor="middle" fill="#2d7d6e">Desktop · MCP</text>
  </g>
  <g font-family="JetBrains Mono, monospace" font-size="11" font-weight="700" letter-spacing="1.5">
    <rect x="390" y="220" width="170" height="32" rx="6" fill="#fff8ed" stroke="#d88a3a"/>
    <text x="475" y="241" text-anchor="middle" fill="#d88a3a">CLI · session archive</text>
    <rect x="570" y="220" width="170" height="32" rx="6" fill="color-mix(in srgb, #2d7d6e 6%, #fff)" stroke="#2d7d6e"/>
    <text x="655" y="241" text-anchor="middle" fill="#2d7d6e">VS Code IDE</text>
  </g>

  <!-- bottom: rule of thumb -->
  <g font-family="Pretendard Variable, Inter, sans-serif" font-size="12.5" fill="#2a2418">
    <rect x="20" y="384" width="720" height="28" rx="8" fill="#f6f3ea" stroke="#5a5140" stroke-dasharray="3 3"/>
    <text x="40" y="402" font-weight="700" fill="#5a5140">Rule:</text>
    <text x="80" y="402" fill="#5a5140">vault work + automation hooks = <tspan fill="#2d7d6e" font-weight="700">Claude Code CLI</tspan> · quick chat = <tspan fill="#2d7d6e" font-weight="700">Claude Desktop</tspan> · code backup = <tspan fill="#d88a3a" font-weight="700">Codex</tspan></text>
  </g>

  <defs>
    <marker id="arrA" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><polygon points="0 0, 6 3, 0 6" fill="#5a5140"/></marker>
  </defs>
</svg>
<figcaption>Both agents see the same vault — different controls and strengths.</figcaption>
</figure>
"""


DIAGRAMS["schema"] = """
<figure class="diagram">
<svg viewBox="0 0 760 320" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Schema: types + relations">
  <!-- title -->
  <text x="20" y="22" font-family="JetBrains Mono, monospace" font-size="10" font-weight="700" letter-spacing="2" fill="#8a7f68">SCHEMA · types and relations</text>

  <!-- TYPE BOXES (top row) -->
  <g font-family="Pretendard Variable, Inter, sans-serif" font-size="13" fill="#2a2418">
    <g>
      <rect x="20" y="40" width="100" height="56" rx="8" fill="#fff" stroke="#d88a3a" stroke-width="2"/>
      <text x="70" y="62" text-anchor="middle" font-weight="700">Person</text>
      <text x="70" y="80" text-anchor="middle" font-size="10" fill="#8a7f68">people</text>
    </g>
    <g>
      <rect x="135" y="40" width="100" height="56" rx="8" fill="#fff" stroke="#2d7d6e" stroke-width="2"/>
      <text x="185" y="62" text-anchor="middle" font-weight="700">Project</text>
      <text x="185" y="80" text-anchor="middle" font-size="10" fill="#8a7f68">active projects</text>
    </g>
    <g>
      <rect x="250" y="40" width="100" height="56" rx="8" fill="#fff" stroke="#4a7c59" stroke-width="2"/>
      <text x="300" y="62" text-anchor="middle" font-weight="700">Grant</text>
      <text x="300" y="80" text-anchor="middle" font-size="10" fill="#8a7f68">external funding</text>
    </g>
    <g>
      <rect x="365" y="40" width="100" height="56" rx="8" fill="#fff" stroke="#9b7eb7" stroke-width="2"/>
      <text x="415" y="62" text-anchor="middle" font-weight="700">Concept</text>
      <text x="415" y="80" text-anchor="middle" font-size="10" fill="#8a7f68">methods · theory</text>
    </g>
    <g>
      <rect x="480" y="40" width="100" height="56" rx="8" fill="#fff" stroke="#c4593f" stroke-width="2"/>
      <text x="530" y="62" text-anchor="middle" font-weight="700">Course</text>
      <text x="530" y="80" text-anchor="middle" font-size="10" fill="#8a7f68">courses</text>
    </g>
    <g>
      <rect x="595" y="40" width="100" height="56" rx="8" fill="#fff" stroke="#8a7f68" stroke-width="2"/>
      <text x="645" y="62" text-anchor="middle" font-weight="700">Manuscript</text>
      <text x="645" y="80" text-anchor="middle" font-size="10" fill="#8a7f68">papers</text>
    </g>
  </g>

  <!-- RELATION ARROWS (middle, dashed with labels) -->
  <g font-family="JetBrains Mono, monospace" font-size="11" fill="#5a5140">
    <text x="380" y="120" text-anchor="middle" font-weight="700" letter-spacing="1.5" fill="#8a7f68">↓ relations ↓</text>
  </g>

  <!-- Relations as rounded labels in a single row -->
  <g font-family="JetBrains Mono, monospace" font-size="11">
    <g>
      <rect x="20" y="140" width="115" height="32" rx="16" fill="#fff8ed" stroke="#d88a3a"/>
      <text x="77" y="160" text-anchor="middle" fill="#d88a3a" font-weight="700">hasPI</text>
    </g>
    <g>
      <rect x="148" y="140" width="115" height="32" rx="16" fill="#fff8ed" stroke="#d88a3a"/>
      <text x="205" y="160" text-anchor="middle" fill="#d88a3a" font-weight="700">advises</text>
    </g>
    <g>
      <rect x="276" y="140" width="115" height="32" rx="16" fill="color-mix(in srgb, #2d7d6e 8%, #fff)" stroke="#2d7d6e"/>
      <text x="333" y="160" text-anchor="middle" fill="#2d7d6e" font-weight="700">usesMethod</text>
    </g>
    <g>
      <rect x="404" y="140" width="115" height="32" rx="16" fill="color-mix(in srgb, #4a7c59 8%, #fff)" stroke="#4a7c59"/>
      <text x="461" y="160" text-anchor="middle" fill="#4a7c59" font-weight="700">fundedBy</text>
    </g>
    <g>
      <rect x="532" y="140" width="115" height="32" rx="16" fill="color-mix(in srgb, #9b7eb7 8%, #fff)" stroke="#9b7eb7"/>
      <text x="589" y="160" text-anchor="middle" fill="#9b7eb7" font-weight="700">taughtIn</text>
    </g>
    <g>
      <rect x="20" y="180" width="115" height="32" rx="16" fill="#fdf2ee" stroke="#c4593f"/>
      <text x="77" y="200" text-anchor="middle" fill="#c4593f" font-weight="700">cites</text>
    </g>
    <g>
      <rect x="148" y="180" width="115" height="32" rx="16" fill="#fdf2ee" stroke="#c4593f"/>
      <text x="205" y="200" text-anchor="middle" fill="#c4593f" font-weight="700">extends</text>
    </g>
    <g>
      <rect x="276" y="180" width="115" height="32" rx="16" fill="#fff" stroke="#5a5140"/>
      <text x="333" y="200" text-anchor="middle" fill="#5a5140" font-weight="700">collaboratesWith</text>
    </g>
    <g>
      <rect x="404" y="180" width="115" height="32" rx="16" fill="#fff" stroke="#5a5140"/>
      <text x="461" y="200" text-anchor="middle" fill="#5a5140" font-weight="700">builtOn</text>
    </g>
    <g>
      <rect x="532" y="180" width="115" height="32" rx="16" fill="#fff" stroke="#5a5140"/>
      <text x="589" y="200" text-anchor="middle" fill="#5a5140" font-weight="700">relatedTo</text>
    </g>
  </g>

  <!-- bottom: how to read -->
  <g font-family="Pretendard Variable, Inter, sans-serif" font-size="12.5" fill="#2a2418">
    <rect x="20" y="240" width="720" height="64" rx="8" fill="#f6f3ea" stroke="#5a5140" stroke-dasharray="3 3"/>
    <text x="40" y="262" font-weight="700" font-size="13">How to read:</text>
    <text x="40" y="282" fill="#5a5140">e.g. <tspan font-family="JetBrains Mono, monospace" fill="#2d7d6e" font-weight="700">[Project]</tspan> <tspan font-family="JetBrains Mono, monospace" fill="#d88a3a" font-weight="700">hasPI</tspan> <tspan font-family="JetBrains Mono, monospace" fill="#d88a3a" font-weight="700">[Person]</tspan>  =  "Project A's PI is Dr. Smith"</text>
    <text x="40" y="298" fill="#5a5140">e.g. <tspan font-family="JetBrains Mono, monospace" fill="#2d7d6e" font-weight="700">[Project]</tspan> <tspan font-family="JetBrains Mono, monospace" fill="#2d7d6e" font-weight="700">usesMethod</tspan> <tspan font-family="JetBrains Mono, monospace" fill="#9b7eb7" font-weight="700">[Concept]</tspan>  =  "Project A uses Method A"</text>
  </g>
</svg>
<figcaption>Schema = 6 types + 10 relations. Writing entity pages auto-builds this graph.</figcaption>
</figure>
"""


DIAGRAMS["ontology-preview"] = """
<figure class="diagram">
<svg viewBox="0 0 720 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ontology graph preview">
  <!-- nodes (generic placeholder graph) -->
  <g font-family="JetBrains Mono, monospace" font-size="11">
    <circle cx="360" cy="140" r="22" fill="#d88a3a" stroke="#fff" stroke-width="2"/>
    <text x="360" y="144" text-anchor="middle" fill="#fff" font-weight="700">Me</text>

    <circle cx="180" cy="80" r="20" fill="#2d7d6e"/>
    <text x="180" y="85" text-anchor="middle" fill="#fff" font-weight="700">Proj A</text>

    <circle cx="180" cy="200" r="20" fill="#2d7d6e"/>
    <text x="180" y="205" text-anchor="middle" fill="#fff" font-weight="700">Proj B</text>

    <circle cx="540" cy="80" r="20" fill="#4a7c59"/>
    <text x="540" y="85" text-anchor="middle" fill="#fff" font-weight="700">Grant X</text>

    <circle cx="540" cy="200" r="20" fill="#9b7eb7"/>
    <text x="540" y="205" text-anchor="middle" fill="#fff" font-weight="700">Method</text>

    <circle cx="360" cy="40" r="14" fill="#c4593f"/>
    <text x="360" y="44" text-anchor="middle" fill="#fff" font-weight="700">Course</text>

    <circle cx="360" cy="240" r="14" fill="#e8a770"/>
    <text x="360" y="244" text-anchor="middle" fill="#fff" font-weight="700">Student</text>
  </g>
  <!-- edges -->
  <g stroke-width="1.5" fill="none">
    <g stroke="#ef4444">
      <line x1="200" y1="80" x2="338" y2="135"/>
      <text x="270" y="100" font-family="IBM Plex Mono, monospace" font-size="10" fill="#ef4444" stroke="none">hasPI</text>
    </g>
    <g stroke="#ef4444">
      <line x1="200" y1="200" x2="338" y2="145"/>
      <text x="260" y="195" font-family="IBM Plex Mono, monospace" font-size="10" fill="#ef4444" stroke="none">hasPI</text>
    </g>
    <g stroke="#10b981">
      <line x1="200" y1="80" x2="520" y2="80"/>
      <text x="350" y="74" font-family="IBM Plex Mono, monospace" font-size="10" fill="#10b981" stroke="none" text-anchor="middle">fundedBy</text>
    </g>
    <g stroke="#8b5cf6">
      <line x1="200" y1="80" x2="520" y2="200"/>
      <text x="370" y="160" font-family="IBM Plex Mono, monospace" font-size="10" fill="#8b5cf6" stroke="none">usesMethod</text>
    </g>
    <g stroke="#ec4899">
      <line x1="180" y1="60" x2="346" y2="40"/>
      <text x="265" y="35" font-family="IBM Plex Mono, monospace" font-size="10" fill="#ec4899" stroke="none" text-anchor="middle">taughtIn</text>
    </g>
    <g stroke="#eab308">
      <line x1="360" y1="162" x2="360" y2="226"/>
      <text x="368" y="200" font-family="IBM Plex Mono, monospace" font-size="10" fill="#eab308" stroke="none">advises</text>
    </g>
  </g>
  <!-- legend -->
  <g font-family="JetBrains Mono, monospace" font-size="10" fill="#2a2418">
    <text x="20" y="22" letter-spacing="2" font-weight="700" fill="#8a7f68">EXAMPLE GRAPH (PLACEHOLDER)</text>
    <rect x="600" y="20" width="105" height="108" rx="6" fill="#fbfaf6" stroke="#5a5140"/>
    <text x="610" y="38" font-weight="700">Legend</text>
    <circle cx="614" cy="52" r="5" fill="#d88a3a"/><text x="626" y="56">Person</text>
    <circle cx="614" cy="68" r="5" fill="#2d7d6e"/><text x="626" y="72">Project</text>
    <circle cx="614" cy="84" r="5" fill="#4a7c59"/><text x="626" y="88">Grant</text>
    <circle cx="614" cy="100" r="5" fill="#9b7eb7"/><text x="626" y="104">Concept</text>
    <circle cx="614" cy="116" r="5" fill="#c4593f"/><text x="626" y="120">Course</text>
  </g>
</svg>
<figcaption>Ontology preview — auto-extracted nodes and relations from your vault. The D3 graph is richer (~100-200 nodes).</figcaption>
</figure>
"""

DIAGRAMS["weekly-flow"] = """
<figure class="diagram">
<svg viewBox="0 0 760 200" xmlns="http://www.w3.org/2000/svg">
  <!-- timeline -->
  <line x1="40" y1="100" x2="720" y2="100" stroke="#0a1f3d" stroke-width="2"/>
  <g font-family="Inter, sans" fill="#0a1f3d">
    <!-- 5 milestones -->
    <g>
      <circle cx="80" cy="100" r="10" fill="#3b82f6"/>
      <text x="80" y="105" text-anchor="middle" fill="#fff" font-size="10" font-weight="700">Morn</text>
      <text x="80" y="135" text-anchor="middle" font-size="11" font-weight="600">Open Today.md</text>
      <text x="80" y="150" text-anchor="middle" font-size="10" opacity="0.7">Deadlines/priorities</text>
      <text x="80" y="165" text-anchor="middle" font-size="10" opacity="0.7">/ overnight changes</text>
    </g>
    <g>
      <circle cx="220" cy="100" r="10" fill="#f59e0b"/>
      <text x="220" y="105" text-anchor="middle" fill="#fff" font-size="10" font-weight="700">Work</text>
      <text x="220" y="135" text-anchor="middle" font-size="11" font-weight="600">Claude Code session</text>
      <text x="220" y="150" text-anchor="middle" font-size="10" opacity="0.7">CLAUDE.md auto</text>
      <text x="220" y="165" text-anchor="middle" font-size="10" opacity="0.7">loads → instant context</text>
    </g>
    <g>
      <circle cx="380" cy="100" r="10" fill="#10b981"/>
      <text x="380" y="105" text-anchor="middle" fill="#fff" font-size="10" font-weight="700">2h</text>
      <text x="380" y="135" text-anchor="middle" font-size="11" font-weight="600">Tracker auto-runs</text>
      <text x="380" y="150" text-anchor="middle" font-size="10" opacity="0.7">Scans new notes</text>
      <text x="380" y="165" text-anchor="middle" font-size="10" opacity="0.7">/ ontology rebuild</text>
    </g>
    <g>
      <circle cx="540" cy="100" r="10" fill="#8b5cf6"/>
      <text x="540" y="105" text-anchor="middle" fill="#fff" font-size="9" font-weight="700">End</text>
      <text x="540" y="135" text-anchor="middle" font-size="11" font-weight="600">Stop hook → digest</text>
      <text x="540" y="150" text-anchor="middle" font-size="10" opacity="0.7">Sessions/&lt;date&gt;.md</text>
      <text x="540" y="165" text-anchor="middle" font-size="10" opacity="0.7">auto-appended</text>
    </g>
    <g>
      <circle cx="680" cy="100" r="10" fill="#b5392a"/>
      <text x="680" y="105" text-anchor="middle" fill="#fff" font-size="9" font-weight="700">Wkend</text>
      <text x="680" y="135" text-anchor="middle" font-size="11" font-weight="600">[REVIEW] check</text>
      <text x="680" y="150" text-anchor="middle" font-size="10" opacity="0.7">apply_situation</text>
      <text x="680" y="165" text-anchor="middle" font-size="10" opacity="0.7">--review</text>
    </g>
    <text x="380" y="30" text-anchor="middle" font-family="Playfair Display, serif" font-weight="700" font-size="18">Daily loop</text>
    <text x="380" y="50" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="10" opacity="0.55" letter-spacing="2">DAILY LOOP</text>
  </g>
</svg>
<figcaption>Morning - work - 2h - end - weekend — you only act twice (morning, weekend).</figcaption>
</figure>
"""


def strip_frontmatter(text: str) -> tuple[str, dict]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return text, {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return text[m.end():], fm


def build_toc(html_body: str) -> tuple[str, str]:
    toc_items = []
    def repl(m):
        level = m.group(1)
        text = m.group(2)
        slug = re.sub(r"[^\w\s\-가-힣]", "", text).strip().lower()
        slug = re.sub(r"[\s_]+", "-", slug)[:60] or "section"
        if level in ("1", "2"):
            toc_items.append((slug, text, level))
        return f'<h{level} id="{slug}">{text}</h{level}>'
    new_body = re.sub(r"<h([1-3])>(.+?)</h\1>", repl, html_body)
    items = []
    for i, (sid, t, lvl) in enumerate(toc_items):
        cls = "lvl1" if lvl == "1" else "lvl2"
        items.append(f'<li class="{cls}"><a href="#{sid}"><span class="num">{i+1:02d}</span> {htmllib.escape(t)}</a></li>')
    return new_body, "\n".join(items)


def render(md_path: Path, out_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    body_md, fm = strip_frontmatter(text)
    title = fm.get("title", "Research Assistant Guide — Beginner")
    subtitle = fm.get("subtitle", "Obsidian + Claude Code 7-Day Setup")
    author = fm.get("author", "")
    affiliation = fm.get("affiliation", "")
    contact = fm.get("contact", "")

    # Process callouts: blockquotes that start with emoji
    body_md = re.sub(
        r"^> 💡 (\*\*[^*]+\*\*:)?(.+?)(?=\n\n|\Z)",
        lambda m: f'<div class="callout callout-tip"><span class="cb">💡 TIP</span> {(m.group(1) or "")}{m.group(2).strip()}</div>',
        body_md, flags=re.MULTILINE | re.DOTALL,
    )
    body_md = re.sub(
        r"^> ⚠️ (\*\*[^*]+\*\*:?)?(.+?)(?=\n\n|\Z)",
        lambda m: f'<div class="callout callout-warn"><span class="cb">⚠ WATCH OUT</span> {(m.group(1) or "")}{m.group(2).strip()}</div>',
        body_md, flags=re.MULTILINE | re.DOTALL,
    )
    body_md = re.sub(
        r"^> ✅ (\*\*[^*]+\*\*:?)?(.+?)(?=\n\n|\Z)",
        lambda m: f'<div class="callout callout-check"><span class="cb">✓ CHECK</span> {(m.group(1) or "")}{m.group(2).strip()}</div>',
        body_md, flags=re.MULTILINE | re.DOTALL,
    )

    # Inline wikilinks → chips
    body_md = re.sub(r"\[\[([^\]|]+?)(\|[^\]]+)?\]\]",
                     lambda m: f'<span class="wikilink">{htmllib.escape(m.group(1).strip())}</span>',
                     body_md)

    md = markdown.Markdown(extensions=["extra", "fenced_code", "tables", "sane_lists"])
    body_html = md.convert(body_md)

    # Substitute diagram placeholders
    for key, svg in DIAGRAMS.items():
        body_html = body_html.replace(f"{{{{DIAGRAM:{key}}}}}", svg)
        body_html = body_html.replace(f"<p>{{{{DIAGRAM:{key}}}}}</p>", svg)

    body_html, toc_html = build_toc(body_html)

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{htmllib.escape(title)}</title>

<!-- SEO + canonical -->
<meta name="description" content="Obsidian + Claude Code 7-day setup guide. AI research assistant for PhDs and researchers. 1-2 hours/day · ~$1-2/month · local-first.">
<meta name="author" content="{htmllib.escape(author)}">
<link rel="canonical" href="https://educatian.github.io/research-assistant-ai-workflow-en/">

<!-- Open Graph (Facebook, LinkedIn, Discord, KakaoTalk) -->
<meta property="og:type" content="article">
<meta property="og:title" content="{htmllib.escape(title)}">
<meta property="og:description" content="Obsidian + Claude Code 7-day setup guide for PhDs and researchers — step-by-step, with diagrams.">
<meta property="og:url" content="https://educatian.github.io/research-assistant-ai-workflow-en/">
<meta property="og:image" content="https://educatian.github.io/research-assistant-ai-workflow-en/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="A Research Assistant System for PhDs — beginner guide — Author Jewoong Moon, The University of Alabama">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="Research Assistant AI Workflow">
<meta property="article:author" content="{htmllib.escape(author)}">

<!-- Twitter / X Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{htmllib.escape(title)}">
<meta name="twitter:description" content="Obsidian + Claude Code 7-day setup guide for PhDs and researchers.">
<meta name="twitter:image" content="https://educatian.github.io/research-assistant-ai-workflow-en/og.png">
<meta name="twitter:image:alt" content="A Research Assistant System for PhDs — beginner guide">

<!-- Discord embed color -->
<meta name="theme-color" content="#2d7d6e">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,800;1,500&family=Hahmlet:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.css">
<style>{BEGINNER_CSS}</style>
</head>
<body>

<header class="masthead">
  <div class="mast-inner">
    <div class="mast-kicker">VOL.01 · BEGINNER · 2026 SPRING</div>
    <h1 class="mast-title">{htmllib.escape(title)}</h1>
    <p class="mast-deck">{htmllib.escape(subtitle)} — step-by-step, with diagrams.</p>
    {f'''<div class="mast-byline">
      <span class="byline-label">by</span>
      <span class="byline-name">{htmllib.escape(author)}</span>
      <span class="byline-sep">·</span>
      <span class="byline-aff">{htmllib.escape(affiliation)}</span>
      <span class="byline-sep">·</span>
      <a class="byline-mail" href="mailto:{htmllib.escape(contact)}">{htmllib.escape(contact)}</a>
    </div>''' if author else ''}
    <div class="mast-meta">
      <div><span>Total</span><strong>7 days</strong></div>
      <div><span>Per day</span><strong>1-2 hours</strong></div>
      <div><span>Monthly</span><strong>$1-2</strong></div>
      <div><span>Audience</span><strong>PhD / researcher</strong></div>
    </div>
  </div>
</header>

<div class="layout">
  <aside class="toc">
    <div class="toc-label">Contents</div>
    <ol>{toc_html}</ol>
    <div class="toc-foot">
      <p>Keyboard</p>
      <p><kbd>F</kbd> narrow · <kbd>D</kbd> dark mode</p>
    </div>
  </aside>
  <article class="prose">
    {body_html}
    <div class="closing">
      <div class="closing-mark">— end of 7-day guide —</div>
      <div class="closing-note">Stuck? Read the full guide (<a class="wikilink" href="full-guide.html" style="text-decoration:none">Research Assistant System Guide</a>) — every component in detail. Happy building!</div>
      {f'''<div class="closing-author">
        <span class="closing-author-label">Author</span>
        <strong>{htmllib.escape(author)}</strong>
        <span>{htmllib.escape(affiliation)}</span>
        <a href="mailto:{htmllib.escape(contact)}">{htmllib.escape(contact)}</a>
      </div>''' if author else ''}
    </div>
  </article>
</div>

<footer class="bottom">
  <div class="bottom-inner">
    <span>Research Assistant System · Beginner Guide</span>
    <span>Obsidian × Claude Code × OpenRouter</span>
    <span>Local-first · BYOK · Open</span>
  </div>
</footer>

<script>
  const links = document.querySelectorAll('.toc a');
  const sections = Array.from(document.querySelectorAll('article h1, article h2'));
  function onScroll() {{
    const y = window.scrollY + 120;
    let active = sections[0]?.id;
    for (const s of sections) if (s.offsetTop <= y) active = s.id;
    links.forEach(a => {{
      const isActive = a.getAttribute('href') === '#' + active;
      a.classList.toggle('active', isActive);
      // Toggle on parent <li> too so :has() and .has-active both work
      if (a.parentElement) a.parentElement.classList.toggle('has-active', isActive);
    }});
  }}
  window.addEventListener('scroll', onScroll); onScroll();
  // Also handle direct clicks (immediate visual response before scroll fires)
  links.forEach(a => a.addEventListener('click', () => {{
    links.forEach(x => {{
      x.classList.remove('active');
      if (x.parentElement) x.parentElement.classList.remove('has-active');
    }});
    a.classList.add('active');
    if (a.parentElement) a.parentElement.classList.add('has-active');
  }}));

  // Click-to-copy on prompt boxes
  document.querySelectorAll('.prompt-box').forEach(box => {{
    box.addEventListener('click', async () => {{
      const pre = box.querySelector('pre');
      if (!pre) return;
      try {{
        await navigator.clipboard.writeText(pre.innerText.trim());
        box.classList.add('copied');
        setTimeout(() => box.classList.remove('copied'), 1500);
      }} catch (e) {{
        const sel = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(pre);
        sel.removeAllRanges();
        sel.addRange(range);
      }}
    }});
  }});
  document.addEventListener('keydown', e => {{
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'f' || e.key === 'F') document.body.classList.toggle('narrow');
    if (e.key === 'd' || e.key === 'D') document.body.classList.toggle('dark');
  }});
</script>
</body></html>"""

    out_path.write_text(html_doc, encoding="utf-8")
    print(f"[done] {out_path}  ({out_path.stat().st_size // 1024} KB)")


BEGINNER_CSS = r"""
/* Adapted directly from open-design html-ppt-course-module skill tokens
   (warm paper + teal-green accent), adjusted for long-form scrolling docs. */
:root {
  --bg: #fbfaf6;
  --bg-soft: #f4f1e8;
  --bg-rgb: 251,250,246;
  --surface: #ffffff;
  --surface-2: #f6f3ea;
  --border: rgba(60,45,20,.12);
  --border-strong: rgba(60,45,20,.24);
  --text-1: #2a2418;
  --text-2: #5a5140;
  --text-3: #8a7f68;
  --text-rgb: 42,36,24;
  --accent:   #2d7d6e;   /* teal-green */
  --accent-2: #d88a3a;   /* warm orange */
  --accent-3: #c4593f;   /* rust */
  --good: #4a7c59;
  --warn: #d88a3a;
  --bad:  #c4593f;
  --grad: linear-gradient(135deg,#2d7d6e,#4ea893);
  --shadow: 0 12px 30px rgba(60,45,20,.07);
  --shadow-lg: 0 24px 60px rgba(60,45,20,.12);
  --radius: 14px;
  --radius-lg: 20px;

  --serif: "Hahmlet", "Playfair Display", "Apple SD Gothic Neo", Georgia, serif;
  --sans: "Pretendard Variable", "Pretendard", "Inter", -apple-system, "Apple SD Gothic Neo", "Segoe UI", sans-serif;
  --mono: "JetBrains Mono", "IBM Plex Mono", "Cascadia Code", "D2Coding", Consolas, monospace;
}

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: var(--sans);
  font-size: 16px;
  line-height: 1.7;
  color: var(--text-1);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-feature-settings: "ss01", "ss02", "cv01", "cv11";  /* Pretendard polish */
  word-break: keep-all;        /* Korean line-break preserves words */
  overflow-wrap: break-word;
}
body.dark {
  --bg: #1c1812;
  --bg-soft: #2a2418;
  --surface: #2a2418;
  --surface-2: #322a1d;
  --border: rgba(244,241,232,.08);
  --border-strong: rgba(244,241,232,.18);
  --text-1: #f4f1e8;
  --text-2: #c2b89f;
  --text-3: #8a7f68;
  --text-rgb: 244,241,232;
}

/* Masthead — course-module hero feel */
.masthead {
  padding: 96px 5vw 64px;
  background: var(--bg-soft);
  border-bottom: 1px solid var(--border);
  position: relative;
  overflow: hidden;
}
.masthead::before {
  content: "";
  position: absolute;
  top: -100px;
  right: -100px;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, color-mix(in srgb, var(--accent) 12%, transparent), transparent 70%);
  pointer-events: none;
}
.mast-inner { max-width: 900px; margin: 0 auto; position: relative; z-index: 1; }
.mast-kicker {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent-2);
  margin-bottom: 24px;
}
.mast-kicker::before { content: "✦ "; color: var(--accent); }
.mast-title {
  font-family: var(--serif);
  font-weight: 800;
  font-size: clamp(40px, 6vw, 76px);
  line-height: 1.04;
  letter-spacing: -0.02em;
  margin: 0 0 24px;
  color: var(--text-1);
}
.mast-deck {
  font-family: var(--sans);
  font-size: clamp(17px, 1.5vw, 22px);
  font-weight: 300;
  line-height: 1.6;
  color: var(--text-2);
  margin: 0 0 28px;
  max-width: 680px;
}
.mast-byline {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 10px;
  margin: 0 0 40px;
  padding: 12px 0;
  border-top: 1px dashed var(--border);
  border-bottom: 1px dashed var(--border);
  max-width: 680px;
}
.byline-label {
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text-3);
  font-weight: 700;
}
.byline-name {
  font-family: var(--serif);
  font-size: 18px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: -0.005em;
}
.byline-aff {
  font-family: var(--sans);
  font-size: 13px;
  font-style: italic;
  color: var(--text-2);
}
.byline-sep {
  color: var(--text-3);
  font-size: 12px;
}
.byline-mail {
  font-family: var(--mono);
  font-size: 12px;
  color: var(--accent-2);
  text-decoration: none;
  border-bottom: 1px dashed var(--accent-2);
  padding-bottom: 1px;
}
.byline-mail:hover { color: var(--accent-3); border-color: var(--accent-3); }
.mast-meta {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  max-width: 760px;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}
.mast-meta > div {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px 24px 20px 0;
  border-right: 1px dashed var(--border);
}
.mast-meta > div:last-child { border-right: none; }
.mast-meta span {
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-3);
  font-weight: 600;
}
.mast-meta strong {
  font-family: var(--serif);
  font-size: 26px;
  font-weight: 700;
  color: var(--accent);
}

/* Layout — sidebar + main, course-module style */
.layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 72px;
  max-width: 1280px;
  margin: 0 auto;
  padding: 72px 5vw 96px;
}

/* TOC sidebar — mimics course-module .obj-list with ○/●/▸ progression */
.toc {
  position: sticky;
  top: 20px;
  align-self: start;
  /* internal scroll when TOC exceeds viewport */
  max-height: calc(100vh - 40px);
  overflow-y: auto;
  overflow-x: hidden;
  border-right: 1px solid var(--border);
  padding: 4px 24px 16px 0;
  /* Firefox scrollbar */
  scrollbar-width: thin;
  scrollbar-color: var(--accent) transparent;
}
/* WebKit scrollbar — thin teal */
.toc::-webkit-scrollbar { width: 4px; }
.toc::-webkit-scrollbar-track { background: transparent; }
.toc::-webkit-scrollbar-thumb {
  background: color-mix(in srgb, var(--accent) 50%, transparent);
  border-radius: 2px;
}
.toc::-webkit-scrollbar-thumb:hover { background: var(--accent); }
.toc-brand {
  font-family: var(--serif);
  font-size: 22px;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 28px;
  display: flex;
  align-items: baseline;
  gap: 6px;
}
.toc-brand::before { content: "✦"; color: var(--accent-2); font-size: 18px; }
.toc-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--text-3);
  margin: 0 0 14px;
}
.toc ol {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 12.5px;
  color: var(--text-2);
  line-height: 1.45;
}
.toc li {
  padding: 7px 0 7px 22px;
  position: relative;
  border-bottom: 1px dashed var(--border);
}
.toc li::before {
  content: "○";
  position: absolute;
  left: 0;
  top: 7px;
  color: var(--accent);
  font-size: 13px;
  line-height: 1;
  transition: color 0.18s ease, transform 0.18s ease;
}
.toc li.lvl1 { font-weight: 600; }
.toc li.lvl1::before { content: "●"; }
.toc li.lvl2 { padding-left: 32px; font-size: 12px; }
.toc li.lvl2::before { left: 12px; font-size: 10px; top: 8px; }
.toc a {
  color: inherit;
  text-decoration: none;
  display: block;
  line-height: 1.4;
  transition: color 0.15s;
}
.toc a:hover { color: var(--text-1); }
.toc li:hover::before { color: var(--accent-2); }

/* Active state — bullet becomes filled accent-2 (warm orange) */
.toc li.has-active::before,
.toc li:has(> a.active)::before {
  content: "●";
  color: var(--accent-2);
  transform: scale(1.15);
}
.toc li.has-active,
.toc li:has(> a.active) {
  color: var(--text-1);
  font-weight: 700;
}
.toc li.has-active > a,
.toc li:has(> a.active) > a {
  color: var(--accent-3);
}
.toc .num {
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 500;
  color: var(--text-3);
  margin-right: 6px;
}
.toc-foot {
  margin-top: 20px;
  padding-top: 14px;
  border-top: 1px dashed var(--border);
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text-3);
}
.toc-foot p { margin: 4px 0; }
.toc-foot kbd {
  display: inline-block;
  padding: 2px 6px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 3px;
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 600;
  color: var(--text-2);
}

/* Prose — academic but friendly */
.prose {
  max-width: 760px;
  font-size: 17px;
  line-height: 1.8;
  counter-reset: section;
}
body.narrow .prose { max-width: 620px; }

.prose h1 {
  font-family: var(--serif);
  font-weight: 800;
  font-size: clamp(36px, 4vw, 56px);
  line-height: 1.05;
  letter-spacing: -0.02em;
  margin: 64px 0 32px;
  color: var(--text-1);
}

.prose h2 {
  font-family: var(--serif);
  font-weight: 700;
  font-size: clamp(28px, 3vw, 40px);
  line-height: 1.15;
  letter-spacing: -0.015em;
  margin: 96px 0 24px;
  color: var(--text-1);
  display: flex;
  align-items: baseline;
  gap: 16px;
  position: relative;
}
.prose h2::before {
  content: counter(section, decimal-leading-zero);
  counter-increment: section;
  font-family: var(--mono);
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-2);
  letter-spacing: 0.1em;
  background: var(--surface-2);
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid var(--border);
  flex: none;
  position: relative;
  top: -4px;
}
.prose h2::after {
  content: "";
  position: absolute;
  bottom: -16px;
  left: 0;
  width: 72px;
  height: 3px;
  background: var(--accent);
  border-radius: 2px;
}

.prose h3 {
  font-family: var(--sans);
  font-weight: 700;
  font-size: 20px;
  letter-spacing: -0.005em;
  margin: 48px 0 14px;
  color: var(--text-1);
  display: flex;
  align-items: center;
  gap: 10px;
}
.prose h3::before {
  content: "";
  width: 4px;
  height: 18px;
  background: var(--accent);
  border-radius: 2px;
  display: inline-block;
}

.prose p { margin: 0 0 20px; color: var(--text-2); }
.prose p strong { color: var(--text-1); font-weight: 700; }
.prose em { font-style: italic; color: var(--text-2); }
.prose a {
  color: var(--accent);
  text-decoration: underline;
  text-decoration-thickness: 1.5px;
  text-underline-offset: 3px;
  transition: color 0.15s;
}
.prose a:hover { color: var(--accent-3); text-decoration-color: var(--accent-3); }
.prose ul, .prose ol { margin: 0 0 20px; padding-left: 20px; color: var(--text-2); }
.prose li { margin-bottom: 8px; }
.prose ul li { list-style: none; position: relative; padding-left: 6px; }
.prose ul li::before {
  content: "○";
  color: var(--accent);
  position: absolute;
  left: -16px;
  top: 0;
}
.prose ol li::marker { color: var(--accent); font-weight: 600; }

/* Inline code */
.prose code {
  font-family: var(--mono);
  font-size: 0.86em;
  background: var(--surface-2);
  border: 1px solid var(--border);
  padding: 1px 6px;
  border-radius: 3px;
  color: var(--accent-3);
}

/* Block code — course-module dark warm-brown */
.prose pre {
  background: #2a2418;
  color: #f4f1e8;
  padding: 22px 26px;
  border-radius: var(--radius);
  overflow-x: auto;
  font-size: 13.5px;
  line-height: 1.7;
  margin: 24px 0;
  font-family: var(--mono);
  position: relative;
  box-shadow: var(--shadow);
}
.prose pre::before {
  content: "code";
  position: absolute;
  top: 12px;
  right: 16px;
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #8a7f68;
}
.prose pre code {
  background: transparent;
  border: none;
  padding: 0;
  color: inherit;
  font-size: inherit;
}

/* Wikilink chip — cream pill */
.wikilink {
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.84em;
  color: var(--accent);
  background: color-mix(in srgb, var(--accent) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--accent) 22%, transparent);
  padding: 1px 8px;
  border-radius: 999px;
  font-weight: 500;
}

/* Tables — academic concept-box vibe */
.prose table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  margin: 32px 0;
  font-size: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
}
.prose th, .prose td {
  text-align: left;
  padding: 12px 18px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}
.prose tr:last-child td { border-bottom: none; }
.prose th {
  font-family: var(--mono);
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-3);
  background: var(--surface-2);
  border-bottom: 1px solid var(--border-strong);
  padding-bottom: 12px;
  font-weight: 700;
}
.prose tr:hover td { background: color-mix(in srgb, var(--accent) 4%, transparent); }
.prose td code { font-size: 12px; }

/* Callouts — directly mirroring course-module .callout */
.callout {
  margin: 28px 0;
  padding: 18px 24px;
  border-left: 4px solid;
  border-radius: 0 var(--radius) var(--radius) 0;
  background: var(--surface-2);
  font-size: 15.5px;
  line-height: 1.7;
}
.callout-tip   { border-left-color: var(--accent-2); background: #fff8ed; }
.callout-warn  { border-left-color: var(--accent-3); background: #fdf2ee; }
.callout-check { border-left-color: var(--accent);   background: color-mix(in srgb, var(--accent) 6%, var(--surface)); }

/* Prompt-box: side-by-side natural-language alternative to raw commands.
   Indigo/purple to distinguish from teal (TIP) / orange (WARN) / green (CHECK). */
.prompt-box {
  margin: 18px 0 28px;
  border: 1.5px solid #9b7eb7;
  border-radius: var(--radius);
  background: color-mix(in srgb, #9b7eb7 5%, var(--surface));
  overflow: hidden;
  position: relative;
}
.prompt-label {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #fff;
  background: #9b7eb7;
  padding: 8px 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.prompt-label .prompt-icon { font-size: 13px; }
.prompt-box pre {
  margin: 0;
  padding: 18px 22px;
  background: transparent;
  color: var(--text-1);
  border: none;
  border-left: none;
  font-family: var(--mono);
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: keep-all;
}
.prompt-box pre::before { content: none; }
.prompt-box::after {
  content: "📋 click to copy";
  position: absolute;
  bottom: 10px;
  right: 14px;
  font-family: var(--mono);
  font-size: 10px;
  color: #9b7eb7;
  opacity: 0.5;
  pointer-events: none;
}
.prompt-box.copied::after { content: "✓ copied"; opacity: 1; color: var(--accent); }
.prompt-box pre { cursor: pointer; }

.callout strong {
  color: var(--text-1);
  font-weight: 700;
}
.callout-tip strong b, .callout-tip > b { color: var(--accent-2); }

.cb {
  display: inline-block;
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  margin-right: 12px;
  padding: 3px 8px;
  border-radius: 3px;
  text-transform: uppercase;
  vertical-align: 1px;
}
.callout-tip .cb   { background: var(--accent-2); color: #fff; }
.callout-warn .cb  { background: var(--accent-3); color: #fff; }
.callout-check .cb { background: var(--accent);   color: #fff; }

/* Day exercise blocks — auto-detect "Day N —" h2 sections */
.prose h2[id^="day-"]::before { background: var(--accent); color: #fff; border-color: var(--accent); }

/* Concept callout (the > with no emoji prefix becomes a regular blockquote) */
.prose blockquote {
  margin: 28px 0;
  padding: 20px 26px;
  border-left: 4px solid var(--accent);
  background: var(--surface);
  border-radius: 0 var(--radius) var(--radius) 0;
  font-family: var(--serif);
  font-size: 17px;
  font-style: italic;
  line-height: 1.65;
  color: var(--text-2);
  box-shadow: var(--shadow);
}
.prose blockquote strong {
  font-style: normal;
  color: var(--accent);
  font-family: var(--sans);
  font-weight: 700;
}
.prose blockquote p:last-child { margin-bottom: 0; }

/* Diagrams — concept-box style cards */
.diagram {
  margin: 40px 0;
  padding: 28px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  position: relative;
}
.diagram::before {
  content: "FIG";
  position: absolute;
  top: 14px;
  right: 18px;
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--text-3);
}
.diagram svg {
  display: block;
  width: 100%;
  height: auto;
  max-width: 100%;
}
.diagram figcaption {
  font-family: var(--serif);
  font-style: italic;
  font-size: 14px;
  color: var(--text-2);
  margin: 20px 0 0;
  padding-top: 16px;
  border-top: 1px dashed var(--border);
  text-align: center;
}

.diagram-hero {
  margin: 0 -5vw 64px;
  padding: 0;
  background: linear-gradient(135deg, #2a2418 0%, #3a2f1c 100%);
  border: none;
  border-radius: 0;
  box-shadow: none;
}
.diagram-hero::before { display: none; }

.diagram-pair {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 20px;
  align-items: center;
  background: transparent;
  border: none;
  padding: 0;
  box-shadow: none;
}
.diagram-pair::before { display: none; }
.pair-side {
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 20px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}
.pair-label {
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.15em;
  background: var(--text-3);
  color: var(--surface);
  display: inline-block;
  padding: 4px 10px;
  border-radius: 3px;
  margin-bottom: 14px;
}
.pair-arrow {
  font-family: var(--serif);
  font-size: 36px;
  color: var(--accent-2);
  text-align: center;
}
.pair-caption {
  font-family: var(--serif);
  font-style: italic;
  font-size: 13px;
  text-align: center;
  margin: 14px 0 0;
  color: var(--text-2);
}

/* Day exercise / phase divider — show 7-day timeline at top of each day */
.prose h2[id^="day-"] {
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent) 8%, var(--bg)), transparent);
  padding: 16px 20px 16px 0;
  margin-left: -20px;
  border-radius: var(--radius) 0 0 var(--radius);
}

/* Closing */
.closing {
  margin-top: 120px;
  padding: 56px 40px;
  background: var(--surface-2);
  border-radius: var(--radius-lg);
  text-align: center;
  border-top: 4px solid var(--accent);
}
.closing-mark {
  font-family: var(--serif);
  font-style: italic;
  font-size: 26px;
  color: var(--accent);
  margin-bottom: 12px;
  letter-spacing: 0.02em;
}
.closing-mark::before, .closing-mark::after { content: "✦"; color: var(--accent-2); margin: 0 12px; font-style: normal; }
.closing-note {
  font-family: var(--sans);
  font-size: 14px;
  color: var(--text-2);
}
.closing-author {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px dashed var(--border);
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  align-items: baseline;
  font-size: 13px;
  color: var(--text-2);
}
.closing-author-label {
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-3);
  font-weight: 700;
}
.closing-author strong {
  font-family: var(--serif);
  font-size: 16px;
  color: var(--accent);
  font-weight: 700;
}
.closing-author a {
  color: var(--accent-2);
  text-decoration: none;
  font-family: var(--mono);
  font-size: 12px;
  border-bottom: 1px dashed var(--accent-2);
}
.closing-author a:hover { color: var(--accent-3); border-color: var(--accent-3); }

/* Footer */
.bottom {
  border-top: 1px solid var(--border);
  background: #2a2418;
  color: #f4f1e8;
  padding: 32px 5vw;
  font-family: var(--mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.bottom-inner {
  display: flex;
  justify-content: space-between;
  max-width: 1280px;
  margin: 0 auto;
  align-items: center;
}
.bottom-inner span:first-child::before {
  content: "✦";
  color: var(--accent-2);
  margin-right: 8px;
}

/* Subtle paper texture (optional) */
body::before {
  content: "";
  position: fixed;
  inset: 0;
  background-image:
    radial-gradient(circle at 25% 20%, rgba(216,138,58,0.02), transparent 40%),
    radial-gradient(circle at 75% 80%, rgba(45,125,110,0.02), transparent 40%);
  pointer-events: none;
  z-index: -1;
}

/* Responsive */
@media (max-width: 980px) {
  .layout { grid-template-columns: 1fr; gap: 40px; padding-top: 48px; }
  .toc { position: static; padding-right: 0; border-right: none; border-bottom: 1px solid var(--border); padding-bottom: 24px; }
  .mast-meta { grid-template-columns: repeat(2, 1fr); }
  .mast-meta > div:nth-child(2) { border-right: none; }
  .diagram-pair { grid-template-columns: 1fr; }
  .pair-arrow { transform: rotate(90deg); padding: 12px 0; }
  .bottom-inner { flex-direction: column; gap: 12px; align-items: flex-start; }
  .diagram-hero { margin-left: -5vw; margin-right: -5vw; }
}
"""


if __name__ == "__main__":
    render(GUIDE, OUT)
