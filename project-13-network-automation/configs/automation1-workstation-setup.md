# AUTOMATION1 Workstation Setup

## Live Network State

```text
Hostname: AUTOMATION1
Interface: ens2
Address: 10.1.99.54/24
Default route: 10.1.99.254
Internal CML routes:
  10.0.0.0/16 via 10.1.99.1
  10.1.0.0/16 via 10.1.99.1
  10.2.0.0/16 via 10.1.99.1
```

## Python Environment

```bash
cd ~/netauto
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install netmiko paramiko pyyaml rich
```

## Route Persistence

Netplan file on AUTOMATION1:

```text
/etc/netplan/99-automation1-mgmt.yaml
```

Expected routes:

```text
default via 10.1.99.254 dev ens2
10.0.0.0/16 via 10.1.99.1 dev ens2
10.1.0.0/16 via 10.1.99.1 dev ens2
10.2.0.0/16 via 10.1.99.1 dev ens2
```
