# P08 — Site-To-Site VPN

- **Status:** ✅ Complete — 2026-05-11
- **Project ID:** `Enterprise-P08`
- **Platform:** Cisco CML 2.9 with IOL routers
- **Scope:** GRE over IKEv2/IPsec between HQ and Branch
- **Parent project:** [P07 — ASAv Perimeter Firewall](../project-07-asav-firewall/)

## Why This Matters

Dynamic routing can keep sites connected, but it does not protect traffic from
someone on the WAN path. I built P08 to encrypt inter-site routing and data
without losing OSPF failover.

## Portfolio Summary

**Situation:** HQ and Branch exchanged traffic in plaintext across the WAN.

**Task:** Build an encrypted preferred path, preserve backup routing, verify the
crypto state, and demonstrate proposal-mismatch troubleshooting.

**Action:** I built GRE first, formed OSPF on Tunnel0, added IKEv2/IPsec with
AES-256/SHA-256/DH14, verified route preference, then broke one proposal and
repaired it from show-command evidence.

**Result:** PASS. OSPF preferred the encrypted tunnel, IPsec counters increased,
and the proposal mismatch was diagnosed and restored without debug commands.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 4](#phase-4--proposal-mismatch-breakfix) |
| Technical reviewer | [Original technical record](technical-details.md), [configs](configs/), and [screenshots](verification/screenshots/) |
| Future operator | [Requirement](requirement.md), [decision log](decision-log.md), and [troubleshooting log](TROUBLESHOOTING-LOG.md) |

## My Test Boundary

| Item | Boundary |
|---|---|
| Peers | HQ-RTR1 and BR-RTR1 |
| Underlay | Existing direct WAN link |
| Overlay | Tunnel0 `10.0.100.0/30` |
| Crypto | IKEv2/IPsec transport mode, AES-256, SHA-256, DH14 |
| Routing | OSPF cost 5 on tunnel; physical paths retained |
| Fault | AES-128 proposal on Branch only, then full restoration |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 1 | GRE And OSPF | Complete |
| 2 | IKEv2 And IPsec | Complete |
| 3 | Protected Route Preference | Complete |
| 4 | Proposal Mismatch Break/Fix | Complete |

## Phase 1 — GRE And OSPF

I created Tunnel0 without crypto first, set a conservative MTU and MSS, and
formed OSPF across the overlay. The tunnel cost made it preferred while the
physical OSPF paths remained available. This separated routing validation from
crypto troubleshooting.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 2 — IKEv2 And IPsec

I added matching IKEv2 proposals, policies, keyrings, profiles, an IPsec
transform set, and tunnel protection on both routers. Claude's review caught
that this IOL image requires numeric IKEv2 policy ID `10`, not the named value
in the first Codex proposal. We corrected it before application, then verified
READY SAs and increasing encapsulation and decapsulation counters.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 3 — Protected Route Preference

I compared OSPF routes and traceroutes with the crypto session. Traffic used
Tunnel0 as the lowest-cost path while the IPsec SA protected the GRE packets.
The IOL engine accepted PFS group14 in configuration but reported inconsistent
SA-level PFS behavior, so the [decision log](decision-log.md) preserves that
platform caveat without calling it a policy failure.

## Phase 4 — Proposal Mismatch Break/Fix

I changed only BR-RTR1 from AES-256 to AES-128, cleared the session, and observed
the missing IKEv2 SA while fallback routing kept the sites reachable. I compared
the two proposal sections, restored AES-256, and verified the tunnel, OSPF route,
and IPsec counters returned. The [troubleshooting log](TROUBLESHOOTING-LOG.md)
records the diagnosis path.

## What I Proved

- GRE can carry OSPF while IPsec protects the underlay packets.
- Cost tuning makes the encrypted overlay preferred without deleting backups.
- IKEv2 and IPsec state can be verified with multiple independent commands.
- A crypto proposal mismatch has a distinct, diagnosable symptom.
- Backup routing preserves site connectivity while the VPN is down.
- Platform crypto limitations can be separated from configuration correctness.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Requirement](requirement.md)
- [Router configurations](configs/)
- [Verification screenshots](verification/screenshots/)
- [Decision log](decision-log.md)
- [Troubleshooting log](TROUBLESHOOTING-LOG.md)
- [Persistent Claude review record](../CLAUDE-REVIEW.md)

## How We Worked Together

### My Input And How I Helped

I applied the reviewed configurations in CML, returned the GRE, OSPF, IKEv2,
IPsec, route, and counter output, and performed the bounded mismatch and repair.

### What Codex Did And How

Codex proposed the GRE, OSPF, and crypto configurations, designed the phase and
fault verification, incorporated Claude's syntax correction, and interpreted
the returned evidence. During this migration, Codex preserved the full record
and wrote the concise story.

### What Claude Did And How

Claude independently reviewed the proposal against existing configs, caught the
unsupported named IKEv2 policy identifier before it touched CML, confirmed the
correct numeric syntax, and reviewed the crypto evidence and PFS caveat.

### How We Communicated And Completed The Project

Codex proposed each bounded phase, Claude reviewed it, and I applied only the
approved version and returned output. Review findings were incorporated before
the next phase, and the break/fix closed only after the encrypted preferred path
and backup routing both verified.

### Pushback And How We Resolved It

Claude rejected one platform-incompatible policy identifier and required numeric
syntax. We corrected the proposal before application. Later, IOL reported PFS
differently from real hardware despite accepting the configuration; we retained
the correct config and documented the simulator behavior instead of forcing a
false claim.

## Reproduce Or Re-Verify

1. Confirm the P07 underlay and all physical OSPF paths are healthy.
2. Apply GRE and verify Tunnel0 routing before adding crypto.
3. Apply the reviewed [configs](configs/) with numeric IKEv2 policy syntax.
4. Verify IKEv2, IPsec, OSPF, route preference, traceroute, and counters together.
5. Back up both peers before the bounded proposal mismatch and verify full repair.

## What Happens Next

P08 is closed. [P09](../project-09-monitoring-visibility/) adds centralized
visibility across the enterprise lab. P08 does not authorize P09.
