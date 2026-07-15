# P01 — Campus Foundation

- **Status:** ✅ Complete — 2026-04-03
- **Project ID:** `Enterprise-P01`
- **Platform:** Cisco CML 2.9 with IOL and IOL-L2
- **Scope:** One HQ campus with segmented user and management networks
- **Series:** [Enterprise Network Labs](../)

## Why This Matters

An enterprise network needs a stable campus before it can add branches,
security, or automation. I built P01 from a blank topology so I could prove the
fundamentals work together: VLANs, trunks, STP, inter-VLAN routing, and protected
device management.

## Portfolio Summary

**Situation:** I had studied the technologies separately but had not designed a
complete campus from written requirements.

**Task:** Segment Engineering, Sales, Guest, and Management; route between the
approved networks; make STP deterministic; and restrict SSH to management.

**Action:** I created VLANs 100/200/300/999, hardened the native VLAN, pruned
trunks, configured router-on-a-stick, split STP root roles, enabled edge
protections, and limited VTY access to the management network.

**Result:** PASS. The campus routed correctly, trunks carried only intended
VLANs, STP selected the planned roots, and SSH succeeded from Management while
failing from an unauthorized user VLAN.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 6](#phase-6--redundancy-breakfix) |
| Technical reviewer | [Original technical record](technical-details.md), [device configurations](configs/), and [verification evidence](verification/) |
| Future operator | [Requirement](requirement.md), [decision log](notes/decision-log.md), and [lab guide](docs/campus-foundation-lab-guide.pdf) |

## My Test Boundary

| Item | Boundary |
|---|---|
| Site | HQ campus only |
| User VLANs | 100 Engineering, 200 Sales, 300 Guest |
| Management | VLAN 999; SSH source restriction |
| Native VLAN | Unused VLAN 1000 |
| Routing | HQ-RTR1 router-on-a-stick |
| Fault scope | VLAN 100 trunk allowance on redundant access uplinks |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 1 | VLAN Foundation | Complete |
| 2 | Trunking | Complete |
| 3 | Inter-VLAN Routing | Complete |
| 4 | STP Hardening | Complete |
| 5 | SSH Management | Complete |
| 6 | Redundancy Break/Fix | Complete |

## Phase 1 — VLAN Foundation

I created separate broadcast domains for Engineering, Sales, Guest, and
Management, then placed endpoint ports in the correct access VLANs. The
[requirements](requirement.md) and [addressing record](technical-details.md#ip-addressing)
fixed the intended roles first. With local Layer 2 membership proven, I could
connect the switches without accidentally extending every VLAN everywhere.

## Phase 2 — Trunking

I configured the inter-switch links as 802.1Q trunks, used VLAN 1000 as an
unused native VLAN, and pruned the allowed list. `show interfaces trunk` and the
[screenshots](verification/screenshots/) proved both ends agreed. Those clean
trunks created the path required for routing and STP verification.

## Phase 3 — Inter-VLAN Routing

I configured HQ-RTR1 subinterfaces as the VLAN gateways and verified traffic
between the approved networks. The saved [router configuration](configs/HQ-RTR1.txt)
and [post-change evidence](verification/post-change/) show the routed boundary.
Once Layer 3 worked, I hardened the redundant Layer 2 design.

## Phase 4 — STP Hardening

I assigned deliberate primary and secondary roots instead of accepting default
bridge elections. PortFast and BPDU Guard protected host-facing ports, while
the redundant distribution paths remained available. This made the forwarding
topology predictable before remote management was enabled.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 5 — SSH Management

I enabled SSHv2, generated the required keys, and restricted VTY access to VLAN
999. A user-VLAN SSH attempt was denied while the management endpoint succeeded.
That separation made the campus manageable without exposing device access to
every department.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 6 — Redundancy Break/Fix

I first removed VLAN 100 from one trunk and expected an outage, but the redundant
uplink carried the traffic. I then removed VLAN 100 from both HQ-ASW1 uplinks,
observed Engineering fail while other VLANs stayed healthy, diagnosed the
missing allowed VLAN with show commands, and restored both lists. The exercise
proved redundancy and showed why one-link tests can hide inconsistent trunks.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## What I Proved

- A campus can be segmented into functional user and management VLANs.
- Pruned trunks and an unused native VLAN reduce unnecessary exposure.
- Router-on-a-stick provides controlled inter-VLAN connectivity.
- Deliberate STP roots make redundant forwarding predictable.
- SSH can be limited to a dedicated management network.
- Dual uplinks survive one fault and expose a full-path configuration error.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Written requirement](requirement.md)
- [Device configurations](configs/)
- [CML topology export](cml/campus-foundation.yaml)
- [Topology diagrams](diagrams/)
- [Verification outputs and screenshots](verification/)
- [Decision log](notes/decision-log.md)
- [Lab guide](docs/campus-foundation-lab-guide.pdf)

## How We Worked Together

### My Input And How I Helped

I designed the topology, applied the configurations in CML, returned the show
outputs, performed the fault injection, and captured the screenshots. I also
recognized that the first fault did not fail because the redundant path worked,
then approved the bounded two-uplink test.

### What Codex Did And How

The retained P01 files do not preserve a reliable agent-by-agent attribution
for the original build, so Codex does not claim work that cannot be proved. For
this migration, Codex preserved the full README as `technical-details.md` and
wrote this evidence-linked phase narrative.

### What Claude Did And How

The retained P01 files likewise do not document a distinct Claude contribution
to the original build. During the documentation migration, Claude independently
reviewed the new summary for factual accuracy, role claims, and link integrity.

### How We Communicated And Completed The Project

I supplied the CML results and kept the configs, diagrams, and troubleshooting
evidence in the repository. For the later migration, I set the documentation
standard, Codex reorganized the entry page, and Claude reviewed it. The original
technical record remains the detailed source.

### Pushback And How We Resolved It

The first break test did not create the expected outage because redundancy did
exactly what it should. I did not call that a failed lab; I documented the path
shift, expanded the fault only to both VLAN 100 uplinks, and proved the repair
without disturbing other VLANs.

## Reproduce Or Re-Verify

1. Build the topology from the [CML export](cml/campus-foundation.yaml) or
   [diagrams](diagrams/).
2. Apply the saved [device configurations](configs/) in phase order.
3. Verify VLANs, trunks, gateways, STP roots, and SSH from both authorized and
   unauthorized sources.
4. Back up the state, remove VLAN 100 from one uplink, observe redundancy, then
   test the bounded two-uplink fault and restore both lists.
5. Compare the result with [verification](verification/) before closing.

## What Happens Next

P01 is closed. [P02](../project-02-multi-site-dhcp/) extends this campus to a
branch with centralized DHCP, DNS, and IPv6. P01 does not authorize that next
project or any new live CML change.
