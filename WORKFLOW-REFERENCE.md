# Enterprise Network Labs — Complete Workflow Reference

**Repo:** `vushueh/enterprise-network-labs` | **Branch:** `main`
**WSL path:** `/home/leonel/code/enterprise-network-labs/`
**Last updated:** 2026-05-10

> **Both Codex and Claude Code read this file at the start of every session.**
> After reading it, each tool confirms they understand the workflow and tells you
> what the current project status is and what to do next.

---

## 1. How the System Works

GitHub is the single source of truth. Every tool reads from and writes to it.

```
Codex proposes config
       ↓
Claude reviews it (you paste between windows)
       ↓
You apply approved config to CML
       ↓
You verify in CML, paste output back
       ↓
Repeat for each phase
       ↓
All phases complete → Codex OR Claude pushes full project to GitHub
       ↓
Claude reviews final push for structure/accuracy
```

### The Four Tools and Their Roles

| Tool | Primary Role | GitHub access |
|------|-------------|---------------|
| **Codex Desktop** | Proposes configs, writes lab docs, saves to session folder | Yes — can push. Preference: Claude pushes final project for structure accuracy |
| **Claude Code** | Reviews configs before CML, final project push + structure check | Yes — full access |
| **VS Code (Remote-WSL)** | File editing, git operations, launching Claude Code CLI | Yes — full access |
| **WSL Terminal** | Git operations, direct file access | Yes — full access |

### The Four Bridge Files (repo root — read by both tools every session)

| File | Written by | Read by | Purpose |
|------|-----------|---------|---------|
| `WORKFLOW-REFERENCE.md` | Claude (this file) | Both tools | Complete working instructions |
| `AGENTS.md` | Claude | Codex | Codex-specific standing orders |
| `CLAUDE-REVIEW.md` | Claude | Codex | Persistent critiques — Codex resolves OPEN items first |
| `CODEX-LOG.md` | Codex | Claude | Session summaries — what was done, where to resume |

---

## 2. What Each Tool Does at Session Start

### Codex — reads from GitHub, then orients you

At the start of every Codex session, Codex will:
1. Read `WORKFLOW-REFERENCE.md`, `AGENTS.md`, `CLAUDE-REVIEW.md`, `CODEX-LOG.md`, `README.md`
2. Report back:
   - Any OPEN items from Claude that need resolving first
   - Current project and phase
   - Exactly where we left off
   - What to do next

### Claude Code — reads from WSL repo, then orients you

At the start of every Claude session, Claude will:
1. Read `WORKFLOW-REFERENCE.md` and `CODEX-LOG.md` from the repo
2. Pull latest from GitHub
3. Report back:
   - Current project status
   - What Codex last did
   - Any corrections needed
   - What to do next

---

## 3. The Phase-by-Phase Workflow

Every project has multiple phases. This is the exact sequence for each phase:

```
Step 1 — Codex proposes
   Codex writes the full config for the phase in [CODEX-PROPOSED] format
   Saves to its Windows session folder (see Section 5 for how to create it)
   Does NOT apply anything to CML — always waits for Claude approval

Step 2 — Switch to Claude (no copy-paste needed)
   Open Claude Code and say:
   "Read Codex's latest session and review the Phase X config before I apply it to CML"
   Claude reads the Codex session file directly — finds the proposed config automatically
   Claude responds with [CLAUDE-REVIEW]: APPROVED or CORRECTIONS REQUIRED

   ✅ If APPROVED → skip Step 3, go straight to Step 4
   ✏️  If CORRECTIONS REQUIRED → do Step 3

Step 3 — Paste corrections back to Codex (only if corrections needed)
   Copy Claude's [CLAUDE-REVIEW] block (one paste, one direction)
   Paste into Codex chat — Codex updates its config and confirms ready

Step 4 — Apply to CML
   Take the approved/corrected config and apply to CML devices manually
   Run verification commands

Step 5 — Paste verification output to Claude
   Paste the CML show command output to Claude
   Claude confirms it looks correct
   If wrong: fix in CML, re-verify, paste again

Step 6 — Save and log
   Tell Codex: "Phase X verified. Save configs and verification output to session folder.
   Update CODEX-LOG.md on GitHub."

Step 7 — Repeat for next phase
```

