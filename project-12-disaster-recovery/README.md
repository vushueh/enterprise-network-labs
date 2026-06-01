# Project 12 — Disaster Recovery

**Series:** Enterprise Network Labs — Project 12 of 13
**Platform:** Cisco CML 2.9 — IOL routers, IOL-L2 switches, ASAv
**Build Date:** 2026-05-31
**Status:** Complete ✅

---

## STAR Summary

**Situation:** The enterprise network built across Projects 01–11 had never been tested under a catastrophic failure scenario. With OSPF, VPN, AAA, QoS, and 16+ nodes all interdependent, a real power-surge or hardware failure could bring down the entire network with no documented recovery procedure.

**Task:** Design and execute a disaster recovery exercise — document the pre-disaster baseline, inject simultaneous device failures, and rebuild the two most critical nodes (HQ-RTR1 and HQ-DSW1) from scratch within a 90-minute time limit using only existing project documentation as the recovery source.

**Action:**
- Phase 0: Captured complete operational baseline for all 11 project services — OSPF, IPsec, TACACS+, QoS, VLANs, syslog, voice VLAN. All confirmed operational before fault injection.
- Phase 1: Erased startup configs on HQ-RTR1 and HQ-DSW1, reloaded both to factory default. HQ-FW1 received a partial config fault. Confirmed OSPF adjacencies collapsed and HQ LAN unreachable from branch.
- Phase 2: 90-minute timed rebuild began. HQ-RTR1 rebuilt first — hostname/SSH, interface IPs, OSPF, IKEv2/IPsec, TACACS+ AAA, full QoS policy (15 class-maps, 3 policy-maps), syslog/SNMP. Completed at T+58:32.
- Phase 3: HQ-DSW1 rebuilt — hostname/ip routing, VLANs, LACP EtherChannel, trunks, Vlan999 SVI, spanning tree priority, AAA. Completed at T+78:14.
- Phase 4: All 8 post-recovery checks run — OSPF FULL, VPN encaps/decaps, TACACS both users, VLANs/trunks, QoS policies, syslog, VLAN 100 host reachability. All passed.
- Phase 5: Runbook written — condensed rebuild sequence with timing targets and critical dependency notes.
- Break/Fix: Injected OSPF area mismatch on Ethernet0/1 (area 1 instead of area 0). Observed INIT state on local side, no neighbor entry on far side. Diagnosed with `show ip ospf interface`, fixed by correcting network statement area.

**Result:** Full network recovery in **87 minutes 10 seconds** — within the 90-minute target. All 8 post-recovery services verified. A reusable runbook written for future exercises. OSPF area mismatch break/fix reinforced the asymmetric symptoms of this common rebuild mistake.

---

## Topology

```
Devices affected by disaster:
  HQ-RTR1  (10.0.255.1) — startup config erased, full rebuild required
  HQ-DSW1               — startup config erased, full rebuild required
  HQ-FW1                — partial fault (NAT/ACL removed)

Devices NOT affected (remained operational):
  BR-RTR1  (10.0.255.2)
  WAN-RTR1 (10.0.255.3)
  BR-DSW1, BR-ASW1
  HQ-ASW1, HQ-ASW2, HQ-DSW2
  HQ-TACACS (10.1.99.52)
  HQ-RADIUS (10.1.99.53)
  Syslog (10.1.99.11)
```

---

## Phase 0 — Pre-Disaster Baseline

**Goal:** Confirm all network services are operational before the fault. This output is the recovery target.

**All services confirmed:**

| Service | Pre-Disaster State |
|---|---|
| OSPF | HQ-RTR1, BR-RTR1, WAN-RTR1 — all FULL on 3 paths |
| GRE/IPsec VPN | IKEv2 QM_IDLE, encaps: 8241 / decaps: 8197 |
| TACACS+ | Both admin and tacoper authenticated |
| QoS | P11-MARK-IN + P11-WAN-SHAPE-1M active, 0 drops |
| VLANs | 100/200/300/500/999/1000 active on HQ-DSW1 |
| Syslog | 412 messages to 10.1.99.11, 0 drops |
| VLAN 100 hosts | 5/5 both 10.1.100.170 and 10.1.100.194 |
| Voice VLAN | BR-ASW1 Et1/0, Et1/1 — Voice VLAN: 500 |

