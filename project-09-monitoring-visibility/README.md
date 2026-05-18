# Project 09 — Monitoring and Visibility

**Series:** Enterprise Network Labs | **Platform:** Cisco CML 2.9 (IOL / IOL-L2 / ASAv)
**Build Date:** 2026-05-17 | **Status:** All Phases Complete ✅

---

## STAR Summary

**Situation:** Projects 01-08 built a fully routed, firewalled, encrypted enterprise network — but there was no visibility into what the network was doing. Failures were invisible until traffic stopped. There was no record of when clocks drifted, who was generating traffic, or what changed in the configuration.

**Task:** Build a monitoring stack covering syslog collection, SNMP polling and traps, NetFlow traffic baselining, authenticated NTP synchronization, EEM automated alerting, and configuration archive with rollback capability. Then run a controlled verification exercise correlating all sources simultaneously.

**Action:** Deployed syslog-ng collector on HQ-SYSLOG (10.1.99.51). Configured tiered syslog on all 10 in-scope devices using severity-appropriate levels: `warnings` on core/distribution/firewall, `informational` on access switches. Added SNMPv2c with ACL-protected community strings on all devices plus SNMPv3 authPriv (SHA + AES128) on the three core routers. Enabled classic NetFlow on HQ-RTR1 exporting to the collector. Configured authenticated NTP with MD5, HQ-RTR1 as stratum-3 master, all other devices as clients — fixed an IOL-L2 management plane routing issue (ip routing + static default route required instead of ip default-gateway alone). Deployed EEM on HQ-RTR1 to auto-generate syslog markers on interface-down events. Enabled config archive on all 9 IOS/IOL devices with `configure replace` rollback practice. Ran a controlled Phase 7 verification: shut Loopback99 on HQ-RTR1 at 23:44:16 UTC, correlated the event across local syslog, EEM history, SNMP trap counters, and NetFlow health counters. Completed Phase 8 CDP/LLDP topology discovery documenting 25 neighbor relationships across all devices.

**Result:** Full monitoring stack operational. Every device ships syslog to HQ-SYSLOG. SNMP configured and verified device-side on all 10 devices. NetFlow exporting from HQ-RTR1 with confirmed zero-error export health. NTP synchronized across all 10 devices (all stratum 4 under HQ-RTR1 stratum 3). EEM fires and forwards alert markers to the collector via syslog. All 9 IOS/IOL devices have config archive with verified rollback. 25-entry CDP/LLDP neighbor table documents the complete physical topology. Platform limitations documented in `LIMITATIONS-AND-HOMELAB-EXPANSION.md` for resolution when the lab expands to physical infrastructure.

---

## Topology

No new nodes were added in Project 09. The monitoring design uses the existing 10 in-scope devices from Projects 01-08.

| Device | Role | Monitoring Source IP |
|--------|------|---------------------|
| HQ-RTR1 | Core router — primary NTP master, NetFlow exporter, EEM host | Loopback0 10.0.255.1 |
| BR-RTR1 | Branch router | Loopback0 10.0.255.2 |
| WAN-RTR1 | WAN transit router | Loopback0 10.0.255.3 |
| HQ-DSW1 | HQ distribution switch | Vlan999 10.1.99.11 |
| HQ-DSW2 | HQ distribution switch | Vlan999 10.1.99.12 |
| BR-DSW1 | Branch distribution switch | Vlan999 10.2.99.2 |
| HQ-ASW1 | HQ access switch | Vlan999 10.1.99.13 |
| HQ-ASW2 | HQ access switch | Vlan999 10.1.99.14 |
| BR-ASW1 | Branch access switch | Vlan999 10.2.99.3 |
| HQ-FW1 | ASAv firewall | inside 10.0.0.14 |
| HQ-SYSLOG | Syslog-ng collector | eth0 10.1.99.51 |

**ISP-RTR1 excluded:** Represents outside/ISP boundary — monitoring it would require a dedicated OOB management path through the ASA.

---

## Phases