### When the Project Is Fully Complete

```
Step A — Tell Codex: "All phases complete. Save everything to session folder.
          Update CODEX-LOG.md with full summary and session folder path. Push CODEX-LOG.md."

Step B — Tell Claude: "Project 8 complete. Codex session folder:
          C:\Users\CHONGONG\Documents\Codex\[date]\[session-name]\
          Review the full project and push to GitHub."

Step C — Claude reads all configs + verification outputs from the session folder
Step D — Claude reviews for correctness and structure
Step E — Claude pushes to GitHub, marks project ✅ in README.md
Step F — Claude clears CLAUDE-REVIEW.md and adds separator to CODEX-LOG.md for next project
```

**Projects push to GitHub when fully complete — not after individual phases.**
**Codex CAN push to GitHub. For final project structure, Claude handles it to ensure accuracy.**

---

## 4. The [CODEX-PROPOSED] / [CLAUDE-REVIEW] Format

### How Codex presents a config for review

```
[CODEX-PROPOSED] Project 8 / Phase 1 / Device: HQ-RTR1
─────────────────────────────────────────────────────
interface Tunnel0
 ip address 10.0.100.1 255.255.255.252
 tunnel source Ethernet0/0
 tunnel destination 10.0.0.2
─────────────────────────────────────────────────────
PENDING-CLAUDE-REVIEW — do not apply to CML until Claude approves.
```

### How Claude responds

```
[CLAUDE-REVIEW] Project 8 / Phase 1 / Device: HQ-RTR1
STATUS: CORRECTIONS REQUIRED

Issues found:
- Tunnel keepalives missing — add: keepalive 10 3
- tunnel mode not specified — default is GRE, but make it explicit

Corrected config:
interface Tunnel0
 ip address 10.0.100.1 255.255.255.252
 tunnel source Ethernet0/0
 tunnel destination 10.0.0.2
 tunnel mode gre ip
 keepalive 10 3

Safe to apply to CML: YES
```

Copy Claude's `[CLAUDE-REVIEW]` block and paste it into Codex. Codex updates its config and confirms ready.

---

## 5. How the Codex Session Folder Works

You do not create the session folder. You do not type any path.

**What you do:**
1. Open Codex Desktop
2. Click **New Chat**
3. Give the conversation a short descriptive title — example: `Project 8 Phase 1 GRE Tunnel`
4. That's it. Codex automatically creates:
   ```
   C:\Users\CHONGONG\Documents\Codex\[today's date]\[title-as-hyphenated-name]\
   ```

**Example:** Title `Project 8 Phase 1 GRE Tunnel` → Codex creates:
```
C:\Users\CHONGONG\Documents\Codex\2026-05-10\project-8-phase-1-gre-tunnel\
```

All files Codex saves during that session go there automatically.

**To see what Codex saved after a session:**
- Windows Explorer → `C:\Users\CHONGONG\Documents\Codex\`
- WSL terminal: `ls /mnt/c/Users/CHONGONG/Documents/Codex/`

---

## 6. Starting a Session — Every Tool

### After Computer Restart or Opening Fresh

Always sync first. GitHub is the truth — your local copy may be behind.

---

### Codex Desktop

1. Open Codex Desktop
2. Click **New Chat** — give it a short descriptive title like `Project 8 Phase 1 GRE Tunnel`
   Codex automatically creates the working directory from the date + title. You do nothing.
3. Paste this startup prompt:

```
Read the following files from vushueh/enterprise-network-labs on GitHub
before doing anything else:
- WORKFLOW-REFERENCE.md (full working instructions)
- AGENTS.md (your standing orders)
- CLAUDE-REVIEW.md (any open items from Claude to resolve first?)
- CODEX-LOG.md (where did we leave off?)
- README.md (current project status)

Then tell me:
1. Any OPEN items from Claude I need to resolve first?
2. Current project and phase — exactly where did we leave off?
3. What is the next step?
```

---

### Claude Code — Desktop App

1. Open Claude Code Desktop app
2. Session startup runs automatically (reads CLAUDE.md, checks repo, verifies GitHub auth)
3. Say:

```
Pull the latest from enterprise-network-labs repo.
Read WORKFLOW-REFERENCE.md and CODEX-LOG.md.
Tell me: what is the current project status and where did Codex leave off?
```

### Claude Code — Launched from VS Code Terminal

1. In VS Code, open WSL terminal (`Ctrl + ``)
2. Navigate to the repo:
   ```bash
   cd /home/leonel/code/enterprise-network-labs
   git pull origin main
   ```
