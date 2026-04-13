# Project 04 — Decision Log

## DL-01 — LACP over PAgP for EtherChannel

**Decision:** Use LACP (802.3ad) with `mode active` on both distribution switches.

**Alternatives considered:**
- PAgP (Cisco proprietary, `desirable` mode)
- Static EtherChannel (`mode on`)

**Why LACP was chosen:**
- Standards-based — works in any multi-vendor environment
- `active` + `active` is the most explicit negotiation mode
- `mode on` is dangerous: no negotiation, no detection of misconfiguration on the remote side. A mismatch with `mode on` causes each side to think EtherChannel is up while the other side disagrees — traffic black-hole.

---

## DL-02 — Root Guard on distribution→access downlinks, not on EtherChannel

**Decision:** Root Guard applied to Et0/1 and Et0/2 on each distribution switch. Not applied to Port-channel1.

**Why:**
- Root Guard is for ports where an unexpected superior BPDU would indicate a misplaced device (access switch trying to become root)
- Port-channel1 is the inter-distribution link — both switches are legitimate participants in STP, they should be able to exchange BPDUs freely
- Applying Root Guard to Po1 would block valid root-path BPDUs between DSW1 and DSW2

---

## DL-03 — Loop Guard on Port-channel1 (inter-distribution EtherChannel)

**Decision:** Loop Guard applied to Port-channel1 on both distribution switches.

**Why:**
- Port-channel1 is the redundant path where a unidirectional failure would be dangerous
- If BPDUs stop arriving on a designated/root port (because a fiber broke in one direction), the port would transition to forwarding based on the age timer — creating a loop
- Loop Guard prevents that transition and puts the port into Loop Inconsistent instead

---

## DL-04 — VTP transparent mode for production, VTP v3 only as a learning exercise

**Decision:** All switches run VTP transparent mode after the Phase 4 learning exercise.

**Why:**
- VTP in server/client mode is a significant operational risk: any switch with a higher revision number can accidentally overwrite the entire VLAN database of the network
- VTP v3 adds primary-server control but the risk of misconfiguration still exists
- Transparent mode is the de-facto standard for enterprise networks where VLAN changes are infrequent and must be deliberate
- Learning VTP v3 is still valuable because many existing production networks run VTP and you must understand it to troubleshoot it

---

## DL-05 — Errdisable recovery interval of 300 seconds

**Decision:** `errdisable recovery interval 300`

**Why:**
- Short enough to automatically restore service without operator intervention in most fault scenarios
- Long enough to prevent rapid port flap (if the underlying fault is still present, the port errdisables again, but there is a 5-minute window between retry attempts)
- 30 seconds would cause excessive port cycling if a rogue device is still connected
- No timeout (disabled recovery) would require manual intervention for every BPDU Guard event

---

## DL-06 — BPDU Filter on router-facing uplink, not BPDU Guard

**Decision:** `spanning-tree bpdufilter enable` on HQ-DSW1 Et0/0 (to HQ-RTR1).

**Why:**
- Routers are not STP participants — applying BPDU Guard would error-disable the port the first time a stray BPDU arrived (possible in some router/IOS versions)
- BPDU Filter stops STP from sending or receiving BPDUs on this port entirely — cleaner than BPDU Guard for a known non-switch neighbor
- BPDU Guard is correct for access ports where any BPDU is unexpected and indicates a rogue switch

---

## DL-07 — Storm control not implemented (platform limitation)

**Decision:** Storm control not configured despite being planned in the project scope.

**Why:**
- CML IOL-L2 images do not support the `storm-control` command at the interface level
- The command is rejected at parser level, confirming this is a platform capability gap, not a syntax error
- Documented as a known limitation rather than attempting a workaround

**Impact:** Low. In a real deployment, storm control would be configured on all access-facing ports with broadcast/multicast thresholds at 1–2% and `action trap` for monitoring. This would be implemented on physical Catalyst hardware.
