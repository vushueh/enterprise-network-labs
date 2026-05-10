# Codex Standing Orders — Enterprise Network Labs

You are working on Leonel's enterprise network lab series built in Cisco CML 2.9.
This repo lives at: `/home/leonel/code/enterprise-network-labs/` (WSL Ubuntu)
GitHub: `vushueh/enterprise-network-labs` (main branch)

## At the START of every session — do these first

1. **Read `CLAUDE-REVIEW.md`** in this repo root.
   - If it contains OPEN critique items, address them before starting new work.
   - After fixing each item, mark it RESOLVED and note what you did.

2. **Read `TROUBLESHOOTING-LOG.md`** to understand past issues — don't repeat known mistakes.

3. **Check `README.md`** to confirm which project is current and which are complete.

---

## File storage rules — CRITICAL

All project files MUST be saved to the live WSL git repo. There are two valid paths to it:

| Access method | Path |
|--------------|------|
| WSL shell (preferred) | `/home/leonel/code/enterprise-network-labs/` |
| Windows UNC (fallback) | `\\wsl.localhost\Ubuntu\home\leonel\code\enterprise-network-labs\` |

**NEVER save to these — they are wrong locations:**
- `C:\Users\CHONGONG\Documents\Codex\...` — Codex session temp folder, not tracked by git
- `C:\home\leonel\code\enterprise-network-labs\` — stale partial copy, no `.git`, do not use

If your shell cannot run `wsl.exe` directly, use the Windows UNC path for file writes and run git via:
```powershell
wsl.exe -- git -C /home/leonel/code/enterprise-network-labs add project-XX-name/
wsl.exe -- git -C /home/leonel/code/enterprise-network-labs commit -m "PXX: phase Y — description"
```
Or use the full WSL invocation:
```powershell
wsl.exe -- bash -c "cd /home/leonel/code/enterprise-network-labs && git add project-08-site-to-site-vpn/ && git commit -m 'P08: phase 1 — baseline verification'"
```

---

## Commit after EVERY completed phase — no exceptions

When a phase is complete and verified:

1. Save all configs and verification outputs to the correct WSL paths (see above)
2. Run from WSL:
```bash
cd /home/leonel/code/enterprise-network-labs
git add project-XX-name/
git commit -m "PXX: phase Y — <one line description of what was built>"
```

**Do NOT accumulate multiple phases in one commit.** One commit per phase keeps the history clean and makes it easy to see exactly what changed.

**Do NOT push automatically.** Commit only. Leonel will push when ready — from Codex, Claude Code, VS Code, or WSL terminal, whichever he's using at that moment.

### Commit message format
```
P08: phase 1 — GRE tunnel baseline verification
P08: phase 2 — IPsec IKEv2 encryption applied
P08: phase 3 — OSPF migrated over tunnel
P08: break/fix — [describe the fault injected and fixed]
```

---

## At the END of every session — always do this

Append a summary to `CODEX-LOG.md`:

```
## [DATE] — [what was worked on]
**Phases completed:** [list]
**Committed:** yes / no — [commit hash if yes]
**Pushed:** yes / no
**Left off at:** [exactly where to resume]
**Files saved to WSL repo:** [list key file paths]
```

---

## Project structure (required for every project)

```
project-XX-name/
├── README.md                  # Full lab guide with phases, STAR, verification
├── requirements.md            # What needs to be built and why
├── decision-log.md            # Every design choice and why
├── configs/                   # Final running configs per device per phase
│   └── DEVICE-phaseN.txt
├── verification-outputs/      # Copied CLI output proving it works
│   └── phaseN-DEVICE-verify.txt
└── screenshots/               # CML topology + key verification screenshots
    └── PXX-phaseN-description.png
```

Follow the **Build → Verify → Break → Fix** cycle for every phase.
All verification CLI output must be saved to `verification-outputs/` — not just shown in chat.

---

## Environment facts

- **CML 2.9** (licensed) — IOL routers (`Ethernet0/x`, `Ethernet1/x`), IOL-L2 switches, ASAv
- **Git credentials**: WSL at `/home/leonel/.config/gh/hosts.yml`
- **Push from anywhere**: WSL terminal, VS Code Remote-WSL, Claude Code, or Codex — all work
- **VS Code** may have files open simultaneously — don't assume files are unchanged between turns
