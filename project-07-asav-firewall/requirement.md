# Project 07 — Business Requirement

**Project:** ASAv Perimeter Firewall
**Series:** Enterprise Network Labs | **Platform:** Cisco CML 2.9
**Completion Scope:** Phases 1-6 complete; break/fix deferred

---

## Business Context

The enterprise network from Projects 01-06 has stable routing, switching, NAT, and campus hardening. The remaining weakness is the internet edge: HQ-RTR1 still owns routing, NAT, and perimeter filtering. That creates a single control point with limited stateful inspection and no dedicated DMZ enforcement.

Project 07 moves internet security to a dedicated ASAv firewall while preserving HQ-RTR1 as the campus router. This separates routing from security policy, gives the public server its own DMZ, and makes firewall behavior visible through packet-tracer, syslog, and connection-table verification.

---

## Requirements

### REQ-01 — Dedicated Stateful Firewall Boundary

Insert HQ-FW1 between HQ-RTR1 and ISP-RTR1. HQ-RTR1 must route internal traffic toward the firewall, and ISP-RTR1 must face the firewall outside interface.

### REQ-02 — DMZ Server Isolation

Move HQ-SRV1 out of the internal server VLAN and place it behind the ASAv DMZ interface. HQ-SRV1 must use HQ-FW1 as its default gateway.

### REQ-03 — Firewall-Owned NAT

Remove Project 05 NAT from HQ-RTR1. Rebuild internal PAT and HQ-SRV1 static NAT on HQ-FW1 so policy and translation occur on the same security device.

### REQ-04 — Outside-In Default Deny

Deny all outside-originated traffic by default. The only inbound exception in this project is HTTP to the DMZ server public address, translated to HQ-SRV1.

### REQ-05 — Application Inspection

Enable ASA inspection for HTTP, DNS, and ICMP so permitted flows receive stateful application-aware handling and ICMP replies work without broad outside ACL permits.

### REQ-06 — Firewall Logging and Visibility

Send firewall logs to HQ-SYSLOG and enable ACL logging for outside interface decisions. Verification must include ACL hit counters, syslog evidence, and active connection-table output.

---

## Acceptance Criteria

| Requirement | Verification Method |
|-------------|---------------------|
| REQ-01 | `show interface ip brief`, `show nameif`, HQ-RTR1 default route to 10.0.0.14, ISP ping to 203.0.113.1 |
| REQ-02 | HQ-SRV1 address 10.1.40.10/24, gateway 10.1.40.1, DMZ interface up on HQ-FW1 |
| REQ-03 | HQ-RTR1 has no active NAT config; HQ-FW1 `show nat detail` shows PAT objects and static NAT |
| REQ-04 | `packet-tracer input outside` permits TCP/80 to 203.0.113.10 and drops outside-to-inside attempts |
| REQ-05 | `show service-policy global` shows HTTP, DNS, and ICMP inspection active |
| REQ-06 | `show logging`, `show access-list ACL-OUTSIDE-IN`, syslog capture, and `show conn` screenshots present |

---

## Constraints

- **Platform:** Cisco ASAv in CML 2.9 uses `GigabitEthernet0/x` interface naming.
- **Routing boundary:** HQ-RTR1 remains the campus router; ASAv is not replacing the router.
- **Public addressing:** Existing lab public range 203.0.113.0/24 is retained for documentation-safe public IP simulation.
- **Break/fix:** Deferred for a future video demonstration and must not be marked complete.

---

## Security Level Model

| Zone | Interface | Security Level | Trust |
|------|-----------|----------------|-------|
| inside | GigabitEthernet0/0 | 100 | Fully trusted campus network |
| dmz | GigabitEthernet0/2 | 50 | Semi-trusted public server segment |
| outside | GigabitEthernet0/1 | 0 | Untrusted internet |

Traffic can initiate from higher to lower security levels by default. Traffic from lower to higher security levels requires an explicit ACL permit.