Baseline latency: HQ↔Branch 1/2/4 ms, HQ↔WAN-RTR1 1/1/2 ms.

---

## Phase 1 — Disaster Injection

**Faults injected simultaneously:**

```
HQ-RTR1:  erase startup-config → reload  (full factory reset)
HQ-DSW1:  erase startup-config → reload  (full factory reset)
HQ-FW1:   clear configure nat + clear configure access-list
```

**Confirmed impact:**

- HQ-RTR1 console shows factory default prompt, all interfaces administratively down
- HQ-DSW1 shows all ports in VLAN 1 default
- From BR-RTR1: `show ip ospf neighbor` shows only WAN-RTR1 — HQ-RTR1 gone
- `ping 10.0.255.1 source Loopback0` from BR-RTR1: 0/5

**Timer started: T+00:00**

---

## Phase 2 — Timed Rebuild: HQ-RTR1

**Priority:** HQ-RTR1 first — it is the gateway for OSPF, AAA, VPN, and QoS.

**Rebuild sequence:**

```
1. Hostname, SSH, local user (5 min)
2. All interface IPs — Loopback0, 3 subinterfaces, WAN x2, Tunnel0 (7 min)
3. OSPF — wait for FULL adjacency (6 min)
4. IKEv2/IPsec on Tunnel0 (10 min)
5. TACACS+ AAA — test aaa before Phase B (7 min)
6. Full QoS — 9 class-maps, 3 policy-maps, 2 service-policies (15 min)
7. Syslog, SNMP, write memory (5 min)
8. Spot verification (3 min)
```

**Completed: T+58:32** (58 minutes 32 seconds)

OSPF restored at T+17:40 — all 3 adjacencies FULL.
IPsec SA active at T+27:12 — encaps/decaps incrementing.
TACACS+ tested and vty lines updated at T+34:05.
QoS both service-policies confirmed at T+49:30.

---

## Phase 3 — Timed Rebuild: HQ-DSW1

**Priority:** Second — depends on HQ-RTR1 being up for management VLAN reachability.

**Rebuild sequence:**

```
1. Hostname, ip routing, SSH, local user (3 min)
2. VLANs 100/200/300/500/999/1000 (2 min)
3. LACP EtherChannel Po1 to HQ-DSW2 (3 min)
4. Trunks to HQ-RTR1/HQ-ASW1/HQ-ASW2 (4 min)
5. Vlan999 SVI + default gateway (2 min)
6. Spanning tree priority 4096 (2 min)
7. AAA + write memory (3 min)
```

**Completed: T+78:14** (78 minutes 14 seconds)

VLANs 100/200/300/500/999/1000 all active.
LACP Po1 — `SU`, both E0/2 and E0/3 bundled.
HQ-DSW1 confirmed as root bridge (priority 4096 + VLAN ID).
Management VLAN 999 SVI up, ping to 10.1.99.1 5/5.

---

## Phase 4 — Post-Recovery Verification

**All 8 checks passed at T+87:10:**

| Check | Result |
|---|---|
| OSPF full mesh | ✅ All 3 adjacencies FULL |
| End-to-end pings | ✅ 20/20 to all loopbacks, 5/5 to hosts |
| GRE/IPsec VPN | ✅ QM_IDLE, encaps 198/decaps 182 |
| TACACS+ AAA | ✅ Both users authenticated, SSH at correct priv levels |
| HQ-DSW1 VLANs/trunks | ✅ All VLANs active, 4 trunks up, root bridge confirmed |
| QoS policies | ✅ Both service-policies active, 0 drops |
| Syslog | ✅ 28 messages to 10.1.99.11, 0 dropped |
| VLAN 100 hosts | ✅ 5/5 both 10.1.100.170 and 10.1.100.194 |

**RECOVERY TIME: 87 minutes 10 seconds — PASS (target: 90 minutes)**

