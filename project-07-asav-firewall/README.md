# P07 — ASAv Perimeter Firewall

- **Status:** ✅ Complete — 2026-05-04
- **Project ID:** `Enterprise-P07`
- **Platform:** Cisco CML 2.9 with ASAv and IOL
- **Scope:** Routed perimeter cutover, DMZ, NAT, ACL, and state inspection
- **Parent project:** [P06 — Security Hardening](../project-06-security-hardening/)

## Why This Matters

A router can translate traffic, but a dedicated firewall adds explicit security
zones, stateful policy, application inspection, and purpose-built diagnostics.
I inserted ASAv without discarding the working campus and internet design.

## Portfolio Summary

**Situation:** HQ-RTR1 still owned perimeter NAT and ACL functions.

**Task:** Move the edge policy to ASAv, create a DMZ, preserve public service and
user access, and prove allowed and denied paths with `packet-tracer` and live state.

**Action:** I inserted HQ-FW1, migrated PAT and static NAT, added outside ACLs and
inspection, tested policy paths, enabled logging, and inspected stateful sessions.

**Result:** PASS for phases 1-6. Inside users reached the internet, outside HTTP
reached only the DMZ service, outside-to-inside traffic was denied, and live
connections appeared in the ASA state table.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 6](#phase-6--stateful-session-analysis) |
| Technical reviewer | [Original technical record](technical-details.md), [configs](configs/), and [screenshots](verification/screenshots/) |
| Future operator | [Requirement](requirement.md), [decision log](decision-log.md), and [troubleshooting log](TROUBLESHOOTING-LOG.md) |

## My Test Boundary

| Item | Boundary |
|---|---|
| Firewall | HQ-FW1 ASAv |
| Zones | inside 100, dmz 50, outside 0 |
| Public service | HTTP to HQ-SRV1 through static NAT |
| User egress | PAT through ASAv |
| Management | SSH from management subnet only |
| Fault | Inside security-level fault deferred |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 1 | ASAv Cutover | Complete |
| 2 | NAT Migration | Complete |
| 3 | ACL And Inspection Policy | Complete |
| 4 | Packet-Tracer Proof | Complete |
| 5 | Firewall Logging | Complete |
| 6 | Stateful Session Analysis | Complete |
| 7 | Deferred Security-Level Fault | Deferred — future video exercise |

## Phase 1 — ASAv Cutover

I inserted HQ-FW1 between the campus router and ISP, assigned inside, outside,
and DMZ interfaces, and moved the relevant routes. I verified reachability at
each boundary before migrating translation so a routing problem would not be
confused with NAT.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 2 — NAT Migration

I removed the old router NAT role and recreated user PAT plus the HQ-SRV1 static
mapping on ASAv. Translation and route output showed one clear perimeter owner.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 3 — ACL And Inspection Policy

I allowed only public HTTP to the DMZ, denied outside-originated inside access,
and enabled the required inspections. Tests confirmed inside-to-outside and
inside-to-DMZ flows while preserving the default lower-to-higher denial.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 4 — Packet-Tracer Proof

I used `packet-tracer` for allowed, denied, and translated flows. The phase-by-
phase verdict showed exactly where ASA policy accepted or dropped the packet,
which made the result reproducible without relying on endpoint symptoms alone.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 5 — Firewall Logging

I configured syslog and generated policy events. The retained evidence connects
ACL hits and firewall messages to the traffic tests used during verification.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 6 — Stateful Session Analysis

I established an outside-to-DMZ HTTP connection and inspected `show conn` to
prove return traffic was allowed by state rather than a broad reverse ACL. That
completed the firewall behavior proof.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 7 — Deferred Security-Level Fault

The documented exercise would set the inside security level to zero, observe the
loss of inside-to-outside access, diagnose it with `show nameif` and
`packet-tracer`, then restore level 100. It was not executed, so it remains a
future demonstration and is not part of the completed evidence.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## What I Proved

- ASAv can become the routed perimeter without rebuilding the campus.
- PAT and one static public service work under a single firewall authority.
- Outside policy denies inside access while allowing only required DMZ HTTP.
- `packet-tracer` explains both allowed and denied paths.
- Firewall logging records policy activity.
- The connection table proves stateful return handling.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Requirement](requirement.md)
- [Configurations](configs/)
- [Verification screenshots](verification/screenshots/)
- [Decision log](decision-log.md)
- [Troubleshooting log](TROUBLESHOOTING-LOG.md)

## How We Worked Together

### My Input And How I Helped

I added the ASAv node and links, applied the cutover and policy, ran endpoint and
packet-tracer tests, and returned the logging and connection evidence.

### What Codex Did And How

The original P07 record does not preserve reliable per-agent attribution. Codex
claims only this migration: preserving the full technical README and creating
the concise evidence-linked story.

### What Claude Did And How

The original P07 record does not prove a distinct historic Claude task. Claude
independently reviewed this migrated summary for ASA accuracy, deferred-work
honesty, and link integrity.

### How We Communicated And Completed The Project

I supplied CML output after each cutover stage and kept configs and screenshots
in the repository. During migration, Codex rewrote the entry page under my
standard and Claude reviewed it without executing the deferred fault.

### Pushback And How We Resolved It

Moving NAT and routing at once could have hidden the fault domain. I separated
interface reachability, routing, translation, ACL, and state verification into
individual phases. I also kept the planned security-level break/fix deferred
because there was no retained execution evidence.

## Reproduce Or Re-Verify

1. Back up the P06 router and server state before inserting ASAv.
2. Apply the [configs](configs/) in order: interfaces/routes, NAT, ACL/inspection,
   logging, and management.
3. Run packet-tracer tests for every required allow and deny path.
4. Generate a live DMZ session and verify the connection and translation tables.
5. Run the deferred security-level fault only in a separately approved window.

## What Happens Next

P07 is closed. [P08](../project-08-site-to-site-vpn/) encrypts inter-site traffic
with GRE over IKEv2/IPsec. P07 does not authorize P08 or the deferred ASAv fault.