| Phase | Name | Scope | Status |
|-------|------|-------|--------|
| 1 | Syslog Infrastructure | All 10 devices → HQ-SYSLOG | ✅ Complete |
| 2 | SNMP Monitoring | SNMPv2c all devices, SNMPv3 core routers | ✅ Complete |
| 3 | NetFlow Traffic Analysis | HQ-RTR1 → HQ-SYSLOG (device-side) | ✅ Complete |
| 4 | NTP Synchronization | HQ-RTR1 master, all devices stratum 4 | ✅ Complete |
| 5 | EEM Automated Alerting | HQ-RTR1 (IOL-L2 does not support EEM) | ✅ Complete |
| 6 | Config Archive + Rollback | All 9 IOS/IOL devices | ✅ Complete |
| 7 | Monitoring Verification Exercise | Loopback99 shutdown correlated across all sources | ✅ Complete |
| 8 | CDP/LLDP Topology Discovery | All 9 IOS/IOL devices, HQ-FW1 noted as unsupported | ✅ Complete |

---

## Phase 1 — Syslog Infrastructure

### Design

- Collector: HQ-SYSLOG (10.1.99.51), syslog-ng, UDP/514
- Source interfaces: Loopback0 on routers, Vlan999 on switches, inside on HQ-FW1
- Severity tiers:
  - `warnings` (level 4): HQ-RTR1, BR-RTR1, WAN-RTR1, HQ-DSW1, HQ-DSW2, BR-DSW1, HQ-FW1
  - `informational` (level 6): HQ-ASW1, HQ-ASW2, BR-ASW1

### Key Config (applied to all IOS/IOL devices)

```text
service timestamps log datetime msec localtime show-timezone
service timestamps debug datetime msec localtime show-timezone
service sequence-numbers
logging buffered 16384 debugging
logging trap warnings          ! (or informational for access switches)
logging source-interface Loopback0   ! (or Vlan999 on switches)
logging host 10.1.99.51
```

### Verification Result

All 10 devices confirmed sending to HQ-SYSLOG. Collector received log lines from each device's management IP. EEM test event forwarded via syslog and appeared in collector stream.

---

## Phase 2 — SNMP Monitoring

### Design

- SNMPv2c: all 10 devices, community `P09V2CRO2026`, restricted by `ACL-SNMP-MANAGERS` (permit 10.1.99.51 only)
- SNMPv3 authPriv: HQ-RTR1, BR-RTR1, WAN-RTR1 — user `p09snmpv3`, SHA auth + AES128 privacy
- Trap destination: 10.1.99.51 UDP/162
- Trap source: Loopback0 on routers, Vlan999 on switches, inside on HQ-FW1
- `snmp-server ifindex persist` on all devices

### IOL Capability Note

IOL supports AES128 privacy — `show snmp user` confirmed `priv: aes 128` on all three core routers. No DES fallback required (contrast with some IOS XE platforms).

### Collector Limitation

HQ-SYSLOG is syslog-ng only. No `snmptrapd` or `snmpwalk` tools are available. All verification is device-side. Full detail in `LIMITATIONS-AND-HOMELAB-EXPANSION.md`.

### Verification Result

`show snmp` on all devices: `SNMP logging: enabled, Logging to 10.1.99.51.162`. `show snmp user` on core routers: `p09snmpv3` configured with SHA and AES128. HQ-FW1 coldstart trap transmitted — confirmed via `show snmp-server statistics: 1 Trap PDUs`.

---

## Phase 3 — NetFlow Traffic Analysis

### Design

- Device: HQ-RTR1 (only device in scope — collector limitation prevents others)
- Export: UDP/2055 → 10.1.99.51, source Loopback0
- Version: NetFlow v9
- Cache timers: active 1 min, inactive 15 sec
- Interfaces with `ip flow ingress`: Ethernet0/0.100, .200, .300, .999, Ethernet0/1, Ethernet0/2, Ethernet0/3, Tunnel0

### IOL Platform Note

