# Project 01 — Campus Foundation Design Decisions

## VLAN Numbering
**Choice:** VLANs start at 100 (Engineering=100, Sales=200, Guest=300, Mgmt=999)
**Alternatives considered:** Starting at VLAN 10 as most lab guides suggest
**Rationale:** VLANs 1-99 are in use on Leonel's physical homelab (OPNsense/Alta Labs). Starting at 100 eliminates any future conflict if CML is ever bridged to the homelab.
**Trade-offs:** VLAN IDs above 255 cannot map directly to the third IP octet, requiring shorthand (e.g., VLAN 300 uses .44 subnet).

## Native VLAN = 1000
**Choice:** Native VLAN set to unused VLAN 1000 on all trunks
**Alternatives considered:** Leaving native VLAN as default (VLAN 1)
**Rationale:** VLAN 1 as native VLAN is a known security risk. Untagged traffic on VLAN 1 can reach management interfaces. VLAN 1000 has no IP and no devices assigned.
**Trade-offs:** Must be consistent on both sides of every trunk or native VLAN mismatch occurs.

## Router-on-a-Stick vs Layer 3 Switch
**Choice:** Router-on-a-stick (subinterfaces on HQ-RTR1)
**Alternatives considered:** SVIs on a Layer 3 distribution switch
**Rationale:** Teaches encapsulation dot1Q and subinterface design directly — core CCNA topics. Layer 3 switching introduced in later projects.
**Trade-offs:** Single physical link to router is a bottleneck; all inter-VLAN traffic hairpins through one interface.

## Dual Distribution Switches
**Choice:** HQ-DSW1 + HQ-DSW2 with redundant uplinks to each access switch
**Alternatives considered:** Single distribution switch
**Rationale:** Real-world redundancy requirement. Two distribution switches require deliberate STP root election — core CCNA topic and stronger portfolio content.
**Trade-offs:** Higher node count, requires STP hardening to prevent loops.
