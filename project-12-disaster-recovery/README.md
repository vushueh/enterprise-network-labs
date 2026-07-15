# P12 — Disaster Recovery

- **Status:** ✅ Complete — 2026-05-31
- **Project ID:** `Enterprise-P12`
- **Platform:** Cisco CML 2.9 with IOL, IOL-L2, and ASAv
- **Scope:** Timed rebuild of HQ-RTR1 and HQ-DSW1 plus partial firewall fault
- **Parent project:** [P11 — QoS Traffic Management](../project-11-qos-traffic-management/)

## Why This Matters

Backups and documentation are only useful when they can restore service under
pressure. I used P12 to test the previous eleven projects as recovery material,
not just as portfolio descriptions.

## Portfolio Summary

**Situation:** The lab contained routing, VPN, AAA, QoS, monitoring, VLANs, and
firewall policy but had never been rebuilt after simultaneous failures.

**Task:** Erase two critical devices, introduce a partial firewall fault, rebuild
the router and switch within 90 minutes, and prove eight services returned.

**Action:** I captured the baseline, reset HQ-RTR1 and HQ-DSW1, started a timer,
rebuilt dependencies in order, verified every service, wrote a condensed runbook,
and fixed an additional OSPF area mismatch.

**Result:** PASS. Recovery completed in 87 minutes 10 seconds, all eight checks
passed, and the OSPF break/fix returned to FULL in 15 seconds.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 4](#phase-4--post-recovery-verification) |
| Technical reviewer | [Original technical record](technical-details.md), [rebuild configs](configs/), and [verification outputs](verification-outputs/) |
| Future operator | [Phase 5 runbook](configs/phase5-runbook-and-lessons-learned.md), [decision log](decision-log.md), and [limitations](LIMITATIONS-AND-HOMELAB-EXPANSION.md) |

## My Test Boundary

| Item | Boundary |
|---|---|
| Full reset | HQ-RTR1 and HQ-DSW1 |
| Partial fault | HQ-FW1 NAT and ACL only |
| Recovery objective | 90 minutes |
| Success checks | OSPF, VPN, TACACS, VLAN/trunk/STP, QoS, syslog, and hosts |
| Additional fault | OSPF area mismatch on HQ-RTR1 E0/1 |
| Evidence | Manual timer and retained CML outputs |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 0 | Pre-Disaster Baseline | Complete |
| 1 | Disaster Injection | Complete |
| 2 | HQ-RTR1 Rebuild | Complete — T+58:32 |
| 3 | HQ-DSW1 Rebuild | Complete — T+78:14 |
| 4 | Post-Recovery Verification | Complete — T+87:10 |
| 5 | Runbook And Lessons | Complete |
| 6 | OSPF Area Mismatch Break/Fix | Complete |

## Phase 0 — Pre-Disaster Baseline

I captured OSPF, VPN counters, TACACS logins, QoS policies, VLANs, syslog, host
reachability, and the Branch voice VLAN. This gave the recovery a measurable
target instead of “the devices booted.”

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 1 — Disaster Injection

I erased and reloaded HQ-RTR1 and HQ-DSW1, then removed selected NAT and ACL
state from HQ-FW1. Branch output confirmed the HQ OSPF neighbor disappeared and
the switch returned to VLAN 1 defaults. I started the 90-minute timer only after
the failure state was proven.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 2 — HQ-RTR1 Rebuild

I restored base identity and access, interfaces, OSPF, GRE/IPsec, TACACS+, QoS,
syslog, and SNMP in dependency order. The [phase evidence](verification-outputs/phase2-timed-rebuild-hq-rtr1-complete.md)
records the checkpoints and completion at T+58:32.

## Phase 3 — HQ-DSW1 Rebuild

I restored routing and SSH, VLANs, LACP Po1, trunks, the management SVI, STP
priority, and AAA. The switch completed at T+78:14 and rejoined the working
distribution layer.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 4 — Post-Recovery Verification

I ran all eight acceptance checks rather than stopping at reachability. OSPF had
three FULL paths, VPN counters increased, TACACS roles worked, VLAN/trunk/root
state matched, QoS policies were active, syslog arrived, and both VLAN 100 hosts
responded. Final time was T+87:10, 2 minutes 50 seconds inside the objective.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 5 — Runbook And Lessons

I converted the recovery chronology into a shorter dependency-based runbook.
The key sequence is routing before VPN, local safety before AAA cutover, and
pre-staged QoS blocks because they consumed the most rebuild time.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 6 — OSPF Area Mismatch Break/Fix

I placed HQ-RTR1 E0/1 in area 1 instead of area 0. The local side showed INIT
while the far side had no neighbor, an asymmetric symptom. `show ip ospf
interface` exposed the area mismatch; restoring area 0 returned FULL in 15 seconds.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## What I Proved

- Existing project documentation can rebuild two critical devices from default state.
- Dependency order materially affects recovery speed and safety.
- Eight independent service checks are stronger than a simple ping test.
- The measured recovery time met a 90-minute objective.
- AAA, VPN, QoS, monitoring, and switching state can survive a documented rebuild.
- An OSPF area mismatch has a recognizable asymmetric failure pattern.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Recovery and fault configurations](configs/)
- [Verification outputs and final closeout](verification-outputs/)
- [Decision log](decision-log.md)
- [Limitations and homelab expansion](LIMITATIONS-AND-HOMELAB-EXPANSION.md)
- [Codex session log](../CODEX-LOG.md)

## How We Worked Together

### My Input And How I Helped

I approved the destructive CML exercise, erased and rebuilt the devices, operated
the timer, returned every checkpoint, and performed the final area-mismatch test.

### What Codex Did And How

Codex prepared the ordered rebuild blocks, verification gates, timing checkpoints,
and break/fix diagnosis. It interpreted each returned result and converted the
chronology into the retained runbook and this migrated page.

### What Claude Did And How

The retained P12 record does not document a distinct historic Claude review, so
I do not claim one. During this migration, Claude included P12 in a repository-
wide read-only review and verified its completion status, but did not read this
page line by line.

### How We Communicated And Completed The Project

Codex supplied the next recovery block, and I applied it while reporting the
timer and output. We did not advance from device rebuild to project closeout
until all eight services passed. Later, Codex rewrote and verified this page,
and Claude checked its status in the wider migration batch.

### Pushback And How We Resolved It

The recovery had a hard deadline and many interdependent services. We resisted
the temptation to restore everything at once, used the pre-disaster baseline as
the target, and followed dependency order. Manual timing is a documented limit;
future exercises should use an independent observer or automated clock.

## Reproduce Or Re-Verify

1. Obtain explicit approval for destructive resets and capture the complete Phase 0 baseline.
2. Keep the [rebuild blocks](configs/) and console access available outside the failed devices.
3. Start the timer only after the outage is verified.
4. Restore HQ-RTR1, then HQ-DSW1, following the dependency runbook.
5. Run every Phase 4 check and stop the timer only when the full service set passes.

## What Happens Next

P12 is closed. [P13](../project-13-network-automation/) turns the manually built
network into an inventory-driven automation target. P12 does not authorize P13
or another destructive recovery exercise.
