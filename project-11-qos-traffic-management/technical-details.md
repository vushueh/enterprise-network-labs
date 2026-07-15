# Project 11 — QoS Traffic Management

**Series:** Enterprise Network Labs — Project 11 of 13
**Platform:** Cisco CML 2.9 — IOL routers, IOL-L2 switches
**Build Date:** 2026-05-31
**Status:** Complete ✅

---

## STAR Summary

**Situation:** The enterprise network built across Projects 01–10 had no QoS policy. All traffic — voice, control plane, bulk data, and background applications — competed equally for the 1 Mbps WAN link between HQ and the branch. Without classification or queuing, time-sensitive traffic like RTP audio could be delayed or dropped during congestion.

**Task:** Implement an end-to-end QoS framework using NBAR-based traffic classification, DSCP marking, MQC hierarchical queuing and shaping on the HQ-to-branch WAN edge, and Voice VLAN 500 provisioning on the branch access layer.

**Action:**
- Phase 0: Confirmed OSPF health, NBAR support, and clean QoS baseline on HQ-RTR1, BR-RTR1, and WAN-RTR1
- Phase 1: Created four NBAR class-maps on HQ-RTR1 (RTP, SIP, OSPF/DNS, FTP/HTTP)
- Phase 2: Built `P11-MARK-IN` policy-map and applied it inbound on Ethernet0/0.100 — DSCP EF, CS3, CS2, AF11
- Phase 3: Built hierarchical WAN policy — 1 Mbps parent shaper (`P11-WAN-SHAPE-1M`) nesting LLQ child policy (`P11-WAN-QUEUE`) — applied outbound on Ethernet0/1
- Phase 4: Full `show policy-map interface` verification of both policies — no drops, queueing strategy confirmed as class-based
- Phase 5: Live HTTP traffic generated from PC-ENG1 — NBAR did not classify traffic on IOL, ACL-based fallback (`P11-BULK-DATA-ACL`) used and confirmed 54 packets marked DSCP AF11
- Phase 6: Voice VLAN 500 added to branch access ports on BR-ASW1 — data VLANs unchanged
- Phase 7: AutoQoS tested on BR-ASW1 Ethernet1/2 — `auto qos` command rejected on IOL-L2; documented as platform limitation
- Break/Fix: Deliberately emptied `P11-BULK-DATA-ACL` class-map (`no match`), observed traffic falling to class-default, diagnosed with `show class-map`, restored and re-verified

**Result:** Working hierarchical QoS policy on HQ-RTR1 with live traffic evidence. DSCP AF11 marking confirmed on 54 real HTTP packets. WAN shaper operating at 1 Mbps with no drops. Voice VLAN 500 active at the branch. Platform limitations documented with working alternatives.

---

## Topology

Devices involved in this project:

```
HQ-RTR1 (10.0.255.1)
 ├── Ethernet0/0.100  <- P11-MARK-IN (inbound DSCP marking, VLAN 100 pilot)
 └── Ethernet0/1      <- P11-WAN-SHAPE-1M (outbound shaping + queuing to BR-RTR1)

BR-RTR1 (10.0.255.2)
 └── Ethernet0/0.500  <- Voice VLAN 500 gateway (10.2.50.1) — pre-existing

BR-DSW1
 └── Trunks carry VLAN 500 — pre-existing, no changes

BR-ASW1
 ├── Ethernet1/0  <- switchport voice vlan 500 added (data: VLAN 100)
 └── Ethernet1/1  <- switchport voice vlan 500 added (data: VLAN 200)

PC-ENG1 (10.1.100.194) — traffic source for Phase 5 testing
Nginx server (10.1.40.10)  — HTTP target
```

---

## Phase 0 — QoS Readiness Check

**Goal:** Confirm topology health and NBAR support before any QoS configuration.

**OSPF:** All three pilot routers (HQ-RTR1, BR-RTR1, WAN-RTR1) show FULL adjacencies on all paths.

**NBAR precheck:** `match protocol http` accepted on all three routers. Temporary test class-maps removed cleanly.

**Baseline latency:**

```text
HQ-RTR1 → BR-RTR1:  min/avg/max = 1/2/4 ms
HQ-RTR1 → WAN-RTR1: min/avg/max = 1/1/2 ms
```

