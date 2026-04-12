# Live Lab Alignment — 2026-04-12

This note records the validated **current live lab state** after rebuilding and checking the HQ distribution layer, HQ router subinterfaces, and centralized DHCP reachability.

## Why this file exists

Some historical files from Project 01 and Project 02 reflect earlier build stages. The live lab has since evolved during Project 03 validation. This file is the **current source of truth** for the live HQ design until the older historical files are refactored.

## Final live design decision

- **HQ keeps VLAN 400** as the routed **Servers** subnet (`10.1.40.0/24`)
- **HQ does NOT use VLAN 500** anymore
- **HQ VLAN 400 is static/routed only for now** — no `ip helper-address` on VLAN 400
- **Branch keeps VLAN 500** as its DHCP-served subnet (`10.2.50.0/24`)
- **HQ-DHCP-DNS stays on HQ-DSW2 Ethernet0/0 in VLAN 999**

## Verified HQ cabling from CDP

### HQ-DSW1
- `Et0/0 -> HQ-RTR1 Et0/0`
- `Et0/1 -> HQ-ASW1 Et0/0`
- `Et0/2 -> HQ-ASW2 Et0/0`
- `Et0/3 -> HQ-DSW2 Et0/3`

### HQ-DSW2
- `Et0/0 -> HQ-DHCP-DNS`
- `Et0/1 -> HQ-ASW1 Et0/1`
- `Et0/2 -> HQ-ASW2 Et0/1`
- `Et0/3 -> HQ-DSW1 Et0/3`

## Verified STP roles

- **HQ-DSW1 root:** VLAN 100, VLAN 400, VLAN 999
- **HQ-DSW2 root:** VLAN 200, VLAN 300

## Verified HQ router subinterfaces

### Active HQ subinterfaces
- `Ethernet0/0.100 = 10.1.100.1/24` with `ip helper-address 10.1.99.50`
- `Ethernet0/0.200 = 10.1.200.1/24` with `ip helper-address 10.1.99.50`
- `Ethernet0/0.300 = 10.1.44.1/24` with `ip helper-address 10.1.99.50`
- `Ethernet0/0.400 = 10.1.40.1/24` **no helper-address**
- `Ethernet0/0.999 = 10.1.99.1/24`

### Removed from live HQ design
- `Ethernet0/0.500` was removed as a valid HQ VLAN gateway design and is no longer used.

## DHCP behavior validated

### HQ DHCP relay VLANs
- VLAN 100
- VLAN 200
- VLAN 300

### HQ non-DHCP VLANs
- VLAN 400 (Servers)
- VLAN 999 (Management)

### Branch DHCP relay VLANs
- VLAN 100
- VLAN 200
- VLAN 300
- VLAN 500

## Repo interpretation

- Project 01 remains the historical campus foundation build.
- Project 02 contains historical DHCP build steps, including older HQ VLAN 500 references.
- Project 03 plus this alignment note should be treated as the **current live operational state**.
