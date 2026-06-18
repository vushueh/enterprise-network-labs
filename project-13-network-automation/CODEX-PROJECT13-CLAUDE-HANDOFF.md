# Project 13 — Claude Implementation Handoff

**Repo:** `vushueh/enterprise-network-labs`
**Local path:** `/home/leonel/code/enterprise-network-labs`
**Project:** `project-13-network-automation`
**Prepared by:** Codex
**Purpose:** Give Claude the exact Project 13 strategy, phase design, proposed files, configs, verification targets, and safety gates.

---

## Source Of Truth

Claude must use this repo-local reference first:

```text
references/projects-02-13.md
```

Project 13 begins at:

```text
# Project 13 — Network Automation (Bonus — Standalone Portfolio Piece)
```

That reference says Project 13 is **not another routing/switching build**. It is a DevNet/network automation portfolio piece that proves Leonel can automate the enterprise network built in Projects 01-12.

Do **not** use the Secure Network Management Labs/SNML Project 13 Cuckoo material for this repo.

---

## Project Intent

The first 12 projects prove Leonel can design, build, verify, break, and fix enterprise networking by hand. Project 13 proves he can automate that network.

The final story should be:

> Managing 20+ devices manually is slow and inconsistent. Project 13 adds an automation workstation, a structured inventory, Netmiko read-only collection, config backup/redaction, compliance checks, controlled configuration deployment, rollback, Ansible comparison, and a deliberate automation break/fix.

The project should stand as a DevNet-style portfolio piece beside the CCNA/network portfolio.

---

## Critical Corrections And Safety Gates

1. **Verify the actual live CML node count before writing "20 devices" everywhere.**
   The reference says 21 nodes total after adding `AUTOMATION1`, but the current repo documentation clearly identifies 9 IOS/IOL devices plus `HQ-FW1` and support nodes. Use live CML evidence when writing final docs.

2. **Syslog IP correction:**
   Project 09 uses `10.1.99.51` for the syslog/SNMP/NetFlow collector. Project 12 has at least one reference saying `Syslog (10.1.99.11)`, but `10.1.99.11` is `HQ-DSW1`. Treat `10.1.99.51` as the collector unless live CML proves otherwise. Document and fix the inconsistency if confirmed.

3. **No plaintext passwords in git.**
   All scripts must read credentials from environment variables or prompt securely. Use `.env.example`, never `.env`.

4. **Read-only first.**
   Build inventory, connectivity, show-command collection, and compliance checks before any config push.

5. **Configuration push must be gated and reversible.**
   The reference calls for pushing standard config such as SSH hardening, SNMP, syslog, NTP, interface descriptions, and banner. For the first implementation, use a safe marker/banner deployment plus a proposed standard-config generator. Do not blindly modify routing, AAA, VPN, QoS, NAT, firewall rules, trunks, or production-facing ACLs.

6. **Break/fix must be controlled.**
   The reference says deliberately push a wrong SNMP community to one device. Implement this only as a reviewed, reversible pilot on one low-risk device after the compliance checker and rollback are ready. If live SNMP monitoring is fragile, document the break/fix with generated configs and a simulated/non-applied compliance mismatch.

---

## Required Project Structure

Create or complete:

```text
project-13-network-automation/
├── README.md
├── requirements.md
├── decision-log.md
├── configs/
│   ├── inventory-devices.yml
│   ├── ansible.cfg
│   ├── ansible-inventory.yml
│   ├── group-vars-example.yml
│   ├── automation1-workstation-setup.md
│   ├── safe-standard-config-template.md
│   └── snmp-breakfix-pilot.md
├── scripts/
│   ├── collect_baseline.py
│   ├── backup_configs.py
│   ├── compliance_check.py
│   ├── push_safe_config.py
│   └── render_report.py
├── ansible/
│   └── playbooks/
│       ├── collect-show-commands.yml
│       ├── deploy-safe-standard.yml
│       └── rollback-safe-standard.yml
├── verification-outputs/
└── screenshots/
```

Update root files at the end:

```text
README.md
CODEX-LOG.md
TROUBLESHOOTING-LOG.md
```

Do not edit `CLAUDE-REVIEW.md` unless Claude intentionally owns that edit. If it contains stale open items with resolutions already embedded, Claude can archive them in its own voice.

---

## Proposed Inventory Baseline

Use this as the starting inventory, then correct it from live CML evidence.