**Existing QoS:** None — no active policy-maps, only class-default.

---

## Phase 1 — NBAR Classification (HQ-RTR1)

**Goal:** Build class-maps that identify traffic types. No marking or queuing yet.

**Precheck:** `match protocol rtp` and `match protocol ospf` both accepted on IOL.

**Class-maps applied:**

```ios
class-map match-any P11-VOICE-LIKE
 match protocol rtp

class-map match-any P11-SIGNALING
 match protocol sip

class-map match-any P11-BULK-DATA
 match protocol ftp
 match protocol http

class-map match-any P11-NETWORK-CONTROL
 match protocol ospf
 match protocol dns
```

**Verification:** `show class-map` confirmed all four class-maps present with correct match statements. No class-map empty.

---

## Phase 2 — DSCP Marking (HQ-RTR1)

**Goal:** Apply inbound DSCP marking to VLAN 100 traffic on HQ-RTR1.

**Policy applied to Ethernet0/0.100:**

```ios
policy-map P11-MARK-IN
 class P11-VOICE-LIKE
  set dscp ef
 class P11-SIGNALING
  set dscp cs3
 class P11-NETWORK-CONTROL
  set dscp cs2
 class P11-BULK-DATA
  set dscp af11
```

**DSCP values selected:**

| Class | DSCP | Value | Reason |
|---|---|---|---|
| Voice-like RTP | EF | 46 | Expedited Forwarding — minimum latency/jitter |
| SIP signaling | CS3 | 24 | Standard marking for call control |
| OSPF/DNS | CS2 | 16 | Infrastructure traffic gets preferential identification |
| FTP/HTTP bulk | AF11 | 10 | Low-priority assured forwarding |
| Everything else | Unchanged | — | Avoid remarking unknown traffic during pilot |

**Verification:** Policy visible on Ethernet0/0.100. VLAN 100 hosts (10.1.100.170, 10.1.100.194) still reachable. class-default saw 16 packets confirming policy is active.

---

## Phase 3 — WAN Edge Queuing And Shaping (HQ-RTR1 Ethernet0/1)

**Goal:** Apply hierarchical outbound QoS policy on the HQ-to-branch WAN link.

**Design — Hierarchical QoS (HQoS):**

```
P11-WAN-SHAPE-1M (parent — shape to 1 Mbps)
  └── P11-WAN-QUEUE (child — LLQ priority queuing)
        ├── P11-DSCP-VOICE        priority percent 30  (300 kbps)
        ├── P11-DSCP-SIGNALING    bandwidth percent 10 (100 kbps)
        ├── P11-DSCP-NETWORK-CONTROL bandwidth percent 5 (50 kbps)
        ├── P11-DSCP-BULK         bandwidth percent 15 (150 kbps)
        └── class-default         fair-queue
```

Bandwidth allocation: 60% committed (30+10+5+15), 40% best-effort to class-default.

**Verification:**

```text
show policy-map interface Ethernet0/1

Service-policy output: P11-WAN-SHAPE-1M
  shape (average) cir 1000000
  Service-policy : P11-WAN-QUEUE
    P11-DSCP-VOICE priority 30% (300 kbps)
    P11-DSCP-SIGNALING bandwidth 10% (100 kbps)
    P11-DSCP-NETWORK-CONTROL bandwidth 5% (50 kbps)
    P11-DSCP-BULK bandwidth 15% (150 kbps)
    class-default Fair-queue
```

Post-policy pings: 10/10 to both 10.0.255.2 and 10.0.255.3. No disruption.

---

## Phase 4 — Policy Map Verification

**Goal:** Full `show policy-map interface` deep read on both applied policies.

**Interface queue status:**

```text
show interfaces Ethernet0/1
  Queueing strategy: Class-based queueing
  Input queue drops: 0
  Total output drops: 0
```

`Class-based queueing` confirms HQoS is active. Zero drops at test traffic levels. class-default counters on the WAN output: 1568 packets, 111544 bytes — normal unmatched traffic using the best-effort pool.

---

## Phase 5 — Traffic Generation And Testing

**Goal:** Generate live traffic and observe QoS class counters move.

