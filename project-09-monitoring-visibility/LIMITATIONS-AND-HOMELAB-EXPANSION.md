# Project 09 — CML Limitations and Homelab Expansion Notes

**Written by:** Claude Code  
**Date:** 2026-05-17  
**Purpose:** Document every capability gap hit during Project 09 in CML so we can build a
production-grade monitoring stack when the lab expands to physical/VM infrastructure.

---

## Why This File Exists

Project 09 covers Syslog, SNMP, NetFlow, NTP, EEM, and config archive. In CML, the
collector infrastructure is minimal — a single syslog-ng node built for Project 07.
Several verification steps that would normally close the loop on monitoring proof were
blocked by platform constraints, not by incorrect configuration.

Every gap below has been verified as a lab infrastructure limitation, not a networking
or configuration error. All device-side configs are correct. When the lab moves to
physical or homelab-VM infrastructure, the items below are the exact gaps to close.

---

## Limitation 1 — HQ-SYSLOG is syslog-ng only, no SNMP capability

**Hit during:** Phase 2 (SNMP)  
**Impact:** Medium

### What the node is

HQ-SYSLOG is a minimal Alpine CML node. Its entire configuration is:

```
syslog-ng 3.38 listening on UDP/514
→ /var/log/syslog
→ /dev/stdout

eth0: 10.1.99.51/24, default gateway 10.1.99.1
```

No shell access, no package manager, no extra services.

### What this blocked

| Verification | Blocked because |
|-------------|----------------|
| SNMP trap receipt proof | UDP/162 not open — snmptrapd not installed |
| snmpwalk polling test | net-snmp tools not installed |
| SNMPv3 trap decoding | No createUser config for snmptrapd |
| Trap counter at collector | No snmptrapd to count received traps |

### Evidence of the gap

When HQ-FW1 sent its coldstart SNMP trap to 10.1.99.51:162, the collector
returned ICMP type 3 code 3 (port unreachable). The ASA logged this:

```
%ASA-3-106014: Deny inbound icmp src inside:10.1.99.51 dst nlp_int_tap:10.0.0.14
(type 3, code 3)
```

This proves the ASA's SNMP trap transmission is working correctly. The gap is
purely on the receiver side.

### Device-side proof that was still captured

- `show snmp` on all devices: `SNMP logging: enabled, Logging to 10.1.99.51.162`
- `show snmp-server statistics` on HQ-FW1: `1 Trap PDUs` sent (coldstart)
- `show snmp user` on all core routers: SNMPv3 user `p09snmpv3` created with SHA auth + AES128 privacy

### Homelab fix

Deploy a real monitoring VM with:

```
LibreNMS  — full SNMP polling, trap collection, graphing, alerting
             snmpwalk built in, SNMPv3 support, autodiscovery via CDP/LLDP
             https://www.librenms.org/

OR

Zabbix    — SNMP polling + traps, alerting, dashboards
             heavier but more enterprise-like for AAA/SNMP lab work

Minimum:  net-snmp (snmpwalk, snmptrapd) on any Linux VM
          + snmptrapd.conf with createUser entries for SNMPv3
```

When deployed, the snmpwalk commands that were prepared but not run:

```bash
# SNMPv2c polling
snmpwalk -v2c -c P09V2CRO2026 10.0.255.1 sysName.0    # HQ-RTR1
snmpwalk -v2c -c P09V2CRO2026 10.1.99.13 sysName.0    # HQ-ASW1

# SNMPv3 polling
snmpwalk -v3 -l authPriv -u p09snmpv3 \
  -a SHA -A P09AuthKey2026 \
  -x AES -X P09PrivKey2026 \
  10.0.255.1 sysName.0

# Verify ifindex stability after reload
snmpwalk -v2c -c P09V2CRO2026 10.0.255.1 ifTable
```

---

## Limitation 2 — No NetFlow collector on HQ-SYSLOG

**Hit during:** Phase 3 (NetFlow)  
**Impact:** High

### What was blocked

NetFlow exports use UDP/2055 (or 9995/9996 depending on collector). HQ-SYSLOG has
no NetFlow collector software. Flow records exported from HQ-RTR1 cannot be received
or decoded.

Phase 3 can still configure the NetFlow exporter on HQ-RTR1 (the device side) and
verify locally with `show ip cache flow` and `show ip flow interface`. But flow
*analysis* — seeing actual traffic breakdowns, top talkers, protocol distribution —
requires a collector.

### Homelab fix

