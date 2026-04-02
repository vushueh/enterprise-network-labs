# Enterprise Network Labs

A 12-project progressive series building a complete enterprise network from scratch
in Cisco CML 2.9. Each project adds one layer of complexity — by the end, the network
includes multi-area OSPF, NAT, ASAv firewall, IPsec VPN, TACACS+/Radius AAA, SNMP/Syslog/NetFlow
monitoring, QoS traffic management, and full disaster recovery testing.

## About Me

I'm Leonel — active duty Air Force (logistics/materiel management) transitioning into
network engineering and cybersecurity. These projects are my hands-on portfolio built
alongside CCNA certification preparation. Every project solves a real engineering problem,
not just a textbook exercise.

## The Series

| # | Project | Key Technologies | Status |
|---|---------|-----------------|--------|
| 01 | [Campus Foundation](project-01-campus-foundation/) | VLANs, trunking, inter-VLAN routing, STP, SSH | 🔄 |
| 02 | Multi-Site + DHCP | DHCP relay, Dnsmasq, static routing, IPv6 | ⬜ |
| 03 | OSPF Dynamic Routing | OSPF multi-area, IP SLA, OSPFv3 | ⬜ |
| 04 | Switching Stability | LACP EtherChannel, STP advanced, guards | ⬜ |
| 05 | Internet + NAT | PAT, static NAT, extended ACLs | ⬜ |
| 06 | Security Hardening | Port security, DHCP snooping, DAI, ACL policy | ⬜ |
| 07 | ASAv Firewall | ASA zones, stateful inspection, DMZ | ⬜ |
| 08 | Site-to-Site VPN | GRE/IPsec, IKEv2, tunnel OSPF | ⬜ |
| 09 | Monitoring | Syslog, SNMPv3, NetFlow, NTP | ⬜ |
| 10 | AAA + Access Control | TACACS+, Radius, 802.1X | ⬜ |
| 11 | QoS | MQC, DSCP marking, priority queuing | ⬜ |
| 12 | Disaster Recovery | Timed rebuild, triage, documentation test | ⬜ |

## Lab Platform

- **CML 2.9** (licensed) — IOL routers, IOL-L2 switches, ASAv firewall
- **Supporting nodes:** Dnsmasq, Radius, TacPlus, Syslog, Nginx, ThousandEyes
- **16+ simultaneous nodes**
- **All configs and verification outputs documented**

## Troubleshooting Log

The most important file in this repo: [TROUBLESHOOTING-LOG.md](TROUBLESHOOTING-LOG.md)

Every problem encountered during every project — what broke, what I checked, what
the actual cause was, and what I learned. This is where the real engineering is.
