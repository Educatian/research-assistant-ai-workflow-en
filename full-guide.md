---
type: concept
title: "Research Assistant System Guide"
subtitle: "Obsidian × Claude Code — the full reference"
created: 2026-05-02
updated: 2026-05-02
tags:
  - meta
  - guide
  - architecture
  - claude-code
  - obsidian
status: active
related:
  - "[[Vault Ontology]]"
  - "[[overview]]"
  - "[[Today]]"
  - "[[LLM Wiki Pattern]]"
---

# Obsidian × Claude Code Research-Assistant System

A reproducible setup for academic researchers who want one persistent knowledge graph that **(a) builds itself from your project files**, **(b) updates as you work**, and **(c) answers structured queries** ("who is the PI of X?", "what methods does Y use?", "what changed this week?"). The system runs locally, uses Claude Code (or Codex) as the agent, Obsidian as the vault UI, and OpenRouter (Gemini Flash) for cheap LLM judgment.

> **Why this exists** — researchers accumulate fragmented context (project drafts, meeting notes, methodology decisions, grant deadlines, advisee status) across dozens of folders. A vault by itself just stores; this layer makes it self-organizing and queryable. The single entry point page replaces the daily "where did I leave off?" search.

## 1. What you get

- **Single entry-point page** (`wiki/Today.md`) — every session opens here. Has a routing cheat-sheet, current deadlines, project-priority tiers, and an auto-updated "Recent activity" block.
- **Knowledge ontology** (197+ nodes / 2200+ edges) auto-extracted from frontmatter + wikilinks, exported as JSON-LD + interactive D3 graph. Query by entity ("MyProject"), predicate ("hasPI"), or type ("Grant").
- **Auto session digests** — every Claude Code or Codex session ends with a structured note in `wiki/sources/Sessions YYYY-MM-DD.md` (goal · outcome · key decisions · files touched · next).
- **Research-note watcher** — every 2 hours, scans new notes/source files, LLM-judges what changed, proposes vault updates (deadlines, status, new collaborators) in `wiki/situation/YYYY-MM-DD.md`. Auto-applies high-confidence changes.
- **Desktop organizer** — LLM judges loose files at Desktop root, files them into structured folders, leaves a manifest `Desktop\_organize_log\<run-id>.txt` with `--undo` support.
- **/slides workflow** — `/slides <topic>` generates a single-file HTML slide deck using cached open-design skill templates + your vault content.
- **Persistent memory** — `~\.claude\projects\<machine>\memory\` auto-loads on every session; future sessions know your projects, advisees, methods, preferences without re-explanation.

All running locally. ~$0.02-0.05/day in LLM costs.

## 2. Architecture

```
                 ┌──────────────────────────────────────────────────────┐
                 │  Obsidian vault (wiki/)                              │
                 │                                                      │
                 │   entities/    projects · people · grants · labs     │
                 │   concepts/    methodology · theory · patterns       │
                 │   sources/     manuscripts · digests · session logs  │
                 │   activity/    daily auto-aggregated activity        │
                 │   situation/   LLM-judged change proposals           │
                 │                                                      │
                 │   Today.md  ← single entry point                     │
                 │   _ontology.json + _ontology_graph.html              │
                 └──────────────────────────────────────────────────────┘
                                       ▲
                                       │
   ┌───────────────────────────────────┼───────────────────────────────────┐
   │                                   │                                   │
   ▼                                   ▼                                   ▼
Session digests              Daily tracker (every 2h)              On-demand commands
(Claude Stop hook +          ─────────────────────────             /slides · /recall
codex_digest.ps1)            • file activity scan                  query_ontology.py
                             • git commits                         apply_situation.py
                             • GitHub events                       organize_desktop.py
                             • calendar / notes                    
                             • ontology rebuild
                             • situation watch (LLM)
                             • desktop organizer (LLM)