```
ntopng     — flow collection, protocol analysis, top-talker graphs
             free community edition works well for home lab
             https://www.ntopng.org/

pmacct     — lightweight flow collector, outputs to various backends
             pairs well with Grafana + InfluxDB for dashboards

nfdump     — command-line NetFlow analysis, pairs with nfcapd collector
             good for quick inspection without a full dashboard

LibreNMS   — also has basic NetFlow support if using the same VM
```

NetFlow commands to run from HQ-RTR1 once a collector is up:

```
show ip cache flow
show ip flow interface
show ip flow export
```

---

## Limitation 3 — No searchable syslog interface

**Hit during:** Phase 1 (Syslog), Phase 7 (Multi-source correlation)  
**Impact:** Medium

### What was blocked

HQ-SYSLOG writes all messages to `/var/log/syslog` and stdout. There is no:
- Search interface
- Time-range filtering
- Per-device filtering with a UI
- Alerting on specific message patterns
- Message correlation across sources

Phase 7 (multi-source correlation: syslog + SNMP trap + NetFlow + EEM trigger within
60 seconds) requires being able to search and correlate messages efficiently. Doing
this by eyeballing raw syslog output is possible but slow.

### Homelab fix

```
Graylog    — syslog input, full text search, alerting, dashboards
             free open-source, runs on a single VM for home lab
             https://graylog.org/

ELK Stack  — Elasticsearch + Logstash + Kibana
(Elastic)    most powerful search, heavier resource requirement

Grafana    — pairs with Loki for log aggregation and syslog search
+ Loki       lightweight option, good integration with existing Grafana

Minimum:   rsyslog or syslog-ng with proper log rotation and grep
```

---

## Limitation 4 — ISP-RTR1 excluded from monitoring scope

**Hit during:** Phase 1 (Syslog), Phase 2 (SNMP)  
**Impact:** Low

### What was excluded

ISP-RTR1 represents the outside/internet side of HQ-FW1. Including it in the
monitoring scope would require:
- A deliberate outside-to-inside monitoring policy on the ASA
- Either a NAT entry for management traffic from ISP-RTR1 to HQ-SYSLOG, or a
  separate out-of-band management path

In CML, neither exists. ISP-RTR1 was left out of syslog and SNMP.

### Homelab fix

When the lab has a real OPNsense or Palo Alto as the perimeter (as Leonel's
homelab already does), configure an out-of-band management VLAN that reaches
all devices including internet-side routers. ISP-RTR1 equivalent devices can
then be monitored via the OOB path without mixing management and production traffic.

---

## Limitation 5 — NTP: no external reference clock

**Hit during:** Phase 4 (NTP)  
**Impact:** Low

### What this means

HQ-RTR1 is configured as NTP master stratum 3 (`ntp master 3`). In CML, there
is no upstream stratum-1 or stratum-2 server to sync to. HQ-RTR1 uses its own
internal clock as the authoritative source.

For the lab this is fine. In production, stratum 3 is already two hops from an
atomic clock. Configuring NTP auth and verifying `show ntp associations` and
`show ntp status` still demonstrates the full NTP model.

### Homelab fix

Point HQ-RTR1 to a real NTP source:

```
! Use pool.ntp.org or a local homelab stratum-2 source
ntp server pool.ntp.org prefer
ntp server time.cloudflare.com

! Or use the OPNsense/Palo Alto as the stratum-2 internal source
ntp server <firewall-management-ip>
```

Then HQ-RTR1 drops to stratum 4 (one below the server) and all campus
devices sync to it as stratum 5 — a realistic hierarchy.

---

## Limitation 6 — EEM cannot call external scripts or APIs

**Hit during:** Phase 5 (EEM)  
**Impact:** Low (informational)

### What this means

EEM applets in IOL can trigger on interface events and run IOS commands. They
cannot call external HTTP endpoints, run Python, or push to external monitoring
systems directly. This is an IOS/IOL platform boundary, not a CML-specific issue.

### Homelab fix (beyond CCNA scope)

In a production environment or with IOS XE, EEM can call Python via the
`guestshell` (IOS XE 16.x+) or use `action cli command` to push to an
API via `ip http client`. In the homelab, consider:
- IOS XE virtual routers (CSR1000v or Catalyst 8000v) for full EEM + Python
- Ansible triggered by SNMP traps or syslog patterns as the external automation layer

---

## Limitation 7 — IOL-L2 switches do not support EEM

**Hit during:** Phase 5 (EEM)
**Impact:** Medium

### What happened

The original Phase 5 pilot was on HQ-ASW1. The IOL-L2 image rejected `event manager applet` with `% Invalid input detected`. EEM is not available on any IOL-L2 switch image in this CML topology. Phase 5 was moved to HQ-RTR1 using a temporary Loopback99 as the test trigger.

### Homelab fix

