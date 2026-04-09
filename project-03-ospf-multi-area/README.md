# Project 03 — OSPF Multi-Area Enterprise Network

> **Difficulty**: CCNP ENCOR (350-401) Level
> **Status**: 🔜 Future Project (build after CCNA exam)
> **Prereq**: Complete Project 01 + 02, pass CCNA 200-301

---

## Scenario

You are a network engineer at a growing enterprise with a headquarters campus, a remote branch office, and a data center. The network has scaled beyond a single OSPF area and is experiencing slow convergence, large LSDBs, and memory pressure on branch routers.

**Your task**: Redesign the OSPF domain using multi-area best practices to improve scalability, convergence, and fault isolation.

---

## Topology

```
                    ┌──────────────────────┐
                    │     AREA 0           │
                    │    (Backbone)        │
              ┌─────┤  R-CORE1 ↔ R-CORE2  ├─────┐
              │     └──────────────────────┘     │
              │                                  │
           [ABR1]                             [ABR2]
          /      \                           /      \
    Area 1        Area 2              Area 1        Area 3
 (Standard)   (Totally                           (NSSA)
               Stubby)
       |              |                    |            |
  R-CAMPUS1      R-BRANCH1            R-CAMPUS1     R-DC1
       |              |                              (ASBR)
   PC-CAMPUS     PC-BRANCH                          PC-DC
                                              (redistributes
                                              192.168.100.0/24)
```

---

## Area Design Summary

| Area | Type | Routers | Purpose |
|------|------|---------|---------|
| Area 0 | Backbone | R-CORE1, R-CORE2 | Redundant backbone — all inter-area traffic transits here |
| Area 1 | Standard | ABR1, ABR2, R-CAMPUS1 | Campus — dual ABR redundancy, full routing table |
| Area 2 | Totally Stubby | R-BRANCH1 | Branch office — single default route only, minimal LSDB |
| Area 3 | NSSA (Totally) | R-DC1 | Data center — local ASBR redistributes external routes |

---

## IP Addressing

### Backbone (Area 0)
| Link | Subnet | Device A | Device B |
|------|--------|----------|----------|
| CORE1 ↔ CORE2 | 10.0.0.0/30 | 10.0.0.1 | 10.0.0.2 |
| CORE1 ↔ ABR1 | 10.0.1.0/30 | 10.0.1.1 | 10.0.1.2 |
| CORE1 ↔ ABR2 | 10.0.2.0/30 | 10.0.2.1 | 10.0.2.2 |
| CORE2 ↔ ABR1 | 10.0.3.0/30 | 10.0.3.1 | 10.0.3.2 |
| CORE2 ↔ ABR2 | 10.0.4.0/30 | 10.0.4.1 | 10.0.4.2 |

### Area 1 (Standard) — summarized as 10.1.0.0/16
| Link | Subnet | Device A | Device B |
|------|--------|----------|----------|
| ABR1 ↔ R-CAMPUS1 | 10.1.0.0/30 | 10.1.0.1 | 10.1.0.2 |
| ABR2 ↔ R-CAMPUS1 | 10.1.0.4/30 | 10.1.0.5 | 10.1.0.6 |
| Campus LAN | 10.1.10.0/24 | GW: 10.1.10.1 | PC: 10.1.10.10 |

### Area 2 (Totally Stubby) — summarized as 10.2.0.0/16
| Link | Subnet | Device A | Device B |
|------|--------|----------|----------|
| ABR1 ↔ R-BRANCH1 | 10.2.0.0/30 | 10.2.0.1 | 10.2.0.2 |
| Branch LAN | 10.2.10.0/24 | GW: 10.2.10.1 | PC: 10.2.10.10 |

### Area 3 (NSSA) — summarized as 10.3.0.0/16
| Link | Subnet | Device A | Device B |
|------|--------|----------|----------|
| ABR2 ↔ R-DC1 | 10.3.0.0/30 | 10.3.0.1 | 10.3.0.2 |
| DC LAN | 10.3.10.0/24 | GW: 10.3.10.1 | PC: 10.3.10.10 |