```

Three persistence layers:

| Layer | Where | Purpose |
|---|---|---|
| **Project knowledge** | `wiki/` | Citable, queryable facts about projects/methods/people. Entity pages with frontmatter (`type:`, `deadline:`, `status:`). |
| **Activity / aggregates** | `wiki/activity/` + `wiki/situation/` + `wiki/sources/Sessions YYYY-MM-DD.md` | Time-series snapshots auto-written by the tracker and session hooks. |
| **Auto memory** | `~\.claude\projects\<machine>\memory\` | Cross-session pointers Claude reads on startup. Index file `MEMORY.md` always in context. |

Privacy posture: everything is **local-first**. The vault is plain markdown. The only external calls are (a) optional OpenRouter LLM completion and (b) optional `gh` CLI for GitHub activity. Sensitive sources stay outside the vault — see § 8.

## 3. Prerequisites

- **Obsidian** (v1.9.10+ recommended)
- **Claude Code** CLI installed and authenticated
- **Python 3.11+** (for the scripts)
- **PowerShell** (Windows) — Bash on macOS/Linux works similarly with minor path edits
- **`gh` CLI** authenticated (optional — for GitHub activity)
- **OpenRouter API key** stored at `_secrets/openrouter.txt` or in `$env:OPENROUTER_API_KEY` (optional — for LLM judgment; system gracefully degrades without it)
- A Python venv or system install with: `pdfplumber`, `python-docx`, `openpyxl`, `python-pptx` for source-file text extraction

## 4. Setup walkthrough

### 4.1 Vault bootstrap

Start from the [claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) seed, or any blank Obsidian vault. The folder layout this guide assumes:

```
ObsidianVault/
├── CLAUDE.md             ← vault-level Claude Code instructions
├── wiki/
│   ├── Today.md          ← single entry point (write the template once)
│   ├── index.md          ← table of contents
│   ├── overview.md       ← project-portfolio narrative
│   ├── log.md            ← append-only event log
│   ├── entities/
│   ├── concepts/
│   ├── sources/
│   ├── activity/         ← created automatically
│   ├── situation/        ← created automatically
│   ├── _ontology.json    ← generated
│   ├── _ontology_summary.md
│   └── _ontology_graph.html
└── scripts/              ← all automation lives here
```

Write a few entity pages by hand to seed the system — for each major project/grant/method, create `wiki/entities/<Name>.md` with this frontmatter:

```yaml
---
type: project        # or grant | concept | person | course | manuscript | lab | tool
title: "MyProject"
status: active
tier: 2
deadline: 2026-05-20
related:
  - "[[Jane Researcher]]"
  - "[[Bayesian Causal Forest]]"
---
# MyProject

[narrative body — methodology, status, decisions, links to other entities]
```

The richer the cross-linking (`[[...]]` wikilinks in body text), the better the ontology will reconstruct relationships.

### 4.2 User-level CLAUDE.md (the "always-load" instructions)

Drop a CLAUDE.md at `C:\Users\<you>\CLAUDE.md` (or `~/CLAUDE.md`). Claude Code walks the parent chain and auto-loads this from any working directory. This is what makes "기억해봐 / tell me about X" instantly grounded.

Key contents:

```markdown
# User-level Claude Code instructions

## On every session start
1. Read `<vault>/wiki/Today.md` — single entry point.
2. Auto-memory at `~\.claude\projects\<machine>\memory\MEMORY.md` is already loaded.
3. Prefer existing knowledge bases over reasoning from scratch.

## Knowledge bases (in priority order)
| Source | What | How to query |
|---|---|---|
| wiki/Today.md | deadlines, priorities, recent | Read |
| wiki/_ontology.json | structured: 12 entity types + 14 relations | Read or query_ontology.py |
| wiki/entities/<Name>.md | per-entity narrative | Read directly |
| wiki/concepts/ | methodology pages | Read |
| wiki/situation/<date>.md | latest LLM-judged changes | Read |
| wiki/sources/Sessions <date>.md | session logs | Read for "what did I do" |

## On "make a slide deck / PT 만들어"
Invoke /slides <topic> — see ~/.claude/commands/slides.md.
```

### 4.3 Slash commands

`~/.claude/commands/recall.md`:

```markdown
---
description: Recall context for a topic from vault + ontology + memory
argument-hint: "[topic or question]"
---
Read wiki/Today.md first. If $ARGUMENTS names a topic, drill: entity page → ontology query → daily situation note. Cite via [[wikilinks]]. Korean reply OK.
```

`~/.claude/commands/slides.md` — see § 6 for the full spec.

### 4.4 Scripts

Drop these in `<vault>/scripts/` (full content in the companion code repo). Brief purpose of each:

| Script | Trigger | What it does |
|---|---|---|
| `update_today.ps1` | Stop hook + manual | Refreshes `Today.md` § Recent block (last 7d vault edits, deadlines from frontmatter) |
| `save_session.ps1` | Stop hook | Calls digest_session.py with the transcript, then update_today.ps1 |
| `digest_session.py` | called by save_session | Parses Claude/Codex JSONL transcript, LLM-summarizes, appends to `wiki/sources/Sessions YYYY-MM-DD.md` |
| `codex_digest.ps1` | manual after Codex session | Finds latest Codex rollout, runs digest_session.py |
| `daily_tracker.ps1` | every 2h scheduled task | Orchestrator — calls all collectors below |
| `build_ontology.py` | tracker §8 | Walks `wiki/`, parses frontmatter + wikilinks, emits `_ontology.json` + summary + D3 graph |
| `situation_watch.py` | tracker §9 | Scans new research notes/source files added to vault since last run, LLM-judges changes, writes `wiki/situation/<date>.md` |
| `apply_situation.py` | manual | Applies AUTO blocks from situation note → entity pages + ontology rebuild |
| `organize_desktop.py` | tracker §10 | LLM-files Desktop root loose files into structured folders, writes `_organize_log/<run>.txt` |
| `query_ontology.py` | manual / from /recall | Fast lookup against `_ontology.json` (`--type Grant`, `--predicate hasPI`, `<pattern>`) |
| `collect_github.ps1` | tracker | gh CLI for PRs/issues/pushes |
| `collect_calendar.ps1` | tracker | Outlook calendar today+tomorrow |
| `collect_notes.ps1` | tracker | Sticky Notes (UWP plum.sqlite) + Outlook Notes folder |
| `collect_social.ps1` | tracker | Stub for LinkedIn/X/Notion if user wires tokens |

### 4.5 Claude Code Stop hook

Edit `~\.claude\settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"<vault>\\scripts\\save_session.ps1\" -Source claude"
          }
        ]
      }
    ]
  }
}
```

After this, every Claude Code session that ends will auto-write a structured digest to `wiki/sources/Sessions YYYY-MM-DD.md`.

### 4.6 Windows scheduled task (every 2h)

```powershell
schtasks.exe /Create /TN "ResearchAssistantTracker" /SC DAILY /ST 00:00 /RI 120 /DU 23:59 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File <vault>\scripts\daily_tracker.ps1" /F