```yaml
devices:
  ios:
    - name: HQ-RTR1
      host: 10.0.255.1
      role: core_router
      platform: cisco_ios
      source_interface: Loopback0
    - name: BR-RTR1
      host: 10.0.255.2
      role: branch_router
      platform: cisco_ios
      source_interface: Loopback0
    - name: WAN-RTR1
      host: 10.0.255.3
      role: wan_router
      platform: cisco_ios
      source_interface: Loopback0
    - name: HQ-DSW1
      host: 10.1.99.11
      role: distribution_switch
      platform: cisco_ios
      source_interface: Vlan999
    - name: HQ-DSW2
      host: 10.1.99.12
      role: distribution_switch
      platform: cisco_ios
      source_interface: Vlan999
    - name: HQ-ASW1
      host: 10.1.99.13
      role: access_switch
      platform: cisco_ios
      source_interface: Vlan999
    - name: HQ-ASW2
      host: 10.1.99.14
      role: access_switch
      platform: cisco_ios
      source_interface: Vlan999
    - name: BR-DSW1
      host: 10.2.99.2
      role: branch_distribution_switch
      platform: cisco_ios
      source_interface: Vlan999
    - name: BR-ASW1
      host: 10.2.99.3
      role: branch_access_switch
      platform: cisco_ios
      source_interface: Vlan999
  asa:
    - name: HQ-FW1
      host: 10.0.0.14
      role: firewall
      platform: cisco_asa
      source_interface: inside
support_nodes:
  automation: AUTOMATION1
  dhcp_dns: 10.1.99.50
  syslog: 10.1.99.51
  tacacs: 10.1.99.52
  radius: 10.1.99.53
```

Credentials must not live in this YAML. Use:

```bash
export NETLAB_USERNAME='<username>'
export NETLAB_PASSWORD='<password>'
export NETLAB_SECRET='<enable_secret>'
```

---

## Phase 1 — Automation Workstation Setup

**Reference phase:** Automation workstation setup.

### CML topology change

Add one node:

| Node | Image | Hostname | Role |
|---|---|---|---|
| Alpine or Ubuntu | Linux | `AUTOMATION1` | Automation workstation with Python/Netmiko |

Connect:

| Side A | Side B | Purpose |
|---|---|---|
| `HQ-ASW1 Ethernet1/2` or `Ethernet1/3` | `AUTOMATION1 eth0` | Management VLAN 999 access |

If `Ethernet1/2` is already used, use `Ethernet1/3`. Verify from CML canvas before applying.

### Proposed switchport config

Apply on `HQ-ASW1` only after verifying the chosen port is unused.

```ios
configure terminal
interface Ethernet1/2
 description ACCESS-AUTOMATION1-VLAN999
 switchport mode access
 switchport access vlan 999
 spanning-tree portfast
 no shutdown
end
write memory
```

If using `Ethernet1/3`, replace the interface.

### AUTOMATION1 Linux setup

Prefer Ubuntu if available because Ansible and Python package support are easier. Alpine is acceptable but may need more package names.

