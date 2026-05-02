---
type: concept
title: "Research Assistant System — Beginner Tutorial"
subtitle: "Obsidian + Claude Code · 7-Day Setup Guide"
author: "Jewoong Moon"
affiliation: "The University of Alabama"
contact: "jmoon19@ua.edu"
created: 2026-05-02
updated: 2026-05-02
audience: beginner
tags:
  - guide
  - tutorial
  - beginner
status: active
---

{{DIAGRAM:hero}}

# A Research Assistant System for PhDs and Researchers — Beginner Guide

> **Who is this for?** You're a PhD student, early-career faculty, or researcher juggling *dozens of projects scattered across folders*; you keep searching *"when was that grant deadline again?"*; and although you use Claude Code/ChatGPT, you find yourself *re-explaining the same context every session*. This guide is for you.
>
> **End state**: every project, methodology, student, and grant lives in a single searchable knowledge graph. The AI auto-records what you do every session. New information triggers automatic graph updates.

---

## Why bother?

Your current setup probably looks like this:

{{DIAGRAM:before-after}}

**Left**: PDFs, docx, and PNGs scattered across the desktop. 16 project folders. *"Where did I write down that method explanation?"* — daily search.

**Right**: every project organized as a vault entity page. An automated tracker processes new notes. Asking the AI *"Tell me about Project X"* yields full context in one line.

Follow this guide to the end and you reach the right side. **1-2 hours per day for 7 days.**

---

## 0. Glossary — 7 terms used throughout

| Term | One-line definition | Analogy |
|---|---|---|
| **Vault** | An Obsidian notes store = a single folder full of `.md` files | "The bookshelf with all my notes" |
| **Entity page** | A single note for one thing — person, project, concept (`wiki/entities/Project A.md`) | One Wikipedia article |
| **Frontmatter** | YAML metadata between `---` lines at the top of a markdown file. The "label" area the computer reads | Library catalog card inside the cover |
| **Wikilink** | Obsidian's `[[Page Name]]` syntax. Auto-tracked, auto-searchable | Hyperlink within a wiki |
| **Hook** | A command that auto-fires the moment a specific event happens | Doorbell — auto-rings when someone arrives |
| **Ontology** | A structured graph of your vault expressed as **types** and **relations** | Family tree + org chart, combined |
| **API key** | Secret string that authenticates you when calling an external LLM service | Library card you show when borrowing |

> 💡 **Concept-to-file mapping**: each entity is a single `.md` file. Frontmatter declares its *type* (`type: project`). Wikilinks declare *relations* to other entities. These three together let the system auto-build your ontology.

---

## 0.5. AI Agents — Claude Code vs Codex

This system uses two AI coding agents **complementarily**. Both are LLM-backed, but **what each does best** and **how you control them** differ.

{{DIAGRAM:agents}}

### Two agents, two roles

**Claude Code** (Anthropic) — *primary engineering agent*
- Deep vault integration: Stop hooks for auto-session-recording, slash commands like `/slides` and `/recall`
- Long context window (200K-1M tokens) — can pull your whole vault into context
- Strengths: multi-step reasoning, careful file edits, vault navigation
- Where: directly reads/writes every file in the vault

**Codex** (OpenAI) — *secondary engineering agent*
- Sessions stored at `~/.codex/sessions/` (rollout JSONL). No Stop hook — manual `pwsh codex_digest.ps1` after each session
- Strengths: fast code generation, image generation, reasoning-mode
- Where: green-field code, cross-checking when Claude is stuck, prototypes

### When to use which

| Situation | Pick |
|---|---|
| **Writing/editing vault pages** | **Claude Code CLI** — Stop hook auto-records |
| **New scripting** (Python/PowerShell) | Either |
| **Multi-file refactor** | **Claude Code** — multi-step edits stable |
| **Second opinion when stuck** | Both, compare answers |
| **Image / mockup generation** | **Codex** — has image_generation tool |
| **Quick chat / "what is this?"** | **Claude Desktop app** (GUI, MCP) |
| **Auto session digest** | **Claude Code** (auto). Codex is manual |

### CLI control — the 5 essentials

**(1) Where to run for auto-context**
```powershell
cd C:\Users\<you>\ObsidianVault
claude                              # Claude Code CLI
# or
codex                               # Codex CLI
```
Both agents walk *up the parent chain* looking for:
- Claude Code: `CLAUDE.md`
- Codex: `AGENTS.md`

So opening either inside your vault means *"tell me about project X"* gets answered immediately.