**HTTP target found:** nginx server at 10.1.40.10. `wget -O - http://10.1.40.10` succeeded (Welcome to nginx! response).

**NBAR classification result:** IOL accepted NBAR syntax but did NOT classify live HTTP or DNS traffic. `match protocol http` and `match protocol dns` counters stayed at zero despite confirmed traffic crossing the router (ACL hit counts confirmed). This is an IOL NBAR PDL limitation.

**ACL fallback — working solution:**

```ios
ip access-list extended P11-HTTP-TRAFFIC
 permit tcp host 10.1.100.194 host 10.1.40.10 eq www

class-map match-any P11-BULK-DATA-ACL
 match access-group name P11-HTTP-TRAFFIC

policy-map P11-MARK-IN
 class P11-BULK-DATA-ACL
  set dscp af11
```

**Evidence:**

```text
Class-map: P11-BULK-DATA-ACL
  54 packets, 4410 bytes
  Match: access-group name P11-HTTP-TRAFFIC  54 matches
  QoS Set — dscp af11 — Packets marked: 54
```

54 real HTTP packets matched, marked AF11, and confirmed. Phase 5 pass condition met.

---

## Phase 6 — Voice VLAN Branch Pilot (BR-ASW1)

**Goal:** Add `switchport voice vlan 500` to branch access ports.

**Precheck result:** No changes needed on BR-RTR1 or BR-DSW1 — VLAN 500 existed, trunks already carrying it, gateway (10.2.50.1) already up.

**BR-ASW1 changes applied:**

```ios
interface Ethernet1/0
 switchport voice vlan 500   ! data: VLAN 100 unchanged

interface Ethernet1/1
 switchport voice vlan 500   ! data: VLAN 200 unchanged
```

**Verification:**

```text
show interfaces Ethernet1/0 switchport
  Access Mode VLAN: 100 (ENGINEERING)
  Voice VLAN: 500 (VOICE)

show vlan brief | include 500
  500  VOICE  active  Et1/0, Et1/1
```

---

## Phase 7 — AutoQoS Review (BR-ASW1)

**Goal:** Compare Cisco AutoQoS against the manual MQC design.

**Result:** IOL-L2 rejects all AutoQoS commands (`auto qos`, `show auto qos`, `show mls qos` — all `% Invalid input`). Platform limitation. No configuration applied. Manual MQC from earlier phases remains the working design.

---

## Break / Fix — Empty Class-Map

**Fault injected:** `no match access-group name P11-HTTP-TRAFFIC` removed the match statement from `P11-BULK-DATA-ACL`, creating `Match none`.

**Symptom observed:** HTTP traffic still crossed the router (ACL incremented) but the QoS class counter froze — traffic fell to class-default instead.

**Diagnosis command:**

```ios
show class-map P11-BULK-DATA-ACL
  Match none
```

`Match none` is visible immediately. Root cause identified without needing to look at the policy-map.

**Fix:** `match access-group name P11-HTTP-TRAFFIC` restored. Post-fix: 66 packets in P11-BULK-DATA-ACL, 66 marked, class-default stayed flat.

**Key lesson:** When traffic unexpectedly hits class-default, run `show class-map <name>` first. A policy-map reference to a class is valid even if the class has no match criteria — the class silently matches nothing.

---

## Platform Limitations

| # | Limitation | Evidence | Workaround |
|---|---|---|---|
| L-01 | NBAR syntax accepted but live HTTP traffic not classified by `match protocol http` on IOL | `show policy-map interface` counter stayed 0 despite confirmed HTTP traffic (ACL verified 83 hits) | ACL-based class `P11-BULK-DATA-ACL` with `match access-group name P11-HTTP-TRAFFIC` |
| L-02 | `match protocol dns` accepted but live DNS traffic not classified on IOL | ACL confirmed 12 DNS packets, NBAR counter 0 | ACL-based class would work; lab accepted `class-default` for DNS in Phase 5 |
| L-03 | AutoQoS not supported on IOL-L2 | `auto qos` → `% Invalid input` on BR-ASW1 | Manual MQC design from Project 11 |
| L-04 | WAN output DSCP class counters (P11-DSCP-VOICE etc.) stayed at zero during testing | HTTP traffic toward 10.1.40.10 exits via firewall path, not Ethernet0/1 | Marking verified on ingress; egress WAN queuing requires traffic destined to BR-RTR1 (10.0.0.x) |