Ubuntu:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git openssh-client sshpass
python3 -m venv ~/p13-venv
source ~/p13-venv/bin/activate
pip install --upgrade pip
pip install netmiko paramiko pyyaml rich jinja2 ansible
```

Alpine:

```bash
sudo apk update
sudo apk add python3 py3-pip py3-virtualenv git openssh-client sshpass gcc musl-dev libffi-dev openssl-dev
python3 -m venv ~/p13-venv
source ~/p13-venv/bin/activate
pip install --upgrade pip
pip install netmiko paramiko pyyaml rich jinja2 ansible
```

### Verification

From `AUTOMATION1`:

```bash
ip addr
ip route
ping -c 5 10.1.99.1
ping -c 5 10.0.255.1
python3 --version
pip --version
python -c "import netmiko, yaml, rich; print('P13 Python imports OK')"
```

Save output:

```text
verification-outputs/phase1-automation1-setup.md
```

---

## Phase 2 — Inventory File

**Reference phase:** Inventory file.

Create:

```text
configs/inventory-devices.yml
```

It is the source of truth for:

- hostname
- management IP
- platform
- role
- command set
- source interface
- in-scope for Netmiko
- in-scope for Ansible

Add an inventory validation command to `scripts/collect_baseline.py` or a helper function:

- duplicate host detection
- required keys present
- platform is one of `cisco_ios`, `cisco_asa`, `linux`
- no password-looking keys are present in inventory

Verification:

```bash
python scripts/collect_baseline.py --inventory configs/inventory-devices.yml --check-inventory-only
```

Save:

```text
verification-outputs/phase2-inventory-validation.md
```

---

## Phase 3 — Read-Only Netmiko Automation

**Reference phase:** Read-only automation.

Create:

```text
scripts/collect_baseline.py
```

Minimum required show commands from the reference:

```text
show cdp neighbors
show ip interface brief
show version
```

Add useful portfolio commands:

IOS:

```text
show clock
show ip ospf neighbor
show logging
show ntp associations
show lldp neighbors
show running-config | include hostname|aaa|tacacs|logging host|snmp-server|ntp|archive|ip ssh
```

ASA:

```text
show version
show interface ip brief
show route
show nameif
show logging
show running-config logging
```

Output layout:

```text
verification-outputs/phase3-read-only/
├── HQ-RTR1.txt
├── BR-RTR1.txt
├── WAN-RTR1.txt
├── ...
└── summary.md
```

Script behavior:

- one failed device must not stop the run
- failed devices are recorded in `summary.md`
- platform mismatch is reported clearly
- connection timeout is short enough for lab use, e.g. 15-30 seconds

---

## Phase 4 — Configuration Backup And Redaction

Create:

```text
scripts/backup_configs.py
```

Collect running configs:

- IOS: `show running-config`
- ASA: `show running-config`

Raw backups go only to:

```text
verification-outputs/private-raw-backups/
```

Redacted backups go to:

```text
verification-outputs/phase4-redacted-backups/
```

Update `.gitignore`:

```text
.env
*.vault
project-13-network-automation/verification-outputs/private-raw-backups/
```

Redact lines matching, case-insensitive:

```text
username
secret
password
key
tacacs
radius-server key
snmp-server community
snmp-server user
tunnel-group
pre-shared-key
crypto isakmp key
```

Verification:

```bash
python scripts/backup_configs.py
rg -i "password|secret|snmp-server community|pre-shared-key|tacacs|radius-server key" verification-outputs/phase4-redacted-backups
```

The grep should show either no secrets or only safe `[REDACTED]` lines.

---

## Phase 5 — Compliance Check

**Reference phase:** Compliance check.

Create:

```text
scripts/compliance_check.py
```

Check:

- SSHv2 enabled
- syslog points to `10.1.99.51`
- NTP server/peer is `10.0.255.1` on non-HQ-RTR1 devices
- no plaintext passwords or type 0 passwords
- SNMP community/user matches the intended standard
- archive configured where supported
- hostname matches inventory

Recommended report outputs:

```text
verification-outputs/phase5-compliance-report.md
verification-outputs/phase5-compliance-report.json
```

Suggested compliance rows:

| Device | SSHv2 | Syslog | NTP | Secrets | SNMP | Archive | Result |
|---|---|---|---|---|---|---|---|

Important: if a platform cannot support a check, mark it `LIMITED`, not `FAIL`.

---

## Phase 6 — Configuration Push

**Reference phase:** Configuration push.

The reference calls for pushing standard configs:

- SSH hardening
- SNMP communities
- syslog destination
- NTP server
- interface descriptions
- banner

Implement this in two layers:

### Layer A — Safe marker deployment

This proves controlled automated config push without changing forwarding behavior.

IOS safe config:

```ios
ip access-list standard P13-AUTOMATION-MARKER
 remark Managed by Project 13 automation - safe marker only
