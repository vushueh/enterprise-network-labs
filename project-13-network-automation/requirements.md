# Project 13 Requirements

Project 13 is the Network Automation capstone for the enterprise CML lab.

## Required Outcomes

1. Build or verify an automation workstation named `AUTOMATION1`.
2. Create a structured inventory for the in-scope network devices.
3. Use Python and Netmiko to run read-only show commands across the fleet.
4. Save per-device output and a summary report.
5. Add configuration backup and redaction.
6. Add compliance checks for SSH, syslog, NTP, secrets, SNMP, archive, and hostname.
7. Add a gated safe configuration push that is reversible.
8. Add an Ansible comparison for the same workflow.
9. Add a controlled break/fix that proves automation can detect and correct drift.

## Security Requirements

- No plaintext passwords in inventory, scripts, reports, or committed outputs.
- Credentials must come from environment variables or secure prompts.
- Raw config backups stay out of git.
- Redacted outputs must be safe to commit.
- Config push must default to dry-run.

## Read-Only Phase Requirements

The first live automation phase must collect at least:

- `show cdp neighbors`
- `show ip interface brief`
- `show version`

Additional useful commands can be collected if outputs are redacted before
saving.

## Completion Gates

Project 13 is complete when the repo contains:

- a safe inventory with no credentials;
- read-only collection script and evidence;
- redacted config backup script and evidence;
- compliance checker and evidence;
- dry-run-first safe config push script;
- Ansible comparison files;
- documented break/fix pilot;
- final README, decision log, and troubleshooting notes.

Live config changes beyond the unused marker ACL require a separate approval.