3. Launch Claude Code CLI from that directory:
   ```bash
   claude
   ```
4. Claude Code opens with the repo as context. Say:
   ```
   Read WORKFLOW-REFERENCE.md and CODEX-LOG.md.
   Tell me the current project status and where Codex left off.
   ```

### Claude Code — Launched from WSL Terminal

1. Open WSL terminal (Windows Terminal → Ubuntu, or `Win+R → wsl`)
2. Navigate and launch:
   ```bash
   cd /home/leonel/code/enterprise-network-labs
   git pull origin main
   claude
   ```
3. Same startup prompt as above

---

### VS Code

1. Open VS Code
2. Connect to WSL: click green `><` button (bottom-left) → **Connect to WSL**
3. Open the repo folder: File → Open Folder → `/home/leonel/code/enterprise-network-labs`
4. Open terminal: `Ctrl + `` ` → sync:
   ```bash
   git pull origin main
   git log --oneline -5
   ```
5. **To launch Claude Code from here:** in the terminal, run `claude`
6. **To push changes:**
   ```bash
   git add .
   git commit -m "your message"
   git push origin main
   ```
   OR use the Source Control panel (branch icon, left sidebar)

---

### WSL Terminal (Ubuntu)

1. Windows Terminal → Ubuntu tab, OR `Win+R → wsl`
2. Sync and check:
   ```bash
   cd /home/leonel/code/enterprise-network-labs
   git pull origin main
   git log --oneline -5
   git status
   ```
3. **To launch Claude Code from here:** run `claude`
4. **To push:**
   ```bash
   git add .
   git commit -m "message"
   git push origin main
   ```

---

## 7. Switching Between Tools Mid-Project

### Codex → Claude Code

1. Copy the `[CODEX-PROPOSED]` block from Codex chat
2. Open Claude Code (Desktop, VS Code terminal, or WSL terminal)
3. Paste and say: `"Review this Phase X config before I apply it to CML"`
4. Claude responds with `[CLAUDE-REVIEW]`
5. If corrections needed: copy `[CLAUDE-REVIEW]` back to Codex

### Codex → VS Code or WSL

1. Tell Codex: `"Update CODEX-LOG.md on GitHub with current status"`
2. In VS Code/WSL terminal:
   ```bash
   cd /home/leonel/code/enterprise-network-labs
   git pull origin main
   ```
3. Codex's session files are at:
   - Windows: `C:\Users\CHONGONG\Documents\Codex\[date]\[session]\`
   - WSL: `/mnt/c/Users/CHONGONG/Documents/Codex/[date]/[session]/`

### VS Code or WSL → Codex

1. Push any changes:
   ```bash
   git add . && git commit -m "message" && git push origin main
   ```
2. Open Codex with the standard startup prompt — it reads GitHub and picks up your push

### Claude Code → Codex

1. Claude commits and pushes whatever it worked on
2. Open Codex with the standard startup prompt — fully in sync

### VS Code ↔ WSL Terminal

Same filesystem — no sync needed. Changes are instant across both.

---

## 8. What to Say to Each Tool

### Codex — start of a phase

```
Project 8, Phase 2 — IPsec IKEv2 encryption.
Write the proposed config for HQ-RTR1 and BR-RTR1.
Use [CODEX-PROPOSED] format. Save to session folder.
I will take it to Claude before applying to CML.
```

### Codex — after phase verified in CML

```
Phase 2 verified. Save the verification output to the session folder.
Update CODEX-LOG.md on GitHub: what was done, where we left off.
```

### Codex — project complete

```
All phases complete and verified. Save everything to session folder.
Update CODEX-LOG.md: project complete, list all files, include the full session folder path.
```

### Claude — review before CML

```
Read Codex's latest session and review the Phase X config before I apply it to CML.
```

No copy-paste needed. Claude reads the Codex session file directly.
Only paste something to Claude if you want to show a specific snippet or error message.

### Claude — final push

```
Project 8 complete. Codex session folder:
C:\Users\CHONGONG\Documents\Codex\[date]\[session-name]\
Review the full project, push to GitHub, mark P08 complete in README.
```

### Claude — check Codex work

```
Check what Codex did — read CODEX-LOG.md and tell me status.
```

---

## 9. Where Files Live

| What | Path |
|------|------|
| Git repo (WSL) | `/home/leonel/code/enterprise-network-labs/` |
| Git repo (Windows UNC) | `\\wsl.localhost\Ubuntu\home\leonel\code\enterprise-network-labs\` |
| Codex session output | `C:\Users\CHONGONG\Documents\Codex\[date]\[session]\` |
| Codex session output (from WSL) | `/mnt/c/Users/CHONGONG/Documents/Codex/[date]/[session]/` |
| Codex chat history (raw JSONL) | `C:\Users\CHONGONG\.codex\sessions\YYYY\MM\DD\` |
| GitHub | `https://github.com/vushueh/enterprise-network-labs` |
| Workflow reference (this file) | `https://github.com/vushueh/enterprise-network-labs/blob/main/WORKFLOW-REFERENCE.md` |

