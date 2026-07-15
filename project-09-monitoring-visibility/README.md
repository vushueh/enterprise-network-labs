# P09 — Monitoring And Visibility

- **Status:** ✅ Complete — 2026-05-17
- **Project ID:** `Enterprise-P09`
- **Platform:** Cisco CML 2.9 with IOL, IOL-L2, ASAv, and syslog-ng
- **Scope:** Ten network devices plus one centralized collector
- **Parent project:** [P08 — Site-To-Site VPN](../project-08-site-to-site-vpn/)

## Why This Matters

A reliable network still needs evidence of what changed, when it changed, and
which traffic or device caused it. I built P09 to turn an operational topology
into an observable and auditable one.

## Portfolio Summary

**Situation:** The enterprise lab had routing, firewalling, and encryption but no
central visibility.

**Task:** Add logs, polling, flow data, time synchronization, automatic alerts,
configuration rollback, and a current neighbor inventory.

**Action:** I deployed syslog-ng, configured tiered syslog, SNMPv2c/v3, NetFlow,
authenticated NTP, EEM, config archives, a correlated event exercise, and
CDP/LLDP discovery.

**Result:** PASS. Ten devices sent logs, SNMP and NetFlow verified device-side,
all ten synchronized time, EEM generated alerts, nine IOS/IOL devices retained
rollback archives, and 25 neighbor relationships were documented.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 7](#phase-7--correlated-event-exercise) |
| Technical reviewer | [Original technical record](technical-details.md), [configs](configs/), and [verification outputs](verification-outputs/) |
| Future operator | [Decision log](decision-log.md) and [limitations and homelab expansion](LIMITATIONS-AND-HOMELAB-EXPANSION.md) |

## My Test Boundary

| Item | Boundary |
|---|---|
| In-scope devices | 3 routers, 6 switches, and HQ-FW1 |
| Collector | HQ-SYSLOG `10.1.99.51` |
| SNMPv3 | Core routers; authPriv |
| NetFlow | HQ-RTR1 exporter |
| EEM | HQ-RTR1; IOL-L2 limitation documented |
| Outside router | ISP-RTR1 excluded from inside monitoring policy |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 1 | Syslog | Complete |
| 2 | SNMP | Complete |
| 3 | NetFlow | Complete |
| 4 | Authenticated NTP | Complete |
| 5 | EEM Alerts | Complete on supported router |
| 6 | Configuration Archive | Complete |
| 7 | Correlated Event Exercise | Complete |
| 8 | CDP/LLDP Discovery | Complete |

## Phase 1 — Syslog

I deployed HQ-SYSLOG and configured severity tiers, timestamps, sequence numbers,
and stable source interfaces on ten devices. Live events reached the collector,
creating the timestamped base needed by every later monitoring source.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 2 — SNMP

I added restricted SNMPv2c and authPriv SNMPv3 on the core routers. The collector
node did not include all polling tools, so device-side `show snmp` evidence became
the honest acceptance criterion. The [limitations record](LIMITATIONS-AND-HOMELAB-EXPANSION.md)
explains how to extend this on a full manager.

## Phase 3 — NetFlow

I enabled classic NetFlow on HQ-RTR1, set the interfaces and exporter, generated
traffic, and verified active cache and zero-error export health. This added
traffic context to the event records.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 4 — Authenticated NTP

I made HQ-RTR1 the authenticated time source and synchronized all in-scope
devices. IOL-L2 required `ip routing` plus a static default route for management-
plane reachability; `ip default-gateway` alone was insufficient. The corrected
design brought every device to stratum 4.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 5 — EEM Alerts

I created an HQ-RTR1 EEM applet that writes a clear syslog marker when a selected
interface goes down. An initial regular-expression assumption failed, so I used
the literal event pattern proved by the platform. IOL-L2 lacked EEM and was left
out rather than mislabeled complete.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 6 — Configuration Archive

I enabled local archive-on-write on nine IOS/IOL devices, introduced a harmless
description change, and restored it with `configure replace`. This proved the
backup path could support recovery, not merely store files.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 7 — Correlated Event Exercise

I shut Loopback99 on HQ-RTR1 and followed one event through local syslog, EEM,
forwarded logging, SNMP counters, and NetFlow health. The [verification outputs](verification-outputs/)
show how multiple sources describe the same operational change.

## Phase 8 — CDP/LLDP Discovery

I collected neighbor data across the topology and built a 25-entry relationship
table. That final inventory connected monitoring identities to physical links and
gave later automation a device-discovery reference.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## What I Proved

- Central syslog receives consistently timestamped events from ten devices.
- SNMP and NetFlow are configured and verifiable within collector limitations.
- Authenticated NTP aligns event time across routers, switches, and firewall.
- EEM can generate a targeted operational alert on supported IOS.
- Configuration archive supports an actual rollback test.
- One event can be correlated across several telemetry sources.
- CDP/LLDP can document the current physical topology.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Phase configurations](configs/)
- [Verification outputs](verification-outputs/)
- [Decision log](decision-log.md)
- [Limitations and expansion guide](LIMITATIONS-AND-HOMELAB-EXPANSION.md)
- [Codex session log](../CODEX-LOG.md)

## How We Worked Together

### My Input And How I Helped

I applied the reviewed configurations, created the CML collector, returned show
and console output, generated test events, and performed the archive rollback.

### What Codex Did And How

Codex proposed the phase configurations, interpreted the returned evidence,
adapted verification to collector and IOL limits, and maintained the session
handoff. The [decision log](decision-log.md) records Codex's implementation role.

### What Claude Did And How

Claude independently reviewed the design and phase proposals, challenged unsafe
or unsupported assumptions, and wrote the platform-expansion guidance. The
[decision log](decision-log.md) records the shared design-review role.

### How We Communicated And Completed The Project

Codex proposed each phase, Claude reviewed it, and I applied the approved
configuration and returned evidence. We corrected each platform finding before
the next phase and closed only after the correlated event and neighbor inventory.

### Pushback And How We Resolved It

The collector lacked some SNMP/flow tools, IOL-L2 needed routed management, and
IOL-L2 did not support EEM. We changed acceptance to supported device-side proof,
fixed the actual management route, limited EEM to HQ-RTR1, and documented how a
full homelab collector would expand the result.

## Reproduce Or Re-Verify

1. Confirm P08 routing and time reachability before deploying the collector.
2. Apply [configs](configs/) phase by phase and generate one event after syslog.
3. Verify SNMP, NetFlow, NTP, EEM, and archives with their supported commands.
4. Perform one reversible archive rollback and one bounded correlated event.
5. Refresh the neighbor table and compare with [verification outputs](verification-outputs/).

## What Happens Next

P09 is closed. [P10](../project-10-aaa-access-control/) adds centralized device
administration and role-based access. P09 does not authorize P10.
