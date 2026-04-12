# Project 02 — Multi-Site Expansion + DHCP

## Problem Statement

HQ exists as an isolated campus. The business opens a second site (branch). You need to
build the branch from scratch — matching the same management architecture and security
baseline — connect it to HQ over a WAN link, deploy centralized DHCP serving both sites
through a relay agent, add IPv6 dual-stack, and prove DNS resolution works end-to-end.

## STAR Summary

**Situation:** A single-site HQ campus network existed with no branch connectivity, no
centralized DHCP service, and no DNS. Every endpoint had static IPs.

**Task:** Design and build a multi-site enterprise network from scratch — branch switching,
WAN connectivity, centralized DHCP with relay, IPv6 dual-stack, and DNS — while keeping
HQ aligned with the current server VLAN design used later in the lab series.

**Action:** Deployed BR-RTR1 (router-on-a-stick), BR-DSW1, and BR-ASW1 with full branch
VLAN infrastructure. Connected HQ and Branch via a point-to-point /30 WAN. Deployed a
centralized Dnsmasq server on HQ that serves all relay-enabled user VLANs using
`ip helper-address`. Kept HQ VLAN 400 as the routed Servers subnet (static/routed only),
while Branch retained VLAN 500 as the additional DHCP-served subnet.

**Result:** Can design a multi-site network, configure centralized DHCP serving remote
sites over a WAN, and verify dual-stack IPv4/IPv6 connectivity and DNS resolution from
branch endpoints back to HQ.

---

## Technologies Used

- Router-on-a-Stick inter-VLAN routing (branch site)
- 802.1Q Trunking with VLAN pruning
- Point-to-point WAN /30 (10.0.0.0/30)
- Static routing — explicit per-subnet routes both directions
- Centralized DHCP (Dnsmasq) with `ip helper-address` relay
- DHCP pools for **7 active relay-served subnets** across 2 sites
- IPv6 dual-stack — /126 WAN, /64 VLAN 100 at both sites
- SLAAC (Stateless Address Autoconfiguration) via Router Advertisements
- DNS with static A records via Dnsmasq `address=` directives
- Rapid-PVST+ STP with BR-DSW1 as root for all branch VLANs
- PortFast + BPDU Guard on all access ports
- SSH v2 with VTY ACL restricted to management VLAN

---

## IP Addressing

### Branch Site (10.2.x.x)

| Device | Interface | IP | Purpose |
|--------|-----------|-----|---------|
| BR-RTR1 | E0/0.100 | 10.2.100.1/24 | Engineering gateway |
| BR-RTR1 | E0/0.200 | 10.2.200.1/24 | Sales gateway |
| BR-RTR1 | E0/0.300 | 10.2.44.1/24 | Guest gateway |
| BR-RTR1 | E0/0.500 | 10.2.50.1/24 | Branch VLAN 500 gateway |
| BR-RTR1 | E0/0.999 | 10.2.99.1/24 | Management gateway |
| BR-DSW1 | Vlan999 | 10.2.99.2/24 | Management SVI |
| BR-ASW1 | Vlan999 | 10.2.99.3/24 | Management SVI |
| PC-BR1 | eth0 | 10.2.100.197/24 | Branch Engineering (DHCP) |
| PC-BR2 | eth0 | 10.2.200.108/24 | Branch Sales (DHCP) |

### WAN Link

| Device | Interface | IP | Purpose |
|--------|-----------|-----|---------|
| HQ-RTR1 | E0/1 | 10.0.0.1/30 | WAN HQ-side |
| BR-RTR1 | E0/1 | 10.0.0.2/30 | WAN Branch-side |

### HQ Current Alignment

| Device | Interface | IP | Purpose |
|--------|-----------|-----|---------|
| HQ-RTR1 | E0/0.100 | 10.1.100.1/24 | Engineering gateway |
| HQ-RTR1 | E0/0.200 | 10.1.200.1/24 | Sales gateway |
| HQ-RTR1 | E0/0.300 | 10.1.44.1/24 | Guest gateway |
| HQ-RTR1 | E0/0.400 | 10.1.40.1/24 | Servers gateway |
| HQ-RTR1 | E0/0.999 | 10.1.99.1/24 | Management gateway |
| HQ-DHCP-DNS | eth0 | 10.1.99.50/24 | Centralized DHCP+DNS server |