`show ip flow interface` and `show ip flow top-talkers` are not supported on this IOL image. Use `show ip cache flow` and `show ip flow export` for all verification.

### Verification Result

`show ip flow export`: NetFlow v9, source 10.0.255.1, destination 10.1.99.51 UDP/2055, 54+ flows exported, 0 export failures. `show ip cache flow`: ICMP flows visible after cross-site ping including Tunnel0 return traffic (`Tu0 10.2.100.1 -> 10.1.100.1`). Flow export health counters: 0 FIB drops, 0 adjacency drops, 0 fragmentation drops.

---

## Phase 4 — NTP Synchronization

### Design

- Master: HQ-RTR1, `ntp master 3` (stratum 3, reference 127.127.1.1)
- Authentication: MD5, key 9
- All devices: `ntp authenticate`, `ntp trusted-key 9`, `ntp server 10.0.255.1 key 9`
- Sources: Loopback0 on routers, Vlan999 on switches, inside on HQ-FW1

### Issue Found and Fixed

HQ switches (DSW1, DSW2, ASW1, ASW2) could not reach 10.0.255.1 despite having `ip default-gateway 10.1.99.1` configured.

**Root cause:** IOL-L2 switches require `ip routing` enabled for the management plane to route toward remote subnets. `ip default-gateway` alone is insufficient when the destination is not in the directly connected subnet.

**Fix applied:**
```text
ip routing
ip route 0.0.0.0 0.0.0.0 10.1.99.1
```

After the fix, all four HQ switches pinged 10.0.255.1 5/5 and selected HQ-RTR1 as their NTP peer.

### Verification Result

All 10 devices synchronized to HQ-RTR1 stratum 4. `show ntp associations` shows `*~10.0.255.1`, reach 377 (or better) on all routers and branch switch. All HQ switches reach 77+ after routing fix.

---

## Phase 5 — EEM Automated Alerting

### Platform Discovery

IOL-L2 images do not support the `event manager` command. The original pilot on HQ-ASW1 was rejected with `% Invalid input detected`. Phase 5 moved to HQ-RTR1.

### Working Applet

```text
event manager applet P09_EEM_LOOP99_DOWN
 event syslog pattern "Line protocol on Interface Loopback99, changed state to down"
 action 1.0 syslog priority warnings msg "P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99"
```

### EEM Pattern Lesson

The first pattern (`"Interface Loopback99, changed state to administratively down"`) did not fire. IOS emits `%LINEPROTO-5-UPDOWN` (not `%LINK-5-CHANGED`) for the protocol-down event, and the actual message wording is:
`"Line protocol on Interface Loopback99, changed state to down"`

EEM `event syslog pattern` does a literal substring match. Always verify the exact wording with `show logging` before writing a pattern.

### Verification Result

Loopback99 shutdown triggered EEM in 3ms. EEM history shows `Actv success` at `Sun May17 18:06:42 2026`. EEM alert marker forwarded to HQ-SYSLOG and visible in collector stream from 10.0.255.1.

---

## Phase 6 — Config Archive and Rollback

### Platform Discovery

CML IOL/IOL-L2 devices do not expose `flash:`. Proposed `path flash:P09-ARCHIVE-$h-` failed on all devices. `show file systems` confirmed `unix:` as the writable filesystem.

### Config Applied (all 9 IOS/IOL devices)

```text
archive
 path unix:/P09-ARCHIVE-$h-
 maximum 5
 write-memory
```

### Rollback Practice (HQ-RTR1)

```text
! Pre-archive:
archive config

! Inject bad change:
interface Loopback99
 description P09-PHASE6-BAD-CHANGE-ROLLBACK-TEST

! Rollback:
configure replace unix:/P09-ARCHIVE-HQ-RTR1--May-17-23-30-15.736-UTC-1 force
! Result: Total number of passes: 1 / Rollback Done
! %SYS-5-CONFIG_R: Config Replace is Done
```

Post-rollback, Loopback99 description returned to `P09-PHASE5-EEM-TEST-INTERFACE`.

