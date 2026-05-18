# Project 09 — Decision Log

**Project:** Enterprise Network Labs — Project 09 Monitoring and Visibility
**Written by:** Claude Code (design review) + Codex (implementation)
**Date:** 2026-05-17

---

## DL-01 — Tiered syslog severity levels

**Decision:** Use `warnings` (level 4) on core/distribution/firewall devices, `informational` (level 6) on access switches.

**Why:** Core devices and the firewall generate high-value operational events (OSPF adjacency changes, ACL hits, SNMP trap sourcing, VPN state) that must always reach the collector. Access switches generate large volumes of lower-severity events (port state, MAC learning) that would flood the collector if set to `informational`. Tiering reduces collector volume while ensuring critical events are never filtered.

**Trade-off considered:** Setting everything to `informational` would capture all events but makes the collector unusable at scale without a search interface. Setting everything to `warnings` risks missing access-layer events that are only `informational` severity. The tiered approach is the enterprise standard.

**Applied to:** Phase 1

---

## DL-02 — SNMPv3 authPriv on core routers only, SNMPv2c everywhere

**Decision:** Deploy SNMPv3 user `p09snmpv3` (SHA auth + AES128 privacy) on HQ-RTR1, BR-RTR1, WAN-RTR1. Use SNMPv2c community `P09V2CRO2026` with ACL-SNMP-MANAGERS on all 10 devices.

**Why:** Core routers are the highest-value SNMP targets and carry routing state, crypto session state, and WAN interface status. SNMPv3 authPriv provides authentication and encryption for polling and traps on these critical devices. Access switches and distribution switches have lower risk profiles and SNMPv2c with a tight ACL provides adequate protection without the operational overhead of per-device SNMPv3 user provisioning on every switch.

**Trade-off considered:** All-SNMPv3 would be more secure, but SNMPv3 user provisioning on IOL-L2 switches requires more per-device configuration effort and the community-based approach with ACL restriction achieves acceptable security for the lab. A production network with a LibreNMS or Zabbix collector would use SNMPv3 everywhere.

**Applied to:** Phase 2

---

## DL-03 — NTP authenticated with MD5, HQ-RTR1 as stratum-3 master

**Decision:** Configure HQ-RTR1 as `ntp master 3` using MD5 key 9. All other devices authenticate with `ntp trusted-key 9` before accepting time from 10.0.255.1.

**Why:** Without NTP authentication, a rogue device or CML misconfiguration could inject a false time source and cause all network events to be timestamped incorrectly — making syslog correlation impossible. MD5 NTP auth ensures devices only sync to the designated master. Stratum 3 is chosen because CML has no external NTP reference; a lower stratum (e.g. 1 or 2) would falsely imply GPS-level accuracy.

**Trade-off considered:** HMAC-SHA-256 NTP authentication is more secure than MD5 but requires NTP version 4 and specific platform support that is inconsistent across IOL images. MD5 is the reliable standard for Cisco IOS NTP authentication and is what CCNA-level certification validates.

**Applied to:** Phase 4

---

## DL-04 — EEM deployed on HQ-RTR1, not access switches

**Decision:** Phase 5 EEM pilot moved from HQ-ASW1 to HQ-RTR1 when IOL-L2 was confirmed as not supporting `event manager`.

**Why:** HQ-RTR1 already has the complete monitoring infrastructure (syslog source, NTP sync, SNMP traps, NetFlow export) needed to demonstrate EEM integration with the monitoring stack. Loopback99 is a safe test interface that does not interrupt production lab forwarding.

**Trade-off considered:** The original plan of using HQ-ASW1 was chosen for "low risk" (a port-channel member shutdown vs. a router loopback). After the IOL-L2 EEM limitation was confirmed, HQ-RTR1 with Loopback99 is equally low-risk and gives richer monitoring evidence because HQ-RTR1 is wired into all four monitoring systems simultaneously.

**Applied to:** Phase 5

---

## DL-05 — Config archive uses unix: path, not flash:

**Decision:** All 9 IOS/IOL devices use `archive path unix:/P09-ARCHIVE-$h-` instead of the proposed `flash:P09-ARCHIVE-$h-`.

**Why:** CML IOL and IOL-L2 images do not expose a `flash:` filesystem. `show file systems` confirms `unix:` as the available writable filesystem on these images. The `$h` variable expands to the device hostname, making each archive file self-identifying.

**Production note:** Physical IOS and IOS XE devices expose `flash:` normally. The `unix:` path is CML IOL-specific. When this lab is rebuilt on physical hardware or IOS XE VMs, change the path back to `flash:`.

**Applied to:** Phase 6

---

## DL-06 — Accept device-side only proof for SNMP traps and NetFlow

**Decision:** Phase 2 SNMP and Phase 3 NetFlow use device-side verification (`show snmp`, `show ip flow export`) as the success criteria. Collector-side proof is not required for phase completion.

**Why:** HQ-SYSLOG is a minimal syslog-ng node built during Project 07. It has no package manager, no CLI, and no SNMP or NetFlow collection software. Demanding collector-side proof would require rebuilding HQ-SYSLOG — a Project 07 change that is out of scope for Project 09. The device-side counters provide honest, accurate evidence that the IOS monitoring configuration is correct and active.

**Trade-off considered:** This means the "receiver side" of the SNMP and NetFlow monitoring loop cannot be validated within this CML topology. The limitation is fully documented in `LIMITATIONS-AND-HOMELAB-EXPANSION.md` with specific homelab resolution steps (LibreNMS for SNMP, ntopng for NetFlow).

**Applied to:** Phases 2, 3, 7

---

## DL-07 — IOL-L2 management routing fix: ip routing + static default route

**Decision:** On HQ-DSW1, HQ-DSW2, HQ-ASW1, and HQ-ASW2 — enable `ip routing` and add `ip route 0.0.0.0 0.0.0.0 10.1.99.1` in addition to (or replacing) `ip default-gateway 10.1.99.1`.

**Why:** These IOL-L2 switches could not reach HQ-RTR1 Loopback0 (10.0.255.1) via NTP, syslog, or SNMP. Investigation confirmed that `ip default-gateway` is only effective when the switch is in non-routing mode and the destination is reachable via a single next-hop. For remote subnets (Loopback0 is 10.0.255.0/24, not directly connected), the management plane requires `ip routing` to be enabled and a real routing table with a default route. After the fix, all four switches pinged 10.0.255.1 5/5 and synced NTP.

**Production note:** On real Cisco Catalyst switches in Layer-2-only mode, `ip default-gateway` behaves correctly for management traffic. IOL-L2 is not a fully faithful simulation of a real Catalyst switch in this regard.

**Applied to:** Phase 4 (carried forward to benefit Phases 5-8)
