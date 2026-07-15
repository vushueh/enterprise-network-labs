# P06 — Security Hardening

- **Status:** ✅ Complete — 2026-05-02
- **Project ID:** `Enterprise-P06`
- **Platform:** Cisco CML 2.9 with IOL, IOL-L2, and Alpine
- **Scope:** HQ access, distribution, routing, and management controls
- **Parent project:** [P05 — Internet Access And NAT](../project-05-internet-nat/)

## Why This Matters

Connectivity alone leaves the campus open to rogue devices, ARP spoofing, IP
spoofing, and broad management access. I layered controls onto the working HQ
network and tested them without rebuilding the foundation.

## Portfolio Summary

**Situation:** User ports accepted arbitrary devices and management networks
were broadly reachable.

**Task:** Enforce endpoint identity, protect DHCP and ARP, restrict source IPs,
shield management, and harden administrative sessions.

**Action:** I added port security, DHCP snooping, static source bindings, DAI,
IP Source Guard, logged inter-VLAN ACLs, login protection, and errdisable
recovery, then simulated MAC, ARP, and IP attacks.

**Result:** PASS within the documented IOL limits. Unauthorized MAC, ARP, IP,
and management traffic was blocked, while approved inter-VLAN and internet
traffic remained available.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 5](#phase-5--management-network-protection) |
| Technical reviewer | [Original technical record](technical-details.md), [configs](configs/), and [verification](verification/) |
| Future operator | [Requirement](requirement.md), [decision log](decision-log.md), and [troubleshooting log](TROUBLESHOOTING-LOG.md) |

## My Test Boundary

| Item | Boundary |
|---|---|
| Devices | HQ-ASW1, HQ-ASW2, and HQ-RTR1 |
| Endpoint controls | Existing access ports only |
| Management protection | Deny user VLANs to `10.1.99.0/24`; log violations |
| Attack node | Alpine test endpoint in the isolated CML lab |
| Platform caveat | IOL-L2 snooping enforcement uses documented static-binding workaround |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 1 | Port Security | Complete |
| 2 | DHCP Snooping | Complete with IOL limitation |
| 3 | Dynamic ARP Inspection | Complete |
| 4 | IP Source Guard | Complete |
| 5 | Management Network Protection | Complete |
| 6 | Management Plane Hardening | Complete |
| 7 | Errdisable Recovery | Complete |
| 8 | Trust-Port Lesson | Documented — conceptual on IOL-L2 |

## Phase 1 — Port Security

I enabled sticky MAC learning and selected restrict or shutdown behavior by port
risk. Replacing an endpoint triggered the expected violation, and I documented
the IOL-specific recovery method when a normal clear command was unavailable.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 2 — DHCP Snooping

I trusted only uplinks and rate-limited access ports. IOL-L2 did not populate or
enforce the binding table as physical Catalyst hardware would, so I added static
source bindings and recorded the simulator limitation. I did not claim hardware
enforcement that the evidence could not show.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 3 — Dynamic ARP Inspection

I built ARP ACLs from the known bindings and enabled DAI on the user VLANs. A
gratuitous spoof attempt was dropped and the victim's ARP table stayed unchanged.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 4 — IP Source Guard

I applied the supported `mac-check` source validation to access ports. Traffic
with a spoofed source IP failed while the authorized endpoint address continued
to work.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 5 — Management Network Protection

I applied inbound ACLs to user VLAN subinterfaces, denied access to VLAN 999,
logged the violations, and retained approved user-to-server paths. Positive and
negative tests proved the ACLs protected management without flattening the campus.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 6 — Management Plane Hardening

I added login block timers, console and VTY idle timeouts, and removed unnecessary
services on the in-scope HQ devices. The resulting show output demonstrated a
smaller and more controlled administrative surface.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 7 — Errdisable Recovery

I enabled recovery only for selected causes with a defined interval. The control
supports lab recovery without hiding the original security event.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 8 — Trust-Port Lesson

I documented how trusting an access port would admit rogue DHCP offers and how
to restore trust to the uplink. Because IOL-L2 does not enforce snooping in the
same way as Catalyst hardware, this remains a configuration and reasoning proof,
not a claimed live packet block.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## What I Proved

- Sticky port security detects unauthorized MAC changes.
- DAI blocks a demonstrated ARP-spoofing attempt.
- IP Source Guard blocks a demonstrated source-IP spoof.
- Logged ACLs protect the management VLAN from user networks.
- Administrative sessions have brute-force and idle-session controls.
- Simulator limitations can be documented with a defensible workaround.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Requirement](requirement.md)
- [Configurations](configs/)
- [Verification and screenshots](verification/)
- [Decision log](decision-log.md)
- [Troubleshooting log](TROUBLESHOOTING-LOG.md)

## How We Worked Together

### My Input And How I Helped

I applied each CML control, replaced test endpoints, generated the attack traffic,
returned show and syslog output, and approved only the isolated fault tests.

### What Codex Did And How

The original P06 record does not provide reliable per-agent attribution. Codex
therefore claims only the 2026 documentation migration: preservation of the
technical record and creation of this concise page.

### What Claude Did And How

The original record does not identify a distinct historic Claude role. During
this migration, Claude included P06 in a repository-wide read-only review and
verified its completion status. Claude did not read this page line by line, so
I do not claim a full independent review of the rewritten story.

### How We Communicated And Completed The Project

I returned CML evidence after each control and saved configs and faults in the
repo. Later, Codex transformed and verified the entry page under my standard,
and Claude checked its status in the wider batch.

### Pushback And How We Resolved It

IOL-L2 accepted several commands but could not enforce or display all physical
switch behaviors. We tested observable controls, used static bindings where the
platform required them, and labeled the DHCP trust exercise conceptual instead
of forcing a misleading success claim.

## Reproduce Or Re-Verify

1. Start from P05 and save the switch and router baseline.
2. Apply each [config](configs/) separately and verify authorized traffic first.
3. Run MAC, ARP, IP, and management negative tests only from the isolated attacker.
4. Confirm recovery and normal traffic after every test.
5. Treat the snooping enforcement gap as an IOL limitation when comparing results.

## What Happens Next

P06 is closed. [P07](../project-07-asav-firewall/) moves perimeter policy and
NAT to an ASAv. P06 does not authorize that cutover.
