# Troubleshooting Log — Project 06 Security Hardening

Project-local troubleshooting entries for Project 06. Add live issues here as the build progresses.

---

## P06-T01 — Planned Break/Fix: DHCP Snooping Trust on Wrong Port

**Date:** 2026-05-02

**Phase:** Break/Fix Challenge — DHCP Snooping

**Symptom:** Legitimate clients fail to receive DHCP leases after DHCP snooping is enabled.

**Root cause:** DHCP snooping trust is placed on an access port instead of the real trunk/uplink toward the authorized DHCP server path. Valid DHCP offers arrive on an untrusted interface and are dropped.

**Fix:** Remove `ip dhcp snooping trust` from the access port and apply it only to the correct uplink/trunk interface. Clear counters, renew DHCP, and verify the binding table.

**Lesson:** DHCP snooping trust is a directional trust decision. Trust the path to the real DHCP server, never the user edge.

---

## Live Issues

No live Project 06 build issues captured yet.