**(2) Hook registration — Claude Code only**

`~\.claude\settings.json`:
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "powershell.exe -File <vault>\\scripts\\save_session.ps1 -Source claude"
        }]
      }
    ]
  }
}
```

Available events: `Stop`, `SessionStart`, `PostToolUse`, `PreToolUse`, `UserPromptSubmit`. We only use `Stop`.

**(3) Slash Commands — Claude Code only**

Create `~\.claude\commands\<name>.md` and call as `/<name> <args>`. Example: `/slides ProjectA`.

**(4) Memory — Claude Code's auto-context**

`~\.claude\projects\<machine>\memory\MEMORY.md` is auto-injected at every session start.

**(5) Codex post-session digest — three approaches**

> 💡 **Correction**: Codex CLI has no event-based hook system. It *does* support schedule-based cron at `~/.codex/automations/`. Three ways to get the same effect:

**Method A — manual**: `pwsh C:\Users\<you>\ObsidianVault\scripts\codex_digest.ps1`

**Method B — shell wrapper**:
```powershell
function cdx {
  codex @args
  pwsh "$env:USERPROFILE\ObsidianVault\scripts\codex_digest.ps1"
}
```

**Method C — Codex automation**:
```toml
# ~/.codex/automations/vault-digest/automation.toml
version = 1
id = "vault-digest"
kind = "cron"
prompt = "Run: pwsh C:\\Users\\<you>\\ObsidianVault\\scripts\\codex_digest.ps1"
status = "ACTIVE"
rrule = "FREQ=HOURLY;INTERVAL=2"
```

> 💡 **Bottom line**: ~95% interchangeable. Same vault, same entity pages.

### Desktop app differences

**Claude Desktop**: no hooks, has MCP, no slash commands. Recommended for quick chat.
**Codex Desktop**: no hooks, IDE-integrated. Recommended for in-IDE coding.

> ⚠️ **Hook-required automation must use CLI**.

---

## 1. The core idea — a 3-layer second brain

{{DIAGRAM:mental-model}}

**Layer 1 — Project knowledge (`wiki/entities/`, `wiki/concepts/`)**: notes you write yourself. *Permanent* asset.

**Layer 2 — Activity log (`wiki/activity/`, `wiki/situation/`, `wiki/sources/Sessions YYYY-MM-DD.md`)**: auto-generated daily snapshots.

**Layer 3 — AI memory (`~/.claude/projects/<machine>/memory/`)**: small files Claude Code auto-loads at session start.

> 💡 **One-liner to remember**: *I write (Layer 1) → the computer refreshes every 2h (Layer 2) → AI auto-reads next session (Layer 3).*

---

## 2. Automation flow — "what happens every 2 hours"

{{DIAGRAM:tracker-flow}}

A **Windows scheduled task** (or macOS launchd, Linux cron) runs every 2 hours. The script:

1. Scans newly added / modified files
2. Collects side-channel signals: git, GitHub, calendar
3. Sends note changes to an LLM that judges *"what changed"*
4. **Rebuilds the ontology graph**
5. Aggregates results into `Today.md`

Cost: ~$0.001-0.005 per run. 12 runs/day = **$0.02-0.05/day** = $1-2/month.

---

## 3. Prerequisites

{{DIAGRAM:checklist}}

**Required from Day 1**:

- [ ] **Obsidian** ([obsidian.md](https://obsidian.md), free)
- [ ] **Claude Code** ([claude.com/claude-code](https://claude.com/claude-code))
- [ ] **Python 3.11+**
- [ ] Basic terminal skills

**Required from Day 4 onward**:
- [ ] **OpenRouter API key** ([openrouter.ai](https://openrouter.ai), $5 lasts months)
- [ ] **`gh` CLI** ([cli.github.com](https://cli.github.com)) — optional

> ⚠️ **This guide is Windows-first**. macOS / Linux work with minor path tweaks.

---

## 3.5. CLI Installation — Claude Code & Codex

### Claude Code (Anthropic) — primary agent

**Prerequisites**: Anthropic subscription · Node.js 18+

**Windows**: download the .exe from <https://claude.com/claude-code> → install → `claude --version` → `claude` (browser auth opens)

Or via npm:
```powershell
npm install -g @anthropic-ai/claude-code
```

**macOS**:
```bash
brew install --cask claude-code
# or
npm install -g @anthropic-ai/claude-code
```

**Linux**: `npm install -g @anthropic-ai/claude-code`

**First-run auth**: `claude` → browser auto-opens for Anthropic login → token saved to `~/.claude/auth.json`.

```powershell
claude /help          # available slash commands
claude /status        # current model / auth / context
```

### Codex (OpenAI) — secondary agent (optional)

**Prerequisites**: ChatGPT subscription · Node.js 18+

**Windows**: <https://chatgpt.com/codex> installer or `npm install -g @openai/codex`
**macOS**: `brew install codex` or npm
**Linux**: `npm install -g @openai/codex`

**First-run auth**: `codex` → browser → OpenAI login → token saved to `~/.codex/auth.json`.

### Both CLIs together

```powershell
cd C:\Users\<you>\ObsidianVault
claude     # primary
codex      # secondary (optional)
```

> 💡 **Both agents see the same vault.** Claude Code reads `CLAUDE.md`, Codex reads `AGENTS.md`. Put both files in your vault for symmetric context.

<div class="prompt-box">
<div class="prompt-label"><span class="prompt-icon">💬</span> Prompt for Claude Code users — adding Codex</div>
<pre>My OS is Windows / macOS / Linux. Help me install Codex CLI through to first-run auth.

1. Verify Node.js 18+
2. npm install -g @openai/codex (or OS-recommended)
3. codex --version
4. codex → browser login

Then create ~/.codex/AGENTS.md with one line:
"My vault is at C:\Users\<me>\ObsidianVault\. Always read wiki/Today.md before starting any work."</pre>
</div>

### Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `claude: command not found` | npm global bin not in PATH | Add `npm config get prefix` + `/bin` to PATH |
| Browser doesn't open during auth | WSL / SSH | `claude --no-auto-open`, paste URL manually |
| `EACCES` permission denied | npm global install perm | sudo or change npm prefix |
| `npm install -g` fails on Windows | No Node | `winget install OpenJS.NodeJS` |
| Console encoding issues | code page | `chcp 65001` for UTF-8 |

> ⚠️ **Subscription vs API key**: CLI auth uses **subscription** (browser). **OpenRouter API key is separate** (Day 6 — for the automated LLM judgment, NOT CLI auth).

---

## Day 1 — Create your vault

**Today's goal**: create an empty Obsidian vault and hand-write an entity page for your most active project. No automation yet.

### Step 1.1 — Create the vault

Launch Obsidian → "Create new vault" → name `ResearchVault`, location `C:\Users\<you>\ObsidianVault\`.

### Step 1.2 — Folder structure

```
ObsidianVault/
└── wiki/
    ├── entities/        ← one page per project / person / grant
    ├── concepts/        ← one page per method / theory
    ├── sources/         ← raw documents / digests / session logs
    └── (activity/, situation/ are auto-created later)