---

## 10. Project Close-Out Checklist

```
□ All phases built and verified in CML
□ Break/fix exercise done and documented
□ All configs saved in Codex session folder
□ All verification outputs saved in Codex session folder
□ Codex updated CODEX-LOG.md with full summary + session folder path
□ Tell Claude: "Project X complete — push to GitHub"
□ Claude reviews, compiles, pushes all files
□ Claude marks project ✅ in README.md
□ Claude archives CLAUDE-REVIEW.md entries for completed project
□ Claude adds separator to CODEX-LOG.md for next project
□ Verify on GitHub: all files present, README updated
□ Ready for next project
```

---

## 11. Quick Reference Card

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REPO:     vushueh/enterprise-network-labs (main)
WSL:      /home/leonel/code/enterprise-network-labs/
WORKFLOW: github.com/vushueh/enterprise-network-labs/blob/main/WORKFLOW-REFERENCE.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SYNC (every tool, every session):
  git pull origin main

CODEX SESSION START (paste this every time):
  "Read WORKFLOW-REFERENCE.md, AGENTS.md, CLAUDE-REVIEW.md,
   CODEX-LOG.md, README.md from vushueh/enterprise-network-labs.
   Any OPEN items? Where did we leave off? What's next?"

LAUNCH CLAUDE CODE (from VS Code terminal or WSL):
  cd /home/leonel/code/enterprise-network-labs
  git pull origin main
  claude

BEFORE ANY CONFIG GOES ON A CML DEVICE:
  Switch to Claude and say:
  "Read Codex's latest session and review the Phase X config"
  Claude reads Codex session file directly — no copy-paste needed
  If APPROVED → apply to CML
  If CORRECTIONS → paste Claude's [CLAUDE-REVIEW] back to Codex only

PHASE COMPLETE:
  Tell Codex: "Phase X done. Save to session folder. Update CODEX-LOG.md."

PROJECT COMPLETE → PUSH:
  Tell Claude: "Project X done. Session folder: C:\Users\CHONGONG\Documents\Codex\[date]\[session]\"
  Claude reviews + pushes to GitHub

CODEX SESSION FOLDER (auto-created — you do nothing):
  Just title your chat descriptively. Codex creates the folder.
  Find it later at: C:\Users\CHONGONG\Documents\Codex\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 12. Current Project Status

| # | Project | Status |
|---|---------|--------|
| 01 | Campus Foundation | ✅ Complete |
| 02 | Multi-Site + DHCP | ✅ Complete |
| 03 | OSPF Dynamic Routing | ✅ Complete |
| 04 | Switching Stability | ✅ Complete |
| 05 | Internet + NAT | ✅ Complete |
| 06 | Security Hardening | ✅ Complete |
| 07 | ASAv Firewall | ✅ Complete |
| 08 | Site-to-Site VPN | 🔄 In Progress |
| 09 | Monitoring | ⬜ |
| 10 | AAA + Access Control | ⬜ |
| 11 | QoS | ⬜ |
| 12 | Disaster Recovery | ⬜ |
| 13 | Network Automation | ⬜ |
