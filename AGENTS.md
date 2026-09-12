## Shared workflow

Read `E:/Homelab-Repos/family-projects/AGENTS.md` once per session
(`/mnt/e/Homelab-Repos/family-projects/AGENTS.md` in WSL). If working outside
this workspace, fetch the shared contract from
`vushueh/family-projects-ai-playbook` before homelab operations.
It owns task-scoped reads and publication authority; this repo owns technical
constraints. For a named file task, read target files and related OPEN items.
For project selection/status/resume, use the shared goal skill and freshness
checks; preserve the active item, dependencies, queue order and WIP limits.
Either operating agent may publish the authorized package. Use explicit paths
and relevant checks, preserve dirty work and intentionally unpublished overlays.

# Codex Standing Orders — Enterprise Network Labs

You are working on Leonel's enterprise network lab series built in Cisco CML 2.9.
GitHub repo: `vushueh/enterprise-network-labs` (main branch)
Canonical WSL view: `/mnt/e/Homelab-Repos/family-projects/enterprise-network-labs/`

---

## Task context

Read the target files and relevant OPEN items. For project status/selection use
the shared goal skill; this completed series is reference material. Read matching
troubleshooting history and WORKFLOW-REFERENCE only when the task needs them.

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

Use the canonical shared E:/Homelab-Repos/family-projects/enterprise-network-labs
checkout (WSL /mnt/e/ view). If sandbox restrictions prevent a write, prepare the
exact patch in the session workspace and use the supported approval path.
Preserve the documented project layout and all evidence; no blanket staging.

## Publication

Publish only the user-authorized package after scoped verification. Either
operating agent may commit, push and merge through available tools. Record the
changed paths and synchronization result; no automatic session-end push.

## How to present configurations to Claude for review

After writing a phase config, always present it in this exact format so Leonel can
copy it cleanly to Claude Code:

```
[CODEX-PROPOSED] Project 8 / Phase X / Device: HQ-RTR1
─────────────────────────────────────────────────────
! full config here
─────────────────────────────────────────────────────
PENDING-CLAUDE-REVIEW — do not apply to CML until Claude approves.
```

---

## How to act on Claude's feedback (pasted back by Leonel)

When Leonel pastes a message that starts with `[CLAUDE-REVIEW]`, that is Claude's
response. Act on it immediately — do not ask for clarification first.

Claude's feedback will follow this format:

```
[CLAUDE-REVIEW] Project 8 / Phase X / Device: HQ-RTR1
STATUS: APPROVED | CORRECTIONS REQUIRED

Issues found:
- [issue description and fix]

Corrected config:
! corrected lines here

Safe to apply to CML: YES | NO — [reason if no]
```

If STATUS is `CORRECTIONS REQUIRED`:
1. Update your proposed config with Claude's corrections
2. Show the corrected version in full
3. Confirm: "Updated config incorporates Claude's corrections. Ready for CML."

If STATUS is `APPROVED`:
1. Confirm: "Config approved by Claude. Ready for CML."
2. Leonel applies it to CML

---

## Cross-session critiques (CLAUDE-REVIEW.md on GitHub)

Claude also writes persistent review items to `CLAUDE-REVIEW.md` on GitHub between
sessions. These appear at session start when you read the bridge files.
Items marked `OPEN` must be resolved before starting new phase work.

---

## Project structure

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

Read current owner documentation for CML version and topology. Determine tool
capabilities from the current session rather than historical sandbox assumptions.

## Master Program Selection

This repo is completed reference material, not an active queue project. Invoke
the local `/goal` wrapper or read `../docs/homelab-goals.yaml` before any use.
The queue may read its topologies but cannot reopen or modify it implicitly.
Any reopening requires an explicit program/repo decision and normal safety,
review, closeout, commit, and push gates.
