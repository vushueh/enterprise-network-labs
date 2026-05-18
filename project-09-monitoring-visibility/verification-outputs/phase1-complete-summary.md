# Project 09 - Phase 1 Complete Summary

Date completed: 2026-05-17

## Status

Project 09 Phase 1 - Syslog Infrastructure is complete.

## Scope

Included:

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

Excluded:

- ISP-RTR1, because it represents the outside/ISP side of the ASA. Including it would require a deliberate outside-to-inside monitoring policy/NAT design.

## Verified Collector Proof

HQ-SYSLOG received logs from:

- HQ-FW1 source `10.0.0.14`
- HQ-ASW1 source `10.1.99.13`
- HQ-ASW2 source `10.1.99.14`
- BR-ASW1 source `10.2.99.3`
- HQ-RTR1 source `10.0.255.1` with `P09_PHASE1_SYSLOG_TEST`
- BR-RTR1 source `10.0.255.2` with `P09_PHASE1_SYSLOG_TEST`
- WAN-RTR1 source `10.0.255.3` with `P09_PHASE1_SYSLOG_TEST`
- HQ-DSW1 source `10.1.99.11` with `P09_PHASE1_SYSLOG_TEST`
- HQ-DSW2 source `10.1.99.12` with `P09_PHASE1_SYSLOG_TEST`
- BR-DSW1 source `10.2.99.2` with `P09_PHASE1_SYSLOG_TEST`

## Cleanup Completed

- Switch debug timestamps corrected and verified on:
  - HQ-DSW1
  - HQ-DSW2
  - BR-DSW1
  - HQ-ASW1
  - HQ-ASW2
  - BR-ASW1
- ISP-RTR1 logging host/source-interface removed.

## Non-Blocking Follow-Up

HQ-RTR1 logged DHCP renewal denies from `ACL-VLAN100-IN` for client UDP/68 to DHCP server `10.1.99.50` UDP/67. This does not block syslog, but should be fixed before later Project 09 correlation exercises so endpoint DHCP renewals do not interfere with traffic tests.

Recommended later check:

```text
show ip access-lists ACL-VLAN100-IN
show ip access-lists ACL-VLAN300-IN
```

## Next Phase

Project 09 Phase 2 - SNMP Monitoring.
