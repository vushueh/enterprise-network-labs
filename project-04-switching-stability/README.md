# P04 — Switching Layer Stability

- **Status:** ✅ Complete — 2026-04-13
- **Project ID:** `Enterprise-P04`
- **Platform:** Cisco CML 2.9 with IOL-L2
- **Scope:** HQ distribution and access switching
- **Parent project:** [P03 — Dynamic Routing With OSPF](../project-03-ospf-dynamic-routing/)

## Why This Matters

Redundant links only improve availability when STP and EtherChannel behavior are
intentional. I hardened the HQ switching layer so a loop, rogue root, bad trunk,
or member mismatch would be contained and diagnosable.

## Portfolio Summary

**Situation:** HQ used default STP behavior and one inter-distribution link.

**Task:** Add link redundancy, deterministic loop protection, fast fault
detection, access safeguards, and a realistic multi-fault exercise.

**Action:** I built a two-member LACP port-channel, split STP roots, added Loop
Guard, Root Guard, UDLD, errdisable recovery, ran a VTPv3 lab, traced MAC paths,
protected access ports, and injected three Layer 2 faults.

**Result:** PASS. Po1 stayed operational, root placement matched the design, and
LACP mismatch, native-VLAN mismatch, and root hijack were diagnosed and repaired.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 7](#phase-7--three-fault-breakfix) |
| Technical reviewer | [Original technical record](technical-details.md), [configs](configs/), and [verification](verification/) |
| Future operator | [Requirement](requirement.md), [decision log](decision-log.md), and [troubleshooting log](TROUBLESHOOTING-LOG.md) |

## My Test Boundary

| Item | Boundary |
|---|---|
| Devices | HQ-DSW1/2 and HQ-ASW1/2 |
| EtherChannel | Et0/3 and Et1/0 bundled as LACP Po1 |
| STP | Split roots by VLAN; access switches cannot become root |
| Edge ports | PortFast and BPDU Guard |
| Faults | One LACP member, one native VLAN, one rogue root priority |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 1 | LACP EtherChannel | Complete |
| 2 | Advanced STP Controls | Complete |
| 3 | UDLD And Recovery | Complete |
| 4 | VTPv3 Learning Lab | Complete |
| 5 | MAC Path Analysis | Complete |
| 6 | Port Protection | Complete |
| 7 | Three-Fault Break/Fix | Complete |

## Phase 1 — LACP EtherChannel

I replaced the single inter-distribution trunk with two physical members in
Po1. I verified both links bundled under LACP before removing the old standalone
assumption. The saved [configs](configs/) and [screenshots](verification/screenshots/)
show the operational port-channel that the STP design uses next.

## Phase 2 — Advanced STP Controls

I split root ownership across HQ-DSW1 and HQ-DSW2, placed Loop Guard on Po1, and
used Root Guard on access-layer downlinks. Some ports entered root-inconsistent
state during verification; I confirmed that was the intended containment
behavior, not a broken trunk.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 3 — UDLD And Recovery

I enabled UDLD on inter-switch links and configured bounded errdisable recovery.
IOL-L2 rejected storm-control commands, so I documented that platform gap rather
than pretending the feature existed. The supported controls remained active.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 4 — VTPv3 Learning Lab

I promoted one switch temporarily, created test VLAN 600, verified propagation,
then returned all switches to transparent mode. VLAN 600 remained until I
removed it explicitly, demonstrating that mode changes do not erase the VLAN
database automatically.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 5 — MAC Path Analysis

I generated traffic from PC-ENG1 and followed its MAC from the access switch
through the distribution layer. The table moved with the actual STP forwarding
path, connecting the logical root design to observed frames.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 6 — Port Protection

I applied PortFast and BPDU Guard to host ports, Root Guard at the access
boundary, and the appropriate BPDU treatment on the router-facing link. These
controls reduced the chance that a host or rogue switch could change campus
topology.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 7 — Three-Fault Break/Fix

I introduced an LACP mode mismatch, a native-VLAN mismatch, and a rogue STP root
priority. `show etherchannel summary`, CDP, and spanning-tree state isolated the
three symptoms. I restored LACP active mode, native VLAN 1000, and the intended
root priority, then re-ran the full Layer 2 verification.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## What I Proved

- Two physical links operate as one LACP port-channel.
- Split-root STP creates predictable active paths.
- Loop Guard and Root Guard contain dangerous control-plane failures.
- VTPv3 changes can be bounded and reversed deliberately.
- MAC tables reveal the actual forwarding path.
- Three concurrent Layer 2 faults can be separated and repaired with show commands.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Requirement](requirement.md)
- [Device configurations](configs/)
- [Verification screenshots](verification/screenshots/)
- [Decision log](decision-log.md)
- [Troubleshooting log](TROUBLESHOOTING-LOG.md)
- [Protection diagrams](diagrams/)

## How We Worked Together

### My Input And How I Helped

I applied the switching configurations, supplied the live show output, performed
the VTP exercise, and injected and repaired the three faults in CML.

### What Codex Did And How

The original P04 files do not preserve reliable per-agent attribution. Codex
therefore limits its claim to this migration: preserving the long README and
writing this linked phase narrative.

### What Claude Did And How

The original P04 record does not identify a distinct Claude task. During this
migration, Claude included P04 in a repository-wide read-only review and
verified its completion status. Claude did not read this page line by line, so
I do not claim a full independent review of the rewritten story.

### How We Communicated And Completed The Project

I returned phase evidence and retained configurations, diagrams, and faults in
the repo. Later, I defined the documentation standard, Codex reorganized and
verified the entry page, and Claude checked its status in the wider batch.

### Pushback And How We Resolved It

IOL-L2 rejected storm control, VTP propagation was not immediate, and expected
Root Guard states looked like failures. I separated simulator limitations from
real configuration errors, waited for protocol state, and used the intended
design to interpret each result before changing anything.

## Reproduce Or Re-Verify

1. Start from the complete P03 topology and back up all four switch configs.
2. Apply the [configs](configs/) in phase order and verify Po1 before STP controls.
3. Confirm roots, guard placement, UDLD, MAC paths, and access protections.
4. Run the VTP exercise only with a temporary VLAN and remove it afterward.
5. Inject the three bounded faults, repair them, and compare with [verification](verification/).

## What Happens Next

P04 is closed. [P05](../project-05-internet-nat/) adds a simulated ISP, PAT,
static NAT, and guest isolation. P04 does not authorize that next project.
