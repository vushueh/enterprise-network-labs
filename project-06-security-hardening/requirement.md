# Project 06 — Business Requirement

**Project:** Security Hardening — HQ Campus Layer 2 and Layer 3 Controls
**Series:** Enterprise Network Labs | **Platform:** Cisco CML 2.9

---

## Business Context

The HQ campus network (Projects 01–05) has a fully functional multi-VLAN switched infrastructure, OSPF routing, internet access through NAT, and EtherChannel trunk stability. However, the network has no Layer 2 security controls. Any device physically connected to an access port joins the network and receives a valid DHCP lease. ARP tables can be poisoned by any host. DHCP servers can be spoofed. User VLANs have unrestricted routed access to the management plane. All three HQ devices accept login attempts indefinitely with no lockout.

The network is functionally complete but operationally insecure. This project implements the security hardening layer.

---

## Requirements

### REQ-01 — MAC-Based Port Access Control

Restrict all user-facing and management-facing access switch ports to authorized MAC addresses. Unauthorized devices connecting to any access port must be detected and their traffic blocked. Management port violations must shut the port down immediately. User port violations must drop frames and log the event while keeping the port operational for the legitimate user.

### REQ-02 — DHCP Server Authentication

Prevent rogue DHCP servers from distributing false gateway or DNS addresses to endpoints. All DHCP Offer and Ack messages must be blocked on untrusted (user-facing) access ports. Only DHCP responses arriving on trusted uplink trunk ports are accepted as legitimate. DHCP starvation attacks must be rate-limited on access ports.

### REQ-03 — ARP Validation

Prevent ARP cache poisoning on all user VLANs. All ARP packets arriving on untrusted access ports must be validated against a known MAC-to-IP binding database. ARP packets that do not match a known binding must be dropped. Violations must be visible in inspection statistics and forwarded to syslog.

### REQ-04 — IP Source Validation

Prevent IP address spoofing on access ports. Any frame originating from an IP address that does not match the registered binding for that port and MAC must be dropped before it enters the routed network.

### REQ-05 — Inter-VLAN Traffic Policy with OOB Management Protection

Enforce a per-VLAN routed access policy at HQ-RTR1:
- No user VLAN (100, 200, 300, 400) may initiate traffic to the management VLAN (10.1.99.0/24) without explicit permit
- Guest VLAN (300) has internet-only access — no access to any internal 10.x.x.x subnet
- All management access violations must be logged to syslog
- Server VLAN (400) may respond to user-initiated TCP sessions (established) but must not initiate new connections to user workstations

### REQ-06 — Management Plane Hardening

All HQ network devices (HQ-RTR1, HQ-ASW1, HQ-ASW2) must:
- Block all login access for 120 seconds after 3 failed authentication attempts within 60 seconds
- Automatically disconnect idle VTY (SSH) sessions after 15 minutes of inactivity
- Automatically disconnect idle console sessions after 10 minutes of inactivity
- Disable all unnecessary services: HTTP management, BOOTP server, TCP/UDP small servers
- Disable CDP on any interface connected to an untrusted external party

### REQ-07 — Automated Errdisable Recovery

All HQ access switches must automatically recover err-disabled ports caused by the following conditions after a 5-minute timer, reducing the operational overhead of manual port recovery:
- Port security violations
- DHCP rate-limit violations
- ARP inspection violations
- BPDU guard violations

---

## Acceptance Criteria

| Requirement | Verification Method |
|-------------|---------------------|
| REQ-01 | Connect a rogue device to an access port; confirm violation mode fires (restrict logs / shutdown err-disables) |
| REQ-02 | `show ip dhcp snooping` — uplinks trusted, rate limits on access ports, snooping enabled on all user VLANs |
| REQ-03 | Send a gratuitous ARP from ATTACKER1; confirm `show ip arp inspection statistics` shows drop count; victim ARP table unchanged |
| REQ-04 | Assign spoofed IP to ATTACKER1; confirm 100% packet loss. Restore real IP; confirm 0% packet loss |
| REQ-05 | Ping from VLAN 100/200 to 10.1.99.x → 0% (ACL deny + syslog). Ping between VLAN 100 and 200 → 100% |
| REQ-06 | `show login`, `show running-config \| include exec-timeout`, `show cdp interface Ethernet0/3` |
| REQ-07 | `show errdisable recovery` — 5 causes enabled, timer interval 300 seconds |

---

## Constraints

- **Platform:** IOL-L2 switches in CML 2.9 — DHCP snooping enforcement engine does not activate (hardware ASIC limitation). Configuration is correct and documented; static `ip source binding` entries provide the binding database for Phase 3 and 4.
- **No new nodes:** All security controls are applied to existing HQ devices. Project 06 does not extend the physical topology.
- **Interface naming:** IOL uses Ethernet format (Ethernet0/0 through Ethernet0/3, Ethernet1/0 through Ethernet1/3) — not GigabitEthernet.
- **IOS version:** IOS 17.16 (IOL) — `ip verify source port-security` not supported; use `ip verify source mac-check`.
- **HQ management range:** 10.1.99.0/24 — protected at the routing layer by inter-VLAN ACLs on HQ-RTR1.
