# Enterprise Network Labs

A 13-project progressive series building a complete enterprise network from scratch
in Cisco CML 2.9. Each project adds one layer of complexity — by the end, the network
includes multi-area OSPF, NAT, ASAv firewall, IPsec VPN, TACACS+/Radius AAA, SNMP/Syslog/NetFlow
monitoring, QoS traffic management, full disaster recovery testing, and network automation
with Python/Netmiko and Ansible.

## About Me

I'm Leonel — active duty Air Force (logistics/materiel management) transitioning into
network engineering and cybersecurity. These projects are my hands-on portfolio built
alongside CCNA certification preparation. Every project solves a real engineering problem,
not just a textbook exercise.

## The Series

Each project follows the **Build → Verify → Break → Fix** method — every lab includes a deliberate fault injection exercise.

| # | Project | Key Technologies | Status |
|---|---------|-----------------|--------|
| 01 | [Campus Foundation](project-01-campus-foundation/) | VLANs, trunking, inter-VLAN routing, STP, SSH, CDP | ✅ |
| 02 | [Multi-Site + DHCP](project-02-multi-site-dhcp/) | DHCP relay, Dnsmasq, static routing, IPv6 | ✅ |
| 03 | [OSPF Multi-Area](project-03-ospf-multi-area/) | Multi-area OSPF, Stub/NSSA/Totally Stubby, dual ABRs, summarization, MD5 auth | 🔜 |
| 04 | Switching Stability | LACP EtherChannel, STP advanced, VTP v3, errdisable | ⬜ |
| 05 | Internet + NAT | PAT, static NAT, extended ACLs, object groups | ⬜ |
| 06 | Security Hardening | Port security, DHCP snooping, DAI, IP Source Guard | ⬜ |
| 07 | ASAv Firewall | ASA security levels, stateful inspection, DMZ, packet-tracer | ⬜ |
| 08 | Site-to-Site VPN | GRE/IPsec, IKEv2, tunnel OSPF | ⬜ |
| 09 | Monitoring | Syslog, SNMPv3, NetFlow, NTP auth, EEM, config archive | ⬜ |
| 10 | AAA + Access Control | TACACS+, Radius, 802.1X, privilege levels, parser views | ⬜ |
| 11 | QoS | MQC, DSCP marking, NBAR, priority queuing, voice VLAN | ⬜ |
| 12 | Disaster Recovery | 90-min timed rebuild, triage, documentation test | ⬜ |
| 13 | Network Automation | Python/Netmiko, Ansible, automated deployment | ⬜ |

## Lab Platform

- **CML 2.9** (licensed) — IOL routers, IOL-L2 switches, ASAv firewall
- **Supporting nodes:** Dnsmasq, Radius, TacPlus, Syslog, Nginx, ThousandEyes
- **16+ simultaneous nodes**
- **Interface naming:** IOL/IOL-L2 use `Ethernet0/x` and `Ethernet1/x` format
- **All configs and verification outputs documented**

## Methodology

Every project follows the **Build → Verify → Break → Fix** cycle:
1. Configure the technology step by step
2. Verify with show commands
3. Introduce a deliberate fault
4. Diagnose and fix using show commands only
5. Document in TROUBLESHOOTING-LOG.md

## Troubleshooting Log

The most important file in this repo: [TROUBLESHOOTING-LOG.md](TROUBLESHOOTING-LOG.md)

Every problem encountered during every project — what broke, what I checked, what
the actual cause was, and what I learned. This is where the real engineering is.
