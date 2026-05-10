# Codex Standing Orders — Enterprise Network Labs

You are working on Leonel's enterprise network lab series built in Cisco CML 2.9.
This repo lives at: `/home/leonel/code/enterprise-network-labs/` (WSL Ubuntu)
GitHub: `vushueh/enterprise-network-labs` (main branch)

## At the START of every session — do these first

1. **Read `CLAUDE-REVIEW.md`** in this repo root.
   - If it contains open critique items (status: OPEN), address them before starting new work.
   - After fixing each item, update its status to RESOLVED and note what you did.

2. **Read `TROUBLESHOOTING-LOG.md`** to understand past issues — don't repeat known mistakes.

3. **Check the live README.md** to confirm which project is current and which are complete.

## During the session

- Work files are in WSL: `/home/leonel/code/enterprise-network-labs/`
- Windows path equivalent: `//wsl.localhost/Ubuntu/home/leonel/code/enterprise-network-labs/`
- VS Code may also be open on the same files — don't assume files are unchanged between turns
- Git is configured in WSL. Push to GitHub from WSL terminal or VS Code (Remote-WSL)

## At the END of every session — always do this

Append a brief summary to `CODEX-LOG.md` in this format:

```
## [DATE] — [Session title / what was worked on]
**What was done:**
- [bullet list of actual changes made]

**Files changed:**
- [list file paths]

**GitHub:** [committed / pushed / not pushed]

**Left off at:** [exactly where to resume next time]
```

## Project structure rules

- Each project folder: `project-XX-name/`
- Required files per project: `README.md`, `requirements.md`, `decision-log.md`, `configs/`, `screenshots/`, `verification-outputs/`
- Follow the Build → Verify → Break → Fix cycle
- All CLI output used for verification must be saved in `verification-outputs/`
- Screenshot naming: `PXX-phaseY-description.png`

## Environment facts

- CML 2.9 (licensed) — IOL routers, IOL-L2 switches, ASAv
- Interface naming: `Ethernet0/x` and `Ethernet1/x` (NOT GigabitEthernet)
- Leonel uses WSL Ubuntu for git operations and VS Code Remote-WSL for editing
- GitHub credentials: stored in WSL at `/home/leonel/.config/gh/hosts.yml`
