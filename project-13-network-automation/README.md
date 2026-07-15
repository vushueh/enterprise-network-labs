# P13 — Network Automation

- **Status:** ✅ Complete — 2026-06-19
- **Project ID:** `Enterprise-P13`
- **Platform:** Python, Netmiko, Ansible, CML, IOS/IOL, and Wazuh
- **Scope:** Inventory-driven automation of the completed enterprise lab
- **Parent project:** [P12 — Disaster Recovery](../project-12-disaster-recovery/)

## Why This Matters

Projects P01-P12 prove I can build and recover a network by hand. P13 proves I
can turn that same network into a repeatable, auditable automation target without
hardcoding credentials or allowing a script to make broad unreviewed changes.

## Portfolio Summary

**Situation:** Ten IOS devices had accumulated configuration drift and required
device-by-device collection and backup.

**Task:** Build an inventory, collect evidence at scale, redact backups, measure
compliance, gate configuration changes, compare Ansible, and onboard direct Wazuh
syslog safely.

**Action:** I built `AUTOMATION1`, inventory and Netmiko scripts, redacted output,
a compliance checker, dry-run-first push logic, Ansible examples, and a separately
confirmed Wazuh syslog workflow. I repaired two remaining IOS access gaps by console.

**Result:** PASS with documented exceptions. The first pass collected and backed
up 8 of 10 devices, found real drift, kept the generic push dry-run only, and
later produced direct Wazuh syslog evidence for all 10 in-scope IOS devices.

## How To Read This Project

