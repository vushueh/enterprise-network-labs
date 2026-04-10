# Design Notes — OSPF Multi-Area Enterprise Lab

## Why These Design Decisions Were Made

### Area 0 — Two Core Routers (R-CORE1 + R-CORE2)
- Full mesh between cores gives a redundant backbone
- If one core fails, ABRs still have a path to Area 0 via the other core
- In real enterprise networks, these would be high-end switches (Catalyst 9500, Nexus 9K)

### Area 1 — Standard Area with Dual ABRs
- Standard area because the campus needs full routing knowledge (E2 routes, inter-area routes)
- Dual ABRs (ABR1 + ABR2) both connect to Area 0 AND Area 1
- R-CAMPUS1 has TWO OSPF neighbors — if ABR1 fails, traffic reroutes via ABR2 automatically
- Summarization: `area 1 range 10.1.0.0 255.255.0.0` on both ABRs
  → Area 0 only sees ONE prefix for all of Area 1, not individual /24s

### Area 2 — Totally Stubby (Branch Office)
- Single-homed branch — only ONE link to ABR1
- No need for external route details or inter-area details — just a default route
- `area 2 stub no-summary` on ABR1 → blocks Type 3, 4, 5 LSAs, injects default
- `area 2 stub` on R-BRANCH1 → accepts the stub area definition
- R-BRANCH1's LSDB has maybe 5 LSAs total — vs hundreds in a standard area
- NOTE: If ABR1 fails, Area 2 loses ALL connectivity (intentional — single-homed design)

### Area 3 — NSSA (Data Center with local ASBR)
- R-DC1 simulates a DC with a local internet breakout (192.168.100.0/24)
- Needed: ASBR capability + stub behavior = NSSA
- `area 3 nssa no-summary` on ABR2 → Totally NSSA behavior
  → R-DC1 can redistribute externals (Type 7)
  → ABR2 translates Type 7 → Type 5 for the rest of the network
  → ABR2 also injects a default into Area 3 (no-summary)
- ABR2 is the Type 7→5 translator (highest Router ID 4.4.4.4 > any other Area 3 ABR)

### Authentication — MD5 on all interfaces
- `area X authentication message-digest` enables MD5 per area
- `ip ospf message-digest-key 1 md5 OSPF-SECRET` on each interface
- Key "OSPF-SECRET" is a placeholder — use a strong password in production
- Prevents unauthorized routers from joining the OSPF domain

### Passive Interfaces
- All non-OSPF interfaces (LANs, Loopbacks) set to passive
- Loopback0 is passive because it's already directly injected via `ip ospf 1 area X`
- LAN interfaces are passive to prevent end hosts from receiving OSPF hellos

### SPF/LSA Throttle Timers
```
timers throttle spf 50 200 5000
timers throttle lsa all 50 200 5000
```
- Start: 50ms (first SPF after topology change)
- Hold: 200ms (doubles each time up to max)
- Max: 5000ms (5 seconds between SPF runs during sustained instability)
- Prevents CPU death during link flaps (e.g., a flapping WAN link)

### Point-to-Point Network Type
- All router-to-router links use `ip ospf network point-to-point`
- Eliminates DR/BDR election (saves 2x Hello/Dead timer wait)
- Faster convergence on point-to-point Ethernet links

---

## Research Reference
Based on: ~/outputs/research/ospf-multi-area-best-practices.md
Sources: RFC 2328, RFC 3101, Cisco OSPF Design Guide, CCNP ENCOR 350-401

## Certification Mapping
- CCNA 200-301: Know concepts only (Area 0, ABR, multi-area exists)
- CCNP ENCOR 350-401: Full configuration and design (this lab)

## When to Build This Lab
After passing CCNA 200-301, before or during CCNP ENCOR study.
Estimated build time: 3-4 hours for an experienced CCNA holder.
