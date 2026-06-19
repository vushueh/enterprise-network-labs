# Project 13 - Network Automation

## Goal

I built Projects 1-12 by hand. Project 13 proves I can now use automation to
manage that same network.

The goal is not to create a new network. The goal is to show that I can:

- keep a clean device inventory;
- log into routers and switches automatically;
- collect show commands from many devices at once;
- back up running configs safely;
- check if devices follow my standards;
- prepare safe config changes without blindly pushing them.

The first automation pass was read-only/dry-run. After Wazuh was prepared to
accept the CML source ranges, I used the same gated automation pattern to apply
the Wazuh syslog target to the reachable IOS devices.

## What This Project Built

| Area | What It Means |
|------|---------------|
| Automation workstation | `AUTOMATION1` is the Linux node inside CML that runs Python/Netmiko. |
| Inventory | A YAML file lists the devices, IPs, platforms, and roles. No passwords are stored in it. |
| Read-only collection | Python logs into devices and collects show-command evidence. |
| Redacted backups | Python collects running configs and hides secrets before saving them. |
| Compliance check | Python checks the network against standards like SSHv2, syslog, NTP, SNMP, and archive. |
| Safe config push | Python generates a harmless dry-run config marker. It does not apply unless approved. |
| Wazuh syslog push | Python can add Wazuh as a second syslog target after the Wazuh receiver allow-list is ready. |
| Ansible comparison | Ansible files show how the same idea would look in a declarative tool. |

## Important Files

| File Or Folder | Purpose |
|----------------|---------|
| [configs/inventory-devices.yml](configs/inventory-devices.yml) | Source-of-truth inventory for the lab devices. |
| [scripts/](scripts/) | Python automation scripts. |
| [ansible/playbooks/](ansible/playbooks/) | Ansible comparison playbooks. |
| [verification-outputs/](verification-outputs/) | Proof from the live lab runs. |
| [decision-log.md](decision-log.md) | Why I made the main design choices. |
| [requirements.md](requirements.md) | What Project 13 needed to prove. |

## If You Want The Details

The README stays simple on purpose. These links point to the deeper technical
details for someone who wants to inspect the code or proof.