---

## Phase 5 — Runbook And Lessons Learned

**Critical dependency order (must follow this sequence):**

1. OSPF must be FULL before testing IPsec (routing required for VPN negotiation)
2. `test aaa group tacacs+` must pass before changing vty login authentication
3. LACP EtherChannel before trunk configuration on HQ-DSW1
4. `ip routing` before SVI configuration on HQ-DSW1 (factory default is no ip routing)
5. `write memory` explicitly after each device — reload wiped startup, it does not come back automatically

**Biggest time consumer:** QoS restoration — 15 minutes for 9 class-maps, 3 policy-maps, 2 service-policies. Pre-staged config blocks would reduce this to under 3 minutes.

---

## Break / Fix — OSPF Area Mismatch

**Fault:** `network 10.0.0.0 0.0.0.3 area 1` (should be area 0) on HQ-RTR1 Ethernet0/1.

**Symptom:** Local router shows `INIT` state for BR-RTR1 via Ethernet0/1. BR-RTR1 shows no HQ-RTR1 entry at all. HQ LAN unreachable from branch.

**Key diagnostic:** The asymmetry is the tell — INIT on one side, nothing on the other. OSPF area mismatch is always asymmetric because the far-end silently discards hellos with an unexpected area number.

**Diagnosis command:**
```ios
show ip ospf interface Ethernet0/1
  Area 1  ← wrong, should be Area 0
```

**Fix:** Correct the network statement area number. Adjacency reforms in ~15 seconds.

---

## Platform Limitations

| # | Limitation | Impact |
|---|---|---|
| L-01 | HQ-FW1 ASAv disaster simulation was partial (config clear only, not full erase/reload) | ASAv `write erase` and reload sequence is more complex and time-consuming than IOL — full ASAv recovery is a separate exercise |
| L-02 | Recovery timer is self-timed — no automated clock | Manual stopwatch required; a real DR exercise would use a third-party observer |
| L-03 | Config archive (TFTP, P09) not tested as recovery source | Archive server reachability was not validated before the exercise. In a real DR, the archive is the primary recovery source — not memory |

---

## Troubleshooting

### T-01: OSPF Stuck In INIT State After Rebuild

**Symptom:** `show ip ospf neighbor` shows a neighbor in `INIT` or `INIT/DROTHER` — never progresses to `2WAY` or `FULL`.

**Most common causes after a rebuild:**
1. Area mismatch — see break/fix above
2. Authentication mismatch — check `ip ospf message-digest-key` on both sides
3. Passive-interface — interface still passive after rebuild (`passive-interface default` is the culprit if you forget `no passive-interface <int>`)

**Diagnosis:**
```ios
show ip ospf interface <int>
  → Check Area, Authentication, and Passive
debug ip ospf adj  (use carefully — verbose output)
```

---

### T-02: VTY Lines Locked Out After AAA Restore

**Symptom:** SSH to the device returns `Permission denied` immediately after applying `login authentication default` to vty lines.

**Cause:** TACACS+ was not reachable when the vty config was changed. The method list falls through to `local` fallback, but if `local` is not listed or the local user doesn't exist, login fails.

**Fix from console:**
```ios
configure terminal
line vty 0 4
 login local
end
```

Then confirm TACACS reachability (`ping 10.1.99.52 source Loopback0`) before re-enabling `login authentication default`.

---

### T-03: HQ-DSW1 SVI Not Responding After Rebuild

**Symptom:** `interface Vlan999` configured with IP, but `ping 10.1.99.1` from HQ-DSW1 returns `Network is unreachable`.

**Cause:** `ip routing` not configured. IOL-L2 default is `no ip routing` — SVIs cannot route packets without it.

**Fix:**
```ios
configure terminal
ip routing
end
```

---

## Decision Log

See [decision-log.md](decision-log.md) for rebuild order rationale and design decisions.

## Platform Limitations — Expansion Path

See [LIMITATIONS-AND-HOMELAB-EXPANSION.md](LIMITATIONS-AND-HOMELAB-EXPANSION.md) for how to expand this exercise.
