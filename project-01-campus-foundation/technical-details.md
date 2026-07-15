# Project 01 — Campus Foundation

## Problem Statement

Building a single-site campus network from scratch. Multiple departments need network
segmentation, a dedicated management network for device access, and inter-VLAN routing
so departments can communicate through controlled paths.

## STAR Summary

**Situation:** I was studying VLANs, trunking, and inter-VLAN routing as separate topics
and realized I had never designed a complete campus network from a blank canvas.

**Task:** Design and build a fully segmented campus network from a written requirement —
choosing the VLAN scheme, IP addressing, trunk design, STP priorities, and SSH hardening.

**Action:** Built a multi-VLAN campus (VLANs 100/200/300/999) with proper trunk pruning,
router-on-a-stick inter-VLAN routing, deliberate STP root election with backup roots,
and SSH-only management access restricted to a dedicated management VLAN.

**Result:** Can design a multi-VLAN campus network from scratch, explain every design
decision, and verify that VLANs, trunking, STP, inter-VLAN routing, and SSH are all
working correctly together.

---

## Topology

### CML Lab Topology
![CML Topology](diagrams/cml-topology.png)

### Physical (draw.io)
![Physical Topology](diagrams/physical-topology.png)

### Logical (draw.io)
![Logical Topology](diagrams/logical-topology.png)

---

## Technologies Used

- VLANs (100, 200, 300, 999, 1000)
- 802.1Q Trunking with VLAN pruning
- Native VLAN hardening (VLAN 1000)
- Router-on-a-Stick inter-VLAN routing
- Rapid-PVST+ with deliberate root bridge election
- PortFast + BPDU Guard on access ports
- SSH v2 with VTY ACL restricted to management VLAN
- CDP neighbor verification
- Interface descriptions on all links

---

## IP Addressing

| Device | Interface | IP | Purpose |
|--------|-----------|-----|---------|
| HQ-RTR1 | E0/0.100 | 10.1.100.1/24 | Engineering gateway |
| HQ-RTR1 | E0/0.200 | 10.1.200.1/24 | Sales gateway |
| HQ-RTR1 | E0/0.300 | 10.1.44.1/24 | Guest gateway |
| HQ-RTR1 | E0/0.999 | 10.1.99.1/24 | Management gateway |
| HQ-RTR1 | Loopback0 | 10.0.255.1/32 | Router ID |
| HQ-DSW1 | Vlan999 | 10.1.99.11/24 | Management |
| HQ-DSW2 | Vlan999 | 10.1.99.12/24 | Management |
| HQ-ASW1 | Vlan999 | 10.1.99.13/24 | Management |
| HQ-ASW2 | Vlan999 | 10.1.99.14/24 | Management |
| PC-ENG1 | eth0 | 10.1.100.10/24 | Engineering endpoint |
| PC-SALES1 | eth0 | 10.1.200.10/24 | Sales endpoint |
| PC-MGMT1 | eth0 | 10.1.99.100/24 | Management endpoint |

---

## Key Verification

| Check | Command | Expected Result |
|-------|---------|-----------------|
| VLANs exist | `show vlan brief` | VLANs 100,200,300,999,1000 active |
| Trunks up | `show interfaces trunk` | All uplinks trunking, native 1000 |
| Inter-VLAN routing | `ping 10.1.200.10` from PC-ENG1 | Success |
| STP root correct | `show spanning-tree root` | DSW1=root VLAN100/999, DSW2=root VLAN200/300 |
| SSH restricted | `ssh` from PC-ENG1 | Denied (wrong VLAN) |
| SSH working | `ssh` from PC-MGMT1 | Success |

---

## Screenshots

### Phase 1 — VLAN Configuration

**show vlan brief — HQ-ASW1**
![show vlan brief ASW1](verification/screenshots/p01-ph1-show-vlan-brief-ASW1.png)

**show vlan brief — HQ-ASW2**
![show vlan brief ASW2](verification/screenshots/p01-ph1-show-vlan-brief-ASW2.png)

---

### Phase 2 — Trunking

**show cdp neighbors — HQ-DSW1**
![show cdp neighbors DSW1](verification/screenshots/p01-ph2-show-cdp-neighbors-DSW1.png)

**show interfaces trunk — HQ-DSW1**
![show interfaces trunk DSW1](verification/screenshots/p01-ph2-show-interfaces-trunk-DSW1.png)

**show interfaces trunk — HQ-DSW2**
![show interfaces trunk DSW2](verification/screenshots/p01-ph2-show-interfaces-trunk-DSW2.png)

---

### Phase 3 — Inter-VLAN Routing

**show ip interface brief — HQ-RTR1**
![show ip interface brief RTR1](verification/screenshots/p01-ph3-show-ip-interface-brief-RTR1.png)

**show ip route — HQ-RTR1**
![show ip route RTR1](verification/screenshots/p01-ph3-show-ip-route-RTR1.png)

**Cross-VLAN ping — PC-ENG1 to PC-SALES1**
![cross vlan ping ENG1 to SALES1](verification/screenshots/p01-ph3-ping-cross-vlan-ENG1-to-SALES1.png)

**Ping to all gateways — PC-MGMT1**
![ping MGMT1 to gateways](verification/screenshots/p01-ph3-ping-MGMT1-to-gateways.png)

---

### Phase 4 — STP Hardening

**show spanning-tree vlan 100 — HQ-DSW1 (root bridge)**
![show spanning-tree vlan100 DSW1](verification/screenshots/p01-ph4-show-spanning-tree-vlan100-DSW1.png)

**show spanning-tree root — HQ-ASW1**
![show spanning-tree root ASW1](verification/screenshots/p01-ph4-show-spanning-tree-root-ASW1.png)

---

### Phase 5 — SSH Hardening

**SSH login success — PC-MGMT1 (management VLAN allowed)**
![ssh login success MGMT1](verification/screenshots/p01-ph5-ssh-login-success-MGMT1.png)

**SSH denied — PC-ENG1 (wrong VLAN, ACL blocks)**
![ssh denied ENG1](verification/screenshots/p01-ph5-ssh-denied-ENG1.png)

---

### Break/Fix Challenge — VLAN 100 Removed from Trunk

**Before break — PC-ENG1 ping working**
![ping working before break](verification/screenshots/p01-breakfix-ping-working-ENG1-before.png)

**Trunk broken — VLAN 100 missing from allowed list**
![trunk broken vlan100 missing](verification/screenshots/p01-breakfix-trunk-broken-vlan100-missing.png)

**PC-ENG1 ping failing — no path to router**
![ping failing ENG1](verification/screenshots/p01-breakfix-ping-failing-ENG1.png)

**Trunk fixed — VLAN 100 restored to allowed list**
![trunk fixed vlan100 restored](verification/screenshots/p01-breakfix-trunk-fixed-vlan100-restored.png)

**PC-ENG1 ping restored — connectivity confirmed**
![ping restored ENG1](verification/screenshots/p01-breakfix-ping-restored-ENG1.png)

---

## Files

- `configs/` — Running configurations for all devices
- `diagrams/` — Physical and logical topology (draw.io + PNG)
- `verification/baseline/` — Show command outputs before changes
- `verification/post-change/` — Show command outputs after each phase
- `verification/screenshots/` — Key screenshots
- `notes/decision-log.md` — Design decisions and rationale
- `cml/` — CML topology YAML export
