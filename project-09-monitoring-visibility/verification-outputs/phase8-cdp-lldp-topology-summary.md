# Project 09 - Phase 8 CDP/LLDP Topology Discovery Summary

Date: 2026-05-17

## Result

Phase 8 is complete.

CDP/LLDP discovery has been collected from all nine IOS/IOL devices. `HQ-FW1` was checked and documented as CDP/LLDP unsupported on this ASAv image.

`cdp run` and `lldp run` were applied successfully on:

- HQ-RTR1
- BR-RTR1
- WAN-RTR1
- HQ-DSW1
- HQ-DSW2
- BR-DSW1
- HQ-ASW1
- HQ-ASW2
- BR-ASW1

## Neighbor Table

| Local Device | Local Interface | Neighbor Device | Neighbor Interface | Protocol Evidence | Neighbor IP / Mgmt IP | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| HQ-RTR1 | Ethernet0/0 | HQ-DSW1 | Ethernet0/0 | CDP + LLDP | 10.1.99.11 | Trunk to HQ distribution |
| HQ-RTR1 | Ethernet0/1 | BR-RTR1 | Ethernet0/1 | CDP + LLDP | 10.0.0.2 | WAN point-to-point |
| HQ-RTR1 | Ethernet0/2 | WAN-RTR1 | Ethernet0/1 | CDP + LLDP | 10.0.0.6 | WAN point-to-point |
| HQ-RTR1 | Ethernet0/3 | HQ-FW1 | inside/Gi0/0 equivalent | Interface description only | 10.0.0.14 expected | ASA discovery still needs check |
| BR-RTR1 | Ethernet0/0 | BR-DSW1 | Ethernet0/0 | CDP | 10.2.99.2 | Branch distribution trunk |
| BR-RTR1 | Ethernet0/1 | HQ-RTR1 | Ethernet0/1 | CDP + LLDP | 10.0.0.1 | WAN point-to-point |
| BR-RTR1 | Ethernet0/2 | WAN-RTR1 | Ethernet0/0 | CDP + LLDP | 10.0.0.9 | WAN point-to-point |
| WAN-RTR1 | Ethernet0/0 | BR-RTR1 | Ethernet0/2 | CDP + LLDP | 10.0.0.10 | WAN point-to-point |
| WAN-RTR1 | Ethernet0/1 | HQ-RTR1 | Ethernet0/2 | CDP + LLDP | 10.0.0.5 | WAN point-to-point |
| HQ-DSW1 | Ethernet0/0 | HQ-RTR1 | Ethernet0/0 | CDP + LLDP | 10.0.0.5 / 10.0.255.1 context | Router trunk |
| HQ-DSW1 | Ethernet0/1 | HQ-ASW1 | Ethernet0/0 | CDP | 10.1.99.13 | Access switch trunk |
| HQ-DSW1 | Ethernet0/2 | HQ-ASW2 | Ethernet0/0 | CDP | 10.1.99.14 | Access switch trunk |
| HQ-DSW1 | Ethernet0/3 | HQ-DSW2 | Ethernet0/3 | CDP + LLDP | 10.1.99.12 | LACP member |
| HQ-DSW1 | Ethernet1/0 | HQ-DSW2 | Ethernet1/0 | CDP + LLDP | 10.1.99.12 | LACP member |
| HQ-DSW2 | Ethernet0/1 | HQ-ASW1 | Ethernet0/1 | CDP | 10.1.99.13 | Access switch trunk |
| HQ-DSW2 | Ethernet0/2 | HQ-ASW2 | Ethernet0/1 | CDP | 10.1.99.14 | Access switch trunk |
| HQ-DSW2 | Ethernet0/3 | HQ-DSW1 | Ethernet0/3 | CDP + LLDP | 10.1.99.11 | LACP member |
| HQ-DSW2 | Ethernet1/0 | HQ-DSW1 | Ethernet1/0 | CDP + LLDP | 10.1.99.11 | LACP member |
| BR-DSW1 | Ethernet0/0 | BR-RTR1 | Ethernet0/0 | CDP + LLDP | 10.2.99.1 / 10.0.255.2 context | Branch router trunk |
| BR-DSW1 | Ethernet0/1 | BR-ASW1 | Ethernet0/0 | CDP + LLDP | 10.2.99.3 | Branch access trunk |
| HQ-ASW1 | Ethernet0/0 | HQ-DSW1 | Ethernet0/1 | CDP + LLDP | 10.1.99.11 | Dual-homed access trunk |
| HQ-ASW1 | Ethernet0/1 | HQ-DSW2 | Ethernet0/1 | CDP | 10.1.99.12 | Dual-homed access trunk |
| HQ-ASW2 | Ethernet0/0 | HQ-DSW1 | Ethernet0/2 | CDP | 10.1.99.11 | Dual-homed access trunk |
| HQ-ASW2 | Ethernet0/1 | HQ-DSW2 | Ethernet0/2 | CDP + LLDP | 10.1.99.12 | Dual-homed access trunk |
| BR-ASW1 | Ethernet0/0 | BR-DSW1 | Ethernet0/1 | CDP + LLDP | 10.2.99.2 | Branch access trunk |

## Endpoint / Server-Facing Interfaces Not Shown By CDP/LLDP

These links are expected not to show CDP/LLDP neighbors because the endpoints/servers may not advertise discovery:

- HQ-DSW1 Ethernet1/1: HQ-SYSLOG
- HQ-DSW2 Ethernet0/0: HQ DHCP/DNS server
- HQ-ASW1 Ethernet0/2: Engineering PC
- HQ-ASW1 Ethernet0/3: P09 syslog test port
- HQ-ASW2 Ethernet0/2: Sales PC
- HQ-ASW2 Ethernet0/3: Attacker/test host
- BR-ASW1 Ethernet1/0: Branch PC VLAN100
- BR-ASW1 Ethernet1/1: Branch PC VLAN200

## Notes

- Several pasted commands show `how ...` instead of `show ...`; these are harmless operator typos and do not affect the successful outputs.
- LLDP was initially disabled on HQ-ASW1 and HQ-ASW2, then enabled successfully.
- Some LLDP outputs show fewer neighbors than CDP. CDP remains the primary evidence source for several IOL-L2 links.
- ASA/HQ-FW1 discovery support still needs to be checked separately.

## HQ-FW1 / ASA Platform Check

`HQ-FW1` rejects CDP/LLDP commands:

```text
show running-config cdp
                             ^
ERROR: % Invalid input detected at '^' marker.

show running-config lldp
                             ^
ERROR: % Invalid input detected at '^' marker.

show cdp neighbors
              ^
ERROR: % Invalid input detected at '^' marker.

show lldp neighbors
              ^
ERROR: % Invalid input detected at '^' marker.
```

Interface state was verified instead:

```text
GigabitEthernet0/0  10.0.0.14    up/up  nameif inside   security 100
GigabitEthernet0/1  203.0.113.1  up/up  nameif outside  security 0
GigabitEthernet0/2  10.1.40.1    up/up  nameif dmz      security 50
```

The `HQ-RTR1` interface description provides the ASA inside-side topology link:

```text
HQ-RTR1 Ethernet0/3 -> HQ-FW1 GigabitEthernet0/0 inside
```

## Completion Result

Phase 8 is complete.

The topology discovery baseline is documented, with ASA discovery limitation noted.
