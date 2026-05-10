# Claude Review File

This file is written by **Claude Code** and read by **Codex**.

- Claude writes critique items here after reviewing Codex session logs
- Codex reads this at the START of every session and resolves OPEN items before new work
- Once resolved, Codex updates status to RESOLVED and logs what it did

---

## Two ways Claude sends feedback to Codex

### 1. Real-time (within a session — you are the messenger)

Codex proposes a config using this format:
```
[CODEX-PROPOSED] Project X / Phase X / Device: NAME
─────────────────────────────
! config here
─────────────────────────────
PENDING-CLAUDE-REVIEW
```

You copy that block to Claude Code. Claude responds with:
```
[CLAUDE-REVIEW] Project X / Phase X / Device: NAME
STATUS: APPROVED | CORRECTIONS REQUIRED

Issues found:
- description and fix

Corrected config:
! corrected lines

Safe to apply to CML: YES | NO
```

You paste Claude's `[CLAUDE-REVIEW]` block back into Codex. Codex acts on it immediately.

### 2. Persistent (between sessions — Codex reads at session start)

Claude appends entries below. Status meanings:
- **OPEN** = not yet addressed — resolve before starting new work
- **RESOLVED** = already fixed — read for context only
- **INFO** = no action needed, background context only

---

<!-- Claude appends persistent review entries below this line -->