```

<div class="prompt-box">
<div class="prompt-label"><span class="prompt-icon">💬</span> Or drop into Claude Code/Codex CLI</div>
<pre>Create a wiki/ folder inside `C:\Users\<me>\ObsidianVault\` with three subfolders: entities/, concepts/, sources/. Put a one-line README.md in each explaining what it holds.</pre>
</div>

### Step 1.3 — Your first entity page

Pick your most active project. Example uses fictional *Project A*:

```markdown
---
type: project
title: "Project A"
status: active
tier: 2
deadline: 2026-08-15
related:
  - "[[<my name>]]"
  - "[[Method A]]"
---

# Project A

(One-sentence project description.)

- **PI**: [[<my name>]]
- **Methods**: [[Method A]], [[Method B]]
- **Status**: pilot N participants in progress, external grant X under review.

## Open issues
- Core component accuracy at X% — needs more validation.
```

> 💡 **Frontmatter anatomy**: the area between top `---` lines. Computer-read *labels*, separate from freeform body.
> - `type: project` — required for ontology recognition
> - `status: active` / `tier: 2` — auto-collected by Today.md
> - `deadline: YYYY-MM-DD` — auto-computed D-counter
> - `related: [...]` — wikilink list, becomes `relatedTo` relation

> 💡 **How wikilinks behave**: `[[Method A]]` auto-renders as link, tracks as stub if target missing, shows as graph edge.

<div class="prompt-box">
<div class="prompt-label"><span class="prompt-icon">💬</span> Drop into Claude Code/Codex CLI</div>
<pre>My most active project is [PROJECT NAME]. Build wiki/entities/[PROJECT NAME].md following the Day 1 step 1.3 template:
- frontmatter: type: project, status: active, tier: 2, deadline: [YYYY-MM-DD]
- related: my name + 1-2 frequently used methods (as wikilinks)

Body: one-sentence description, PI / Methods / Status bullets, ## Open issues section.</pre>
</div>

### Step 1.4 — Repeat for one or two more

Add an advisee, a frequently-used method, an in-progress grant. *At least 3-4 entities* for the next-day automation to have a meaningful graph.

> ✅ **Day 1 check**: Obsidian's graph view (Ctrl+G) shows your nodes as a small constellation.

---

## Day 2 — Today.md (single entry point)

**Today's goal**: build the *one page* you read every day.

### Step 2.1 — Create `wiki/Today.md`

```markdown
---
type: meta
title: "Today — Single Entry Point"
---

