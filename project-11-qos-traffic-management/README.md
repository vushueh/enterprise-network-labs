# P11 — QoS Traffic Management

- **Status:** ✅ Complete — 2026-05-31
- **Project ID:** `Enterprise-P11`
- **Platform:** Cisco CML 2.9 with IOL and IOL-L2
- **Scope:** HQ classification and WAN policy plus Branch voice-VLAN pilot
- **Parent project:** [P10 — AAA And Network Access Control](../project-10-aaa-access-control/)

## Why This Matters

Without QoS, voice, routing, web, and bulk traffic compete equally when a WAN
link is congested. I built P11 to classify traffic, mark it consistently, and
reserve bandwidth through a controlled 1 Mbps edge policy.

## Portfolio Summary

**Situation:** The enterprise WAN had no traffic differentiation.

**Task:** Classify applications, mark DSCP, build hierarchical shaping and
queuing, verify real packets, and prepare voice access at the Branch.

**Action:** I created NBAR and ACL classes, applied inbound marking, nested an
LLQ child under a 1 Mbps parent shaper, generated HTTP traffic, added voice VLAN
500 on two ports, evaluated AutoQoS, and broke one class-map deliberately.

**Result:** PASS. Fifty-four live HTTP packets were marked AF11, the hierarchical
policy operated with no drops during verification, and the voice VLAN stayed
separate from each port's data VLAN.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 5](#phase-5--live-traffic-and-fallback-classification) |
| Technical reviewer | [Original technical record](technical-details.md), [configs](configs/), and [verification outputs](verification-outputs/) |
| Future operator | [Decision log](decision-log.md) and [limitations and expansion](LIMITATIONS-AND-HOMELAB-EXPANSION.md) |

## My Test Boundary

| Item | Boundary |
|---|---|
| Pilot router | HQ-RTR1 |
| Marking point | Ethernet0/0.100 inbound |
| WAN policy | Ethernet0/1 outbound; 1 Mbps shaper |
| Voice pilot | BR-ASW1 Et1/0 and Et1/1; VLAN 500 |
| Fault | Remove one class-map match, then restore it |
| Platform limit | AutoQoS unsupported on IOL-L2 |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 0 | Readiness | Complete |
| 1 | Classification | Complete |
| 2 | DSCP Marking | Complete |
| 3 | Hierarchical WAN Policy | Complete |
| 4 | Policy Verification | Complete |
| 5 | Live Traffic And Fallback Classification | Complete |
| 6 | Voice VLAN Pilot | Complete |
| 7 | AutoQoS Limitation | Deferred — unsupported on IOL-L2 |
| 8 | Empty Class-Map Break/Fix | Complete |

## Phase 0 — Readiness

I confirmed OSPF adjacencies, baseline latency, supported class-map syntax, and
the absence of an existing service policy. That prevented an old policy or
routing fault from contaminating the QoS result.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 1 — Classification

I created classes for voice, signaling, network control, and bulk data. The IOL
parser accepted the NBAR statements, so I could build the marking policy before
attaching it to traffic.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 2 — DSCP Marking

I applied `P11-MARK-IN` to Engineering traffic and mapped RTP to EF, SIP to CS3,
OSPF/DNS to CS2, and bulk data to AF11. Initial class-default counters proved
the policy was active even before application-specific traffic was generated.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 3 — Hierarchical WAN Policy

I created a 1 Mbps parent shaper and nested the LLQ/bandwidth child policy beneath
it. Voice received priority treatment, other classes received defined shares,
and class-default used fair queueing. Post-change pings confirmed routing stayed
healthy.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 4 — Policy Verification

I inspected both interfaces and the nested policy structure. The shaper and
queues were active with zero drops during the verification window, establishing
the correct framework before live application testing.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 5 — Live Traffic And Fallback Classification

I generated HTTP from PC-ENG1 to the Nginx server. IOL's NBAR PDL did not classify
the live traffic, so I added a narrowly scoped ACL-based class rather than
calling the test a failure. The counters showed 54 packets matched and marked
AF11, proving the operational policy with a supported method.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 6 — Voice VLAN Pilot

The router gateway and trunks already carried VLAN 500, so I changed only the
two Branch access ports to add `switchport voice vlan 500`. Their existing data
VLANs remained unchanged, and switchport output proved the dual-role design.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 7 — AutoQoS Limitation

IOL-L2 rejected `auto qos` and its verification commands. I applied nothing and
retained the manual MQC design as the working solution. The [limitations guide](LIMITATIONS-AND-HOMELAB-EXPANSION.md)
defines how to repeat AutoQoS on a capable platform.

## Phase 8 — Empty Class-Map Break/Fix

I removed the ACL match from the bulk class, observed traffic fall into
class-default, and diagnosed `Match none` with `show class-map`. Restoring the
match returned 66 packets to the intended class and marking path.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## What I Proved

- MQC can classify, mark, shape, and queue traffic in separate layers.
- Hierarchical policy can enforce a WAN rate while preserving class treatment.
- Live packet counters are stronger proof than accepted syntax.
- ACL classification is a valid fallback when IOL NBAR cannot identify traffic.
- A voice VLAN can coexist with an unchanged data VLAN on the same access port.
- An empty class-map produces a clear, reversible failure signature.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Phase configurations](configs/)
- [Verification outputs](verification-outputs/)
- [Decision log](decision-log.md)
- [Limitations and expansion guide](LIMITATIONS-AND-HOMELAB-EXPANSION.md)
- [Codex session log](../CODEX-LOG.md)

## How We Worked Together

### My Input And How I Helped

I applied each reviewed QoS phase in CML, generated HTTP traffic, returned the
policy counters, added the voice-VLAN settings, and performed the break/fix.

### What Codex Did And How

Codex designed the phased MQC policy, supplied the exact verification commands,
recognized the NBAR traffic limitation, proposed the ACL fallback, and interpreted
the returned counters. Codex also migrated this project page.

### What Claude Did And How

Claude served as the independent review gate under the repository workflow,
checking the phase safety, platform syntax, and evidence before closeout. The
retained files do not reproduce every review comment, so I do not claim more.

### How We Communicated And Completed The Project

Codex proposed a phase, Claude reviewed it, and I applied it and returned the
show output. We used the same loop for the NBAR fallback, voice pilot, and
break/fix, then closed only after counters proved the restored class.

### Pushback And How We Resolved It

NBAR accepted the configuration but did not classify live HTTP, and AutoQoS was
absent. We relied on observed counters, adopted a narrow ACL fallback for live
proof, and documented AutoQoS as a platform limitation rather than pretending
the simulator supported it.

## Reproduce Or Re-Verify

1. Verify OSPF, latency, and an empty QoS baseline.
2. Apply [configs](configs/) in order from classes to marking to nested WAN policy.
3. Generate live traffic and verify class, mark, shaper, queue, and drop counters.
4. Add voice VLAN 500 only after confirming the existing trunk and gateway.
5. Back up the class-map before the bounded empty-match fault and prove restoration.

## What Happens Next

P11 is closed. [P12](../project-12-disaster-recovery/) uses the accumulated
project records to rebuild critical devices under a timer. P11 does not
authorize that destructive exercise.
