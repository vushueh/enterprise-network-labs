# Project 09 - Phase 2 SNMP Collector Limitation Summary

Date: 2026-05-17

## Finding

HQ-SYSLOG does not expose an interactive CLI in this CML node, so collector-side SNMP tools cannot be checked with:

```text
which snmpwalk
which snmptrapd
sudo ss -lunp | grep ':162'
```

## Evidence From Syslog Output

HQ-SYSLOG continues to display normal syslog messages from devices, proving Phase 1 syslog is still working.

After SNMP was configured on HQ-FW1, HQ-SYSLOG showed:

```text
%ASA-3-106014: Deny inbound icmp src inside:10.1.99.51 dst nlp_int_tap:10.0.0.14 (type 3, code 3)
```

ICMP type 3 code 3 is destination port unreachable. This strongly suggests `10.1.99.51` is returning port-unreachable for SNMP trap traffic, meaning no SNMP trap receiver is currently listening on UDP/162.

## Interpretation

SNMP device-side configuration can be verified locally with:

- `show running-config | include snmp-server|ACL-SNMP-MANAGERS`
- `show snmp`
- `show snmp user`
- `show snmp group`
- `show ip access-lists ACL-SNMP-MANAGERS`
- reachability to `10.1.99.51`

Collector-side SNMP trap verification is blocked until a node with SNMP tools/trap daemon is available.

## Recommended Closeout Path

Treat Phase 2 as device-side complete after:

1. All devices show expected SNMP running-config.
2. Core routers show SNMPv3 user/group present.
3. Each device can reach `10.1.99.51`.
4. At least one trap-triggering event increments device-side `Trap PDUs` in `show snmp`.

Document collector-side trap visibility as a platform limitation of the current HQ-SYSLOG node, to be revisited if a Linux/NMS node with CLI is added.
