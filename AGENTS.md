# Codex Standing Orders — Enterprise Network Labs

You are working on Leonel's enterprise network lab series built in Cisco CML 2.9.
GitHub repo: `vushueh/enterprise-network-labs` (main branch)
WSL repo (local): `/home/leonel/code/enterprise-network-labs/`

---

## At the START of every session — do these first

Read these three files from GitHub before doing anything else:

1. `CLAUDE-REVIEW.md` — resolve any OPEN items before new work
2. `TROUBLESHOOTING-LOG.md` — don't repeat known mistakes
3. `README.md` — confirm which project is current and which are complete

---

## How Codex saves and commits files — CRITICAL

**Codex Desktop runs in a sandbox that cannot access WSL or UNC paths.**
The only way Codex can write to the git repo is via the **GitHub connector**.

### Rule: use GitHub connector to create/update files directly on the repo

For every config file, verification output, README, or doc Codex produces:
- Use the GitHub connector to create or update that file at the correct path in `vushueh/enterprise-network-labs`
- Commit message format: `P08: phase 1 — GRE tunnel baseline verification`
- One commit per completed phase — do not batch multiple phases

**Correct repo paths for Project 8:**
```
project-08-site-to-site-vpn/README.md
project-08-site-to-site-vpn/requirements.md
project-08-site-to-site-vpn/decision-log.md
project-08-site-to-site-vpn/configs/HQ-RTR1-phase1.txt
project-08-site-to-site-vpn/configs/BR-RTR1-phase1.txt
project-08-site-to-site-vpn/verification-outputs/phase1-HQ-RTR1-verify.txt
project-08-site-to-site-vpn/verification-outputs/phase1-BR-RTR1-verify.txt
```

**NEVER save to these — they cannot be pushed:**
- `C:\Users\CHONGONG\Documents\Codex\...` — Codex session folder, not git-tracked
- `C:\home\leonel\...` — stale partial copy, no `.git`

### After GitHub push — tell Leonel to pull

After committing via GitHub connector, always say:
> "Files pushed to GitHub. Run `git pull` in WSL, VS Code, or Claude Code to sync locally."

Claude Code will handle the local pull and any additional commit work if needed.

---

## At the END of every session — update CODEX-LOG.md via GitHub connector

Append to `CODEX-LOG.md` on the repo:

```
## [DATE] — [what was worked on]
**Phases completed:** [list]
**Pushed to GitHub:** yes / no — [commit hash(es)]
**Left off at:** [exactly where to resume next]
**Files pushed:** [list key file paths]
```

---

## Project structure (required for every project)

```
project-XX-name/
├── README.md                     # Full lab guide: phases, STAR, verification
├── requirements.md               # What needs to be built and why
├── decision-log.md               # Every design choice and why
├── configs/
│   └── DEVICE-phaseN.txt         # Final running config per device per phase
├── verification-outputs/
│   └── phaseN-DEVICE-verify.txt  # Copied CLI output proving it works
└── screenshots/                  # CML topology + key verification screenshots
    └── PXX-phaseN-description.png
```

Follow **Build → Verify → Break → Fix** for every phase.
Save all verification CLI output to `verification-outputs/` — not just shown in chat.

---

## Environment facts

- **CML 2.9** (licensed) — IOL routers (`Ethernet0/x`, `Ethernet1/x`), IOL-L2 switches, ASAv
- **Codex sandbox**: no WSL access, no UNC path access — GitHub connector is the only write path
- **Claude Code**: has full WSL access, handles git pull/push locally when needed
- **VS Code Remote-WSL**, **WSL terminal**, **Claude Code** — all can pull from GitHub after Codex pushes