| Question | Link |
|----------|------|
| What Python code did I write? | [scripts/](scripts/) |
| What does each script do? | [Automation Scripts](#automation-scripts) |
| What devices are automated? | [configs/inventory-devices.yml](configs/inventory-devices.yml) |
| How are credentials kept out of Git? | [configs/.env.example](configs/.env.example) |
| What did the live lab prove? | [verification-outputs/](verification-outputs/) |
| What did the compliance check find? | [Phase 5 compliance summary](verification-outputs/phase5-compliance/summary.md) |
| What configs were backed up safely? | [Phase 4 redacted backups](verification-outputs/phase4-redacted-backups/) |
| What is the safe config push? | [configs/safe-standard-config-template.md](configs/safe-standard-config-template.md) |
| What would the break/fix look like? | [configs/snmp-breakfix-pilot.md](configs/snmp-breakfix-pilot.md) |
| How would Ansible do this? | [ansible/playbooks/](ansible/playbooks/) |
| Why did I make these choices? | [decision-log.md](decision-log.md) |

## Automation Scripts

| Script | What It Does | Live Outcome |
|--------|--------------|--------------|
| [collect_baseline.py](scripts/collect_baseline.py) | Logs into devices and runs read-only commands like `show cdp neighbors`, `show ip interface brief`, and `show version`. | Worked on 8 of 10 devices. |
| [backup_configs.py](scripts/backup_configs.py) | Collects running configs and redacts secrets before saving them. | Worked on 8 of 10 devices. |
| [compliance_check.py](scripts/compliance_check.py) | Checks whether devices follow standards for SSHv2, syslog, NTP, SNMP, archive, and password safety. | Found real configuration drift. |
| [push_safe_config.py](scripts/push_safe_config.py) | Creates a safe dry-run config push using an unused ACL marker. | Dry-run only. No live config changed. |
| [push_wazuh_syslog.py](scripts/push_wazuh_syslog.py) | Adds Wazuh `192.168.10.156` as a syslog target on IOS devices while keeping the existing lab syslog server. | Dry-run ready. Apply only after Wazuh allows the CML source subnets. |
| [render_report.py](scripts/render_report.py) | Builds a short final report from the automation results. | Created the final Project 13 report. |

## Live Results

| Phase | Evidence | Result |
|-------|----------|--------|
| Phase 1 - Workstation routing | [phase1-automation1-routing.md](verification-outputs/phase1-automation1-routing.md) | `AUTOMATION1` has the correct internal and internet routing. |
| Phase 2 - Inventory validation | [phase2-inventory-validation.md](verification-outputs/phase2-inventory-validation.md) | 10 devices are listed in the inventory. |
| Phase 3 - Read-only collection | [summary.md](verification-outputs/phase3-read-only/summary.md) | 8 of 10 devices succeeded. |
| Phase 4 - Redacted backups | [summary.md](verification-outputs/phase4-redacted-backups/summary.md) | 8 of 10 devices succeeded. |
| Phase 5 - Compliance check | [summary.md](verification-outputs/phase5-compliance/summary.md) | 8 devices are reachable but non-compliant; 2 devices failed. |
| Phase 6 - Safe config dry-run | [summary.md](verification-outputs/phase6-safe-config/summary.md) | Safe config was generated only. Nothing was applied. |
| Wazuh syslog onboarding | [summary.md](verification-outputs/wazuh-syslog/summary.md) | 8 IOS devices now send syslog to Wazuh. |
| Final report | [project13-final-report.md](verification-outputs/project13-final-report.md) | Final automation summary. |

## What The Automation Found

The automation worked, and it also found problems that need fixing.

1. `WAN-RTR1` is reachable on SSH, but login fails.
   - Meaning: the device is online, but AAA/local credentials do not match the documented baseline.

2. `HQ-FW1` is reachable by ping, but SSH port 22 is refused.
   - Meaning: the ASA firewall needs a separate SSH management fix.

3. The 8 reachable IOS devices are missing explicit `ip ssh version 2`.
   - Meaning: SSH works, but the config does not clearly show the hardening standard.

4. `HQ-RTR1` is missing the expected NTP line.
   - Meaning: time configuration needs cleanup on that router.

## Why This Matters

This project shows that I can use automation like a network engineer:

- I did not hardcode device logins into scripts.
- I did not store passwords in Git.
- I did not push changes before collecting evidence.
- I let automation report failures honestly.
- I separated read-only checks from live config changes.

That is the real DevNet lesson: automation should make network operations safer,
more repeatable, and easier to audit.

## What Needs Approval Before Changing Devices

The next steps would change live configs, so they need approval first:

1. Fix `WAN-RTR1` AAA/local login.
2. Fix `HQ-FW1` ASA SSH management.
3. Add explicit `ip ssh version 2` to IOS devices.
4. Add the missing NTP config on `HQ-RTR1`.
5. Apply the safe marker config to one pilot device.
6. Run the SNMP break/fix pilot on one access switch.
7. Build a dedicated CML-node Cisco dashboard filter after more lab-node logs accumulate.

## How To Run The Scripts

Run from `AUTOMATION1`:

```bash
cd ~/netauto
source .venv/bin/activate

export NETLAB_USERNAME='<username>'
export NETLAB_PASSWORD='<password>'
export NETLAB_SECRET='<enable-secret>'
export NETLAB_SNMP_RO_COMMUNITY='<standard-snmp-community>'
```

Validate the inventory:

```bash
python scripts/collect_baseline.py --inventory inventory/devices.yml --check-inventory-only
```

Collect read-only evidence:

```bash
python scripts/collect_baseline.py \
  --inventory inventory/devices.yml \
  --output-dir outputs/phase3-read-only
```

Back up redacted configs:

```bash
python scripts/backup_configs.py \
  --inventory inventory/devices.yml \
  --output-dir outputs/phase4-redacted-backups
```

Run compliance:

```bash
python scripts/compliance_check.py \
  --inventory inventory/devices.yml \
  --output-dir outputs/phase5-compliance
```

Generate the safe config dry-run:

```bash
python scripts/push_safe_config.py \
  --inventory inventory/devices.yml \
  --output-dir outputs/phase6-safe-config
```

Generate the Wazuh syslog dry-run:

```bash
python scripts/push_wazuh_syslog.py \
  --inventory inventory/devices.yml \
  --output-dir outputs/wazuh-syslog-dry-run
```

Apply the Wazuh syslog config only after Wazuh allows the CML source ranges:

```bash
python scripts/push_wazuh_syslog.py \
  --inventory inventory/devices.yml \
  --output-dir outputs/wazuh-syslog-apply \
  --apply \
  --confirm APPLY_WAZUH_SYSLOG
```

## Simple Summary

Project 13 proves I can automate my enterprise CML network with Python and
Netmiko, compare that approach with Ansible, collect evidence from the live lab,
find real configuration drift, and avoid unsafe config pushes.
