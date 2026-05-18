# Project 09 - Phase 2 SNMP Core Routers Verification Summary

Date: 2026-05-17

## Status

Core router SNMP configuration is applied and locally verified on:

- HQ-RTR1
- BR-RTR1
- WAN-RTR1

## Verified Baseline

Before configuration, the core routers showed no existing SNMP config and could reach `10.1.99.51`.

## HQ-RTR1

Verified:

- `ACL-SNMP-MANAGERS` exists.
- ACL permits `10.1.99.51`.
- SNMPv2c read-only community `P09V2CRO2026` is bound to `ACL-SNMP-MANAGERS`.
- Trap source is `Loopback0`.
- SNMP trap host `10.1.99.51` exists for SNMPv2c.
- SNMP trap host `10.1.99.51` exists for SNMPv3 user `p09snmpv3`.
- SNMP traps enabled for authentication, linkdown, linkup, coldstart, and warmstart.
- SNMPv3 group `P09-SNMPV3-GROUP` exists with `v3 priv`.
- SNMPv3 user `p09snmpv3` exists with SHA authentication and AES128 privacy.
- Ping to `10.1.99.51` sourced from Loopback0 succeeded 5/5.

## BR-RTR1

Verified:

- `ACL-SNMP-MANAGERS` exists.
- ACL permits `10.1.99.51`.
- SNMPv2c read-only community `P09V2CRO2026` is bound to `ACL-SNMP-MANAGERS`.
- Trap source is `Loopback0`.
- SNMP trap host `10.1.99.51` exists for SNMPv2c.
- SNMP trap host `10.1.99.51` exists for SNMPv3 user `p09snmpv3`.
- SNMP traps enabled for authentication, linkdown, linkup, coldstart, and warmstart.
- SNMPv3 group `P09-SNMPV3-GROUP` exists with `v3 priv`.
- SNMPv3 user `p09snmpv3` exists with SHA authentication and AES128 privacy.
- Ping to `10.1.99.51` sourced from Loopback0 succeeded 5/5.

## WAN-RTR1

Verified:

- `ACL-SNMP-MANAGERS` exists.
- ACL permits `10.1.99.51`.
- SNMPv2c read-only community `P09V2CRO2026` is bound to `ACL-SNMP-MANAGERS`.
- Trap source is `Loopback0`.
- SNMP trap host `10.1.99.51` exists for SNMPv2c.
- SNMP trap host `10.1.99.51` exists for SNMPv3 user `p09snmpv3`.
- SNMP traps enabled for authentication, linkdown, linkup, coldstart, and warmstart.
- SNMPv3 group `P09-SNMPV3-GROUP` exists with `v3 priv`.
- SNMPv3 user `p09snmpv3` exists with SHA authentication and AES128 privacy.
- Ping to `10.1.99.51` sourced from Loopback0 succeeded 5/5.

## Notes

The typed command lines displayed some wrapped/truncated text, but final verification proves the intended commands were present in running config.

`show snmp` currently shows `0 SNMP packets input` and `0 Trap PDUs`, which is expected until a collector polls the devices or a trap-triggering event occurs.

## Remaining Phase 2 Work

- Apply SNMPv2c baseline to distribution switches.
- Apply SNMPv2c baseline to access switches.
- Apply or review ASAv SNMP syntax for HQ-FW1.
- Verify whether HQ-SYSLOG has `snmpwalk` and `snmptrapd`.
- Generate a trap event and verify collector-side receipt if UDP/162 trap receiver is running.
