---
name: goal
description: Resume and track the canonical homelab master program. Use when Leonel types /goal, asks what is active or next, starts a new session in any homelab repo or the Obsidian vault, or asks to start, block, defer, or complete a project.
---

# Homelab Goal Discovery Wrapper

This is a thin discovery wrapper. It never owns, copies, or edits program
status by itself.

## Load Canonical Control

1. Read the canonical skill completely from the first path that exists:
   - Windows: `E:\Homelab-Repos\family-projects\.claude\skills\goal\SKILL.md`
   - WSL: `/mnt/e/Homelab-Repos/family-projects/.claude/skills/goal/SKILL.md`
2. Follow that skill exactly.
3. Read canonical state/order files, not similarly named local files:
   - `family-projects/docs/state.yaml` owns current status.
   - `family-projects/docs/homelab-goals.yaml` owns queue, cycle, WIP, and dependencies.
4. Reconcile the queue-selected owning repo README/project status and
   `CLAUDE-REVIEW.md` before recommending or starting work.

## Selection Rule

Resume the active primary item. If none exists, return exactly the
lowest-sequence ready queue item. Do not give Leonel a project menu. If the
item is blocked, do not advance until it is repaired, safely rescoped, or
closed Deferred with a precise revival trigger and synchronized records.

Live mutation, credentials, purchases, destructive actions, publication,
commit, and push always remain Leonel decisions.
