# Research Assistant AI Workflow (English)

> A 7-day setup guide for PhDs and researchers — Obsidian × Claude Code AI research-assistant system.

🌐 **Live**: <https://educatian.github.io/research-assistant-ai-workflow-en/>
🇰🇷 **Korean version**: <https://educatian.github.io/research-assistant-ai-workflow-ko/>

---

## What is this?

A guide for building a personal AI research-assistant system — an Obsidian vault that auto-indexes, queries, and visualizes your research portfolio (papers, methods, students, grants), driven by Claude Code (or Codex).

- **1-2 hours/day for 7 days** to get a working system in your own vault
- **~$1-2/month** in LLM API costs
- **Local-first**: all data lives on your machine. External LLM is invoked only at decision points
- **BYOK**: any model via OpenRouter (Gemini Flash default, swappable to Claude Sonnet, etc.)

## Guide structure

| | Contents |
|---|---|
| **§ 0** | Glossary — Vault / Entity / Frontmatter / Wikilink / Hook / Ontology / API key |
| **§ 0.5** | AI agents — Claude Code vs Codex, CLI vs Desktop |
| **§ 1-3** | Mental model · automation flow · prerequisites checklist |
| **§ 3.5** | CLI install (Claude Code + Codex) — Windows/macOS/Linux |
| **Day 1** | Create the vault + first entity page |
| **Day 2** | `Today.md` single entry point |
| **Day 3** | Connect Claude Code + Stop hook |
| **Day 4** | Every-2-hour tracker (Windows scheduled task) |
| **Day 5** | Ontology — make the vault query-able |
| **Day 6** | LLM auto-detects note changes (situation watch) |
| **Day 7** | `/slides` auto-generate presentations |
| **After** | Daily rhythm · 5 scenarios · troubleshooting · customization patterns |

## Output preview

The HTML guide is single-file (~150KB) and contains:

- 🎨 **Inline SVG diagrams** — 3-layer mental model · tracker flow · 7-day timeline · ontology schema · agents comparison · 5 scenarios
- 📚 **40+ callouts** — 💡 TIP / ⚠ WATCH OUT / ✓ CHECK / 🛠 CUSTOMIZE
- 💬 **8 prompt boxes** — natural-language alternatives to raw shell commands (click to copy)
- 🎯 **Sticky TOC** — scroll-active highlighting (○ → ●)
- ⌨ **Keyboard shortcuts** — `F` narrow column · `D` dark mode

## Build it yourself

```bash
pip install markdown playwright pillow
playwright install chromium
python render.py              # generates index.html
python generate_og_image.py   # generates og.png + og.jpg
```

Edit `guide.md` and re-run to regenerate.

Custom paths:
```bash
python render.py custom.md custom.html
```

## Stack

- [Obsidian](https://obsidian.md) — vault UI (free)
- [Claude Code](https://claude.com/claude-code) — Anthropic AI agent
- [Codex CLI](https://github.com/openai/codex) — OpenAI agent (optional)
- [OpenRouter](https://openrouter.ai) — LLM proxy (BYOK)
- [open-design](https://github.com/nexu-io/open-design) — slide-deck skill templates
- Python 3.11+ / PowerShell / Markdown

## Author

**Jewoong Moon** · The University of Alabama · [jmoon19@ua.edu](mailto:jmoon19@ua.edu)

Questions, feedback, and PRs welcome.

## License

- **Content** (`guide.md`, `index.html`): [CC BY-SA 4.0](LICENSE-content) — attribution + share-alike
- **Code** (`render.py`, `generate_og_image.py`): [MIT](LICENSE-code) — free use

## Contributing

Issues and PRs welcome. Add scenarios from your domain, new ontology types, slide skills, etc.
