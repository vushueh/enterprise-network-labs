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

---

## [INFO] Project 08 / Phase 1 / HQ-RTR1 + BR-RTR1 — GRE Tunnel

**Reviewed:** 2026-05-10
**Status:** INFO — APPROVED, safe to apply to CML

**Verified against:** `project-05-internet-nat/configs/HQ-RTR1.txt` and `project-07-asav-firewall/configs/HQ-RTR1-changes.md`

All Codex assumptions confirmed correct:
- `tunnel source Ethernet0/1` — E0/1 is `10.0.0.1/30`, the HQ↔Branch WAN link ✅
- `tunnel destination 10.0.0.2` — BR-RTR1's WAN IP on the same `/30` ✅
- `tunnel source Ethernet0/1` on BR-RTR1 — HQ-RTR1 description confirms BR-RTR1 uses E0/1 ✅
- `10.0.100.0/30` tunnel subnet — no conflicts with existing address space ✅
- OSPF key `OSPF-WAN-KEY` — matches existing key on E0/1 and E0/2 ✅
- OSPF cost 5 on Tunnel0 — correctly beats E0/1 (cost 100) and WAN-RTR1 path (E0/2, cost 10) ✅
- `ip mtu 1400` / `ip tcp adjust-mss 1360` — correct values for GRE (24-byte overhead) ✅
- No `ip nat inside` on Tunnel0 — NAT was fully removed from HQ-RTR1 in P07 ✅
- `no passive-interface Tunnel0` added to OSPF — required, passive-interface default is active ✅

**Three things to be aware of (no config changes needed):**

1. **Two OSPF adjacencies expected after Phase 1** — `show ip ospf neighbor` on HQ-RTR1 will show two entries toward BR-RTR1: one over physical E0/1 (cost 100, fallback) and one over Tunnel0 (cost 5, primary). This is correct by design. Don't remove the physical adjacency — it is the fallback path.

2. **Verify `10.2.100.1` on BR-RTR1 before running the traceroute** — The verification step `traceroute 10.1.100.1 source 10.2.100.1` assumes that IP exists on BR-RTR1. Run `show ip interface brief` on BR-RTR1 first to confirm.

3. **Interface-level OSPF vs network statement style** — Tunnel0 uses `ip ospf 1 area 0` directly on the interface rather than a `network` statement in `router ospf 1`. Both methods coexist fine in IOS. The tunnel subnet `10.0.100.0/30` will be advertised into Area 0 as expected.
