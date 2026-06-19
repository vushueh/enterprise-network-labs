# Project 13 — Network Automation

**Status:** Complete with live findings and approval-gated change phases
**Platform:** Cisco CML 2.9 enterprise lab
**Focus:** Python/Netmiko automation first, Ansible comparison later

## Objective

This project proves that I can automate the enterprise network built in Projects
01-12. The earlier projects show manual design, configuration, verification,
break/fix, monitoring, security, QoS, AAA, VPN, firewalling, and disaster
recovery. Project 13 turns that same network into a DevNet-style automation
portfolio piece.

The implementation intentionally starts read-only. I want automation to prove
inventory, reachability, collection, backup, reporting, and compliance before it
is allowed to push configuration.

## Current Live State

| Item | State |
|------|-------|
| Automation workstation | `AUTOMATION1` on `10.1.99.54` |
| CML edge | `CML-EDGE1` routes default traffic to Route10 over VLAN 160 |
| Internal routes on AUTOMATION1 | `10.0.0.0/16`, `10.1.0.0/16`, `10.2.0.0/16` via `10.1.99.1` |
| Default route on AUTOMATION1 | `10.1.99.254` |
| Inventory reachability | 10 in-scope devices reachable from AUTOMATION1 |
| Credential handling | Environment variables only; no passwords in inventory |

## Live Automation Results

Evidence lives under [`verification-outputs/`](verification-outputs/).

| Phase | Result | What It Proved |
|-------|--------|----------------|
| Phase 1 — Workstation | Complete | `AUTOMATION1` has internet through `CML-EDGE1`, plus deterministic internal routes. |
| Phase 2 — Inventory | Complete | 10 in-scope devices modeled with no credentials in YAML. |
| Phase 3 — Read-only collection | 8/10 successful | Netmiko collected 9 commands per reachable IOS device. |
| Phase 4 — Redacted backups | 8/10 successful | Running configs collected and redacted for reachable IOS devices. |
| Phase 5 — Compliance | 8 non-compliant, 2 failed | Automation found real drift instead of rubber-stamping the lab. |
| Phase 6 — Safe push | Dry-run complete | Generated a reversible, unused ACL marker; no live config was changed. |
| Phase 7 — Ansible | Implemented as comparison | Inventory and playbooks show the declarative alternative. |
| Phase 8 — Break/fix | Pilot documented | SNMP wrong-community test is ready but requires explicit approval. |

## Findings

Automation found three important issues:

1. `WAN-RTR1` is reachable on TCP/22 but rejects the documented credentials,
   including console login attempts. This is AAA/local-login drift from the
   Project 10 baseline.
2. `HQ-FW1` is reachable by IP but refuses TCP/22 from `AUTOMATION1`; ASA SSH
   management needs a separate platform-specific fix.
3. The 8 reachable IOS devices are missing explicit `ip ssh version 2` in
   running config. `HQ-RTR1` also lacks the expected NTP line. The lab works,
   but compliance correctly flags missing hardening intent.

## In-Scope Devices

| Device | IP | Platform | Role |
|--------|----|----------|------|
| `HQ-RTR1` | `10.0.255.1` | IOS | Core/HQ router |
| `BR-RTR1` | `10.0.255.2` | IOS | Branch router |
| `WAN-RTR1` | `10.0.255.3` | IOS | WAN router |
| `HQ-DSW1` | `10.1.99.11` | IOS | HQ distribution switch |
| `HQ-DSW2` | `10.1.99.12` | IOS | HQ distribution switch |
| `HQ-ASW1` | `10.1.99.13` | IOS | HQ access switch |
| `HQ-ASW2` | `10.1.99.14` | IOS | HQ access switch |
| `BR-DSW1` | `10.2.99.2` | IOS | Branch distribution switch |
| `BR-ASW1` | `10.2.99.3` | IOS | Branch access switch |
| `HQ-FW1` | `10.0.0.14` | ASA | Firewall |

## Phase Plan

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Automation workstation setup | Complete |
| 2 | Structured inventory | Complete |
| 3 | Read-only Netmiko collection | Complete with findings |
| 4 | Config backup and redaction | Complete with findings |
| 5 | Compliance checker | Complete with findings |
| 6 | Gated safe config push | Dry-run complete; live apply approval-gated |
| 7 | Ansible comparison | Complete |
| 8 | Controlled break/fix | Designed; live injection approval-gated |

## How To Run

From `AUTOMATION1`:

```bash
cd ~/netauto
source .venv/bin/activate
export NETLAB_USERNAME='<username>'
export NETLAB_PASSWORD='<password>'
export NETLAB_SECRET='<enable-secret>'
export NETLAB_SNMP_RO_COMMUNITY='<standard-snmp-community>'
python scripts/collect_baseline.py --inventory inventory/devices.yml
```

For inventory-only validation:

```bash
python scripts/collect_baseline.py --inventory inventory/devices.yml --check-inventory-only
```

For redacted backups:

```bash
python scripts/backup_configs.py \
  --inventory inventory/devices.yml \
  --output-dir outputs/phase4-redacted-backups
```

For compliance:

```bash
python scripts/compliance_check.py \
  --inventory inventory/devices.yml \
  --output-dir outputs/phase5-compliance
```

For a dry-run safe config push:

```bash
python scripts/push_safe_config.py \
  --inventory inventory/devices.yml \
  --output-dir outputs/phase6-safe-config
```

To apply the safe marker after approval:

```bash
python scripts/push_safe_config.py \
  --inventory inventory/devices.yml \
  --output-dir outputs/phase6-safe-config \
  --apply \
  --confirm APPLY_SAFE_CONFIG
```

Outputs are written under:

```text
outputs/
```

The same script is stored in this repo under:

```text
project-13-network-automation/scripts/collect_baseline.py
```

## Ansible Comparison

Ansible files are included under:

```text
configs/ansible.cfg
configs/ansible-inventory.yml
ansible/playbooks/
```

Netmiko remains the primary implementation because it demonstrates Python
control flow, exception handling, redaction, report writing, and safe gates.
Ansible is the comparison path for declarative collection and deployment.

## Next Approved Changes

These are intentionally not applied automatically:

- recover `WAN-RTR1` AAA/local login from console and rerun Phase 3-5;
- enable/fix `HQ-FW1` ASA SSH management from the inside path;
- explicitly configure `ip ssh version 2` on the IOS fleet;
- add the missing NTP line on `HQ-RTR1`;
- apply and roll back the safe marker ACL on one pilot device;
- run the SNMP break/fix pilot on one access switch.

## Safety Rules

- Do read-only collection before any config push.
- Do not store credentials in git.
- Do not let one failed device stop the whole run.
- Redact sensitive-looking command output before saving it.
- Treat config push and break/fix as separate approval-gated phases.
