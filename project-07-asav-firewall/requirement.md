# Project 07 — Business Requirement

## Requirement

The network security team has determined that using a router as the sole internet security
boundary is insufficient. The following requirements must be met:

1. A dedicated stateful firewall must be inserted between the campus network and the ISP.
2. The public-facing web server must be isolated in a DMZ — it must not share a segment
   with internal user VLANs.
3. NAT must be performed by the firewall, not the router.
4. All traffic from the untrusted internet zone to the internal network must be denied
   by default. Exceptions require explicit policy.
5. HTTP, DNS, and ICMP traffic must be subject to application-layer inspection.
6. All firewall deny events must be logged to the central syslog server.

## Platform

ASAv (Adaptive Security Appliance virtual) — Cisco's dedicated firewall platform.
Runs stateful inspection, application-layer inspection, zone-based ACL policy,
NAT, and VPN in a dedicated security context separate from the routing layer.

## Security Level Model

| Zone | Interface | Security Level | Trust |
|------|-----------|---------------|-------|
| Inside | GigabitEthernet0/0 | 100 | Fully trusted campus network |
| DMZ | GigabitEthernet0/2 | 50 | Semi-trusted — public-facing servers |
| Outside | GigabitEthernet0/1 | 0 | Untrusted internet |

Traffic flows freely from higher to lower security levels (inside → outside, inside → DMZ).
Traffic from lower to higher requires an explicit ACL permit (outside → DMZ, outside → inside).
Traffic between equal security levels is denied by default.
