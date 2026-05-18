# Project 09 - Phase 1 Syslog Pre-Check Summary

Date: 2026-05-16

## Result

Pre-check passed. HQ-SYSLOG is reachable from the key devices tested.

## Device Findings

### HQ-RTR1

- `show ip interface brief` confirms:
  - `Ethernet0/0.999` = `10.1.99.1`, up/up
  - `Loopback0` = `10.0.255.1`, up/up
  - `Tunnel0` = `10.0.100.1`, up/up
- `ping 10.1.99.51 source 10.1.99.1` succeeded 5/5.
- `show logging` shows existing trap level informational.
- Logging source-interface output is blank, so Phase 1 source-interface config is still needed.

### BR-RTR1

- `show ip interface brief` confirms:
  - `Ethernet0/0.999` = `10.2.99.1`, up/up
  - `Loopback0` = `10.0.255.2`, up/up
  - `Tunnel0` = `10.0.100.2`, up/up
- `ping 10.1.99.51 source 10.2.99.1` succeeded 5/5.
- `show logging` shows existing trap level informational.
- Logging source-interface output is blank, so Phase 1 source-interface config is still needed.

### HQ-DSW1

- `show cdp neighbors` confirms HQ-RTR1, HQ-DSW2, HQ-ASW1, and HQ-ASW2 neighbors.
- `show interfaces status | include Et1/1` confirms:
  - `Et1/1` description `MGMT-HQ-SYSLOG-ETH`
  - connected
  - VLAN 999
- `show vlan brief | include 999` confirms VLAN 999 includes `Et1/1`.
- `ping 10.1.99.51` succeeded 4/5. First packet loss is consistent with ARP resolution, not a failure.

### HQ-FW1

- `show route` confirms:
  - inside route toward 10.0.0.0/16, 10.1.0.0/16, and 10.2.0.0/16 via `10.0.0.13`
  - default route via outside `203.0.113.2`
- `ping inside 10.1.99.51` succeeded 5/5.
- `show logging` confirms:
  - syslog logging enabled
  - timestamp logging enabled
  - device ID hostname `HQ-FW1`
  - logging to inside `10.1.99.51`
  - UDP TX counter present

## Follow-Up Found During Pre-Check

HQ-RTR1 logged DHCP renewal denies from VLAN 100:

```text
%SEC-6-IPACCESSLOGP: list ACL-VLAN100-IN denied udp 10.1.100.194(68) -> 10.1.99.50(67)
%SEC-6-IPACCESSLOGP: list ACL-VLAN100-IN denied udp 10.1.100.170(68) -> 10.1.99.50(67)
```

This matches the known Project 06 ACL issue previously documented for VLAN 200: DHCP renewals are unicast client-to-server packets and hit the inbound VLAN ACL. Project 06 notes said to apply the same correction to VLAN 100 and VLAN 300.

This does not block syslog to `10.1.99.51`, but it should be fixed before relying on stable endpoint DHCP leases during later Project 09 phases.

Recommended follow-up for Claude review:

```text
ip access-list extended ACL-VLAN100-IN
 5 permit udp 10.1.100.0 0.0.0.255 eq 68 host 10.1.99.50 eq 67
 6 permit udp 10.1.100.0 0.0.0.255 host 10.1.99.50 eq 53
 7 permit tcp 10.1.100.0 0.0.0.255 host 10.1.99.50 eq 53
```

Also check whether `ACL-VLAN300-IN` needs the same DHCP/DNS exception pattern for `10.1.99.50`.

## Scope Decision

ISP-RTR1 is excluded from Project 09 Phase 1 internal syslog collection. It represents
the simulated ISP/outside network, while HQ-SYSLOG is inside on management VLAN 999.
Testing confirmed ISP-RTR1 could accept the `logging host 10.1.99.51` command, but
could not reach the collector from Loopback0. Including it would require a deliberate
ASA outside-to-inside policy/NAT design and is not part of Phase 1 internal monitoring.
