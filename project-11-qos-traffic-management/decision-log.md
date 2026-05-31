# Project 11 — Decision Log

## DL-01 — Pilot on HQ-RTR1 First, Not All Routers

**Decision:** Apply QoS classification and marking only on `HQ-RTR1` before expanding to `BR-RTR1` or `WAN-RTR1`.

**Why:** HQ-RTR1 sees HQ LAN traffic, branch WAN traffic, and default-route/firewall traffic — the broadest traffic mix. Piloting here proves the classification model before it touches every router. A broken WAN policy on HQ-RTR1 is recoverable from console; a broken policy on all three routers simultaneously is harder to triage.

---

## DL-02 — Apply Marking Policy on Ethernet0/0.100, Not the Physical Trunk

**Decision:** Attach `P11-MARK-IN` inbound on `Ethernet0/0.100` (VLAN 100 subinterface) rather than `Ethernet0/0` (the physical trunk) or all subinterfaces.

**Why:** VLAN 100 (Engineering) is the only VLAN with confirmed live hosts at the time of Phase 2. Applying to the physical trunk would affect all HQ VLANs simultaneously. Piloting on one VLAN limits blast radius and lets you confirm the policy works on known traffic before expanding.

---

## DL-03 — Do Not Remark class-default in P11-MARK-IN

**Decision:** Leave `class-default` without a `set dscp` action in `P11-MARK-IN`.

**Why:** Remarking all unmatched traffic (e.g., `set dscp default`) resets any existing DSCP markings that entered the network pre-marked by endpoints. During a pilot, preserving existing markings is safer than overwriting them. This can be changed to a trust-boundary policy in a later phase.

---

## DL-04 — Shape to 1 Mbps on Ethernet0/1

**Decision:** Use `shape average 1000000` (1 Mbps) as the parent shaping rate on the HQ-to-branch WAN link.

**Why:** CML lab interfaces run at much higher speeds than real WAN links. Without shaping, the QoS queuing policy has no congestion to manage and DSCP class counters will never increment (there is no queue to build). The 1 Mbps shape creates artificial congestion that exercises the LLQ and bandwidth guarantees.

---

## DL-05 — LLQ (Priority) for Voice, Not Just Bandwidth Guarantee

**Decision:** Use `priority percent 30` for `P11-DSCP-VOICE` rather than `bandwidth percent 30`.

**Why:** `priority` creates a strict Low Latency Queue — voice traffic gets served before all other queues, with a latency guarantee. `bandwidth` only guarantees minimum throughput but does not reduce latency. Voice-like RTP traffic (EF-marked) requires both low latency and low jitter, not just bandwidth.

---

## DL-06 — ACL-Based Fallback When NBAR Does Not Classify

**Decision:** When NBAR counters stayed at zero for HTTP and DNS traffic, add an ACL-based class (`P11-BULK-DATA-ACL`) rather than declaring Phase 5 as a failure.

**Why:** The goal of Phase 5 is to prove that MQC can classify, mark, and count real traffic. IOL's NBAR PDL limitation means NBAR syntax is accepted but does not process live packets. ACL-based classification is a real-world technique used when NBAR is unavailable or insufficient. Using it here proves the same MQC capability with a reliable alternative.

---

## DL-07 — Voice VLAN at Branch Only in Phase 6

**Decision:** Add `switchport voice vlan 500` only at the branch (`BR-ASW1`), not at HQ access switches.

**Why:** `HQ-RTR1 Ethernet0/0.500` (the HQ Voice VLAN gateway) was previously removed. Adding voice VLAN at HQ access switches without a functioning gateway subinterface would create an incomplete configuration. Branch was confirmed ready — gateway (10.2.50.1) up, VLAN 500 on all trunks. HQ voice VLAN expansion is a future controlled step.
