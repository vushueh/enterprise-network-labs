# Project 09 - Phase 2 SNMP Switch and Firewall Verification Summary

Date: 2026-05-17

## Status

SNMPv2c baseline is applied and locally verified on:

- HQ-DSW1
- HQ-DSW2
- BR-DSW1
- HQ-ASW1
- HQ-ASW2
- BR-ASW1
- HQ-FW1

## Distribution Switches

### HQ-DSW1

Verified:

- `ACL-SNMP-MANAGERS` exists.
- ACL permits `10.1.99.51`.
- SNMPv2c read-only community `P09V2CRO2026` is bound to `ACL-SNMP-MANAGERS`.
- Trap source is `Vlan999`.
- SNMP trap host `10.1.99.51` exists for SNMPv2c.
- SNMP traps enabled for authentication, linkdown, linkup, coldstart, and warmstart.
- Ping to `10.1.99.51` succeeded 5/5.

### HQ-DSW2

Verified:

- `ACL-SNMP-MANAGERS` exists.
- ACL permits `10.1.99.51`.
- SNMPv2c read-only community `P09V2CRO2026` is bound to `ACL-SNMP-MANAGERS`.
- Trap source is `Vlan999`.
- SNMP trap host `10.1.99.51` exists for SNMPv2c.
- SNMP traps enabled for authentication, linkdown, linkup, coldstart, and warmstart.
- Ping to `10.1.99.51` succeeded 5/5.

### BR-DSW1

Verified:

- `ACL-SNMP-MANAGERS` exists.
- ACL permits `10.1.99.51`.
- SNMPv2c read-only community `P09V2CRO2026` is bound to `ACL-SNMP-MANAGERS`.
- Trap source is `Vlan999`.
- SNMP trap host `10.1.99.51` exists for SNMPv2c.
- SNMP traps enabled for authentication, linkdown, linkup, coldstart, and warmstart.
- Ping to `10.1.99.51` succeeded 5/5.

## Access Switches

### HQ-ASW1

Verified:

- `ACL-SNMP-MANAGERS` exists.
- ACL permits `10.1.99.51`.
- SNMPv2c read-only community `P09V2CRO2026` is bound to `ACL-SNMP-MANAGERS`.
- Trap source is `Vlan999`.
- SNMP trap host `10.1.99.51` exists for SNMPv2c.
- SNMP traps enabled for authentication, linkdown, linkup, coldstart, and warmstart.
- Ping to `10.1.99.51` succeeded 5/5.

### HQ-ASW2

Verified:

- `ACL-SNMP-MANAGERS` exists.
- ACL permits `10.1.99.51`.
- SNMPv2c read-only community `P09V2CRO2026` is bound to `ACL-SNMP-MANAGERS`.
- Trap source is `Vlan999`.
- SNMP trap host `10.1.99.51` exists for SNMPv2c.
- SNMP traps enabled for authentication, linkdown, linkup, coldstart, and warmstart.
- Ping to `10.1.99.51` succeeded 5/5.

### BR-ASW1

Verified:

- `ACL-SNMP-MANAGERS` exists.
- ACL permits `10.1.99.51`.
- SNMPv2c read-only community `P09V2CRO2026` is bound to `ACL-SNMP-MANAGERS`.
- Trap source is `Vlan999`.
- SNMP trap host `10.1.99.51` exists for SNMPv2c.
- SNMP traps enabled for authentication, linkdown, linkup, coldstart, and warmstart.
- Ping to `10.1.99.51` succeeded 5/5.

## HQ-FW1

Verified:

- `snmp-server host inside 10.1.99.51 community ***** version 2c` exists.
- SNMP location is `P09-CML-LAB-FIREWALL`.
- SNMP contact is `Leonel - Enterprise Network Labs`.
- `show snmp-server statistics` shows:
  - `0 SNMP packets input`
  - `1 SNMP packets output`
  - `1 Trap PDUs`
- `ping inside 10.1.99.51` succeeded 5/5.

## Notes

- IOS switch `show snmp` counters show `0 SNMP packets input` and `0 Trap PDUs` until a manager polls or a trap event is generated.
- HQ-FW1 already generated one Trap PDU after SNMP config, proving ASA-side trap generation is active.

## Remaining Phase 2 Work

- Verify HQ-SYSLOG collector tooling:
  - `which snmpwalk`
  - `which snmptrapd`
  - `sudo ss -lunp | grep ':162'`
- If `snmpwalk` exists, test SNMPv2c polling from HQ-SYSLOG.
- If `snmptrapd` is listening on UDP/162, generate a link flap on an access switch and verify linkUp/linkDown traps at the collector.
