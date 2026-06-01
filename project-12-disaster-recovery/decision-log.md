# Project 12 — Decision Log

## DL-01 — Rebuild HQ-RTR1 Before HQ-DSW1

**Decision:** Target HQ-RTR1 first in the timed rebuild, even though both devices failed simultaneously.

**Why:** HQ-RTR1 is the dependency anchor for everything else. OSPF adjacencies require HQ-RTR1 to form (it is the router ID 10.0.255.1 that all WAN paths depend on). AAA requires HQ-RTR1 as the source-interface for TACACS+. Management VLAN 999 gateway (10.1.99.1) is on HQ-RTR1. Without HQ-RTR1, no management path exists to reach HQ-DSW1 via SSH — you must use the CML console directly. Restoring HQ-RTR1 first unlocks SSH access for all downstream devices.

---

## DL-02 — QoS Config Applied In Full During Rebuild

**Decision:** Restore the complete QoS policy (all 9 class-maps, 3 policy-maps, 2 service-policies) during the timed rebuild rather than deferring it.

**Why:** QoS is attached to live interfaces. A service-policy on Ethernet0/1 that references a policy-map that doesn't exist yet causes `% Policy-map does not exist` rejection. The order is: class-maps first, then policy-maps, then service-policy on interface. Since QoS must be rebuilt in order anyway, doing it completely is not slower than doing it partially — a partial restore would still require returning to it.

---

## DL-03 — Phase A / Phase B Split For AAA During Rebuild

**Decision:** Even during the time pressure of a rebuild exercise, apply TACACS+ AAA in two phases — Phase A (AAA config and `test aaa`) then Phase B (vty line changes).

**Why:** The same rule applies during a rebuild as during initial deployment. If TACACS is not confirmed reachable before changing vty lines, you lock yourself out and must recover from console — which costs more time than the Phase A test takes. The 2-minute cost of `test aaa` before Phase B is always worth it.

---

## DL-04 — Partial Fault For HQ-FW1 (Not Full Erase/Reload)

**Decision:** Simulate the HQ-FW1 fault by clearing NAT and ACL config (`clear configure nat`, `clear configure access-list`) rather than a full `write erase` + `reload`.

**Why:** ASAv erase and reload from factory default is significantly more complex than IOL. The ASAv boot sequence, license configuration, and initial setup take longer. The primary disaster recovery skills being tested (OSPF restore, TACACS restore, inter-VLAN routing restore) are all on IOL devices. The HQ-FW1 partial fault tests the concept without consuming the time budget on ASAv specifics, which deserve their own dedicated exercise.

---

## DL-05 — 90-Minute Time Limit

**Decision:** Set 90 minutes as the target rebuild time for this first exercise.

**Why:** 90 minutes represents a realistic RTO (Recovery Time Objective) for a small enterprise network rebuild where the engineer has full documentation. It is long enough to avoid rushing into mistakes but short enough to be a meaningful constraint. Future exercises should target 60 minutes (with pre-staged config blocks) and eventually 30 minutes (with automation from Project 13).

---

## DL-06 — OSPF Area Mismatch For Break/Fix

**Decision:** Use an OSPF area mismatch as the break/fix fault rather than an interface shutdown or wrong IP.

**Why:** Area mismatches are the most common rebuild mistake — under time pressure, engineers type `area 1` instead of `area 0` or forget which interfaces belong to which area. The symptom (INIT state on local, no neighbor on remote) is non-obvious and teaches the asymmetric nature of OSPF area negotiation. Interface shutdown and wrong IPs produce symmetric symptoms that are easier to spot.