Use IOS XE-based switches (Catalyst 9000v) or routers (CSR1000v / Catalyst 8000v) in the homelab. All current IOS XE images support EEM fully. Alternatively, deploy EEM on the IOS routers only and use external tools (Ansible, Python scripts triggered by syslog) to automate responses on the switches.

---

## Limitation 8 — EEM syslog pattern matching is literal — must match exact IOS message wording

**Hit during:** Phase 5 (EEM)
**Impact:** Low (operational knowledge — affects all future EEM work)

### What happened

The first EEM pattern on HQ-RTR1 was:
```
event syslog pattern "Interface Loopback99, changed state to administratively down"
```
This did not fire. The actual IOS message generated was:
```
%LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to down
```
The working pattern was:
```
event syslog pattern "Line protocol on Interface Loopback99, changed state to down"
```

### Rule to remember

EEM `event syslog pattern` does a **literal substring match** against the full syslog message string as emitted by the IOS process. The exact wording varies by:
- IOS vs IOS XE vs ASA
- Interface type (physical, loopback, tunnel, VLAN SVI)
- Event type (LINK-3-UPDOWN vs LINEPROTO-5-UPDOWN)

Always verify the exact message wording with `show logging` before writing an EEM pattern. Use the shortest unambiguous substring to keep the pattern portable across interface names.

---

## Limitation 9 — CML IOL/IOL-L2 devices do not expose flash: for config archive

**Hit during:** Phase 6 (Config Archive)
**Impact:** Low — easy workaround

### What happened

The Phase 6 archive config used `path flash:P09-ARCHIVE-$h-`. On every CML IOL and IOL-L2 device, `flash:` was not available as a writable filesystem. `show file systems` and `archive path ?` both confirmed `unix:` as the correct local writable filesystem.

### Working path for all CML IOL/IOL-L2 devices

```
archive
 path unix:/P09-ARCHIVE-$h-
 maximum 5
 write-memory
```

### Homelab fix

Physical or VM-based IOS XE routers (CSR1000v, Catalyst 8000v) expose `flash:` normally. Use `flash:` on real hardware. Use `unix:` only for CML IOL/IOL-L2 images.

---

## Summary Table

| # | Limitation | Phases Affected | Homelab Fix |
|---|-----------|-----------------|-------------|
| 1 | No snmptrapd / snmpwalk on HQ-SYSLOG | Phase 2 | LibreNMS or net-snmp VM |
| 2 | No NetFlow collector on HQ-SYSLOG | Phase 3 | ntopng or pmacct + Grafana |
| 3 | No searchable syslog interface | Phase 1, 7 | Graylog or ELK |
| 4 | ISP-RTR1 excluded from monitoring | Phase 1, 2 | OOB management VLAN |
| 5 | No upstream NTP reference | Phase 4 | pool.ntp.org or OPNsense NTP |
| 6 | EEM cannot call external APIs | Phase 5 | IOS XE guestshell or Ansible |
| 7 | IOL-L2 switches do not support EEM | Phase 5 | IOS XE switches (Catalyst 9000v) |
| 8 | EEM pattern matching is literal — wording varies by IOS image | Phase 5 | Always verify exact message with show logging first |
| 9 | CML IOL/IOL-L2 has no flash: — use unix: for config archive | Phase 6 | Use flash: on real hardware / IOS XE VMs |

---

## Homelab Target Architecture (when ready)

```
┌─────────────────────────────────────────────────────────┐
│  Monitoring VM (Ubuntu/Debian — 4 vCPU, 8GB RAM)        │
│                                                          │
│  LibreNMS    → SNMP polling + trap collection            │
│               → SNMPv3 for core devices                  │
│               → CDP/LLDP autodiscovery                   │
│               → Alerting (email/Slack/webhook)           │
│                                                          │
│  Graylog     → Syslog UDP/514                            │
│               → Full text search + alerting              │
│               → Correlation rules                        │
│                                                          │
│  ntopng      → NetFlow UDP/2055                          │
│               → Traffic analysis + top talkers           │
│                                                          │
│  snmptrapd   → UDP/162 trap receiver                     │
│               → SNMPv3 user config for p09snmpv3         │
│                                                          │
│  NTP server  → Syncs to pool.ntp.org                     │
│               → Serves as stratum-2 for all lab devices  │
└─────────────────────────────────────────────────────────┘

All devices point syslog, SNMP traps, and NetFlow to this one VM.
The existing device-side configs (ACL-SNMP-MANAGERS, logging host,
ip flow-export destination) only need the destination IP updated.
```

---

*This file is maintained by Claude Code and should be reviewed at the start of
every homelab expansion session. As each limitation is resolved in the physical
lab, mark it RESOLVED with the date and what was deployed.*
