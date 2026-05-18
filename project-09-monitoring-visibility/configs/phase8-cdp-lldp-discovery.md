# Project 09 - Phase 8 CDP/LLDP Topology Discovery

Status: CODEX-PROPOSED - pending Claude review
Date: 2026-05-17

## Phase Goal

Use CDP and LLDP to build a verified topology neighbor table for Project 09.

This phase proves the monitoring stack can support topology discovery and gives documentation-quality evidence for the GitHub project.

## In Scope

Collect discovery output from:

- HQ-RTR1
- BR-RTR1
- WAN-RTR1
- HQ-DSW1
- HQ-DSW2
- BR-DSW1
- HQ-ASW1
- HQ-ASW2
- BR-ASW1
- HQ-FW1, discovery only if supported

## Why This Matters

- CDP gives Cisco-native neighbor discovery.
- LLDP gives vendor-neutral discovery.
- `show cdp neighbors detail` reveals neighbor management IPs and platform details.
- `show interfaces description` lets you compare discovered neighbors against intended interface labels.
- The final neighbor table becomes the documentation baseline for troubleshooting and future Project 12 disaster recovery.

## Pre-Check On IOS/IOL Devices

Run on each IOS/IOL device:

```text
show running-config | include ^cdp run|^lldp run
show cdp neighbors
show lldp neighbors
show interfaces description
```

Expected:

- CDP should already be active unless explicitly disabled.
- LLDP may not be enabled yet.
- Interface descriptions should help validate neighbor relationships.

## Optional Discovery Config On IOS/IOL Devices

Apply only on IOS/IOL devices. If `lldp run` is unsupported on any image, document it and continue with CDP.

```text
! ============================================================
! DEVICE: <DEVICE-NAME> | PROJECT: 09 - Monitoring and Visibility
! PHASE: 8 - CDP/LLDP Topology Discovery
! ============================================================
enable
configure terminal

! --- Cisco Discovery Protocol ---
! WHY: Keeps Cisco-native neighbor discovery enabled for topology mapping.
cdp run

! --- Link Layer Discovery Protocol ---
! WHY: Enables vendor-neutral neighbor discovery so the topology can be
! documented using both Cisco and standards-based discovery.
lldp run

end
write memory
```

Apply to:

- HQ-RTR1
- BR-RTR1
- WAN-RTR1
- HQ-DSW1
- HQ-DSW2
- BR-DSW1
- HQ-ASW1
- HQ-ASW2
- BR-ASW1

## ASA / HQ-FW1 Check

Do not force IOS syntax on the ASA. Run discovery checks only:

```text
show running-config cdp
show running-config lldp
show cdp neighbors
show lldp neighbors
```

If commands are unsupported, document HQ-FW1 as discovery-limited.

## Verification Collection

Run on each IOS/IOL device:

```text
show cdp neighbors
show cdp neighbors detail
show lldp neighbors
show lldp neighbors detail
show interfaces description
show ip interface brief
```

For `HQ-FW1`, run only supported variants:

```text
show cdp neighbors
show lldp neighbors
show interface ip brief
show nameif
```

## Final Neighbor Table Template

Create the final table from the outputs:

| Local Device | Local Interface | Neighbor Device | Neighbor Interface | Discovery Protocol | Neighbor IP | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| HQ-DSW1 | Ethernet0/1 | HQ-ASW1 | Ethernet0/0 | CDP/LLDP | TBD | Example |

## Completion Criteria

Phase 8 is complete when:

- CDP neighbor outputs are collected from all IOS/IOL devices.
- LLDP neighbor outputs are collected where supported.
- Unsupported commands are documented as platform limitations.
- A complete neighbor table is built or enough output is saved to build it.
- Interface descriptions and discovered neighbors do not reveal unexpected cabling.
