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

# CLAUDE.md — enterprise-network-labs

Shared rules: [../AGENTS.md](../AGENTS.md) ·
[../AI-HOMELAB-PLAYBOOK.md](../AI-HOMELAB-PLAYBOOK.md). Last updated:
2026-07-04.

## What this repo owns

- The complete CML 2.9 enterprise lab series — **all 13 projects ✅ complete**
  (campus foundation → multi-site DHCP → OSPF → switching → NAT → security
  hardening → ASAv → site-to-site VPN → monitoring → AAA → QoS → DR →
  automation)
- Lab guides (PDF), diagrams, troubleshooting log, CML recovery notes
  (`docs/cml-stale-container-recovery.md`)

## Current status source

Current project status lives in
[../docs/state.yaml](../docs/state.yaml). This repo is normally reference
material; reopening a project here requires Leonel's say-so.

## What this repo must NOT touch

- The CML controller itself (192.168.10.177) beyond read-only checks without
  approval — other repos run live labs on it
- Physical lab facts → Homelab_CCNA · household network facts → route10 repo

## Repo standards

- Build → Verify → Break → Fix method with fault-injection per project — keep
  that structure if anything is ever amended
- Evidence conventions per the global `cml-evidence-documentation` skill
- Review file: CLAUDE-REVIEW.md (existing style); bridge files active

## Cross-repo links

- Homelab_CCNA explicitly expands this repo onto physical gear — its projects
  cite these labs as the virtual counterpart
- CML transit routing (VLAN 160, 192.168.160.0/30 → CML-EDGE1) is owned by
  the route10 repo
- freepbx F05 plans CML automation against the same controller — coordinate
  via review files if both become active

## `/goal` Session Start

Run `/goal next` before using this repo. The local wrapper loads the canonical
skill; if unavailable, read the family root `docs/homelab-goals.yaml`. This
repo is completed reference material; the queue may read it but may not reopen
or modify it implicitly.
