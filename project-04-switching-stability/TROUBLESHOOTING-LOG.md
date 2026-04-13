# Project 04 — Troubleshooting Log

## P04-T01 — Storm Control rejected on IOL-L2

**Date:** 2026-04-13
**Phase:** Phase 6 — Access Port Protection
**Symptom:** `storm-control broadcast level 1.00 0.50` rejected with `% Invalid input detected at '^' marker` on HQ-ASW1 and HQ-ASW2 access interfaces.
**Root cause:** CML IOL-L2 image does not implement storm control (ASIC-level hardware feature not available in software switch image).
**Fix:** Platform limitation — not fixable in CML IOL-L2. Applied available protections (PortFast, BPDU Guard, BPDU Filter).
**Lesson:** Always verify platform feature support with `show ?` before building a phase around a specific command.

## P04-T02 — LACP member rejected when changing mode during fault injection

**Date:** 2026-04-13
**Phase:** Phase 7 — Break/Fix, Fault 1
**Symptom:** `channel-group 1 mode on` rejected with `Command rejected: the interface can not be added to the channel group` on HQ-DSW2 Et1/0.
**Root cause:** Port retained internal LACP state after `no channel-group 1`. Attempting to re-add with incompatible mode `on` while the other side was still LACP active caused a conflict.
**Fix:** Used `default interface Ethernet1/0` to fully reset the port state, then re-configured with correct LACP settings.
**Lesson:** Use `default interface` as a clean reset before re-configuring a port that was removed from an EtherChannel.

## P04-T03 — Root Inconsistent on expected ports (confirmed correct behavior)

**Date:** 2026-04-13
**Phase:** Phase 2 — Advanced STP Controls
**Symptom:** `show spanning-tree inconsistentports` showed DSW1 Et0/1 and Et0/2 as Root Inconsistent for VLANs 200/300; DSW2 Et0/1 and Et0/2 as Root Inconsistent for VLANs 100/999.
**Root cause:** Expected behavior. In a split-root design, access switches have uplinks to both distribution switches and advertise root-path BPDUs for all VLANs. Root Guard blocks the ones where the local switch is not the intended root.
**Fix:** No fix required — correct and intended behavior.
**Lesson:** Cross-reference `show spanning-tree inconsistentports` with `show spanning-tree root` to determine if an inconsistency is expected (design) or unexpected (fault).

## P04-T04 — VTP client did not sync immediately

**Date:** 2026-04-13
**Phase:** Phase 4 — VTP v3 Learning Lab
**Symptom:** After setting HQ-ASW1 to VTP v3 client mode, `show vtan brief` did not immediately show VLAN 600.
**Root cause:** VTP sync is event-driven, not instantaneous on mode change.
**Fix:** Waited 5–10 seconds, then re-ran `show vlan brief`. VLAN 600 appeared after one sync cycle.
**Lesson:** Always wait 5–10 seconds after VTP mode change before checking for VLAN propagation.

## P04-T05 — VLAN 600 persisted after returning to VTP transparent mode

**Date:** 2026-04-13
**Phase:** Phase 4 — VTP v3 Learning Lab (cleanup)
**Symptom:** After switching back to `vtp mode transparent`, VLAN 600 remained in `show vlan brief` on client switches.
**Root cause:** Changing from VTP client to transparent mode does not delete learned VLANs. The VLAN database is preserved on mode change.
**Fix:** Manually removed VLAN 600 on each affected switch with `configure terminal → no vlan 600`.
**Lesson:** Returning to VTP transparent mode is not a clean slate. Test VLANs must always be removed explicitly.