# Allow run-when-missed (catch-up after computer was off):
$task = Get-ScheduledTask -TaskName ResearchAssistantTracker
$task.Settings.StartWhenAvailable = $true
$task.Settings.DisallowStartIfOnBatteries = $false
$task.Settings.StopIfGoingOnBatteries = $false
Set-ScheduledTask -TaskName ResearchAssistantTracker -Settings $task.Settings
```

The task runs 12 times/day (00:00, 02:00, …, 22:00). If the computer is off during a slot, Windows fires it as soon as possible after wake; the tracker's dynamic-window logic uses a `.tracker_state.json` to compute "time since last successful run" and widens its scan window accordingly (capped at 7 days).

## 5. Components in detail

### 5.1 The vault ontology

The schema lives at `wiki/concepts/Vault Ontology.md` — a human-readable spec of 12 entity types and 14 relations. Build script `build_ontology.py`:

1. Walks every `wiki/**/*.md`, parses frontmatter for `type:`.
2. Registers each page as a node, keyed by `vault:<type>/<slug>`.
3. For each `[[wikilink]]` in body text, looks at a ±100 character window around the link and tries to match a relation cue:
   - "PI" / "Principal Investigator" → `hasPI`
   - "advisee of" / "supervised by" → `advisedBy`
   - "uses" / "applies" / "method" → `usesMethod`
   - "funded by" / "$" → `fundedBy`
   - … 14 relations total.
4. **Type-domain enforcement** — if subject type doesn't match the relation's declared domain (e.g. `hasPI` is `Project|Grant → Person`), it swaps subject/object. This handles the common pattern where a person's page mentions "[[MyProject]] (PI)" → emits `MyProject hasPI <Person>`, not the reverse.
5. Emits `_ontology.json` (JSON-LD with foaf/schema/skos/vault namespaces), `_ontology_summary.md` (counts + hubs + orphans), `_ontology_triples.tsv` (flat for grep), and `_ontology_graph.html` (D3 force-directed, type-colored nodes, type filter checkboxes).

Querying:

```bash
python query_ontology.py "MyProject"          # show entity + outbound + inbound
python query_ontology.py --predicate hasPI  # all PI relationships
python query_ontology.py --type Grant       # all grants with email_count etc.
python query_ontology.py --orphans          # degree-0 nodes (likely stubs)
```

Sample output for a Person node — shows the grants where that person is PI (`hasPI`), their advisees (`advisedBy`), and collaborators.

### 5.2 Today.md as the entry point

`Today.md` has a strict structure:

1. **§ 1 Routing cheat-sheet** — table of "if you ask X, look here Y"
2. **§ 2 Active deadlines** — auto-collected from any entity page with `deadline: YYYY-MM-DD` in frontmatter
3. **§ 3 Project priority tiers** — manually edited (this is the only section the user touches regularly)
4. **§ 4 Recent activity (auto)** — last 7d vault edits + new source files added (between `<!-- BEGIN AUTO RECENT -->` markers, regenerated by `update_today.ps1`)
5. **§ 5 Outstanding follow-ups** — manual queue
6. **§ 6 Sessions / automation status** — table of all hooks/jobs with what + trigger
7. **§ 7 Quick commands** — the 5-6 most-used PowerShell commands

The Stop hook regenerates § 4 after every Claude Code session, so it's never stale.

### 5.3 Session digests

When a Claude Code session ends, the Stop hook receives `transcript_path` via stdin JSON. `digest_session.py`:

1. Parses the JSONL — for Claude Code: `type=user|assistant` with `message.content` blocks. For Codex: `type=response_item` with nested `payload.type=message|function_call|custom_tool_call`.
2. Counts: user messages, files Edited/Written/Read, Bash commands.
3. Sends top-30 user messages + last assistant text + tool signals to OpenRouter Gemini Flash with prompt: "summarize as JSON `{topic, goal, outcome, key_decisions, next, tags}`."
4. Appends a `## HH:MM-HH:MM [source] <topic> (sid: 8char)` section to `wiki/sources/Sessions YYYY-MM-DD.md`.
5. One-line entry to `wiki/log.md`.

