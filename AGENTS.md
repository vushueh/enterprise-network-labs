# Codex Standing Orders — Enterprise Network Labs

You are working on Leonel's enterprise network lab series built in Cisco CML 2.9.
GitHub repo: `vushueh/enterprise-network-labs` (main branch)
WSL repo (local): `/home/leonel/code/enterprise-network-labs/`

---

## At the START of every session — do these first

Read these three files from GitHub before doing anything else:

1. `CLAUDE-REVIEW.md` — check for OPEN items from Claude. Resolve them before new work.
2. `TROUBLESHOOTING-LOG.md` — review past issues. Do not repeat known mistakes.
3. `README.md` — confirm which project is current and which are complete.

---

## Your role in the workflow

Codex **proposes and writes** configurations. Claude **reviews and approves** them before
anything is applied to CML. This is the order — never skip it:

```
Codex writes proposed config for the phase
              ↓
Claude reviews it (Leonel pastes to Claude or Claude reads session files)
              ↓
Claude approves or corrects
              ↓
Leonel applies the approved config to CML devices
              ↓
Leonel verifies in CML and pastes output back
              ↓
Move to next phase
```

**Leonel applies configs to CML — not Codex. Codex proposes, Claude approves, Leonel types.**

---

## Where to save your work

Codex Desktop sandbox cannot write to WSL or GitHub directly for project files.
Save all configs and outputs to your **Windows session folder**:

```
C:\Users\CHONGONG\Documents\Codex\[date]\[session-name]\project-XX\
    configs\
        DEVICE-phaseN.txt      ← full running config for that device at end of phase
    verification-outputs\
        phaseN-DEVICE-verify.txt  ← CLI output Leonel pastes back after verifying
    decision-log.md
    requirements.md
```

Claude can read these files from the Windows path when it's time to push.
**Do not save project files to GitHub** — Claude handles all GitHub pushes at project completion.

---

## The only thing you push to GitHub

The only file you write to GitHub directly is **`CODEX-LOG.md`** — your session summary.
Push this via GitHub connector at the end of every session:

```
## [DATE] — [what was worked on]
**Project:** P0X — [name]
**Phases proposed this session:** [list]
**Claude reviewed:** yes / pending
**Configs saved to Windows session folder:** [full path]
**Left off at:** [exactly where to resume]
```

---

## How to present configurations to Claude for review

After writing a phase config, always say:

> "Here is the proposed Phase X configuration for [DEVICE]. Tag: PENDING-CLAUDE-REVIEW.
> Do not apply to CML until Claude approves."

Then paste the full config block in chat so Leonel can copy it to Claude Code.

---

## Project structure (what Claude will push to GitHub on completion)

```
project-XX-name/
├── README.md
├── requirements.md
├── decision-log.md
├── configs/
│   └── DEVICE-phaseN.txt
├── verification-outputs/
│   └── phaseN-DEVICE-verify.txt
└── screenshots/
    └── PXX-phaseN-description.png
```

Follow **Build → Verify → Break → Fix** for every phase.
Save all CLI verification output — not just shown in chat.

---

## Environment facts

- **CML 2.9** (licensed) — IOL routers (`Ethernet0/x`, `Ethernet1/x`), IOL-L2 switches, ASAv
- **Codex sandbox**: no WSL/UNC access. Windows session folder + GitHub connector only.
- **Claude Code**: has full WSL + GitHub access. Handles all project GitHub pushes.
- **Project goes to GitHub only when all phases are complete** — Claude pushes, not Codex.
