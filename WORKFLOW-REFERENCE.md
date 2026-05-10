# Enterprise Network Labs — Complete Workflow Reference

**Repo:** `vushueh/enterprise-network-labs` | **Branch:** `main`
**WSL path:** `/home/leonel/code/enterprise-network-labs/`
**Last updated:** 2026-05-10

---

## 1. How the System Works

GitHub is the single source of truth. Every tool reads from and writes to it.

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR WORKFLOW                        │
│                                                         │
│  Codex ──proposes configs──► Claude ──reviews/approves──► You apply to CML │
│    │                            │                           │              │
│    │                            │                     CML verifies         │
│    │                            │                           │              │
│    └──CODEX-LOG.md──► GitHub ◄──┴──pushes complete project─┘              │
└─────────────────────────────────────────────────────────┘
```

### The Three Tools and Their Roles

| Tool | Role | Can write to GitHub? |
|------|------|---------------------|
| **Codex Desktop** | Proposes configurations, writes lab docs | CODEX-LOG.md only |
| **Claude Code** | Reviews configs before CML, pushes completed projects | Yes — all project files |
| **VS Code / WSL / Terminal** | Direct file editing, git operations | Yes — full access |

### The Three Bridge Files (always in the repo root)

| File | Written by | Read by | Purpose |
|------|-----------|---------|---------|
| `AGENTS.md` | Set once, updated by Claude | Codex | Codex standing orders every session |
| `CLAUDE-REVIEW.md` | Claude | Codex | Claude's critiques — Codex resolves before new work |
| `CODEX-LOG.md` | Codex | Claude | Session summaries — what was done, where we left off |

---

## 2. The Phase-by-Phase Workflow (How a Project Gets Built)

Every project has multiple phases. This is the exact sequence for each phase:

```
Step 1 — Codex proposes
   Codex writes the full configuration for the phase
   Saves it to: C:\Users\CHONGONG\Documents\Codex\[date]\[session]\project-XX\configs\
   Presents it in chat with label: "PENDING-CLAUDE-REVIEW"
   Does NOT apply anything to CML

Step 2 — Claude reviews (before any CML work)
   Copy Codex's [CODEX-PROPOSED] block from Codex chat
   Paste it to Claude Code and say: "Review this before I apply to CML"
   Claude checks for errors, topology consistency, anything that would break
   Claude responds with a [CLAUDE-REVIEW] block: APPROVED or CORRECTIONS REQUIRED

Step 3 — Feed Claude's response back to Codex (if corrections needed)
   Copy Claude's [CLAUDE-REVIEW] block
   Paste it into Codex chat — Codex reads it and updates the config automatically
   Codex confirms: "Updated config incorporates Claude's corrections. Ready for CML."

Step 4 — Apply to CML
   Take the approved/corrected config from Codex
   Apply it to the CML devices manually
   Run verification commands (show ip interface brief, show ip ospf neighbor, etc.)

Step 4 — Paste verification output back
   Paste the CML output to Claude
   Claude confirms it looks correct
   If something is wrong: fix in CML, re-verify

Step 5 — Save verification output
   Codex saves the verification output to:
   C:\Users\CHONGONG\Documents\Codex\[date]\[session]\project-XX\verification-outputs\