Sessions <3 user messages are skipped. Cost per session: ~$0.001.

For Codex (no Stop hook), user runs `pwsh codex_digest.ps1` after each session — finds latest `~/.codex/sessions/*.jsonl` and runs the same digest.

### 5.4 Situation watch (research-note tracker)

The most LLM-heavy component. Every 2h:

1. Scan vault `wiki/sources/` and `wiki/.raw/` for **new or modified files** since `situation_eval`'s last-seen timestamp (tracked in a small SQLite table or JSON file).
2. Triage: score each new note by (a) entity matches against the ontology vocab (149 entities), (b) importance keywords ("deadline", "decision", "submitted", "rejected", "approved", "Co-PI", "defense", "R&R", "IRB approval", + Korean equivalents), (c) attachment count.
3. Top-N (default 10) → OpenRouter with a strict prompt: identify situational changes as JSON `{entity_label, change_type, new_value, evidence_quote, confidence, auto_applicable, reasoning}`.
4. Output to `wiki/situation/YYYY-MM-DD.md` with `[AUTO]` and `[REVIEW]` blocks plus a triage table.
5. Mark all evaluated note IDs in `situation_eval` so they don't re-LLM next run.

Auto-apply policy is conservative: `confidence ≥ 0.85` AND `change_type ∈ {deadline_update, status_update, progress_update}`. Everything else (role changes, new collaborators, new methods) waits for user review.

`apply_situation.py` reads the daily note, finds `[AUTO]` blocks, looks up the target entity page, upserts frontmatter (`deadline:` / `status:`), appends a `## Recent situation updates` body line with the evidence quote, logs to `wiki/log.md`, and finally rebuilds the ontology. Result: the network graph reflects new state within minutes.

### 5.5 Desktop organizer

When you save random files to your desktop, `organize_desktop.py` (every 2h, with `--apply`):

1. Lists Desktop root files only — never recurses into structured folders.
2. Skips: `credential.txt` and other secrets; `~$*` Word/Excel lock files; `desktop.ini`; files modified in the last 60 minutes (probably actively editing); dot-files; `*.lnk`/`*.crdownload`/`*.tmp`.
3. For each candidate: extracts text preview (PDF via pdfplumber, docx via python-docx, etc.), sends to LLM with the whitelist of destinations (`_archive`, `_projects`, `_writing`, `22_Grants`, `20_Advising`, `27_Media/_screenshots` …) and the ontology entity catalog.
4. LLM returns `{action, destination, destination_subpath, confidence, reason}`.
5. **Auto-move only at confidence ≥ 0.90** AND the destination is whitelisted. Everything else stays as REVIEW in the manifest.
6. Manifest: `Desktop\_organize_log\YYYY-MM-DD_HHmm.txt`. Plain text, three sections (Files moved / Proposed / Needs review), every move with FROM → TO + reason + confidence.
7. Every move appended to `Desktop\_organize_log\.history.jsonl` for `--undo <run-id>` reversibility.

Forbidden destination: `_secrets`. If the LLM ever proposes routing a file there, the script downgrades to `review_needed`.

### 5.6 /slides workflow

The user types `/slides <topic>` (or natural language "PT 만들어 줘 / make a deck about X"). The slash command at `~/.claude/commands/slides.md` instructs the agent to:

