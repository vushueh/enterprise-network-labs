# Codex Action Log

This file is written by **Codex** and read by **Claude Code**.
Codex appends a session summary at the end of every session.
Claude reads this to understand what Codex did without parsing the full session JSONL.

---

## 2026-05-09 — Project 8 planning and bridge setup session

**What was done:**
- Read local CCNA project home, confirmed P05/06/07 complete on GitHub, P08 open
- Laid out Project 8 plan: GRE tunnel (Tunnel0, 10.0.100.0/30), IKEv2/IPsec later, OSPF over tunnel
- Updated local project-home handoff notes (Windows only, not pushed to GitHub)
- Participated in Claude-Codex bridge setup coordination (AGENTS.md, CLAUDE-REVIEW.md, CODEX-LOG.md)

**Pushed to GitHub:** CODEX-LOG.md test write only
**Left off at:** Project 8 not yet started in CML — baseline verification pending

---

## PROJECT 8 KICKOFF — Ready to build

**Project:** 08 — Site-to-Site VPN
**Status:** NOT STARTED — CML work begins next session
**Claude Phase 1 review:** APPROVED (see CLAUDE-REVIEW.md)

### What Project 8 builds
GRE tunnel between HQ-RTR1 and BR-RTR1, layered with IKEv2/IPsec encryption,
with OSPF preferring the tunnel path over physical WAN links.

### Phases
| Phase | What gets built |
|-------|----------------|
| 1 | GRE tunnel (Tunnel0), OSPF over tunnel, no encryption yet |
| 2 | IKEv2/IPsec encryption on the GRE tunnel |
| 3 | Verify OSPF prefers tunnel, physical WAN stays as fallback |
| 4 | Break/fix — deliberately fault the tunnel, diagnose, restore |

### Phase 1 config — APPROVED by Claude, ready for CML

**HQ-RTR1:**
```
interface Tunnel0
 description GRE-TO-BR-RTR1-TUN0-P08
 ip address 10.0.100.1 255.255.255.252
 ip mtu 1400
 ip tcp adjust-mss 1360
 ip ospf 1 area 0
 ip ospf network point-to-point
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 OSPF-WAN-KEY
 ip ospf cost 5
 tunnel source Ethernet0/1
 tunnel destination 10.0.0.2
 tunnel mode gre ip
 no shutdown

router ospf 1
 no passive-interface Tunnel0
```

**BR-RTR1:**
```
interface Tunnel0
 description GRE-TO-HQ-RTR1-TUN0-P08
 ip address 10.0.100.2 255.255.255.252
 ip mtu 1400
 ip tcp adjust-mss 1360
 ip ospf 1 area 0
 ip ospf network point-to-point
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 OSPF-WAN-KEY
 ip ospf cost 5
 tunnel source Ethernet0/1
 tunnel destination 10.0.0.1
 tunnel mode gre ip
 no shutdown

router ospf 1
 no passive-interface Tunnel0
```

### Before applying Phase 1 — run these baselines in CML first
```
! On HQ-RTR1:
show ip interface brief
show ip ospf neighbor
show ip route 10.2.0.0

! On BR-RTR1:
show ip interface brief
show ip ospf neighbor
show ip route 10.1.0.0
```

### Phase 1 verification commands (after applying)
```
! Both routers — tunnel should be up/up:
show interface Tunnel0
show ip ospf neighbor
show ip route 10.0.100.0

! HQ-RTR1 — traffic should prefer tunnel:
traceroute 10.2.100.1 source 10.1.100.1
show ip ospf neighbor detail
```

---

<!-- Codex appends new session entries below this line -->
