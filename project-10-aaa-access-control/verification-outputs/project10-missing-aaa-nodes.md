# Project 10 - Missing AAA Nodes

Date: 2026-05-22

## Finding

`HQ-TACACS` and `HQ-RADIUS` are not present in the current CML topology.

This explains why all devices failed to ping:

- `10.1.99.52` for TACACS+
- `10.1.99.53` for RADIUS

It also explains the incomplete ARP on `HQ-RTR1` for `10.1.99.52`.

## Interpretation

Project 10 cannot begin TACACS+/RADIUS configuration until the AAA server nodes are added, connected, addressed, and verified.

## Required Topology Additions

Add two nodes:

- `TacPlus`, renamed `HQ-TACACS`, expected at `10.1.99.52/24`
- `RADIUS`, renamed `HQ-RADIUS`, expected at `10.1.99.53/24`

Both should be in VLAN 999 with default gateway `10.1.99.1`.

## Recommended Connections

Use available HQ distribution switch access ports, for example:

- `HQ-TACACS eth0` -> `HQ-DSW1 Ethernet1/2`
- `HQ-RADIUS eth0` -> `HQ-DSW1 Ethernet1/3`

If those ports are already used by another real node, choose other unused HQ switch access ports and document the choice.

## Next Step

Create and boot the AAA nodes before continuing with Project 10 Phase 1.

## Switch Port Configuration Applied

`HQ-DSW1 Ethernet1/2`:

```text
description SERVER-HQ-TACACS-VLAN999
switchport mode access
switchport access vlan 999
spanning-tree portfast
no shutdown
```

`HQ-DSW1 Ethernet1/3`:

```text
description SERVER-HQ-RADIUS-VLAN999
switchport mode access
switchport access vlan 999
spanning-tree portfast
no shutdown
```

## Appliance Console Note

The TacPlus and RADIUS CML service nodes do not expose a normal interactive console in this environment. Verification will be performed from the network side using switch MAC learning, ARP, ping, and later AAA test commands.