### Verification Result

All 9 IOS/IOL devices have archive configured under running config. Rollback verified functional on HQ-RTR1. HQ-FW1 excluded — ASAv uses `write memory` only, no `configure replace` support.

---

## Phase 7 — Monitoring Verification Exercise

### Controlled Event

Device: HQ-RTR1 — Loopback99 shutdown at `23:44:16.407 UTC May 17 2026`.

### Evidence Correlated Across All Sources

**Local syslog + EEM (HQ-RTR1):**
```text
001908: May 17 23:44:16.407 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to down
001910: May 17 23:44:16.410 UTC: %HA_EM-4-LOG: P09_EEM_LOOP99_DOWN: P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99
001912: May 17 23:44:45.096 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to up
```

**HQ-SYSLOG collector:**
```text
May 17 23:44:17 10.0.255.1 001910: May 17 23:44:16.410 UTC: %HA_EM-4-LOG: P09_EEM_LOOP99_DOWN: P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99
```

**SNMP device-side:** Trap counters increased from 6 to 10 sent, 0 dropped.

**NetFlow device-side:** 5727 flows exported, 0 export failures, 0 drops — export remained healthy throughout the event.

### Interpretation

The same 23:44:16 UTC event was visible in four independent monitoring sources within one second. Collector-side SNMP and NetFlow proof is not possible without snmptrapd and a flow collector on HQ-SYSLOG — documented as infrastructure limitations.

---

## Phase 8 — CDP/LLDP Topology Discovery

### Scope

`cdp run` and `lldp run` applied and verified on all 9 IOS/IOL devices. HQ-FW1 (ASAv) confirmed as CDP/LLDP discovery-limited — commands rejected as invalid input on this image.

### Neighbor Table (25 relationships)

| Local Device | Local Interface | Neighbor Device | Neighbor Interface | Protocol |
|---|---|---|---|---|
| HQ-RTR1 | Ethernet0/0 | HQ-DSW1 | Ethernet0/0 | CDP + LLDP |
| HQ-RTR1 | Ethernet0/1 | BR-RTR1 | Ethernet0/1 | CDP + LLDP |
| HQ-RTR1 | Ethernet0/2 | WAN-RTR1 | Ethernet0/1 | CDP + LLDP |
| HQ-RTR1 | Ethernet0/3 | HQ-FW1 | GigabitEthernet0/0 inside | Description only |
| BR-RTR1 | Ethernet0/0 | BR-DSW1 | Ethernet0/0 | CDP |
| BR-RTR1 | Ethernet0/1 | HQ-RTR1 | Ethernet0/1 | CDP + LLDP |
| BR-RTR1 | Ethernet0/2 | WAN-RTR1 | Ethernet0/0 | CDP + LLDP |
| WAN-RTR1 | Ethernet0/0 | BR-RTR1 | Ethernet0/2 | CDP + LLDP |
| WAN-RTR1 | Ethernet0/1 | HQ-RTR1 | Ethernet0/2 | CDP + LLDP |
| HQ-DSW1 | Ethernet0/0 | HQ-RTR1 | Ethernet0/0 | CDP + LLDP |
| HQ-DSW1 | Ethernet0/1 | HQ-ASW1 | Ethernet0/0 | CDP |
| HQ-DSW1 | Ethernet0/2 | HQ-ASW2 | Ethernet0/0 | CDP |
| HQ-DSW1 | Ethernet0/3 | HQ-DSW2 | Ethernet0/3 | CDP + LLDP |
| HQ-DSW1 | Ethernet1/0 | HQ-DSW2 | Ethernet1/0 | CDP + LLDP |
| HQ-DSW2 | Ethernet0/1 | HQ-ASW1 | Ethernet0/1 | CDP |
| HQ-DSW2 | Ethernet0/2 | HQ-ASW2 | Ethernet0/1 | CDP |
| HQ-DSW2 | Ethernet0/3 | HQ-DSW1 | Ethernet0/3 | CDP + LLDP |
| HQ-DSW2 | Ethernet1/0 | HQ-DSW1 | Ethernet1/0 | CDP + LLDP |
| BR-DSW1 | Ethernet0/0 | BR-RTR1 | Ethernet0/0 | CDP + LLDP |
| BR-DSW1 | Ethernet0/1 | BR-ASW1 | Ethernet0/0 | CDP + LLDP |
| HQ-ASW1 | Ethernet0/0 | HQ-DSW1 | Ethernet0/1 | CDP + LLDP |
| HQ-ASW1 | Ethernet0/1 | HQ-DSW2 | Ethernet0/1 | CDP |
| HQ-ASW2 | Ethernet0/0 | HQ-DSW1 | Ethernet0/2 | CDP |
| HQ-ASW2 | Ethernet0/1 | HQ-DSW2 | Ethernet0/2 | CDP + LLDP |
| BR-ASW1 | Ethernet0/0 | BR-DSW1 | Ethernet0/1 | CDP + LLDP |