# Today — Single Entry Point

> **Always start here.** Read first every session.

## 1. Where to ask what

| If you need… | Look here |
|---|---|
| **"My project X — design / theory / methods"** | `wiki/entities/<X>.md` |
| **"Who advises whom; grants where I'm PI"** | [[<my name>]] |
| **"Methodology"** | `wiki/concepts/` |
| **"What do I need to do today?"** | This page § 2-3 |

## 2. Active deadlines

| Deadline | Item | D- |
|---|---|---|
| YYYY-MM-DD | [[Grant Name]] submission | D-XX |

## 3. Active project priorities

### Tier 1 — Submit-imminent
- [[Project A]] — one-line status

### Tier 2 — Active development
- [[Project B]] — one-line status

### Tier 3 — Backlog
- [[Project C]]

## 4. Recent activity (auto-updated)
<!-- BEGIN AUTO RECENT -->
(filled automatically on Day 4)
<!-- END AUTO RECENT -->

## 5. Quick commands
(added Day 4-7)
```

<div class="prompt-box">
<div class="prompt-label"><span class="prompt-icon">💬</span> Drop into Claude Code/Codex CLI</div>
<pre>Build wiki/Today.md from the Day 2 template. Fill § 2 and § 3:
- Deadline: [grant name] [YYYY-MM-DD]
- Tier 1: [project nearing deadline]
- Tier 2: [1-3 active-development projects]
- Tier 3: [backlog projects]

Leave BEGIN/END AUTO RECENT markers in § 4 alone — Day 4 fills those. Then walk me through Pinning Today.md in Obsidian.</pre>
</div>

### Step 2.2 — Pin in Obsidian

Right-click `Today.md` → "Pin".

> ✅ **Day 2 check**: every morning, the first page you see is `Today.md`.

---

## Day 3 — Connect Claude Code + auto session log

### Step 3.1 — User-level CLAUDE.md

Create `C:\Users\<you>\CLAUDE.md`:

```markdown
# User-level Claude Code instructions

## On every session start
1. Read `C:\Users\<you>\ObsidianVault\wiki\Today.md` first.
2. Auto-memory at `~\.claude\projects\<machine>\memory\MEMORY.md` is auto-injected.
3. Prefer existing vault content over reasoning from scratch.

## Knowledge locations
| Question type | Where |
|---|---|
| Project design / methods / status | `wiki/entities/<project>.md` |
| Methodology / theory | `wiki/concepts/` |
| Recent activity | `wiki/activity/<date>.md` |

## User style
- Reply in English (or Korean — user is bilingual).
- Short and direct.
```

<div class="prompt-box">
<div class="prompt-label"><span class="prompt-icon">💬</span> Drop into Claude Code/Codex CLI</div>
<pre>Create `C:\Users\<me>\CLAUDE.md` from the Day 3 step 3.1 template:
- "On every session start" section
- "Knowledge locations" table
- "User style" (concise, direct)

My vault path: C:\Users\<me>\ObsidianVault\</pre>
</div>

### Step 3.2 — Register the session-recording hook

> 💡 **What's a hook?** Claude Code auto-runs commands when specific events fire. The **`Stop`** hook fires the moment a session ends.

`~\.claude\settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"C:\\Users\\<you>\\ObsidianVault\\scripts\\save_session.ps1\" -Source claude"
          }
        ]
      }
    ]
  }
}
```

### Step 3.3 — Minimal save_session.ps1

```powershell
$VaultRoot = 'C:\Users\<you>\ObsidianVault'
$LogFile   = Join-Path $VaultRoot 'wiki\log.md'

$stdin = [Console]::In.ReadToEnd()
$session = if ($stdin) { $stdin | ConvertFrom-Json } else { @{} }
$sid = if ($session.session_id) { $session.session_id.Substring(0, 8) } else { '--------' }

$stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm')
$line  = "- $stamp [claude $sid] session ended"

if (-not (Test-Path $LogFile)) { New-Item $LogFile -ItemType File -Force | Out-Null }
Add-Content -Path $LogFile -Value $line -Encoding UTF8
```

<div class="prompt-box">
<div class="prompt-label"><span class="prompt-icon">💬</span> Drop into Claude Code/Codex CLI — full Day 3 hook setup</div>
<pre>Set up Day 3 steps 3.2-3.3:

1. Add a Stop hook in `~\.claude\settings.json` (create if missing). Command:
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\<me>\ObsidianVault\scripts\save_session.ps1 -Source claude

2. Create `C:\Users\<me>\ObsidianVault\scripts\save_session.ps1`. Behavior:
   - Read JSON on stdin from the Stop hook
   - Append "- YYYY-MM-DD HH:mm [claude SID8] session ended" to wiki\log.md

Watch out for Windows backslash escaping in JSON.</pre>
</div>

### Step 3.4 — Verify

Open a Claude session, ask about your project, end the session. `wiki/log.md` should have a new line.

> ✅ **Day 3 check**: Claude already knows your project + log line written.

> 💡 **🛠 Customizing — other hooks**: Claude Code has `SessionStart`, `PostToolUse`, `UserPromptSubmit`, etc. Document changes in `wiki/sources/My Hook Setup.md`.

---

## Day 4 — The every-2-hour automated tracker

### Step 4.1 — `daily_tracker.ps1`

```powershell
$VaultRoot = 'C:\Users\<you>\ObsidianVault'
$ActivityDir = Join-Path $VaultRoot 'wiki\activity'
$today = (Get-Date).ToString('yyyy-MM-dd')
$note  = Join-Path $ActivityDir "$today.md"

if (-not (Test-Path $ActivityDir)) { New-Item -ItemType Directory $ActivityDir -Force | Out-Null }

$lines = @("# Activity $today", "")
$cutoff = (Get-Date).AddHours(-24)
$recent = Get-ChildItem -Path "$VaultRoot\wiki" -Recurse -File -Include *.md |
    Where-Object { $_.LastWriteTime -gt $cutoff } |
    Sort-Object LastWriteTime -Descending | Select-Object -First 30

