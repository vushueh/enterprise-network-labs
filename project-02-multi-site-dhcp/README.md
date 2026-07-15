# P02 — Multi-Site Expansion And DHCP

- **Status:** ✅ Complete — 2026-04-05
- **Project ID:** `Enterprise-P02`
- **Platform:** Cisco CML 2.9, IOL/IOL-L2, and Dnsmasq
- **Scope:** HQ-to-Branch expansion with centralized services
- **Parent project:** [P01 — Campus Foundation](../project-01-campus-foundation/)

## Why This Matters

A campus design must scale beyond one building. I used P02 to prove that a new
branch can follow the same segmentation and management standards while sharing
central DHCP and DNS services across a routed WAN.

## Portfolio Summary

**Situation:** HQ had working VLANs but no branch, centralized address service,
DNS, or IPv6.

**Task:** Build the branch, connect both sites, relay DHCP for eight user pools,
add dual-stack connectivity, and resolve infrastructure names end to end.

**Action:** I built the branch router and switches, added a /30 WAN, configured
explicit static routes, deployed Dnsmasq at HQ, added helpers and reservations,
enabled IPv6 SLAAC, and populated DNS records.

**Result:** PASS. Branch endpoints received reserved addresses from HQ, both
sites routed over IPv4 and IPv6, and infrastructure names resolved across the
WAN.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 6](#phase-6--three-fault-dhcp-breakfix) |
| Technical reviewer | [Original technical record](technical-details.md), [configs](configs/), and [verification](verification/) |
| Future operator | [Requirement](requirement.md), [decision log](notes/decision-log.md), and [lab guide](docs/multi-site-dhcp-lab-guide.pdf) |

## My Test Boundary

| Item | Boundary |
|---|---|
| Sites | Existing HQ plus one new Branch |
| WAN | `10.0.0.0/30` IPv4 and `2001:db8:0:1::/126` IPv6 |
| DHCP/DNS | Central Dnsmasq node at HQ |
| Relay scope | User VLAN subinterfaces at both sites |
| Routing | Explicit static routes for this phase |
| Fault scope | Three bounded DHCP faults; DNS and management preserved |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 1 | Branch Campus Baseline | Complete |
| 2 | WAN Connectivity | Complete |
| 3 | Centralized DHCP | Complete |
| 4 | IPv6 Dual-Stack | Complete |
| 5 | DNS End-To-End | Complete |
| 6 | Three-Fault DHCP Break/Fix | Complete |

## Phase 1 — Branch Campus Baseline

I mirrored the HQ VLAN and management model on BR-RTR1, BR-DSW1, and BR-ASW1.
A cabling mismatch initially placed PC-BR1 on a different interface than the
configured access port; I cross-checked the CML canvas, corrected the physical
attachment, and verified local VLAN and gateway reachability. That stable branch
provided one end of the WAN.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 2 — WAN Connectivity

I addressed the HQ-to-Branch /30 link and installed explicit routes in both
directions. BR-ASW1 needed `ip routing` plus a default route because its
management plane could not answer remote-subnet ICMP with only
`ip default-gateway`. Once both sites could reach each other's infrastructure,
the HQ service node could serve remote clients.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 3 — Centralized DHCP

I deployed Dnsmasq at `10.1.99.50` and added `ip helper-address` to every served
VLAN interface. Startup timing, an `interface=eth0` restriction, missing access
VLAN configuration, and absent helper addresses each blocked part of the flow.
I corrected them at their owning layer and added MAC reservations for stable
endpoint identities. The [phase configs](configs/) and [DHCP evidence](verification/)
record the final relay path.

## Phase 4 — IPv6 Dual-Stack

I added a /126 IPv6 WAN and /64 Engineering prefixes at both sites. Router
advertisements gave endpoints SLAAC addresses, and cross-site IPv6 tests proved
the new stack without removing IPv4. This prepared the design for dynamic IPv6
routing in P03.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 5 — DNS End-To-End

I learned that `domain=` and `local=` route queries but do not create records.
I added explicit infrastructure records, paired endpoint names with reserved
DHCP addresses, re-enabled IOS domain lookup where needed, and verified names
from both sites. That made the service layer depend on stable addressing rather
than a temporary lease.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 6 — Three-Fault DHCP Break/Fix

I injected three DHCP failures at once: one missing helper, one wrong pool
range, and one disabled server path. The resulting helpdesk symptoms affected
specific VLANs while DNS and management stayed available. I followed the packet
path from client to relay to server, repaired each fault, and renewed the leases.
The project-level [troubleshooting log](notes/TROUBLESHOOTING-LOG.md) preserves
the evidence and lessons.

## What I Proved

- The campus design can be reproduced at a second site.
- Static WAN routing can connect the two campuses predictably.
- One centralized Dnsmasq server can serve remote VLANs through DHCP relay.
- Reservations make DHCP-backed DNS records stable across restarts.
- IPv4 and IPv6 can operate together across the WAN.
- Layered troubleshooting can isolate simultaneous service faults.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Requirement](requirement.md)
- [Phase configurations](configs/)
- [Verification outputs and screenshots](verification/)
- [Project troubleshooting log](notes/TROUBLESHOOTING-LOG.md)
- [Decision log](notes/decision-log.md)
- [CML topology](diagrams/cml-topology.png)
- [Lab guide](docs/multi-site-dhcp-lab-guide.pdf)

## How We Worked Together

### My Input And How I Helped

I built and cabled the CML nodes, applied every approved configuration, returned
the live outputs, tested both protocol stacks, and performed the three-fault
exercise. My console checks identified the wrong node and port during two key
troubleshooting steps.

### What Codex Did And How

The retained P02 record does not reliably divide the original work by agent, so
Codex does not claim an unsupported historic role. In this migration, Codex
preserved all detail in `technical-details.md` and produced this linked story.

### What Claude Did And How

The retained P02 record does not document a distinct historic Claude role.
During this migration, Claude included P02 in a repository-wide read-only
review and verified its completion status. Claude did not read this page line
by line, so I do not claim a full independent review of the rewritten story.

### How We Communicated And Completed The Project

I supplied live CML results and saved the configs, output, and troubleshooting
record. During the later migration, I defined the required format, Codex rewrote
and verified the entry page, and Claude checked its status in the wider batch.

### Pushback And How We Resolved It

The DHCP service failed for several unrelated reasons that looked similar from
the client. We stopped treating “no lease” as one problem and checked node state,
switch VLAN, relay, server binding, pool, and startup timing in order. Each fix
was verified before continuing to DNS and IPv6.

## Reproduce Or Re-Verify

1. Start from a healthy [P01](../project-01-campus-foundation/) campus.
2. Apply the branch and WAN [configs](configs/) in phase order and verify ports
   against the CML canvas.
3. Deploy Dnsmasq without restrictive interface binding, add every helper, and
   verify relay traffic before adding DNS.
4. Add reservations, DNS records, and IPv6 prefixes, then test both sites.
5. Compare all results with [verification](verification/) before attempting the
   bounded DHCP break/fix.

## What Happens Next

P02 is closed. [P03](../project-03-ospf-dynamic-routing/) replaces manual route
maintenance with authenticated, redundant dynamic routing. P02 does not
authorize that next project or any new CML mutation.
