# P03 — Dynamic Routing With OSPF

- **Status:** ✅ Complete — 2026-04-11
- **Project ID:** `Enterprise-P03`
- **Platform:** Cisco CML 2.9 with IOL routers
- **Scope:** Redundant authenticated IPv4 and IPv6 routing between HQ and Branch
- **Parent project:** [P02 — Multi-Site Expansion And DHCP](../project-02-multi-site-dhcp/)

## Why This Matters

Static routes work in a small lab but do not scale or heal themselves. I built
P03 to make the two-site network learn routes dynamically, prefer a designed
path, detect failures quickly, and retain a last-resort fallback.

## Portfolio Summary

**Situation:** Every P02 subnet was maintained manually and the direct WAN link
was a single inter-site failure point.

**Task:** Add a second WAN path, migrate to multi-area OSPF, authenticate updates,
tune path preference, speed failure detection, and replace IPv6 static routes.

**Action:** I added WAN-RTR1, built OSPF in stages, separated campus and backbone
areas, added MD5, tuned costs, tested convergence, bound BFD, added tracked
floating statics, and enabled OSPFv3.

**Result:** PASS. The preferred OSPF path failed over in under one second with
BFD, the backup OSPF path carried traffic, and tracked floating routes provided
a third recovery layer.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 5](#phase-5--failure-and-convergence) |
| Technical reviewer | [Original technical record](technical-details.md), [router configs](configs/), and [troubleshooting log](TROUBLESHOOTING-LOG.md) |
| Future operator | [Requirement](requirement.md), [decision log](notes/decision-log.md), and [lab guide](docs/ospf-dynamic-routing-lab-guide.pdf) |

## My Test Boundary

| Item | Boundary |
|---|---|
| Sites | HQ and Branch |
| Transit | Direct /30 plus WAN-RTR1 alternate path |
| IPv4 | Multi-area OSPF with campus summarization |
| Authentication | MD5 on WAN-facing adjacencies |
| Fast failure | BFD on supported WAN links |
| Last resort | IP SLA tracked floating statics, AD 250 |
| IPv6 | OSPFv3 across the same area model |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 1 | Single-Area Migration | Complete |
| 2 | Multi-Area Design | Complete |
| 3 | Neighbor Authentication | Complete |
| 4 | Path Preference | Complete |
| 5 | Failure And Convergence | Complete |
| 6 | BFD | Complete |
| 7 | Tracked Last Resort | Complete |
| 8 | OSPFv3 | Complete |

## Phase 1 — Single-Area Migration

I added WAN-RTR1 and introduced OSPF before removing the working static routes.
This staged change let me verify neighbors and learned prefixes while a known
fallback still existed. I corrected point-to-point network types where DR/BDR
behavior did not fit the /30 links, then removed the obsolete static entries.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 2 — Multi-Area Design

I placed the WAN and loopbacks in area 0, HQ campus prefixes in area 1, and
Branch prefixes in area 2. HQ-RTR1 and BR-RTR1 became ABRs and summarized their
campus ranges. The [area diagram](diagrams/ospf-area-design.png) and
[technical record](technical-details.md) explain the resulting LSDB boundary.

## Phase 3 — Neighbor Authentication

I added matching MD5 keys on every WAN-facing OSPF interface and verified that
adjacencies returned to FULL. A mismatch would prevent route exchange, so I
checked both configuration and neighbor state before tuning costs.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 4 — Path Preference

I set the WAN-RTR1 transit path to a lower cost than the direct HQ-to-Branch
link. Route and traceroute output proved traffic used the intended primary path
while the direct link remained available as backup.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 5 — Failure And Convergence

I shut the preferred link, watched OSPF reconverge to the backup, verified
inter-site reachability, and then restored the link. This proved self-healing
routing, but the default detection interval remained longer than the target.
That result justified the BFD phase.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 6 — BFD

I enabled BFD on the WAN interfaces and bound it to OSPF. The next controlled
failure converged in under one second instead of waiting for the normal dead
timer. The [verification screenshots](verification/screenshots/) retain the
neighbor and failover proof.

## Phase 7 — Tracked Last Resort

I configured IP SLA probes on the directly connected backup path, tracked their
state, and installed floating statics with administrative distance 250. They
stay out of the routing table while OSPF is healthy and appear only if the
dynamic layer cannot provide the route.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 8 — OSPFv3

I replaced IPv6 static routes with OSPFv3, matched the multi-area design, and
used point-to-point network types on the transit links. IPv6 reachability and
neighbors verified that the second protocol stack could recover dynamically too.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## What I Proved

- OSPF can replace a growing static route set without a blind cutover.
- Multi-area design and summarization contain campus detail.
- MD5 prevents an unauthenticated neighbor from joining the routing domain.
- Cost tuning creates a predictable primary and backup path.
- BFD reduces link-failure detection to under one second in this lab.
- IP SLA tracked statics provide a third routing fallback.
- OSPFv3 gives IPv6 the same dynamic recovery model.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Requirement](requirement.md)
- [Router configurations](configs/)
- [Verification screenshots](verification/screenshots/)
- [Project troubleshooting log](TROUBLESHOOTING-LOG.md)
- [Decision log](notes/decision-log.md)
- [OSPF area diagram](diagrams/ospf-area-design.png)
- [Lab guide](docs/ospf-dynamic-routing-lab-guide.pdf)

## How We Worked Together

### My Input And How I Helped

I added and cabled WAN-RTR1, applied the CML configurations, returned neighbor,
route, BFD, IP SLA, and IPv6 output, and performed the controlled link failures.
I approved each step only after the prior routing state was recoverable.

### What Codex Did And How

The retained P03 files do not support precise historic agent attribution, so
Codex does not invent it. For this migration, Codex preserved the complete
technical README and created this concise evidence-linked phase story.

### What Claude Did And How

The retained P03 record does not identify a separate historic Claude task.
During this migration, Claude included P03 in a repository-wide read-only
review and verified its completion status. Claude did not read this page line
by line, so I do not claim a full independent review of the rewritten story.

### How We Communicated And Completed The Project

I returned the live CML output after each routing stage and retained configs and
fault evidence in the repository. Later, I set the documentation standard,
Codex reorganized and verified the entry page, and Claude checked its status in
the wider batch.

### Pushback And How We Resolved It

Point-to-point WAN links initially showed behavior associated with a broadcast
network type, and configuration changes temporarily removed expected addresses.
We restored known-good interface state first, changed the OSPF network type
explicitly, and reverified neighbors before continuing to authentication or BFD.

## Reproduce Or Re-Verify

1. Start from the complete [P02](../project-02-multi-site-dhcp/) state.
2. Add WAN-RTR1 and apply the saved [configs](configs/) in phase order.
3. Keep a working route while introducing OSPF, then verify neighbor, LSDB,
   route, and traceroute output before removing statics.
4. Add authentication, cost, BFD, tracked statics, and OSPFv3 one layer at a time.
5. Perform the bounded link-failure tests and compare with the retained evidence.

## What Happens Next

P03 is closed. [P04](../project-04-switching-stability/) hardens the Layer 2
foundation beneath this routing design. P03 does not authorize P04 or any new
CML change.