$lines += "## File activity (last 24h)"
foreach ($f in $recent) {
    $rel = $f.FullName.Replace($VaultRoot, '').Replace('\','/')
    $lines += "- $($f.LastWriteTime.ToString('HH:mm')) ``$rel``"
}

Set-Content -Path $note -Value ($lines -join "`r`n") -Encoding UTF8
Write-Output "Wrote $note"
```

### Step 4.2 — Register the Windows scheduled task

**Method A — natural language to Claude Code/Codex CLI (recommended)**:

<div class="prompt-box">
<div class="prompt-label"><span class="prompt-icon">💬</span> Drop into Claude Code/Codex CLI</div>
<pre>Register a Windows scheduled task "ResearchAssistantTracker" with:
- Daily start at 00:00 → repeat every 120 minutes → 23:59 duration (12 fires/day)
- Command: powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\<me>\ObsidianVault\scripts\daily_tracker.ps1
- Extras: StartWhenAvailable=true, DisallowStartIfOnBatteries=false, StopIfGoingOnBatteries=false

Use schtasks.exe + Get-ScheduledTask + Set-ScheduledTask. After registering, show next-fire time.</pre>
</div>

**Method B — direct (raw)**:

```powershell
schtasks.exe /Create /TN "ResearchAssistantTracker" `
  /SC DAILY /ST 00:00 /RI 120 /DU 23:59 `
  /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\<you>\ObsidianVault\scripts\daily_tracker.ps1" /F
```

12 fires/day (00, 02, 04, ..., 22).

> 💡 **🛠 Customizing — match your rhythm**: change two numbers.
> - `/RI 120` = repeat interval (minutes). `60` hourly, `240` every 4h, etc.
> - `/ST 00:00` = start time.
> - Work-hours-only: `/SC DAILY /ST 09:00 /RI 60 /DU 10:00`.
> - Document in `wiki/sources/My Tracker Setup.md` so future-you knows why.

### Step 4.3 — Catch-up after computer was off

```powershell
$task = Get-ScheduledTask -TaskName ResearchAssistantTracker
$task.Settings.StartWhenAvailable = $true
$task.Settings.DisallowStartIfOnBatteries = $false
Set-ScheduledTask -TaskName ResearchAssistantTracker -Settings $task.Settings
```

### Step 4.4 — Run once now

```powershell
powershell.exe -File C:\Users\<you>\ObsidianVault\scripts\daily_tracker.ps1
```

> ✅ **Day 4 check**: at the next even hour, a new `wiki/activity/YYYY-MM-DD.md` should appear.

---

## Day 5 — Ontology

### 5.0 — What's an ontology and why bother?

Just remember **two tables**:

**(1) Types**:

| Type | What | Example |
|---|---|---|
| `Person` | A single person | yourself, advisees |
| `Project` | An active project | research system |
| `Grant` | External funding | NSF entity |
| `Concept` | Methodology / theory | "BKT", "ECD" |
| `Course` | Taught course | semester courses |
| `Manuscript` | A paper | journal-submitted papers |
| `Lab` / `Institution` / `Funder` | Organizations | your lab, university |
| `Tool` | Platforms | Supabase, OpenRouter |

**(2) Relations**:

| Relation | Meaning | Example |
|---|---|---|
| `hasPI` | "X has PI Y" | Project A → hasPI → me |
| `advises` | "X advises Y" | me → advises → student 1 |
| `usesMethod` | "X uses method Y" | Project A → usesMethod → Method A |
| `fundedBy` | "X funded by Y" | Project A → fundedBy → Grant X |
| `collaboratesWith` | "X with Y" | me → collaboratesWith → collab |
| `taughtIn` | "X covered in Y" | Method A → taughtIn → Course |
| `relatedTo` | (catch-all) | default |

> 💡 **Ontology = types + relations.** That's it.

{{DIAGRAM:schema}}

> 💡 **🛠 Customizing — your domain**: HCI → `Study`/`Participant`. Clinical → `Trial`/`Cohort`. Edit `RELATION_RULES` in `build_ontology.py` + log in `wiki/sources/My Ontology Customization.md`.

### 5.0.1 — How auto-extraction works

`build_ontology.py` runs every 2 hours and:

1. Reads every `wiki/**/*.md`, parses `type:` frontmatter
2. Extracts every `[[wikilink]]` in body
3. Cue-word matching ±100 chars (e.g., *"funded by"* → `fundedBy`)
4. Type-domain enforcement (auto-orient direction)
5. Outputs JSON-LD

> 💡 **JSON-LD?** "JSON for Linked Data" — W3C standard, RDF/SPARQL compatible.

### Step 5.1-5.5

<div class="prompt-box">
<div class="prompt-label"><span class="prompt-icon">💬</span> Drop into Claude Code/Codex CLI — full Day 5 setup</div>
<pre>Pull the full build_ontology.py from the guide (https://educatian.github.io/research-assistant-ai-workflow-en/) into my vault scripts/. Then:

1. Run python build_ontology.py once → confirm wiki/_ontology.json + _ontology_summary.md + _ontology_graph.html appear
2. Append `& python "$VaultRoot\scripts\build_ontology.py"` to daily_tracker.ps1
3. Open _ontology_graph.html and visually confirm

My vault: C:\Users\<me>\ObsidianVault\</pre>
</div>

```powershell
python C:\Users\<you>\ObsidianVault\scripts\build_ontology.py
# → wiki/_ontology.json + _ontology_graph.html

# Add to tracker
# (append to daily_tracker.ps1)
& python "$VaultRoot\scripts\build_ontology.py"

# Query
python scripts\query_ontology.py "Project A"
python scripts\query_ontology.py --type Grant
python scripts\query_ontology.py --predicate hasPI
```

> ✅ **Day 5 check**: `python query_ontology.py "<your name>"` returns advisees, grants, collaborators.

---

## Day 6 — LLM detects changes in your notes

### Step 6.1 — OpenRouter API key

> 💡 **OpenRouter** = LLM proxy (use any provider's models through one API). **API key** = secret string for auth.

Sign up → top up $5 → save key:
```
C:\Users\<you>\Desktop\_secrets\openrouter.txt
```

> ⚠️ **Never put `_secrets/` inside the vault.**

### Step 6.2 — situation_watch.py

<div class="prompt-box">
<div class="prompt-label"><span class="prompt-icon">💬</span> Drop into Claude Code/Codex CLI — full Day 6 setup</div>
<pre>Help me set up Day 6 situation_watch:

1. Save my OpenRouter API key in C:\Users\<me>\Desktop\_secrets\openrouter.txt (NEVER inside vault)
2. Pull situation_watch.py + apply_situation.py into vault scripts/
3. First run: python situation_watch.py --hours 168
4. Verify wiki/situation/<today>.md has [AUTO]/[REVIEW] proposals
5. Append to daily_tracker.ps1: `& python "$VaultRoot\scripts\situation_watch.py" --hours 24`

My vault: C:\Users\<me>\ObsidianVault\</pre>
</div>

```powershell
python C:\Users\<you>\ObsidianVault\scripts\situation_watch.py --hours 168
```

`wiki/situation/<today>.md` will contain:
```markdown
### [AUTO] Project A — deadline_update
- new_value: 2026-09-01
- confidence: 0.92
- reason: new deadline mentioned in README
- evidence: "Final pilot deadline pushed to September 1, 2026"
```

### Step 6.5 — Apply

```powershell
python C:\Users\<you>\ObsidianVault\scripts\apply_situation.py
```

Auto-applies `[AUTO]` only (confidence ≥ 0.85). `[REVIEW]` items wait for `--review` flag.

> ⚠️ **Auto-apply is conservative**: AI auto-applies *factual* changes only (deadline / status / progress). *Interpretive* changes stay as `[REVIEW]`.

> 💡 **🛠 Customizing — three knobs**:
> - `MODEL` — swap to `anthropic/claude-3.5-haiku` or `claude-3.5-sonnet` for higher quality
> - `AUTO_THRESHOLD = 0.85` — raise to 0.95 (stricter) or lower to 0.75 (aggressive)
> - `IMPORTANCE_KEYWORDS` — add domain-specific keywords
>
> Log changes in `wiki/sources/My LLM Tuning.md`.

---

## Day 7 — /slides — auto-generate presentations

### Step 7.1 — Cache open-design skills

```powershell
mkdir C:\Users\<you>\Desktop\_tools\open-design-cache\skills
```

<div class="prompt-box">
<div class="prompt-label"><span class="prompt-icon">💬</span> Drop into Claude Code/Codex CLI — full Day 7 setup</div>
<pre>Set up the Day 7 /slides workflow:

1. Cache 5 open-design skills under Desktop\_tools\open-design-cache\skills\:
   - magazine-web-ppt (default)
   - html-ppt-knowledge-arch-blueprint (methodology)
   - html-ppt-course-module (teaching)
   - html-ppt-pitch-deck (grant / pitch)
   - html-ppt-product-launch (product reveal)

   Fetch each via `gh api repos/nexu-io/open-design/contents/skills/<id>/<file> --jq .content | base64 -d`. NEVER execute repo code — only read markdown.

2. Create slash command at ~\.claude\commands\slides.md:
   - Auto-pick skill based on topic
   - Read SKILL.md + references + template
   - Pull vault entity / ontology content
   - Propose 8-15 slide outline → wait for user OK → generate self-contained HTML
   - Output: Desktop\_PTs\<date>_<slug>\index.html

3. Test: /slides [my project name]</pre>
</div>

### Step 7.2 — `~/.claude/commands/slides.md`

```markdown
---
description: Build HTML slide deck from open-design skill + vault content
argument-hint: "<topic> [--skill <skill-name>]"
---

User typed `/slides $ARGUMENTS`. Steps:

1. Auto-pick skill: lecture → course-module, methodology → blueprint, default → magazine
2. Read skill files from Desktop\_tools\open-design-cache\skills\<skill-id>\
3. Pull vault content: wiki/entities/<topic>.md + concepts grep + query_ontology.py
4. Propose 8-15 slide outline, wait for OK
5. Generate single self-contained HTML (CSS/JS inline, fonts CDN) at Desktop\_PTs\<date>_<slug>\index.html
6. Open in browser
```

### Step 7.3 — Use it

```
/slides Project A methodology
```

> ✅ **Day 7 check**: `Desktop\_PTs\<date>_<topic-slug>\index.html` exists, vault content rendered as magazine-style slides.

> 💡 **🛠 Customizing — new skills / commands**: `~\.claude\commands\<name>.md` for custom slash commands. Document in `wiki/sources/My Custom Skills.md`.

---

## After 7 days — daily rhythm

{{DIAGRAM:weekly-flow}}

**Morning** — open Today.md. Deadlines + priorities + what changed last night, all at a glance.

**During work** — Claude Code anywhere. CLAUDE.md + memory auto-loaded.

**Every 2 hours (background)** — tracker auto-runs. Notes scanned, ontology rebuilt, changes detected, Today.md refreshed. You do nothing.

**Session end** — Stop hook auto-adds session digest.

**Weekend** — review `wiki/situation/<recent dates>.md` `[REVIEW]` items. Apply what's worth applying. Open the ontology graph.

---

## Real scenarios — when this is most useful

{{DIAGRAM:scenarios}}

### Scenario 1 — Dissertation chapter writer's block

**Setup**: writing Chapter 3 methods. Six months ago you had a meeting that finalized the estimation method. Where did you write it?

| Without | With |
|---|---|
| Slack DM search + old notes + email → 30-45 min | `python query_ontology.py "Method A"` → all related sessions. `Read wiki/sources/Sessions 2025-11-XX.md` → 5-line summary. **3 minutes**. |

> 💡 **Why it works**: Day 3's Stop hook auto-records every session digest.

### Scenario 2 — Grant deadline D-7 panic

**Setup**: 9 docx files for one grant. Did they stay consistent?

| Without | With |
|---|---|
| Manual diff. *"narrative says $35K but current_support says $30K"* — easy to miss | situation_watch reviews changes via LLM every 2h → flags inconsistencies. **Caught before submission**. |

> 💡 **Why it works**: Day 6 situation_watch flags *changes you might miss*.

### Scenario 3 — Onboarding new advisee

**Setup**: explain "my research portfolio" in one hour.

| Without | With |
|---|---|
| New PPT → 2-3 hours | `/slides my research portfolio` + `wiki/_ontology_graph.html`. **5 minutes**. |

> 💡 **Why it works**: Day 7 + Day 5 build *portfolio-at-a-glance* automatically.

### Scenario 4 — Reviewer 2 ("explain why you didn't use method X")

**Setup**: R&R asks why you rejected method X six months ago.

| Without | With |
|---|---|
| Improvise → vague answer | `grep "X-method" wiki/sources/Sessions*.md` → finds your past `key_decisions`. **2 minutes**. |

> 💡 **Why it works**: Session digests preserve *decision rationales* — future-you can defend past-you.

### Scenario 5 — Comp exam / quals prep

**Setup**: 80 papers in 6 months. Need the citation network.

| Without | With |
|---|---|
| EndNote has metadata; relations are in your head | If you wrote each paper as `wiki/sources/<paper>.md` with `cites: [[Method A]]` + `extends: [[Theory B]]` → ontology auto-builds the graph. `--predicate cites` for citation network. |

> 💡 **Why it works**: Reading 1-2 papers/day with vault notes → exam prep already done.

---

> 💡 **The common pattern**: in all five, *"leave traces while working anyway → computer fetches answers when needed"*. The system is infrastructure that quietly accumulates material for future-you.

---

## Common pitfalls (troubleshooting)

| Symptom | Cause | Fix |
|---|---|---|
| Stop hook doesn't fire | settings.json escape | `\\` doubling, `\"` quoting |
| Tracker not firing every 2h | computer asleep, StartWhenAvailable not set | `schtasks /Query /V` to see last/next |
| Ontology has 0 nodes | missing `type:` frontmatter | add `type: project` to every entity |
| `query_ontology.py` returns nothing | label case mismatch | run `--type Project` first |
| situation_watch shows `(LLM error)` | OpenRouter key issue | test with curl |
| `/slides` produces empty slides | no entity in vault for topic | hand-write `wiki/entities/<topic>.md` first |

> 💡 **Almost every failure is frontmatter or path-escape.**

---

## Customizing — log every change as a note

Every number/threshold/keyword is **designed to be customized**. As complexity grows, document each change:

```
wiki/sources/
├── My Tracker Setup.md          ← cadence / start time
├── My LLM Tuning.md              ← model / threshold / keywords
├── My Ontology Customization.md  ← types/relations
├── My Hook Setup.md              ← hook events
└── My Custom Skills.md           ← slash commands / slide skills
```

Each note: `type: source` + `tags: [tuning, customization]` + timestamp. Day 5 ontology auto-picks them up — `python query_ontology.py "tuning"` answers *"how has my system evolved?"*.

---

## Core principles

1. **A single entry point eliminates search** — `Today.md` instead of *"where did I write that"*.
2. **Memory beats prompt engineering** — `~/.claude/projects/<machine>/memory/` instead of re-explaining.
3. **Ontology beats flat tags** — *"all grants where I'm PI"* in one CLI line.
4. **LLM at the edges only** — orchestrator is plain Python/PowerShell.
5. **Auto-apply is conservative** — every LLM proposal has confidence + `[REVIEW]` fallback.
6. **Every action must be reversible** — undo, audit logs, regeneratable graph.