```

Do not apply the ACL to any interface.

ASA safe config:

```asa
banner motd Project 13 automation validation - safe banner marker
```

If ASA banner syntax differs on the image, document limitation and skip ASA deployment.

Create:

```text
scripts/push_safe_config.py
```

Support modes:

```bash
python scripts/push_safe_config.py --dry-run
python scripts/push_safe_config.py --apply --device HQ-ASW1
python scripts/push_safe_config.py --apply --all-ios
python scripts/push_safe_config.py --rollback --device HQ-ASW1
```

Safety requirements:

- default mode is dry-run
- apply requires explicit `--apply`
- never pushes to all devices unless `--all-ios` is supplied
- writes proposed commands to a file before sending them
- rollback commands are generated before apply

### Layer B — Standard config proposal

Generate standard config blocks but do not blindly apply them:

```text
configs/safe-standard-config-template.md
verification-outputs/phase6-standard-config-proposals/
```

Standard intended values:

```text
ip ssh version 2
logging host 10.1.99.51
ntp server 10.0.255.1 key 9
snmp-server community <REDACTED> RO ACL-SNMP-MANAGERS
```

Claude must compare against Projects 09-12 before approving any production-impacting push.

---

## Phase 7 — Ansible Alternative

**Reference phase:** Ansible alternative.

Create:

```text
configs/ansible.cfg
configs/ansible-inventory.yml
configs/group-vars-example.yml
ansible/playbooks/collect-show-commands.yml
ansible/playbooks/deploy-safe-standard.yml
ansible/playbooks/rollback-safe-standard.yml
```

Ansible should use:

```yaml
ansible_connection: network_cli
ansible_network_os: cisco.ios.ios
```

For ASA:

- use `cisco.asa.asa` only if the collection is installed and working
- otherwise document `HQ-FW1` as Netmiko-only for Project 13

Comparison to document:

| Area | Netmiko | Ansible |
|---|---|---|
| Best for | procedural show collection, custom parsing | idempotent config tasks |
| Strength | Python control and rich reports | inventory and repeatable playbooks |
| Weakness | must write error handling yourself | platform collections/syntax can be heavy |
| Project use | collection, backup, compliance | read-only collection, safe marker push |

---

## Phase 8 — Break/Fix Challenge

**Reference fault:** wrong SNMP community pushed to one device.

Use a low-risk pilot device, preferably `HQ-ASW1` or another non-core IOS switch. Do not use `HQ-RTR1` for the first break/fix unless Leonel explicitly approves.

### Fault

Change intended SNMP standard in inventory/template for one pilot device:

```text
expected_snmp_community: WRONG-P13-COMMUNITY
```

Either:

1. Apply to the pilot device after Claude approval, then prove compliance fails; or
2. If live SNMP is too fragile, document it as a generated config mismatch and do not apply.

### Expected symptom

- compliance checker flags SNMP mismatch
- SNMP monitoring for that device would fail or use wrong community

### Diagnosis path

```bash
python scripts/compliance_check.py --device HQ-ASW1
```

Compare:

```text
configs/inventory-devices.yml
show running-config | include snmp-server community
```

### Fix

- correct inventory/template
- re-run safe push or manually restore approved SNMP config
- re-run compliance check

Save:

```text
verification-outputs/breakfix-wrong-snmp-community.md
```

---

## Phase 9 — Final Documentation

Final `README.md` must include:

- Project statement: DevNet portfolio piece, not a routing project
- STAR summary from `references/projects-02-13.md`
- Topology: 21 nodes if live CML confirms; otherwise exact verified count
- `AUTOMATION1` connection
- phase summaries
- commands to run
- table of scripts and purpose
- Netmiko vs Ansible comparison
- break/fix result
- limitations
- next steps

Root `README.md`:

- mark Project 13 complete
- keep the "13-project progressive series" framing
- link to `project-13-network-automation/`

`CODEX-LOG.md`:

- add a Project 13 completion/handoff entry

`TROUBLESHOOTING-LOG.md`:

- add Project 13 break/fix entry

---

## Commands Claude Should Use During Implementation

From repo root:

```bash
python3 -m venv .venv-p13
source .venv-p13/bin/activate
pip install -r project-13-network-automation/requirements.md
```

If using a normal requirements file instead, create:

```text
project-13-network-automation/requirements.txt
```

with:

```text
netmiko
paramiko
pyyaml
rich
jinja2
ansible
```

Run examples:

```bash
export NETLAB_USERNAME='<username>'
export NETLAB_PASSWORD='<password>'
export NETLAB_SECRET='<enable_secret>'

cd project-13-network-automation
python scripts/collect_baseline.py --inventory configs/inventory-devices.yml
python scripts/backup_configs.py --inventory configs/inventory-devices.yml
python scripts/compliance_check.py --inventory configs/inventory-devices.yml
python scripts/push_safe_config.py --dry-run
ansible-playbook -i configs/ansible-inventory.yml ansible/playbooks/collect-show-commands.yml
```

---

## Completion Criteria

Project 13 is complete only when:

- `AUTOMATION1` exists in CML and reaches management VLAN 999.
- inventory file exists and validates.
- read-only Netmiko collection produces per-device output.
- config backup script produces redacted backups.
- compliance checker produces pass/fail report.
- safe config push and rollback are proven on at least one IOS device.
- Ansible read-only collection works, or limitations are documented honestly.
- Netmiko vs Ansible comparison is written.
- wrong-SNMP break/fix is documented.
- root README marks Project 13 complete.
- `CODEX-LOG.md` and `TROUBLESHOOTING-LOG.md` are updated.
- no secrets are committed.

---

## Claude Start Prompt

Leonel can paste this to Claude:

```text
Pull latest enterprise-network-labs.
Read references/projects-02-13.md and project-13-network-automation/CODEX-PROJECT13-CLAUDE-HANDOFF.md.
Use the Project 13 section of projects-02-13.md as source of truth.
Complete Project 13 Network Automation following the handoff, with read-only automation first, gated config push, no plaintext secrets, and full portfolio documentation.
```
