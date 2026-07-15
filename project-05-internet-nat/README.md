# P05 — Internet Access And NAT

- **Status:** ✅ Complete — 2026-05-02
- **Project ID:** `Enterprise-P05`
- **Platform:** Cisco CML 2.9 with IOL, IOL-L2, and Nginx
- **Scope:** Simulated internet edge for HQ and Branch
- **Parent project:** [P04 — Switching Layer Stability](../project-04-switching-stability/)

## Why This Matters

Private networks need a controlled edge to reach outside services and publish
selected internal applications. I built P05 to demonstrate translation, default
routing, guest isolation, and the difference between expected pre-NAT failure
and a real fault.

## Portfolio Summary

**Situation:** HQ and Branch routed internally but had no internet edge.

**Task:** Add an ISP, provide PAT, publish one server with static NAT, preserve
guest isolation, and prove Branch traffic exits through HQ.

**Action:** I added ISP-RTR1 and two web servers, advertised a default route,
configured PAT and static NAT, refactored ACLs with object groups, restricted
Guest, applied MSS clamping, and traced Branch traffic.

**Result:** PASS. User networks reached the external server through PAT,
HQ-SRV1 was reachable as `203.0.113.10`, and Guest retained internet access
without access to private enterprise networks.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 7](#phase-7--branch-internet-proof) |
| Technical reviewer | [Original technical record](technical-details.md), [configs](configs/), and [screenshots](verification/screenshots/) |
| Future operator | [Requirement](requirement.md), [decision log](decision-log.md), and [troubleshooting log](TROUBLESHOOTING-LOG.md) |

## My Test Boundary

| Item | Boundary |
|---|---|
| Public lab range | Documentation range `203.0.113.0/24` |
| Edge | HQ-RTR1 connected to ISP-RTR1 |
| Outbound | PAT for approved HQ and Branch user networks |
| Inbound | One static mapping for HQ-SRV1 |
| Guest | Internet allowed; private enterprise ranges denied |
| Fault | Bad NAT ACL documented; live injection deferred |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 1 | ISP Simulation | Complete |
| 2 | PAT Overload | Complete |
| 3 | Static NAT | Complete |
| 4 | Object-Group Refactor | Complete |
| 5 | Guest Isolation | Complete |
| 6 | MSS Clamping | Complete |
| 7 | Branch Internet Proof | Complete |
| 8 | Deferred Bad-ACL Exercise | Deferred — documented future exercise |

## Phase 1 — ISP Simulation

I connected HQ-RTR1 to ISP-RTR1, created an outside web segment, added the
internal HQ server VLAN, and originated the default route into OSPF. Branch
learned the default but could not receive replies from the ISP while still using
private addresses. I retained that expected failure because it proved Phase 2
was necessary.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 2 — PAT Overload

I marked inside and outside interfaces, matched only approved source networks,
and overloaded traffic onto `203.0.113.1`. Translation and endpoint tests then
succeeded from HQ and Branch. The [verification evidence](verification/)
connects the observed traffic to the NAT table.

## Phase 3 — Static NAT

I placed HQ-SRV1 at `10.1.40.10`, mapped it to `203.0.113.10`, and added the
specific ISP route needed for that public address. Outside HTTP tests and NAT
state proved an inbound connection could reach only the published service.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 4 — Object-Group Refactor

I replaced repetitive NAT source entries with named object groups while keeping
the same traffic scope. Before-and-after translation tests proved the refactor
changed maintainability, not behavior.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 5 — Guest Isolation

I added an ingress Guest ACL that denied internal HQ and Branch ranges while
permitting the simulated internet. Positive and negative tests showed guests
could browse outward without reaching enterprise subnets.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 6 — MSS Clamping

I applied conservative TCP MSS adjustment on the WAN-facing path and verified
the interface configuration. This prepared the path for later tunnel overhead
without changing existing reachability.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 7 — Branch Internet Proof

I verified Branch default routing, endpoint traffic, the HQ edge translation,
and the external server response. The route, traceroute, NAT, and server evidence
showed the full cross-site path rather than only an HQ-local test.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 8 — Deferred Bad-ACL Exercise

The project documents a NAT ACL fault, expected symptoms, diagnosis, and repair,
but the retained evidence does not show that fault was injected live. I keep it
deferred instead of converting a plan into a completed result.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## What I Proved

- OSPF can distribute a controlled default route to the Branch.
- PAT translates multiple private networks through one public edge address.
- Static NAT can publish one service with an explicit upstream route.
- Guest can reach the internet while internal ranges remain blocked.
- Object groups simplify policy without changing its scope.
- Branch traffic follows the intended WAN-to-edge-to-ISP path.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Requirement](requirement.md)
- [Configurations](configs/)
- [Verification and screenshots](verification/)
- [Decision log](decision-log.md)
- [Troubleshooting log](TROUBLESHOOTING-LOG.md)

## How We Worked Together

### My Input And How I Helped

I added the CML nodes and links, applied the edge and NAT configurations, ran
the endpoint tests, and returned the route, translation, and screenshot proof.

### What Codex Did And How

The original P05 record does not reliably attribute each proposal to an agent.
Codex limits this claim to preserving the technical record and creating the new
phase-based README during the documentation migration.

### What Claude Did And How

The original P05 files do not prove a separate Claude task. During this
migration, Claude included P05 in a repository-wide read-only review and
verified its completion status. Claude did not read this page line by line, so
I do not claim a full independent review of the rewritten story.

### How We Communicated And Completed The Project

I supplied live CML results and committed the configs and evidence. Later, I set
the new documentation rules, Codex reorganized and verified the story, and
Claude checked its status in the wider batch.

### Pushback And How We Resolved It

Branch learned the default route but initially could not receive internet replies.
Instead of changing OSPF, I recognized the missing return path for private
addresses, added PAT, and verified the translation. An early ping also waited on
ARP; a repeat test after neighbor resolution separated timing from configuration.

## Reproduce Or Re-Verify

1. Start from P04 and add the ISP and server nodes shown in [technical details](technical-details.md).
2. Verify the default route before NAT and retain the expected private-address failure.
3. Apply PAT, static NAT, ACL, and MSS [configs](configs/) one phase at a time.
4. Test HQ, Branch, Guest, and inbound server paths separately.
5. Do not run the deferred bad-ACL fault without a new bounded CML window.

## What Happens Next

P05 is closed. [P06](../project-06-security-hardening/) adds access-layer and
management protections. P05 does not authorize P06 or the deferred NAT fault.
