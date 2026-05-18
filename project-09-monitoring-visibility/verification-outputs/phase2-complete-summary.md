# Project 09 - Phase 2 Complete Summary

Date completed: 2026-05-17

## Status

Project 09 Phase 2 - SNMP Monitoring is complete.

## Scope

SNMP configured on all 10 in-scope devices:

- HQ-RTR1
- BR-RTR1
- WAN-RTR1
- HQ-DSW1
- HQ-DSW2
- BR-DSW1
- HQ-ASW1
- HQ-ASW2
- BR-ASW1
- HQ-FW1

ISP-RTR1 remains excluded because it represents the outside/ISP side of the ASA.

## Device-Side Verification

Verified:

- SNMPv2c read-only community plus `ACL-SNMP-MANAGERS` on all in-scope devices.
- SNMPv3 authPriv using SHA authentication and AES128 privacy on:
  - HQ-RTR1
  - BR-RTR1
  - WAN-RTR1
- Trap source:
  - `Loopback0` on routers
  - `Vlan999` on switches
- All in-scope devices reach `10.1.99.51`.
- Trap destination `10.1.99.51` is registered on in-scope devices.

## Platform Limitation

HQ-SYSLOG is a syslog-ng-only node from the Project 07 build. It has no exposed CLI and no available `snmptrapd` or net-snmp tools from the current interface.

SNMP trap collector-side proof is not possible without rebuilding or adding a node that includes SNMP tools.

ASA coldstart trap generation was confirmed from the device side:

```text
show snmp-server statistics
1 Trap PDUs
```

HQ-SYSLOG returned ICMP port unreachable for UDP/162 traffic, confirming traps are transmitted from the ASA side but no trap receiver is listening on the collector.

## Next Phase

Project 09 Phase 3 - NetFlow Traffic Analysis.
