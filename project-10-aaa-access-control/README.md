# P10 — AAA And Network Access Control

- **Status:** ✅ Complete — 2026-05-22
- **Project ID:** `Enterprise-P10`
- **Platform:** Cisco CML 2.9, TACACS+, FreeRADIUS, and IOS/IOL
- **Scope:** Centralized administration on seven devices; 802.1X feasibility pilot
- **Parent project:** [P09 — Monitoring And Visibility](../project-09-monitoring-visibility/)

## Why This Matters

Shared local administrator accounts cannot show who logged in, what role they
had, or what commands they ran. I built P10 to centralize device administration
while proving local console and login fallback before depending on TACACS+.

## Portfolio Summary

**Situation:** Network devices had no central authentication, role separation,
or accounting trail.

**Task:** Deploy TACACS+, distinguish administrators from operators, restrict a
NOC role, test accounting and failover, and evaluate RADIUS/802.1X support.

**Action:** I added TACACS and RADIUS nodes, enrolled seven devices through a
two-stage safety gate, verified privilege levels and a parser view, checked
accounting evidence, and tested unreachable-server and wrong-key behavior.

**Result:** PASS for centralized administration. Seven devices used TACACS+,
roles and local fallback were proven, and the 802.1X phase was honestly limited
by missing IOL-L2 operational commands.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 6](#phase-6--aaa-failover-breakfix) |
| Technical reviewer | [Original technical record](technical-details.md), [configs](configs/), and [verification outputs](verification-outputs/) |
| Future operator | [Decision log](decision-log.md) and [limitations and expansion](LIMITATIONS-AND-HOMELAB-EXPANSION.md) |

## My Test Boundary

| Item | Boundary |
|---|---|
| TACACS+ | Seven IOS/IOL devices |
| Console safety | Local method list before any VTY cutover |
| Roles | Administrator, operator, and NOC parser view |
| RADIUS | Server foundation only |
| 802.1X | HQ-ASW1 pilot; no completion claim without session commands |
| Faults | Unreachable TACACS and wrong shared key on HQ-RTR1 |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 1 | Safe TACACS+ Rollout | Complete |
| 2 | Privilege Separation | Complete |
| 3 | NOC Parser View | Complete |
| 4 | 802.1X Feasibility | Deferred — IOL-L2 cannot expose required session proof |
| 5 | Accounting Evidence | Complete with server-log limitation |
| 6 | AAA Failover Break/Fix | Complete |

## Phase 1 — Safe TACACS+ Rollout

I added HQ-TACACS and HQ-RADIUS to management VLAN 999 and verified their ports
before touching IOS AAA. Each device received a local console method first.
Phase A added and tested the server method list; only then did Phase B attach it
to VTY lines. This order protected access throughout the rollout.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 2 — Privilege Separation

I mapped administrator users to privilege 15 and the operator to privilege 1.
SSH tests proved the operator could view allowed state but could not enter
configuration mode, while administrators retained full access.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 3 — NOC Parser View

I created `NOC-VIEW` on HQ-RTR1 with eight operational commands. Tests proved
the view could inspect health but not show the running config, reload, or enter
global configuration.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 4 — 802.1X Feasibility

IOL-L2 accepted parts of the 802.1X configuration but rejected the operational
commands required to prove an authenticated session. I stopped before claiming
success and documented IOSvL2 or physical Catalyst as the precise retry trigger.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 5 — Accounting Evidence

I enabled command and session accounting, generated a TACACS-authenticated
session, and confirmed the server's authentication and authorization activity.
The service-node image did not expose a complete command-accounting log, so the
remaining visibility limitation is explicit in [verification outputs](verification-outputs/).

## Phase 6 — AAA Failover Break/Fix

I first pointed HQ-RTR1 to an unused TACACS address and proved local fallback
still granted the prepared local administrator. I then used a wrong shared key;
the reachable server rejected the user and local fallback did not run. Debug and
counter evidence distinguished “server unavailable” from “server rejected,” and
restoring the key returned central authentication.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## What I Proved

- A two-stage rollout avoids attaching VTY lines to an untested AAA method.
- Local console and login fallback can prevent administrative lockout.
- TACACS+ can assign different IOS privilege levels.
- Parser views can limit an operational role more precisely.
- Unreachable and rejecting TACACS servers produce different fallback behavior.
- 802.1X must remain unproven when the platform cannot show session state.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Phase configurations](configs/)
- [Verification outputs](verification-outputs/)
- [Decision log](decision-log.md)
- [Limitations and expansion guide](LIMITATIONS-AND-HOMELAB-EXPANSION.md)
- [Topology](topology/project10-cml-topology.png)
- [Persistent Claude review record](../CLAUDE-REVIEW.md)

## How We Worked Together

### My Input And How I Helped

I added and started the AAA nodes, applied each approved phase in CML, supplied
server and IOS output, tested real role logins, and performed the bounded
fallback and wrong-key exercises.

### What Codex Did And How

Codex designed the gated rollout, wrote the phase proposals and verification
plans, incorporated review items, diagnosed returned output, and documented the
platform and accounting limits. Codex also migrated this entry page.

### What Claude Did And How

Claude independently reviewed safety prerequisites, required local fallback and
service checks before `aaa new-model`, challenged phase evidence, and supplied
corrections preserved in the [review outputs](verification-outputs/).

### How We Communicated And Completed The Project

Codex proposed each bounded step, Claude reviewed it, and I applied it and
returned evidence. We stopped when a node, fallback, or verification prerequisite
was missing, repaired the prerequisite, and resumed only after review.

### Pushback And How We Resolved It

The AAA nodes initially lacked working network state, WAN-RTR1 lacked SSH keys,
and early AAA behavior risked console lockout. We fixed VLAN/IP reachability,
generated keys in the correct order, and installed the console-local safeguard
before VTY cutover. We deferred 802.1X rather than accepting configuration syntax
as proof of authentication.

## Reproduce Or Re-Verify

1. Verify the TACACS and RADIUS services and management reachability.
2. Confirm a working local user and local console method on every target.
3. Apply Phase A and test AAA before attaching Phase B to VTY lines.
4. Test admin, operator, parser view, and accounting with separate sessions.
5. Back up HQ-RTR1 before the bounded failover tests and restore central AAA.

## What Happens Next

P10 is closed. [P11](../project-11-qos-traffic-management/) adds classification,
marking, queuing, shaping, and a voice VLAN. P10 does not authorize P11, and the
802.1X retry requires a capable platform.