| Reader | Start here |
|---|---|
| Hiring manager or non-technical reader | [Portfolio Summary](#portfolio-summary), [What I Proved](#what-i-proved), and [Phase 5](#phase-5--compliance-findings) |
| Technical reviewer | [Original technical record](technical-details.md), [scripts](scripts/), and [final report](verification-outputs/project13-final-report.md) |
| Future operator | [Requirements](requirements.md), [decision log](decision-log.md), and [inventory](configs/inventory-devices.yml) |

## My Test Boundary

| Item | Boundary |
|---|---|
| Workstation | `AUTOMATION1` inside CML |
| Inventory | Ten in-scope IOS/IOL devices; no plaintext passwords |
| Generic push | Dry-run unless exact confirmation token and approval exist |
| Applied change | Wazuh syslog target only after receiver allow-list readiness |
| Exceptions | HQ-FW1 ASA and ISP-RTR1 remain separate workflows |
| Deferred | ASA SSH, fleet SSHv2/NTP cleanup, generic marker, and SNMP fault pilot |

## Phase Status

| Phase | Work | Status |
|---:|---|---|
| 1 | Automation Workstation | Complete |
| 2 | Inventory | Complete |
| 3 | Read-Only Collection | Complete — 8/10 on first pass |
| 4 | Redacted Backups | Complete — 8/10 on first pass |
| 5 | Compliance Findings | Complete — real drift found |
| 6 | Safe Config Dry Run | Complete — no generic config applied |
| 7 | Ansible Comparison | Complete |
| 8 | Wazuh Syslog Onboarding | Complete — 10 IOS devices proven |
| 9 | Deferred Exceptions | Deferred — separate approval required |

## Phase 1 — Automation Workstation

I built `AUTOMATION1`, installed the Python dependencies, and verified both lab
routing and controlled internet access. The [workstation evidence](verification-outputs/phase1-automation1-routing.md)
established the execution boundary before any device login was attempted.

## Phase 2 — Inventory

I created a YAML inventory with addresses, platform types, roles, and groups for
ten devices. Credentials remained in environment variables, and the committed
`.env.example` contains names only. The [inventory validation](verification-outputs/phase2-inventory-validation.md)
proved the structure before parallel collection.

## Phase 3 — Read-Only Collection

The Netmiko collector gathered interface, neighbor, routing, and version output
from 8 of 10 devices. WAN-RTR1 rejected the documented login, and HQ-FW1 refused
SSH. I preserved both failures in the [summary](verification-outputs/phase3-read-only/summary.md)
instead of deleting unreachable devices from the report.

## Phase 4 — Redacted Backups

The backup script collected running configs from the same eight reachable IOS
devices and removed known secret patterns before saving them. The
[backup summary](verification-outputs/phase4-redacted-backups/summary.md) and
committed redacted files prove both coverage and the two exceptions.

## Phase 5 — Compliance Findings

The checker evaluated SSHv2, syslog, NTP, SNMP, archive, and password-safety
standards. All eight reachable devices showed at least one gap; two failed
connection. This was a successful finding, not a failed project, because the
automation measured real drift and produced an actionable [summary](verification-outputs/phase5-compliance/summary.md).

## Phase 6 — Safe Config Dry Run

I built a harmless marker template and a script that defaults to generation
only. The [dry-run summary](verification-outputs/phase6-safe-config/summary.md)
shows `applied=False`. No generic fleet change or SNMP fault was applied merely
to demonstrate that the code could push.

## Phase 7 — Ansible Comparison

I created Ansible inventory and collect, deploy, and rollback playbooks that
mirror the Python safety model. They provide a declarative comparison while the
live evidence remains tied to the tested Netmiko workflow.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## Phase 8 — Wazuh Syslog Onboarding

After Wazuh was ready to accept the CML source ranges, I used a separately gated
script to add Wazuh as a second target while retaining the existing lab syslog.
Console repairs closed the WAN-RTR1 and CML-EDGE1 IOS gaps. The
[Wazuh summary](verification-outputs/wazuh-syslog/summary.md) and
[final update](verification-outputs/wazuh-syslog/2026-06-19-wan-cml-edge-update.md)
prove direct events from all ten in-scope IOS devices.

## Phase 9 — Deferred Exceptions

HQ-FW1 needs an ASA-specific SSH and logging workflow; ISP-RTR1 remains outside
the inside-management scope. Explicit IOS SSHv2 declarations, HQ-RTR1 NTP cleanup,
the safe marker, and the SNMP pilot also require separate approvals. They remain
future work and do not change the completed automation framework result.

The [full technical record](technical-details.md) preserves the detailed commands and evidence for this phase.

## What I Proved

- A structured inventory can drive repeatable collection across a device fleet.
- Credentials and SNMP values can remain outside committed files.
- Running configs can be collected and redacted before publication.
- Compliance automation can expose real drift and connection exceptions honestly.
- Configuration scripts can default to dry-run and require explicit apply gates.
- Python/Netmiko and Ansible can express the same guarded workflow.
- A narrowly approved automation change produced Wazuh evidence from ten IOS devices.

## Technical Evidence

- [Original detailed README](technical-details.md)
- [Requirements](requirements.md)
- [Codex-to-Claude implementation handoff](CODEX-PROJECT13-CLAUDE-HANDOFF.md)
- [Inventory and safety templates](configs/)
- [Python automation](scripts/)
- [Ansible playbooks](ansible/playbooks/)
- [Verification outputs](verification-outputs/)
- [Final report](verification-outputs/project13-final-report.md)
- [Decision log](decision-log.md)

## How We Worked Together

### My Input And How I Helped

I defined automation as the capstone, provided the CML workstation and approved
scope, kept credentials outside Git, authorized the bounded Wazuh update, and
performed console repairs where automation could not authenticate safely.

### What Codex Did And How

Codex translated the project reference into a detailed implementation handoff,
corrected inventory and syslog facts, defined the dry-run and secret-safety gates,
and specified the scripts, evidence, retry logic, and stop conditions. Codex
also migrated this README after completion.

### What Claude Did And How

Claude used the reviewed handoff to implement and structure the repository
package, checked it against earlier projects, recorded live findings and
exceptions, and maintained the final evidence boundary. Claude did not turn the
generic dry run or SNMP pilot into an unapproved live push.

### How We Communicated And Completed The Project

Codex prepared one bounded implementation handoff, Claude implemented and
reviewed the package, and I supplied approvals and console actions at the live
boundaries. Results moved through committed summaries rather than secrets or
unnecessary transcripts. The project closed with explicit exceptions.

### Pushback And How We Resolved It

WAN-RTR1 rejected automation credentials, HQ-FW1 refused SSH, and compliance
found the reachable fleet non-compliant. We did not weaken authentication or
hide the failures. I repaired IOS gaps through console, kept ASA as a separate
workflow, used a narrowly confirmed Wazuh change, and left the broad hardening
and fault pilots approval-gated.

## Reproduce Or Re-Verify

1. Build `AUTOMATION1` from [the setup guide](configs/automation1-workstation-setup.md).
2. Export credentials only into the current shell and validate the
   [inventory](configs/inventory-devices.yml).
3. Run read-only collection, redacted backup, and compliance before any dry run.
4. Inspect generated changes and require both approval and the exact confirmation
   token before an apply-capable script runs.
5. Treat ASA, ISP, and fault pilots as separate workflows with their own evidence.

## What Happens Next

P13 closes the 13-project enterprise series. The related
[Homelab_CCNA physical expansion](https://github.com/vushueh/Homelab_CCNA)
reuses these ideas on physical gear. This closeout does not authorize another
CML change or reopen any completed project.