Step 6 — Repeat for next phase
```

### When the Project is Fully Complete (all phases done + break/fix done)

```
Step A — Tell Claude: "Project X is complete. Review everything and push to GitHub."
Step B — Claude reads all configs + verification outputs from Codex's Windows session folder
Step C — Claude reviews the full project for consistency
Step D — Claude writes any final corrections to CLAUDE-REVIEW.md
Step E — Claude compiles all files into the correct repo structure
Step F — Claude commits and pushes the complete project to GitHub
Step G — Claude marks the project ✅ in README.md
Step H — Claude clears CLAUDE-REVIEW.md and CODEX-LOG.md for the next project
```

**Projects are only pushed to GitHub when fully complete — not after individual phases.**

---

## 3. Starting a Session — Every Tool

### After a Computer Restart or Opening Fresh

Always do a git pull first on whichever tool you open. GitHub is the truth — your local copy may be behind.

---

### Opening Codex Desktop

1. Open Codex Desktop
2. Set working directory: `C:\Users\CHONGONG\Documents\Codex\[today's date]\[session-name]`
3. Paste this at the start of **every** Codex session:

```
Read my standing orders and project status from GitHub before we begin.
Read these from vushueh/enterprise-network-labs:
- AGENTS.md (your standing orders)
- CLAUDE-REVIEW.md (any open items from Claude?)
- CODEX-LOG.md (where did we leave off?)
- README.md (which project is current?)

Then tell me:
1. Any open Claude review items I need to resolve first?
2. Where exactly did we leave off?
3. What is the next phase to work on?
```

4. Codex reads all three bridge files from GitHub and orients itself
5. Begin working — Codex proposes configs, you take them to Claude for review

---

### Opening Claude Code (Desktop App)

1. Open Claude Code — session startup runs automatically
   (reads CLAUDE.md, checks recent file changes, verifies GitHub auth)
2. To pick up where Codex left off:

```
Check CODEX-LOG.md in the enterprise-network-labs repo and tell me where Codex left off.
Then pull the latest from GitHub.
```

3. Claude pulls the repo, reads CODEX-LOG.md, and reports status
4. To review a config Codex proposed, paste it and say:

```
Review this Phase X config for Project 8 before I apply it to CML.
Check for errors, consistency with the existing topology, and anything that could break.
```

---

### Opening VS Code

1. Open VS Code
2. Connect to WSL: click the green `><` button (bottom-left) → **Connect to WSL**
   OR open a recent WSL folder from File → Open Recent
3. Open terminal: `Ctrl + `` ` (backtick) — this gives you a WSL bash shell
4. Sync with GitHub:

```bash
cd /home/leonel/code/enterprise-network-labs
git pull origin main
git log --oneline -5    # see what's new
```

5. Edit files normally in the VS Code editor
6. To push changes:

```bash
git add .
git commit -m "your message"
git push origin main
```

OR use the Source Control panel (left sidebar, branch icon) → Stage → Commit → Push

---

### Opening WSL Terminal (Ubuntu)

1. Open Windows Terminal → click the `∨` dropdown → **Ubuntu**
   OR: press `Win + R` → type `wsl` → Enter
2. Sync with GitHub:

```bash
cd /home/leonel/code/enterprise-network-labs
git pull origin main
git log --oneline -5
git status
```

3. Run any git commands from here:

```bash
git add project-08-site-to-site-vpn/
git commit -m "P08: complete — all phases verified"
git push origin main
```

---

## 4. Switching Between Tools Mid-Project

### Codex → Claude Code

1. In Codex: copy the proposed config from chat
2. In Claude Code, paste it and say:
   `"Review this Phase X config for Project 8 before I apply it to CML"`
3. Claude reviews, corrects if needed, approves
4. Apply the approved config to CML

### Codex → VS Code or WSL (to check files or push)

1. Codex saves files to its Windows session folder — it does NOT push project files
2. In VS Code/WSL terminal:

```bash
cd /home/leonel/code/enterprise-network-labs
git pull origin main    # get any CODEX-LOG.md updates
```

3. Files Codex wrote are at:
   `C:\Users\CHONGONG\Documents\Codex\[date]\[session]\` (Windows)
   `/mnt/c/Users/CHONGONG/Documents/Codex/[date]\[session]\` (WSL)

### VS Code or WSL → Codex

1. Commit and push your changes first:

```bash
git add .
git commit -m "your message"
git push origin main
```

2. Open Codex with the standard startup prompt — it reads GitHub and picks up your changes

### Claude Code → Codex

1. Claude commits and pushes whatever it worked on
2. Open Codex with the standard startup prompt — fully in sync via GitHub

### VS Code ↔ WSL Terminal

These share the same filesystem — no sync needed. Changes made in VS Code are instantly visible in WSL terminal and vice versa.

---

## 5. What to Say to Each Tool

### Codex — Per Phase

**Start of phase:**
```
We are on Project 8, Phase 2 — IPsec IKEv2 encryption.
Write the proposed configuration for HQ-RTR1 and BR-RTR1.
Save to your session folder.
Label it PENDING-CLAUDE-REVIEW — I will take it to Claude before applying to CML.
```

**After verification passes:**
```
Phase 2 verified in CML. Save the verification output to your session folder.
Update CODEX-LOG.md on GitHub with what we completed today and where we left off.
```

**End of final phase (project complete):**
```
All phases are complete and verified. Save everything to your session folder.
Update CODEX-LOG.md: project complete, list all files saved, include the Windows session folder path.
Claude will handle the GitHub push for the full project.
```

### Claude — Per Phase

**Before applying to CML:**
```
Review this Phase X config for Project 8 before I apply it to CML.
[paste config]
```

**After all phases done:**
```
Project 8 is complete. All phases verified.
Codex saved the files to: C:\Users\CHONGONG\Documents\Codex\[date]\[session]\
Pull the latest, review the full project, push to GitHub, and mark it complete in README.
```

**To check on Codex's work:**
```
Check what Codex did — read CODEX-LOG.md and the latest session files.
```

---

## 6. Where Files Live

| What | Location |
|------|----------|
| Live git repo (WSL) | `/home/leonel/code/enterprise-network-labs/` |
| Same repo (Windows path) | `\\wsl.localhost\Ubuntu\home\leonel\code\enterprise-network-labs\` |
| Same repo (WSL from Windows) | `/mnt/c/...` does NOT apply — repo is in WSL, not Windows |
| Codex session output | `C:\Users\CHONGONG\Documents\Codex\[date]\[session]\` |
| Codex session output (from WSL) | `/mnt/c/Users/CHONGONG/Documents/Codex/[date]/[session]/` |
| Codex chat history (JSONL) | `C:\Users\CHONGONG\.codex\sessions\YYYY\MM\DD\` |
| GitHub | `https://github.com/vushueh/enterprise-network-labs` |

---

## 7. Project Close-Out Checklist

When a project is 100% complete:

```
□ All phases built and verified in CML
□ Break/fix exercise done
□ All configs saved in Codex session folder
□ All verification outputs saved in Codex session folder
□ Tell Claude: "Project X complete — push to GitHub"
□ Claude reviews, compiles, pushes
□ Claude marks project ✅ in README.md
□ Claude archives CLAUDE-REVIEW.md entries for that project
□ Claude adds clean separator to CODEX-LOG.md for next project
□ Confirm on GitHub that all files are present and README is updated
□ Ready for next project
```

---

## 8. Quick Reference Card

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REPO:     vushueh/enterprise-network-labs (main)
WSL:      /home/leonel/code/enterprise-network-labs/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SYNC (run on any tool after opening):
  git pull origin main

CODEX SESSION START:
  "Read AGENTS.md, CLAUDE-REVIEW.md, CODEX-LOG.md, README.md
   from vushueh/enterprise-network-labs. Any open items? Where did we leave off?"

CODEX PHASE SAVE:
  "Phase X done. Save configs + verification to session folder.
   Update CODEX-LOG.md on GitHub."

BEFORE APPLYING ANY CONFIG TO CML:
  Paste to Claude: "Review this Phase X config before I apply it to CML"
  Wait for Claude approval. Then apply.

PROJECT COMPLETE → GITHUB PUSH:
  Tell Claude: "Project X complete. Files at C:\Users\CHONGONG\Documents\Codex\[date]\[session]\
  Review and push to GitHub."

CLAUDE REVIEWS CODEX WORK:
  "Check what Codex did" → Claude reads CODEX-LOG.md + session JSONL files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 9. Current Project Status

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