### Loopbacks (Router IDs)
| Router | Loopback | Area |
|--------|----------|------|
| R-CORE1 | 1.1.1.1/32 | 0 |
| R-CORE2 | 2.2.2.2/32 | 0 |
| ABR1 | 3.3.3.3/32 | 0 |
| ABR2 | 4.4.4.4/32 | 0 |
| R-CAMPUS1 | 5.5.5.5/32 | 1 |
| R-BRANCH1 | 6.6.6.6/32 | 2 |
| R-DC1 | 7.7.7.7/32 + 192.168.100.1/24 (external) | 3 |

---

## Lab Phases

### Phase 1 — Build Area 0 Backbone
- Configure R-CORE1 and R-CORE2
- Verify: `show ip ospf neighbor` shows FULL state between cores

### Phase 2 — Connect ABRs to Area 0
- Configure ABR1 and ABR2 Area 0 interfaces
- Verify: All 4 Area 0 neighbors in FULL state

### Phase 3 — Area 1 (Standard Area)
- Configure ABR1 E0/2, ABR2 E0/2, and R-CAMPUS1
- Verify: R-CAMPUS1 has two OSPF neighbors (ABR1 + ABR2)
- Verify: `show ip route ospf` on R-CORE1 shows `O IA 10.1.0.0/16` (summary)

### Phase 4 — Area 2 (Totally Stubby)
- Configure ABR1 E0/3 and R-BRANCH1
- Verify: `show ip route ospf` on R-BRANCH1 shows ONLY `O*IA 0.0.0.0/0`
- Verify: R-BRANCH1 can ping PC-CAMPUS via default route

### Phase 5 — Area 3 (NSSA + ASBR)
- Configure ABR2 E0/3 and R-DC1
- Verify: `show ip ospf database nssa-external` on R-DC1 shows Type 7 LSA
- Verify: `show ip ospf database external` on ABR2 shows Type 5 (translated)
- Verify: `show ip route 192.168.100.0` on R-CORE1 shows `O E2`

### Phase 6 — ABR Failover Test
- Shut down ABR1 (`shutdown` on all interfaces)
- Verify: Traffic from Area 1 still flows via ABR2
- Verify: Area 2 (Totally Stubby) loses connectivity (single-homed — expected!)
- Restore ABR1 and verify reconvergence

---

## Key Learning Objectives

After completing this lab you will be able to:

- [ ] Explain why multi-area OSPF is needed for enterprise scale
- [ ] Configure and verify all 4 OSPF area types
- [ ] Implement dual ABRs for redundancy and explain the failover behavior
- [ ] Configure route summarization at ABRs and explain the benefit
- [ ] Distinguish Type 3, Type 5, and Type 7 LSAs in the LSDB
- [ ] Explain the Type 7 → Type 5 translation process at the ABR
- [ ] Implement OSPF MD5 authentication across all areas
- [ ] Use `show ip ospf database` to verify LSA scope per area type

---

## CCNP ENCOR Exam Topics Covered

- 3.1 — Layer 3 technologies: OSPF
- 3.1.a — OSPF area types
- 3.1.b — Multi-area OSPF
- 3.1.c — OSPF route summarization
- 3.1.d — OSPF authentication

---

## Files

```
project-03-ospf-multi-area/
├── README.md                   ← This file
├── cml/
│   └── ospf-multi-area.yaml    ← Import into CML
├── configs/
│   ├── R-CORE1.txt             ← Area 0 backbone router
│   ├── R-CORE2.txt             ← Area 0 backbone router
│   ├── ABR1.txt                ← ABR: Area 0 + Area 1 + Area 2
│   ├── ABR2.txt                ← ABR: Area 0 + Area 1 + Area 3
│   ├── R-CAMPUS1.txt           ← Area 1 standard area
│   ├── R-BRANCH1.txt           ← Area 2 totally stubby
│   └── R-DC1.txt               ← Area 3 NSSA + ASBR
└── notes/
    └── DESIGN-NOTES.md         ← Design decisions and research
```