---

## Verification Summary

| Phase | Success Criteria | Result |
|-------|-----------------|--------|
| 1 — Syslog | All 10 devices confirmed in collector | ✅ |
| 2 — SNMP | SNMPv3 SHA+AES128 on 3 core routers, v2c on all 10 | ✅ |
| 3 — NetFlow | 54+ flows exported, 0 failures | ✅ |
| 4 — NTP | All 10 stratum 4 under HQ-RTR1 stratum 3 | ✅ |
| 5 — EEM | Applet fired in 3ms, marker arrived at collector | ✅ |
| 6 — Archive | All 9 devices configured, rollback verified on HQ-RTR1 | ✅ |
| 7 — Verification | Single event correlated across 4 sources | ✅ |
| 8 — CDP/LLDP | 25 neighbor relationships documented | ✅ |

---

## Key Technologies

| Technology | What Was Built |
|------------|---------------|
| Syslog-ng | Centralized collector at 10.1.99.51, all 10 devices forwarding |
| SNMPv2c | ACL-protected community string, all 10 devices |
| SNMPv3 authPriv | SHA + AES128, core routers only — snmpwalk-ready for homelab |
| Classic NetFlow v9 | 8-interface export from HQ-RTR1, zero-error export verified |
| NTP MD5 auth | HQ-RTR1 stratum 3 master, all other devices stratum 4 |
| EEM syslog applet | Pattern match → auto-alert forwarded through syslog stack |
| Config archive | unix: path on IOL/IOL-L2, `configure replace` rollback |
| CDP / LLDP | Full topology neighbor table, 25 relationships, ASAv noted as unsupported |

---

## CML Platform Limitations

This project ran against several CML/IOL limitations. See `LIMITATIONS-AND-HOMELAB-EXPANSION.md` for full detail and homelab resolution for each.

| Limitation | Impact |
|-----------|--------|
| HQ-SYSLOG has no snmptrapd or NetFlow collector | SNMP and NetFlow proof is device-side only |
| IOL `show ip flow interface` unsupported | Use `show ip cache flow` instead |
| IOL-L2 does not support EEM | EEM deployed on HQ-RTR1 only |
| CML IOL/IOL-L2 has no flash: | Config archive uses `unix:` path |
| ASAv (HQ-FW1) rejects CDP/LLDP commands | Topology link documented via interface description |
| HQ-SYSLOG has no searchable interface | All queries via raw log file |

---

## Troubleshooting Log

See the root [TROUBLESHOOTING-LOG.md](../TROUBLESHOOTING-LOG.md) for P09 entries covering:

- IOL-L2 management routing: `ip routing` + static default route required (not just `ip default-gateway`)
- EEM pattern mismatch: LINEPROTO vs. LINK message wording
- Config archive: `flash:` unavailable on IOL — corrected to `unix:`
- SNMP trap collector-side gap (HQ-SYSLOG has no snmptrapd)
- ASAv CDP/LLDP unsupported — documented via interface description
