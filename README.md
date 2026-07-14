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
| 03 | [OSPF Dynamic Routing](project-03-ospf-dynamic-routing/) | Single-area OSPF, OSPF auth, IP SLA, BFD, OSPFv3 | ✅ |
| 04 | [Switching Stability](project-04-switching-stability/) | LACP EtherChannel, STP advanced, UDLD, VTP v3, errdisable recovery | ✅ |
| 05 | [Internet + NAT](project-05-internet-nat/) | PAT, static NAT, extended ACLs, object groups | ✅ |
| 06 | [Security Hardening](project-06-security-hardening/) | Port security, DHCP snooping, DAI, IP Source Guard | ✅ |
| 07 | [ASAv Firewall](project-07-asav-firewall/) | ASA security levels, stateful inspection, DMZ, packet-tracer | ✅ |
| 08 | [Site-to-Site VPN](project-08-site-to-site-vpn/) | GRE/IPsec, IKEv2, tunnel OSPF, DPD, PFS | ✅ |
| 09 | [Monitoring and Visibility](project-09-monitoring-visibility/) | Syslog, SNMPv3, NetFlow, NTP auth, EEM, config archive, CDP/LLDP | ✅ |
| 10 | [AAA + Access Control](project-10-aaa-access-control/) | TACACS+, privilege levels, parser views, AAA accounting, AAA failover | ✅ |
| 11 | [QoS Traffic Management](project-11-qos-traffic-management/) | MQC, DSCP marking, NBAR, HQoS shaping/queuing, voice VLAN, ACL classification | ✅ |
| 12 | [Disaster Recovery](project-12-disaster-recovery/) | 90-min timed rebuild, OSPF/AAA/QoS/VPN restore, break/fix OSPF area mismatch | ✅ |
| 13 | [Network Automation](project-13-network-automation/) | Python/Netmiko, Ansible, automated deployment | ✅ |

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

## Future Projects (CCNP Level)

Labs designed and ready to build — held back until after CCNA certification.
These go beyond the 13-project CCNA series into CCNP ENCOR territory.

| Project | Key Technologies | Level | Prereq |
|---------|-----------------|-------|--------|
| [OSPF Multi-Area](future-ospf-multi-area/) | Multi-area OSPF, Stub/Totally Stubby/NSSA, dual ABRs, route summarization, Type 7→5 LSA translation, MD5 auth | CCNP ENCOR | Pass CCNA first |

---

## Troubleshooting Log

The most important file in this repo: [TROUBLESHOOTING-LOG.md](TROUBLESHOOTING-LOG.md)

Every problem encountered during every project — what broke, what I checked, what
the actual cause was, and what I learned. This is where the real engineering is.

## Related Families

| Family | Repo | Connection |
|--------|------|------------|
| CCNA Physical Expansion | [Homelab_CCNA](https://github.com/vushueh/Homelab_CCNA) | Expands these CML labs onto physical gear — its P01 bridges CML to the homelab via CML-EDGE1 |
| Route10 Network Core | [homelab-route10-network-core](https://github.com/vushueh/homelab-route10-network-core) | Owns the CML transit routing (VLAN 160, 192.168.160.0/30 → CML-EDGE1) |
| Windows Server Labs | [windows-server-business-admin-labs](https://github.com/vushueh/windows-server-business-admin-labs) | Future P13 plans CML router authentication through Windows NPS/RADIUS |
| FreePBX VoIP Labs | [freepbx-family-voip-labs](https://github.com/vushueh/freepbx-family-voip-labs) | Future F05 plans safe VoIP automation/observability work on the same CML controller |
| **Master Hub** | [homelab-management](https://github.com/vushueh/homelab-management) | Navigation hub — see [cross-repo map](https://github.com/vushueh/homelab-management/blob/main/docs/CROSS-REPO-MAP.md) |

## Master Program Placement

This completed repo remains a reference source for network and capstone
topologies. It has no active queue item and is not reopened by the master
program. The forced queue in `../docs/homelab-goals.yaml` may link to its
evidence for N/C-track design, but changes require an explicit reopening
decision and normal closeout rules.

### Master Queue Status

| Queue assignment | Clickable project list | Status |
|---|---|---|
| None — reference repository | [Projects 01-13](#the-series) | ✅ All 13 projects complete; no open master-queue project |