---

## Troubleshooting

### T-01 — NBAR Counters Stay At Zero (All NBAR Classes)

**Symptom:** `show policy-map interface Ethernet0/0.100` shows `P11-BULK-DATA`, `P11-NETWORK-CONTROL`, `P11-VOICE-LIKE`, and `P11-SIGNALING` all at 0 packets even after generating DNS and HTTP traffic.

**Check 1 — Confirm traffic is reaching the interface:**

```ios
show access-lists ACL-VLAN100-IN
show ip arp | include 10.1.100
```

If ACL hit counts are increasing but QoS counters are not, the issue is classification, not reachability.

**Check 2 — Confirm the policy is attached:**

```ios
show running-config interface Ethernet0/0.100 | include service-policy
```

Must show `service-policy input P11-MARK-IN`.

**Check 3 — Check NBAR PDL support:**

```ios
show ip nbar protocol-discovery
```

On IOL, this may show limited protocol support.

**Resolution:** On IOL, NBAR syntax is accepted but the PDL does not reliably classify real-time HTTP or DNS traffic. Use ACL-based classification as a fallback:

```ios
ip access-list extended P11-HTTP-TRAFFIC
 permit tcp <source-host> <destination> eq www
class-map match-any P11-BULK-DATA-ACL
 match access-group name P11-HTTP-TRAFFIC
```

---

### T-02 — QoS Class Not Matching Traffic (General)

**Symptom:** Traffic expected in a specific QoS class is going to class-default instead.

**Step 1 — Check the class-map directly:**

```ios
show class-map <class-name>
```

If output shows `Match none`, the class-map has no match criteria. Restore the missing match statement.

**Step 2 — Verify policy-map references the correct class name:**

```ios
show policy-map <policy-name>
```

A typo in the class name creates a new empty class rather than referencing the existing one.

**Step 3 — Confirm traffic matches the criteria:**

For ACL-based classes, check ACL counters:

```ios
show access-lists <acl-name>
```

For NBAR classes, NBAR may not classify the protocol on IOL — see T-01.

---

### T-03 — WAN Output DSCP Class Counters Stay At Zero

**Symptom:** `show policy-map interface Ethernet0/1` shows P11-DSCP-VOICE, P11-DSCP-BULK etc. all at zero, but class-default is increasing.

**This is expected if:** Traffic is not exiting via Ethernet0/1. Check the routing:

```ios
show ip route <destination>
```

Traffic toward 10.1.40.0/24 (nginx) exits via the firewall (10.0.0.14), not toward BR-RTR1. Only traffic routed toward 10.0.0.2 (BR-RTR1 E0/1) will hit the WAN queue.

**To test WAN output queue:** Ping or generate traffic to 10.0.255.2 (BR-RTR1 Loopback0) or 10.2.x.x (branch subnets) from HQ — that traffic exits via Ethernet0/1.

---

### T-04 — Service-Policy Rejected On Interface

**Symptom:** `service-policy output P11-WAN-SHAPE-1M` rejected when applied to Ethernet0/1.

**Check 1 — Policy-map exists:**

```ios
show policy-map P11-WAN-SHAPE-1M
show policy-map P11-WAN-QUEUE
```

**Check 2 — Remove existing policy first:**

```ios
interface Ethernet0/1
 no service-policy output <old-policy>
```

You cannot apply a second service-policy output on the same interface.

**Check 3 — Child policy must exist before parent references it:**

Apply `P11-WAN-QUEUE` first, then `P11-WAN-SHAPE-1M`. If the child doesn't exist when you configure `service-policy P11-WAN-QUEUE` inside the parent, IOS creates an empty placeholder — verify both exist before applying to interface.

---

## Decision Log

See [decision-log.md](decision-log.md) for architectural decisions and tradeoffs.

## Platform Limitations — Homelab Expansion Path

See [LIMITATIONS-AND-HOMELAB-EXPANSION.md](LIMITATIONS-AND-HOMELAB-EXPANSION.md) for homelab fix paths.