### IPv6 Addressing

| Interface | IPv6 | Purpose |
|-----------|------|---------|
| HQ-RTR1 E0/1 | 2001:db8:0:1::1/126 | WAN HQ-side |
| BR-RTR1 E0/1 | 2001:db8:0:1::2/126 | WAN Branch-side |
| HQ-RTR1 E0/0.100 | 2001:db8:1:100::1/64 | HQ Engineering IPv6 GW |
| BR-RTR1 E0/0.100 | 2001:db8:2:100::1/64 | Branch Engineering IPv6 GW |

---

## DHCP Pool Summary

| Tag | Subnet | Range | Gateway | DNS |
|-----|--------|-------|---------|-----|
| hq-eng | 10.1.100.0/24 | .100–.200 | 10.1.100.1 | 10.1.99.50 |
| hq-sales | 10.1.200.0/24 | .100–.200 | 10.1.200.1 | 10.1.99.50 |
| hq-guest | 10.1.44.0/24 | .100–.200 | 10.1.44.1 | 10.1.99.50 |
| br-eng | 10.2.100.0/24 | .100–.200 | 10.2.100.1 | 10.1.99.50 |
| br-sales | 10.2.200.0/24 | .100–.200 | 10.2.200.1 | 10.1.99.50 |
| br-guest | 10.2.44.0/24 | .100–.200 | 10.2.44.1 | 10.1.99.50 |
| br-voice | 10.2.50.0/24 | .100–.200 | 10.2.50.1 | 10.1.99.50 |

> HQ VLAN 400 (`10.1.40.0/24`) is a routed/static Servers subnet in the current live lab.
> It is **not** DHCP-relayed in the current design.

---

## Key Configuration Notes

### DHCP Relay

- **HQ-RTR1** uses `ip helper-address 10.1.99.50` on VLANs **100, 200, and 300** only.
- **BR-RTR1** uses `ip helper-address 10.1.99.50` on VLANs **100, 200, 300, and 500**.
- HQ VLAN 400 does **not** use DHCP relay in the current design.

### Dnsmasq Pools

- The HQ Dnsmasq server serves the 3 HQ user pools and the 4 branch pools.
- Static `address=` records provide name resolution for key infrastructure devices.
- DHCP clients receive `10.1.99.50` as their DNS server.

### HQ Distribution Layer

- HQ-DSW2 Ethernet0/0 is the access port for the `HQ-DHCP-DNS` server in VLAN 999.
- HQ trunks allow `100,200,300,400,999`.
- HQ-DSW1 is root for VLANs `100,400,999`; HQ-DSW2 is root for VLANs `200,300`.

---

## Key Verification Commands

| Command | Device | Expected Result |
|---------|--------|-----------------|
| `show ip interface brief` | BR-RTR1 | E0/0.100–.999 all up/up with 10.2.x.x IPs |
| `show interfaces trunk` | BR-DSW1 | E0/0 and E0/1 trunking, native 1000 |
| `show running-config \| section helper` | HQ-RTR1 | helper-address on E0/0.100, .200, .300 |
| `show running-config \| section helper` | BR-RTR1 | helper-address on E0/0.100, .200, .300, .500 |
| `udhcpc -i eth0` | PC-BR1 / PC-BR2 | Lease from 10.1.99.50 in correct branch range |
| `nslookup hq-rtr1.lab.local 10.1.99.50` | Branch client | Resolves 10.1.99.1 |
| `show vlan brief` | HQ-DSW2 | Et0/0 in VLAN 999 for DHCP/DNS server |

---

## Files

- `configs/` — Phase-by-phase running configs and delta configs for all devices
- `diagrams/` — CML topology screenshot
- `verification/` — Command outputs and screenshots by phase
- `notes/decision-log.md` — Design decisions and rationale
- `cml/` — CML topology YAML export