1. Pick a skill from cached templates at `Desktop\_tools\open-design-cache\skills\`. Cached from [`nexu-io/open-design`](https://github.com/nexu-io/open-design):
   - `magazine-web-ppt` (default, editorial magazine)
   - `html-ppt-knowledge-arch-blueprint` (research methodology / system architecture)
   - `html-ppt-course-module` (teaching / workshop)
   - `html-ppt-pitch-deck` (grant proposal / fundraising)
   - `html-ppt-product-launch` (tool/feature reveal)
2. Read `SKILL.md` + `references/*.md` + `assets/template.html` (or `example.html`) — these are inert markdown/HTML specs, no code execution.
3. Pull vault content for the topic: `wiki/entities/<topic>.md` → `wiki/concepts/` → `query_ontology.py "<topic>"` → optional web research when vault is thin.
4. Propose 8-15 slide outline first; user OKs.
5. Generate single-file self-contained HTML at `Desktop\_PTs\<YYYY-MM-DD>_<topic-slug>\index.html` — all CSS/JS inline, fonts from CDN.
6. Append entry to `wiki/sources/Decks <year>.md`.

Cost: ~3-5 minutes generation, $0.005-0.02 per deck depending on length.

## 6. Daily flow (what it looks like in practice)

**Morning** — open vault, look at `Today.md`. § 2 shows current deadlines (D-counter), § 3 shows project priority tiers, § 4 shows what changed in the last 7 days (and what new research notes / source files were added overnight).

**During work** — start a Claude Code session anywhere on your machine. CLAUDE.md auto-loads, MEMORY.md auto-loads, you can immediately ask "what's the status of X?" or "make a slide deck about Y". The agent has full context without re-explanation.

**Every 2 hours (background)** — tracker fires. New source files in `wiki/sources/` get scanned, important changes proposed in `wiki/situation/<date>.md`, ontology rebuilt, Today.md refreshed, Desktop loose files filed away.

**End of session** — Stop hook runs digest_session.py, appends a structured entry to `wiki/sources/Sessions <date>.md`. The next session you open can `Read` it to remember what you decided.

**End of week** — review `wiki/situation/<date>.md` files for proposed changes, apply via `apply_situation.py`, glance at `wiki/sources/Sessions <date>.md` for a record of what you actually built.

## 7. Cost & performance

| Component | Frequency | Cost |
|---|---|---|
| Daily tracker (collectors only, no LLM) | every 2h | ~free, ~30s wall time |
| Ontology rebuild | every 2h | ~free, ~3s |
| Situation watch (LLM) | every 2h, top-10 of new notes | ~$0.001-0.005/run |
| Session digest (LLM) | every session end | ~$0.001/session |
| Desktop organizer (LLM) | every 2h, ~5-15 loose files/day | ~$0.001/day |
| /slides generation (LLM via Claude Code itself) | on demand | ~$0.005-0.02/deck |
| **Total** | | **~$0.02-0.05/day** with Gemini Flash via OpenRouter |

Switch to `anthropic/claude-3.5-haiku` for ~10× quality at ~10× cost (still under $0.50/day).

## 8. Privacy and safety

- **Vault contains aggregates only**, not raw sensitive content. Email bodies, IRB participant data, and credential files **never enter the vault**. Source notes added by you are visible to the LLM during situation_watch summarization, so don't paste sensitive PII into research notes you want auto-processed — keep those in a separate folder excluded from the watcher.
- **Desktop organizer** has explicit `_secrets` ban (LLM-recommended secrets routing is downgraded to manual review). It also skips files modified in the last 60 minutes (probably in active edit), Word/Excel lock files, and any `desktop.ini` / `thumbs.db`.
- **Undo support** — every desktop move is logged to `_organize_log/.history.jsonl`; `python organize_desktop.py --undo <run-id>` reverses an entire run.
- **Apply policy** for situation_watch is conservative — only `deadline_update / status_update / progress_update` with confidence ≥ 0.85 auto-apply. Role changes, new collaborators, funding decisions all stay as REVIEW.
- **Local-first** — vault is plain markdown, ontology is plain JSON-LD. No proprietary format, no sync requirement. Works offline (LLM steps gracefully skipped without network).
- **OpenRouter key** stored only in `_secrets/` outside the vault, read at runtime. Never committed.

## 9. Customization

### Add a new entity type
1. Add a row to `wiki/concepts/Vault Ontology.md` § 1 (Entity types).
2. Add type detection rule in `build_ontology.py`'s `infer_type()` (path-based fallback or `type:` frontmatter).
3. Add to `query_ontology.py`'s type filter if you want `--type` lookup.

### Add a new relation
1. Add a row to `wiki/concepts/Vault Ontology.md` § 2 (Relation types) with cue phrases.
2. Add an entry to `RELATION_RULES` dict in `build_ontology.py` with cue regexes + subject_types + object_types.
3. Future ontology rebuilds pick it up automatically.

### Add a new slide skill
```bash
gh api "repos/nexu-io/open-design/contents/skills/<skill-id>/SKILL.md" --jq '.content' | base64 -d > Desktop\_tools\open-design-cache\skills\<skill-id>\SKILL.md
gh api "repos/nexu-io/open-design/contents/skills/<skill-id>/example.html" --jq '.content' | base64 -d > Desktop\_tools\open-design-cache\skills\<skill-id>\example.html
```
Then add a routing rule to `~/.claude/commands/slides.md` § 2.

### Add a new collector to the daily tracker
Add a new section in `daily_tracker.ps1` after the existing § 1-10 blocks. Pattern:
```powershell
$lines += ''
$lines += '## My new collector'
$lines += ''
$out = & <command> 2>$null
if ($out) { $lines += $out } else { $lines += '- (no new <thing>)' }
```

### Replace OpenRouter with another LLM provider
All scripts read `OPENROUTER_URL` and `MODEL` constants at the top. Swap to `https://api.anthropic.com/v1/messages` (with header changes) or local Ollama (`http://localhost:11434/api/chat`) — keep the response_format JSON contract the same.

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `Today.md § Recent` not updating | Stop hook not configured or PowerShell path wrong | Check `~\.claude\settings.json`; run `powershell -File save_session.ps1` manually |
| Tracker fires but no `activity/<date>.md` | scheduled task running with wrong user / no profile | `schtasks /Query /TN ResearchAssistantTracker /V /FO LIST`, check Logon Mode |
| `query_ontology.py` returns "no matches" | label case-mismatch or page lacks frontmatter `type:` | grep the entity, add `type: project` to its frontmatter, rebuild ontology |
| Situation watch outputs `(LLM error)` | OpenRouter key missing/expired or rate-limited | `cat _secrets/openrouter.txt`, test with `curl ...models` |
| Wrong file moved by organize_desktop | overconfident LLM judgment | `python organize_desktop.py --undo <run-id>` from manifest, raise `AUTO_THRESHOLD` |
| Slides skill missing | not cached locally | `gh api repos/nexu-io/open-design/contents/skills/<id>/SKILL.md ...` |

## 11. Ontology as event-hub (the unifying spine)

Most of the components above produce daily markdown files (`activity/<date>.md`, `situation/<date>.md`, `sources/Sessions <date>.md`). Each is queryable, but they live in separate folders. To make "show me everything about MyProject in the past 7 days" answerable in one query, the ontology absorbs **selected events as first-class nodes**.

### What gets noded vs what stays as property

| Event | Where it lives | Becomes ontology node? |
|---|---|---|
| Daily activity log | `wiki/activity/<date>.md` | No — too noisy, file-write churn would dominate |
| Situation change | `wiki/situation/<date>.md` | No — applied changes mutate the target entity's frontmatter (`deadline:`, `status:`) and that's already picked up |
| Desktop file move | `Desktop\_organize_log\<run>.txt` | No — pure file-system action, no semantic relation |
| **Session digest** | `wiki/sources/Sessions <date>.md` | **Yes — Session node + `aboutEntity` edges** |
| **Slide deck generation** | `wiki/sources/Decks <year>.md` | **Yes — Deck node + `aboutEntity` edges** |

Sessions and Decks are the events researchers most want to query historically: *"all sessions about CSCL last semester"*, *"every deck I made about the AERA-NSF proposal"*. Activity logs and organize-runs are operational ephemera; their value lives in the daily file, not in cross-time joins.

### Three new entity types

- **Session** — `vault:session/<YYYY-MM-DD>-<HHMM>-<source>-<sid8>`. Properties: `date`, `ts_start`, `ts_end`, `source` (claude/codex), `sid` (8-char), `topic`. One per `## ` heading in `wiki/sources/Sessions YYYY-MM-DD.md`.
- **Deck** — `vault:deck/<YYYY-MM-DD>-<topic-slug>`. Properties: `date`, `skill` (open-design skill id), `topic`, `summary`. One per row in `wiki/sources/Decks YYYY.md`.
- **Fold** — `vault:fold/<sessions|decks>-<YYYY-MM>`. A monthly compaction node that holds all Session/Deck items older than a threshold (default 30 days). Members get a `partOfFold` edge. Visualizations can hide the underlying nodes by default.

### Three new relations

- **`aboutEntity`** — Session/Deck → Project/Grant/Concept/Course/Manuscript/Person/Lab. Auto-extracted from the section body's `[[wikilinks]]` and word-boundary matches against ontology labels.
- **`producedBy`** — Session/Deck → Person. The user (or other contributor). Currently inferred as the vault owner.
- **`partOfFold`** — Session/Deck → Fold. Set during the age-based compaction pass.

### Why fold compaction matters

Without retention, every 2-hour tick adds Session nodes indefinitely. After a year that's 1500-3000 nodes just from session digests, drowning out the 200 substantive entities. Fold compaction:

1. After main extraction, scan all Session and Deck nodes.
2. Group by year-month. Anything older than 30 days gets a `partOfFold` edge to `vault:fold/<sessions|decks>-<YYYY-MM>`.
3. Mark the original node `properties.folded = true` so the D3 viz can filter it out by default.
4. The Fold node itself carries `member_count` for stats.

Effect: the live graph stays roughly stable in size (200-300 nodes) regardless of how long the system runs, while the full history remains queryable by un-hiding folded nodes.

### Querying the event-hub

```bash
# All sessions about MyProject in the last month
python query_ontology.py "MyProject" | grep -A 40 "<-aboutEntity"

# All decks (any topic, any time)
python query_ontology.py --type Deck

# Everything that touched Bayesian Causal Forest (sessions + decks + projects)
python query_ontology.py "Bayesian Causal Forest"

# Total work artifacts about a project: count of aboutEntity edges
python query_ontology.py --predicate aboutEntity | grep MyProject | wc -l
```

The vault-text-as-snapshot model still works for entities, but Sessions/Decks add a temporal layer where the ontology now answers *"what did I produce about X, and when?"* — a question the flat vault structure couldn't reach.

### Tradeoff for guide adopters

If you're starting fresh, decide:
- **Light** (this guide's default): Sessions + Decks as nodes, 30-day fold. Keeps graph navigable, supports historical queries on the two artifact types most worth tracking.
- **Heavy**: also node SituationChange, OrganizedFile, dailyActivitySummary. Graph triples in a year reach ~50K. You'll need a real triple store (e.g. Apache Jena, Neo4j) and the D3 viz becomes inadequate. Useful only if you genuinely need cross-event SPARQL ("which projects had a deadline-update AND a session in the same week?"). Most researchers don't.
- **None**: keep the original snapshot-only ontology. Simplest, but you lose the unified-history query.

The light setting is the best fit for the audience this guide targets: a single researcher who wants to retrieve historical work without standing up an RDF stack.

## 12. Why this works (design notes)

- **Single entry point removes search.** Researchers waste 30+ min/day re-finding context. `Today.md` is the universal landing — every session, every agent, every "where was I?" question starts here.
- **Persistent memory beats prompt engineering.** Putting facts about your projects in `~\.claude\projects\<machine>\memory\` means every session loads them automatically; no re-explaining "I'm an academic researcher who works on…".
- **Ontology over flat tags.** A type-and-relation graph (Project hasPI Person, Project usesMethod Concept, Person advises Person) is queryable in ways flat tags aren't. `who is the PI of every grant I'm on?` is one SPARQL/CLI query.
- **LLM at the edges, not the center.** The orchestrator is plain Python/PowerShell. LLM is called only at decision points (situation judgment, file routing, slide generation). Most of the system runs free, and the LLM cost is bounded by triage filters.
- **Conservative auto-apply.** Every LLM-proposed change has a confidence score and a `[REVIEW]` fallback. Auto-applies only the boring cases (date updates, status flips). The system never silently rewrites your interpretive content.
- **Reversible operations.** Desktop moves have undo. Frontmatter updates leave audit trail in `wiki/log.md`. Ontology is regenerated, not edited — you can always rebuild from source.
- **Composable.** Every script is a single file. Each does one thing. The tracker is a 200-line orchestrator. You can fork any piece without touching the rest.

## 13. Repository layout (suggested)

```
research-assistant-system/
├── README.md             ← this guide
├── ObsidianVault/
│   ├── CLAUDE.md
│   ├── wiki/
│   │   ├── Today.md      (template)
│   │   ├── concepts/
│   │   │   └── Vault Ontology.md
│   │   └── ...
│   └── scripts/
│       ├── daily_tracker.ps1
│       ├── build_ontology.py
│       ├── query_ontology.py
│       ├── digest_session.py
│       ├── situation_watch.py
│       ├── apply_situation.py
│       ├── organize_desktop.py
│       ├── update_today.ps1
│       ├── save_session.ps1
│       ├── codex_digest.ps1
│       ├── collect_github.ps1
│       ├── collect_calendar.ps1
│       ├── collect_notes.ps1
│       └── collect_social.ps1
├── claude-config/
│   ├── settings.json     (Stop hook excerpt)
│   └── commands/
│       ├── slides.md
│       └── recall.md
└── examples/
    ├── entity-page-template.md
    ├── concept-page-template.md
    └── sample-ontology-graph.html
```

## 14. Acknowledgements

- [claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) — the seed vault structure and the LLM Wiki Pattern.
- [nexu-io/open-design](https://github.com/nexu-io/open-design) — slide-deck skill specs (magazine / pitch / blueprint / course / launch). Cached SKILL.md + template HTML referenced read-only; no code from open-design runs in this system.
- BERTopic, sentence-transformers — for the topic-clustering layer that complements the ontology when categorical analysis is needed.

## 15. Design rationale and evidence base

Each decision below is deliberate. This section ties the choices to published work so you can evaluate — or challenge — them rather than take them on faith. The beginner tutorial omits this layer to stay actionable; it lives here.

**Single entry point over search.** `Today.md` exists because resuming an interrupted task is expensive. In Mark, Gudith, and Klocke's (2008) field study of information workers, people who were interrupted compensated by working faster but did so under measurably higher stress, frustration, and effort; related work in the same research program puts the time to fully resume an interrupted task at roughly 20+ minutes. A fixed landing page removes the repeated "where did I leave off?" search at every context switch.

**Persistent memory over re-prompting.** Putting durable facts in `~\.claude\projects\<machine>\memory\` mirrors the memory-tiering idea formalized in MemGPT, which pages information between a small in-context window and a larger external store so an agent retains knowledge across sessions (Packer et al., 2023). The situation-watch loop — observe new notes, synthesize a judged change, write it back — is the observe → reflect → retrieve cycle that let the agents in Park et al. (2023) stay coherent over long horizons.

**Ontology over flat tags.** A typed entity–relation graph (Project `hasPI` Person, Person `advisedBy` Person) answers queries that flat tags cannot ("who is the PI of every grant I'm on?"). That is the defining advantage of the knowledge-graph data model surveyed by Hogan et al. (2021), and the reason the export uses standard vocabularies — JSON-LD (W3C, 2020) with FOAF and SKOS terms and schema.org types — instead of a bespoke format. The interactive graph is drawn with D3 (Bostock, Ogievetsky, & Heer, 2011).

**LLM at the edges, not the center.** The orchestrator is plain Python/PowerShell; the model is invoked only at judgment points (situation triage, file routing). Using a strong model to score or classify candidates is the LLM-as-judge pattern, which Zheng et al. (2023) found agrees with human preference over 80% of the time on open-ended tasks — sufficient for "is this a deadline change?" while staying cheap and bounded by triage filters. The same paper documents position, verbosity, and self-enhancement biases, which is why auto-apply stays conservative (§5.4, §8).

**Grounding generation in your own corpus.** `/slides` pulls vault entities and ontology facts before generating, so the deck is conditioned on retrieved, attributable content rather than the model's parametric memory alone — the retrieval-augmented generation approach of Lewis et al. (2020), which improves factuality and supplies provenance for what the output claims.

**Notes as the substrate.** The hand-written entity pages are atomic, densely cross-linked notes in your own words — the Zettelkasten practice systematized for modern tools by Ahrens (2017). The richer the `[[wikilink]]` cross-referencing, the better the ontology reconstructs relationships (§5.1). When categorical structure is needed beyond the ontology, topic clustering uses Sentence-BERT embeddings (Reimers & Gurevych, 2019) with BERTopic (Grootendorst, 2022).

## 16. References and further reading

**Primary literature**

1. Mark, G., Gudith, D., & Klocke, U. (2008). The cost of interrupted work: More speed and stress. *Proceedings of CHI 2008*, 107–110. <https://ics.uci.edu/~gmark/chi08-mark.pdf>
2. Packer, C., Fang, V., Patil, S. G., Lin, K., Wooders, S., & Gonzalez, J. E. (2023). MemGPT: Towards LLMs as operating systems. *arXiv:2310.08560*. <https://arxiv.org/abs/2310.08560>
3. Park, J. S., O'Brien, J., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative agents: Interactive simulacra of human behavior. *Proceedings of UIST 2023*. <https://arxiv.org/abs/2304.03442>
4. Hogan, A., Blomqvist, E., Cochez, M., et al. (2021). Knowledge graphs. *ACM Computing Surveys, 54*(4), Article 71. <https://doi.org/10.1145/3447772>
5. Zheng, L., Chiang, W.-L., Sheng, Y., et al. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. *Advances in Neural Information Processing Systems 36 (NeurIPS 2023)*. <https://arxiv.org/abs/2306.05685>
6. Lewis, P., Perez, E., Piktus, A., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems 33 (NeurIPS 2020)*. <https://ai.meta.com/research/publications/retrieval-augmented-generation-for-knowledge-intensive-nlp-tasks/>
7. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *Proceedings of EMNLP-IJCNLP 2019*, 3982–3992. <https://aclanthology.org/D19-1410/>
8. Grootendorst, M. (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure. *arXiv:2203.05794*. <https://arxiv.org/abs/2203.05794>
9. Bostock, M., Ogievetsky, V., & Heer, J. (2011). D³: Data-driven documents. *IEEE Transactions on Visualization and Computer Graphics, 17*(12), 2301–2309. <https://doi.org/10.1109/TVCG.2011.185>
10. Ahrens, S. (2017). *How to take smart notes*. Sönke Ahrens. <https://www.soenkeahrens.de/en/takesmartnotes>

**Tools and standards**

11. Claude Code documentation. <https://code.claude.com/docs/en/overview>
12. Obsidian. <https://obsidian.md>
13. OpenRouter API documentation. <https://openrouter.ai/docs>
14. W3C (2020). *JSON-LD 1.1: A JSON-based serialization for linked data*. <https://www.w3.org/TR/json-ld11/>
15. W3C (2009). *SKOS Simple Knowledge Organization System reference*. <https://www.w3.org/TR/skos-reference/>
16. *FOAF vocabulary specification*. <http://xmlns.com/foaf/spec/>
17. *schema.org vocabulary*. <https://schema.org/>

---

_This guide describes a working system in production for a single researcher's portfolio (dozens of projects and grants). Numbers reported (~197 ontology nodes, 2200+ edges, ~$0.02-0.05/day LLM cost) are real measurements as of 2026-05-02. Adapt thresholds and skill choices to your scale._
