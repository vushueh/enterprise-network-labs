# Projects 02-13 — Reference Index

This file contains the detailed breakdown for Projects 02 through 13.
Full step-by-step configs (like Project 01) will be generated when Leonel
says "let's start Project X" — Claude reads this file and expands each
phase into complete copy-paste-ready configurations with inline comments,
interface descriptions, CDP verification, and break/fix challenges.

## VLAN Mapping Reference (applies to ALL projects)

| VLAN | Name | HQ Subnet | Branch Subnet |
|------|------|-----------|---------------|
| 100 | Engineering | 10.1.100.0/24 | 10.2.100.0/24 |
| 200 | Sales | 10.1.200.0/24 | 10.2.200.0/24 |
| 300 | Guest | 10.1.44.0/24 | 10.2.44.0/24 |
| 400 | Servers | 10.1.40.0/24 | — |
| 500 | Voice | 10.1.50.0/24 | 10.2.50.0/24 |
| 999 | Management | 10.1.99.0/24 | 10.2.99.0/24 |
| 1000 | Native | — (no IP) | — (no IP) |

## Interface Naming Convention

All IOL and IOL-L2 devices use `Ethernet` format:
- Slot 0: Ethernet0/0, Ethernet0/1, Ethernet0/2, Ethernet0/3
- Slot 1: Ethernet1/0, Ethernet1/1, Ethernet1/2, Ethernet1/3

**Every interface gets a description.** Format:
- Trunk uplinks: `description TRUNK-TO-[REMOTE-HOSTNAME]-E[x/x]`
- WAN links: `description WAN-TO-[REMOTE-HOSTNAME]-E[x/x]`
- Access ports: `description ACCESS-[DEVICE-NAME]-VLAN[xxx]`
- Server ports: `description SERVER-[SERVER-NAME]-VLAN[xxx]`
- Subinterfaces: `description GATEWAY-VLAN[xxx]-[NAME]`

## Operational Standards (Apply to EVERY Project)

Before configuring a new or modified topology:
1. Boot all new devices, set hostnames
2. Run `show cdp neighbors` on all devices to verify cabling
3. If cabling doesn't match design — fix BEFORE configuring
4. Add interface descriptions as you configure each interface
5. After all phases: run the break/fix challenge
6. Update decision-log.md with design rationale
7. Update TROUBLESHOOTING-LOG.md even if the build was clean

---

# Project 02 — Multi-Site Expansion + DHCP Architecture

## Topology (14 nodes — adds 6 to Project 01)

| New Node | Image | Hostname | Role |
|----------|-------|----------|------|
| IOL | IOL | BR-RTR1 | Branch router — WAN link to HQ |
| IOL-L2 | IOL-L2 | BR-DSW1 | Branch distribution switch |
| IOL-L2 | IOL-L2 | BR-ASW1 | Branch access switch |
| Dnsmasq | Dnsmasq | HQ-DHCP-DNS | Centralized DHCP and DNS server at HQ |
| Alpine | Alpine | PC-BR1 | Branch workstation (VLAN 100) |
| Alpine | Alpine | PC-BR2 | Branch workstation (VLAN 200) |

### New Connections

| Side A | Side B | Purpose |
|--------|--------|---------|
| HQ-RTR1 Ethernet0/1 | BR-RTR1 Ethernet0/1 | WAN link (10.0.0.0/30) |
| BR-RTR1 Ethernet0/0 | BR-DSW1 Ethernet0/0 | Router-on-a-stick trunk |
| BR-DSW1 Ethernet0/1 | BR-ASW1 Ethernet0/0 | Distribution to access trunk |
| BR-ASW1 Ethernet1/0 | PC-BR1 eth0 | Access port VLAN 100 |
| BR-ASW1 Ethernet1/1 | PC-BR2 eth0 | Access port VLAN 200 |
| HQ-ASW1 Ethernet1/2 | HQ-DHCP-DNS eth0 | Server port VLAN 999 |

## Phases

1. **Branch site base** — Build BR-RTR1, BR-DSW1, BR-ASW1 with matching VLAN scheme (100/200/300/999/1000). Branch uses 10.2.x.0/24 ranges. Router-on-a-stick on BR-RTR1. Interface descriptions on all links. CDP verification after cabling.
2. **WAN connectivity** — Point-to-point link (10.0.0.0/30), descriptions on WAN interfaces (`description WAN-TO-BR-RTR1-E0/1`), static routes both directions, bandwidth/delay statements on WAN interfaces (prepares for OSPF cost in Project 03). Verify end-to-end cross-site ping.
3. **Centralized DHCP with Dnsmasq** — Configure Dnsmasq with pools for ALL VLANs at BOTH sites. Configure `ip helper-address` on both routers. DHCP relay crosses WAN. After DHCP assigns addresses, verify with `show ip arp` on routers to understand ARP-to-VLAN relationships.
4. **IPv6 dual-stack introduction** — Enable `ipv6 unicast-routing`, manual /126 on WAN, SLAAC on VLAN 100, IPv6 static routes between sites.
5. **DNS end-to-end testing** — Don't just ping IPs. From endpoints, test DNS resolution using `nslookup` to verify Dnsmasq works end to end through the relay chain.

## Break/Fix Challenge
**The Fault:** Configure the wrong `ip helper-address` on BR-RTR1 (point it to 10.1.99.99 instead of 10.1.99.50).
**Symptom:** Branch PCs don't get DHCP addresses.
**Diagnosis path:** `show ip dhcp relay statistics` (if available), `debug ip dhcp server packet` on router, check `show running-config | include helper`.
**Fix:** Correct the helper-address to 10.1.99.50.

## CCNA: DHCP (4.0), relay/helper (4.0), DNS (4.0), static routing (3.0), IPv6 addressing (1.0), IPv6 static routing (3.0)
## Beyond CCNA: Centralized Dnsmasq DHCP/DNS, relay across WAN, dual-stack as WAN overlay, multi-site subnet planning, ARP table analysis, bandwidth/delay for OSPF prep

## Decision Log Entries
- Why centralized DHCP at HQ instead of per-site DHCP servers
- Why relay across WAN instead of local DHCP
- Why bandwidth/delay statements on WAN interfaces now
- Why SLAAC for IPv6 instead of DHCPv6

## STAR
- **S:** Single-site campus had no multi-site connectivity, no DHCP, no IPv6.
- **T:** Expand to two sites with centralized DHCP/DNS and IPv6 dual-stack.
- **A:** Built branch site with matching VLAN scheme, WAN connectivity with static routes, Dnsmasq with cross-site DHCP relay, and IPv6 SLAAC. Used CDP to verify branch cabling, tested DNS resolution end-to-end, diagnosed a relay misconfiguration.
- **R:** Can design multi-site DHCP architecture with centralized services, relay agents, and IPv6 dual-stack.

---

# Project 03 — Dynamic Routing with OSPF

## Topology (15 nodes — adds 1)

| New Node | Image | Hostname | Role |
|----------|-------|----------|------|
| IOL | IOL | WAN-RTR1 | ISP/WAN router — second path between sites |

### New Connections

| Side A | Side B | Purpose |
|--------|--------|---------|
| HQ-RTR1 Ethernet0/2 | WAN-RTR1 Ethernet0/0 | WAN path 2 (10.0.0.4/30) |
| BR-RTR1 Ethernet0/2 | WAN-RTR1 Ethernet0/1 | WAN path 2 (10.0.0.8/30) |

Original direct link (HQ-RTR1 E0/1 ↔ BR-RTR1 E0/1) becomes backup path.

## Phases

1. **Single-area OSPF migration** — Remove ALL static routes. OSPF Area 0 on all routers. `passive-interface default` then `no passive-interface` on WAN-facing links only. Verify neighbor adjacency with `show ip ospf neighbor`. Descriptions on WAN interfaces to WAN-RTR1.
2. **Multi-area OSPF design** — Area 0 backbone (WAN links), Area 1 (HQ campus VLANs), Area 2 (Branch campus VLANs). ABR config on HQ-RTR1 and BR-RTR1. Route summarization at ABRs.
3. **OSPF authentication** — MD5 authentication on ALL WAN-facing interfaces. Never run unauthenticated OSPF on a link that crosses outside your building. `ip ospf message-digest-key 1 md5 [key]` and `ip ospf authentication message-digest` under the interface.
4. **Redundant WAN with cost manipulation** — Add WAN-RTR1, tune OSPF costs using the bandwidth/delay values set in Project 02, verify path selection with traceroute. Enable `log-adjacency-changes detail` on all routers so adjacency events hit syslog.
5. **Link failure and convergence testing** — Shut primary WAN, verify failover, time convergence, bring back up. Use `show ip ospf statistics` to check SPF run count.
6. **BFD for sub-second failover** — Configure BFD (Bidirectional Forwarding Detection) on WAN interfaces and bind to OSPF. BFD detects link failure in milliseconds instead of waiting for OSPF dead timer (40 seconds). `bfd interval 300 min_rx 300 multiplier 3` on interfaces, `ip ospf bfd` under OSPF process.
7. **IP SLA + OSPF tracking** — ICMP echo probe, tracked object, floating static as belt-and-suspenders backup.
8. **OSPFv3 for IPv6** — Replace IPv6 static routes with OSPFv3.

## Break/Fix Challenge
**The Fault:** Set `passive-interface Ethernet0/1` on HQ-RTR1 (the WAN link to BR-RTR1).
**Symptom:** HQ-RTR1 and BR-RTR1 lose OSPF adjacency. Branch site becomes unreachable from HQ campus VLANs.
**Diagnosis path:** `show ip ospf neighbor` (missing neighbor), `show ip ospf interface Ethernet0/1` (shows passive), `show ip protocols` (shows passive interfaces list).
**Fix:** `no passive-interface Ethernet0/1` under the OSPF process.

## CCNA: OSPFv2 single-area (3.0), cost/path selection (3.0), route types O/O IA (3.0), OSPFv3 (3.0)
## Beyond CCNA: Multi-area OSPF with ABR, inter-area summarization, OSPF MD5 authentication, BFD, IP SLA, convergence testing, floating statics, log-adjacency-changes

## Decision Log Entries
- Why multi-area instead of single-area (scalability, summarization)
- Why Area 0 on WAN links and separate areas for campus
- Why MD5 auth on WAN interfaces
- Why BFD in addition to OSPF timers
- Why passive-interface default strategy

## STAR
- **S:** Two-site network relied on static routes with no automatic failover.
- **T:** Migrate to OSPF multi-area with redundancy, authentication, BFD, and IP SLA tracking.
- **A:** Built multi-area OSPF, added MD5 authentication on WAN links, configured BFD for sub-second failover, tested failure/recovery, diagnosed a passive-interface misconfiguration.
- **R:** Can design multi-area OSPF with redundancy, authentication, cost-based traffic engineering, BFD, and intelligent failover.

---

# Project 04 — Switching Layer Stability

## Topology (15 nodes — no new devices)

Works entirely on existing switches. Focus is L2 optimization.

## Phases

1. **EtherChannel between distribution switches** — LACP Port-Channel between HQ-DSW1 ↔ HQ-DSW2 (if additional links available, otherwise configure LACP on the existing inter-distribution trunk). Configure on port-channel interface. Intentionally break with PAgP mismatch, fix, document. Add descriptions to port-channel interface.
2. **Advanced STP control** — Add redundant link creating loop. Manipulate port priority. Configure root guard on distribution downlink ports (toward access switches), loop guard on non-designated ports. Configure `spanning-tree pathcost method long` for 10G-aware cost values.
3. **UDLD and errdisable recovery** — Enable UDLD (UniDirectional Link Detection) on all inter-switch links to detect one-way cable faults. Configure errdisable recovery for: bpduguard, udld, security-violation, psecure-violation, dhcp-rate-limit. Set recovery interval to 300 seconds. This prevents ports from staying permanently shutdown after a transient fault.
4. **VTP Version 3 — Learning Module** — This is NOT the default design for this lab series. It is a learning exercise. Configure HQ-DSW1 as VTP v3 primary server, other switches as VTP clients. Create a test VLAN (VLAN 600 "VTP-Test") on the server and verify it propagates. Discuss: revision number risks in VTPv1/v2, how VTPv3 primary server concept prevents accidental wipes, why many production environments use VTP transparent mode or disable VTP entirely. After learning, return to explicit VLAN control (VTP transparent mode on all switches).
5. **MAC address table analysis** — Use `show mac address-table` as a troubleshooting tool. Trace where a specific MAC (PC-ENG1) appears across all switches to understand the forwarding path. Practice `show mac address-table address [mac]` and `show mac address-table vlan 100`.
6. **Access port protection** — Storm control on access ports. BPDU Filter on WAN uplinks (router-facing ports). Test rogue switch with Unmanaged Switch node triggering BPDU Guard.
7. **L2 troubleshooting exercise** — Introduce 3 simultaneous faults: wrong LACP mode, native VLAN mismatch on VLAN 1000, STP root hijack (lower priority on an access switch). Diagnose and fix all three.

## Break/Fix Challenge (this IS Phase 7)
The L2 troubleshooting exercise is the break/fix for this project — 3 simultaneous faults.
This project already has the strongest break/fix component of any project in the series.

## CCNA: EtherChannel LACP (2.0), STP root election (2.0), Rapid-PVST+ (2.0), PortFast/BPDU Guard (2.0), VTP concepts (2.0)
## Beyond CCNA: Root guard, loop guard, storm control, BPDU Filter, UDLD, errdisable recovery, VTP v3, MAC table forensics, multi-fault troubleshooting, pathcost method long

## Decision Log Entries
- Why LACP over PAgP (standards-based vs Cisco proprietary)
- Why VTP transparent mode in production (revision number risk)
- Why errdisable recovery with 300-second interval
- Why root guard on downlinks vs uplinks
- Why pathcost method long

## STAR
- **S:** STP was working by accident. No EtherChannel, no protection against rogue switches, no UDLD, no automated recovery.
- **T:** Take full control of L2 — EtherChannel, STP hardening, UDLD, errdisable recovery, VTP v3 learning, deliberate fault testing.
- **A:** Built LACP EtherChannels, hardened STP with root/loop guard, configured UDLD and errdisable recovery, learned VTP v3 then reverted to transparent mode, introduced and diagnosed three simultaneous faults.
- **R:** Can design stable L2 domain, protect against rogue devices and cable faults, understand VTP risks, troubleshoot multi-fault scenarios.

---

# Project 05 — Internet Access and NAT

## Topology (17 nodes — adds 2)

| New Node | Image | Hostname | Role |
|----------|-------|----------|------|
| IOL | IOL | ISP-RTR1 | Simulated ISP router |
| Nginx | Nginx | EXT-WEB1 | External web server (simulated internet) |

Also adds: Nginx node HQ-SRV1 on Server VLAN 400.

### New Connections

| Side A | Side B | Purpose |
|--------|--------|---------|
| HQ-RTR1 Ethernet0/3 | ISP-RTR1 Ethernet0/0 | ISP handoff (203.0.113.0/30 initially, moves to firewall in P07) |
| ISP-RTR1 Ethernet0/1 | EXT-WEB1 eth0 | Simulated internet |
| HQ-DSW1 Ethernet1/0 | HQ-SRV1 eth0 | Server VLAN 400 access port |

## Phases

1. **ISP simulation** — ISP-RTR1 with public IP range 203.0.113.0/24. Default route on HQ-RTR1. Redistribute into OSPF with `default-information originate`. Descriptions on all new interfaces.
2. **PAT (NAT overload)** — Extended ACL defining source subnets. Exclude Management VLAN 999. PAT on outside interface. Test with `curl` from Alpine (not just ping — prove full HTTP works).
3. **Static NAT for internal server** — HQ-SRV1 on VLAN 400 mapped to public IP 203.0.113.10. Verify inbound access from EXT-WEB1. Use `show ip nat translations` and `show ip nat statistics` as core verification tools.
4. **Object groups for ACLs** — Refactor the NAT ACL using object groups. Group source networks into named objects instead of individual ACL lines. This is how production ACLs are managed — not 15 individual permit lines.
5. **Guest VLAN isolation with ACLs** — Extended ACL: permit Guest (VLAN 300) → internet, deny Guest → internal. Test and verify hit counters with `show access-lists`.
6. **ip tcp adjust-mss** — Configure `ip tcp adjust-mss 1452` on the ISP-facing interface to prevent MTU/fragmentation issues with NAT. Every production NAT router has this.
7. **Branch internet via HQ** — OSPF default route already propagated. Verify Branch → internet path. Test `curl` from branch Alpine to EXT-WEB1.

## Break/Fix Challenge
**The Fault:** Write the NAT ACL with a wrong subnet (permit 10.1.100.0 0.0.0.255 instead of the correct inside source — or miss a subnet entirely).
**Symptom:** One VLAN can reach the internet, another cannot.
**Diagnosis path:** `show ip nat translations` (missing translations for broken VLAN), `show ip nat statistics` (check miss count), `show access-lists` (check hit counts per line).
**Fix:** Correct the ACL to include all intended source subnets.

## CCNA: NAT/PAT (4.0), static NAT (4.0), extended ACLs (5.0), default route redistribution (3.0)
## Beyond CCNA: Object groups for ACLs, ip tcp adjust-mss, Guest isolation ACL, multi-site NAT architecture, NAT translation table analysis, curl testing (not just ping)

## Decision Log Entries
- Why PAT instead of dynamic NAT pool
- Why exclude VLAN 999 from NAT
- Why object groups over individual ACL lines
- Why ip tcp adjust-mss on NAT interfaces

## STAR
- **S:** No internet access, no NAT, never written an ACL.
- **T:** Design internet access with PAT, static NAT, object-group ACLs, and guest isolation.
- **A:** Built ISP simulation, PAT + static NAT, OSPF default redistribution, refactored ACLs with object groups, configured ip tcp adjust-mss, guest isolation ACL, diagnosed a NAT ACL error.
- **R:** Can design NAT for multi-site, write and verify ACLs using object groups, troubleshoot NAT translation failures.

---

# Project 06 — Security Hardening

## Topology (18 nodes — adds 1)

| New Node | Image | Hostname | Role |
|----------|-------|----------|------|
| Net-Tools | Net-Tools | ATTACKER1 | Rogue device for testing security controls |

### New Connections

| Side A | Side B | Purpose |
|--------|--------|---------|
| HQ-ASW2 Ethernet1/1 | ATTACKER1 eth0 | Rogue device on access port |

## Phases

1. **Port security** — Sticky MAC, max 2 addresses, violation modes (restrict then shutdown test). ATTACKER1 triggers violation.
2. **DHCP snooping** — Global enable, trust uplinks (trunk ports), rate limit access ports (15 pps). Test rogue DHCP from ATTACKER1.
3. **Dynamic ARP Inspection** — DAI on VLANs 100/200/300, trust uplinks. Test ARP spoof from ATTACKER1.
4. **IP Source Guard** — Builds on top of DHCP snooping to prevent IP spoofing at the access layer. Any packet with a source IP that doesn't match the DHCP binding table gets dropped.
5. **Inter-VLAN ACL policy with OOB management protection** — Full policy matrix: Eng(100)↔Sales(200) permitted, Guest(300)→internet only, Server(400)→respond only (established), Management(999)→everything. **OOB enhancement:** Strict ACLs that block user VLANs from initiating connections to VLAN 999. Log any attempts to cross into management — this simulates a true out-of-band architecture. Test EVERY rule.
6. **Management plane protection** — Comprehensive VTY ACL (extend from Project 01), disable unused services, login block-for (rate limit failed logins), banners. CoPP awareness: discuss Control Plane Policing concept and what it protects against (SSH brute force, SNMP floods hitting CPU).
7. **Errdisable integration** — Verify errdisable recovery from Project 04 is working for security violation triggers (port security, DHCP rate limit). Confirm ports auto-recover after the configured interval.

## Break/Fix Challenge
**The Fault:** Set the DHCP snooping trust on an ACCESS port instead of the trunk uplink.
**Symptom:** DHCP requests from legitimate PCs on that switch are being dropped.
**Diagnosis path:** `show ip dhcp snooping` (check trust assignments), `show ip dhcp snooping statistics` (check drop counters).
**Fix:** Move trust to the correct uplink interface, remove trust from the access port.

## CCNA: Port security (5.0), DHCP snooping (5.0), DAI (5.0), extended ACLs (5.0), device hardening (5.0)
## Beyond CCNA: IP Source Guard, complete ACL policy matrix, ACL `established` keyword, OOB management simulation, CoPP awareness, security testing with attacker node, layered L2/L3 defense, errdisable integration

## Decision Log Entries
- Why sticky MAC instead of static MAC
- Why trust uplinks only for DHCP snooping
- Why IP Source Guard on top of DHCP snooping
- Why logging management VLAN access attempts (OOB simulation)
- Why CoPP matters even if not fully implemented

## STAR
- **S:** Network had no L2 security, no access control beyond VTY ACLs, and management VLAN was reachable from any user VLAN.
- **T:** Build layered security — L2 protections, inter-VLAN ACL policy, OOB management simulation, and active attack testing.
- **A:** Configured port security, DHCP snooping, DAI, IP Source Guard, full ACL policy matrix with OOB management protection, tested every control against ATTACKER1, diagnosed a misplaced DHCP snooping trust.
- **R:** Can design layered security, write complex ACL policies, enforce OOB management principles, test controls by simulating attacks.

---

# Project 07 — Perimeter Firewall with ASAv

## Topology (19 nodes — adds 1, reorganizes links)

| New Node | Image | Hostname | Role |
|----------|-------|----------|------|
| ASAv | ASAv | HQ-FW1 | Perimeter firewall between HQ and ISP |

Reorganized: HQ-RTR1 inside → HQ-FW1 inside → HQ-FW1 outside → ISP-RTR1. NAT moves from HQ-RTR1 to HQ-FW1.

### Connection Changes

| Side A | Side B | Purpose |
|--------|--------|---------|
| HQ-RTR1 Ethernet0/3 | HQ-FW1 Gi0/0 (inside) | Router to firewall inside (10.0.0.12/30) |
| HQ-FW1 Gi0/1 (outside) | ISP-RTR1 Ethernet0/0 | Firewall to ISP (203.0.113.0/30) |
| HQ-FW1 Gi0/2 (DMZ) | HQ-SRV1 eth0 | DMZ segment (move server here) |

Note: ASAv uses GigabitEthernet interfaces, not Ethernet. This is the one exception.

## Phases

1. **ASAv basic setup** — Interfaces (inside/outside/DMZ), security levels (100/0/50), nameif, static routes. Descriptions on all ASA interfaces.
2. **Migrate NAT to firewall** — Remove NAT from HQ-RTR1. PAT + static NAT on HQ-FW1. Verify all previous internet access still works.
3. **Access control policies** — ASA ACL syntax (`access-list` + `access-group`), outside→inside deny, outside→DMZ permit HTTP, inspection policies (`inspect http`, `inspect dns`, `inspect icmp`).
4. **Packet-tracer — the #1 ASA troubleshooting tool** — `packet-tracer input inside tcp 10.1.100.10 12345 203.0.113.100 80` traces a packet through EVERY policy on the ASA. This is the single most useful command on the platform. Practice it for allowed flows, denied flows, and NAT translations.
5. **Firewall logging** — Syslog from ASAv to HQ-SYSLOG, logging levels, ACL hit logging with `log` keyword. Enable basic `threat-detection statistics` to see top talkers.
6. **show conn — understanding stateful inspection** — Inspect the connection table with `show conn` and `show conn detail`. Understand how the ASA tracks state, what "established" means at the firewall level, and how to read connection flags.

## Break/Fix Challenge
**The Fault:** Set the inside interface security level to 0 instead of 100.
**Symptom:** All traffic from inside to outside is denied (security levels reversed — traffic flows from higher to lower by default).
**Diagnosis path:** `packet-tracer input inside ...` (shows implicit deny), `show interface ip brief` (check security levels), `show nameif`.
**Fix:** Correct the security level: `security-level 100` on inside interface.

## CCNA: Firewall concepts (5.0), NAT on firewall (4.0), ACLs different platform (5.0), syslog (4.0)
## Beyond CCNA: ASA CLI/architecture, stateful inspection, DMZ design, packet-tracer troubleshooting, application-layer inspection, threat-detection statistics, connection table analysis, NAT migration

## Decision Log Entries
- Why insert firewall between router and ISP (not replace router)
- Why security level 100/50/0 assignment
- Why DMZ at security level 50
- Why application inspection for HTTP/DNS

## STAR
- **S:** Internet security relied on stateless router ACLs. No DMZ, no application inspection.
- **T:** Deploy ASAv as dedicated perimeter firewall with stateful inspection and DMZ.
- **A:** Inserted ASAv, migrated NAT, built zone-based ACL policies, enabled HTTP/DNS inspection, mastered packet-tracer troubleshooting, analyzed stateful connection table, diagnosed a security level misconfiguration.
- **R:** Can deploy and configure ASA firewall, design DMZ architecture, migrate NAT between platforms, troubleshoot with packet-tracer.

---

# Project 08 — Site-to-Site VPN

## Topology (19 nodes — no new, tunnel overlay added)

Tunnel: HQ-RTR1 ↔ BR-RTR1 GRE over IPsec (Tunnel0). OSPF adjacency moves to tunnel.

## Phases

1. **GRE tunnel without encryption** — Tunnel0 interfaces (10.0.100.0/30), OSPF over tunnel. Descriptions on tunnel interfaces. Verify with `show interface Tunnel0`.
2. **Add IPsec encryption** — IKEv2 keyring, proposal (AES-256, SHA-256, DH14), IPsec profile, apply to tunnel. Verify with `show crypto session` (the one-liner for VPN health checks) and `show crypto ikev2 sa`.
3. **Crypto debugging methodology** — Practice structured approach to `debug crypto ikev2` output. Know what each phase means (IKE_SA_INIT, IKE_AUTH). Understand anti-replay window and what causes anti-replay drops in production.
4. **VPN failover testing** — Shut tunnel source, verify OSPF failover to backup, bring back, verify reconvergence. Use BFD (from Project 03) to accelerate tunnel failure detection.

## Break/Fix Challenge
**The Fault:** Configure a mismatched IKEv2 proposal — AES-128 on one side, AES-256 on the other.
**Symptom:** Tunnel interface is UP but IPsec SA never forms. Traffic is unencrypted or blackholed.
**Diagnosis path:** `show crypto session` (shows DOWN), `show crypto ikev2 sa` (no SA), `debug crypto ikev2` (shows proposal mismatch).
**Fix:** Match the proposal on both sides.

## CCNA: VPN concepts (5.0), IPsec fundamentals (5.0), encryption concepts (5.0)
## Beyond CCNA: Full IKEv2 + IPsec implementation, GRE over IPsec, OSPF over encrypted tunnels, structured crypto debugging, anti-replay, VPN failover testing, show crypto session as primary tool

## Decision Log Entries
- Why GRE over IPsec (vs pure IPsec)
- Why IKEv2 over IKEv1
- Why AES-256/SHA-256/DH14 parameters
- Why OSPF over tunnel instead of static routes

## STAR
- **S:** Inter-site WAN traffic completely unencrypted.
- **T:** Encrypt WAN with GRE over IPsec/IKEv2, maintain OSPF over tunnel, test failover.
- **A:** Built GRE tunnel, layered IKEv2/IPsec, migrated OSPF to tunnel, practiced structured crypto debugging, tested failure/recovery, diagnosed an IKEv2 proposal mismatch.
- **R:** Can design and implement encrypted site-to-site VPN with dynamic routing over tunnels and troubleshoot crypto failures methodically.

---

# Project 09 — Monitoring and Visibility

## Topology (20 nodes — activates Syslog node fully)

Syslog node: HQ-SYSLOG at 10.1.99.51.

## Phases

1. **Syslog infrastructure** — All devices send syslog to HQ-SYSLOG. Tiered logging levels (informational for access switches, warnings for core). Timestamps + sequence numbers. Use `show logging | include` to filter specific events.
2. **SNMP monitoring** — SNMPv2c on all devices with community strings, traps (link-down/up, auth failure). Then SNMPv3 on core routers (authPriv with SHA + AES). Understand the security gap between v2c and v3.
3. **NetFlow traffic analysis** — NetFlow on HQ-RTR1 inside/outside. Flow export to collector. Traffic baselining — establish what "normal" looks like before you can identify "abnormal."
4. **NTP synchronization** — HQ-RTR1 as NTP master (stratum 3). All devices as clients. NTP authentication with MD5 key. Verify with `show ntp associations` and `show ntp status`.
5. **EEM (Embedded Event Manager)** — Write a basic EEM applet that triggers on an interface going down and automatically runs a `show` command or sends a syslog message. This is on-device automation — no external tools needed.
6. **Configuration archive and rollback** — Configure `archive` with automatic config backups on write memory. Practice `configure replace` to roll back a bad change. This is insurance for every future project.
7. **Monitoring verification exercise** — Simulate failure (shut an interface), correlate syslog message + SNMP trap + NetFlow change + EEM trigger within 60 seconds. Prove you can see the same event from four different sources.
8. **CDP/LLDP for topology discovery** — Run `show cdp neighbors detail` across all devices and build a complete neighbor table. This is how tools like LibreNMS auto-discover your network. Document the full CDP topology map.

## Break/Fix Challenge
**The Fault:** Configure the syslog destination IP with a typo (10.1.99.52 instead of 10.1.99.51 — points to TACACS server instead of syslog server).
**Symptom:** No logs appearing on syslog server despite events being generated.
**Diagnosis path:** `show logging` (check destination IP), ping the configured destination (it responds because TACACS is there — misleading!), compare intended vs configured.
**Fix:** Correct the logging host IP.

## CCNA: Syslog (4.0), SNMP (4.0), NTP (4.0)
## Beyond CCNA: NetFlow, SNMPv3, EEM applets, configuration archive/rollback, multi-source event correlation, NTP auth, network baselining, CDP-based topology mapping

## Decision Log Entries
- Why tiered syslog levels per device role
- Why SNMPv3 on core but v2c on access (transition plan)
- Why NTP authentication
- Why EEM instead of external monitoring for basic triggers
- Why configuration archive on every write

## STAR
- **S:** Zero visibility into network behavior. No logs, no monitoring, no ability to correlate events.
- **T:** Build complete monitoring stack — Syslog, SNMP, NetFlow, NTP, EEM, config archive.
- **A:** Configured syslog on all devices, SNMP with traps + SNMPv3, NetFlow, NTP with auth, EEM applets, config archive, CDP topology mapping, tested multi-source event correlation, diagnosed a syslog destination typo.
- **R:** Can build monitoring infrastructure, correlate events from multiple sources, automate responses with EEM, baseline normal behavior, and roll back bad changes.

---

# Project 10 — AAA and Network Access Control

## Topology (20 nodes — activates existing Radius and TacPlus nodes)

TacPlus → HQ-TACACS at 10.1.99.52. Radius → HQ-RADIUS at 10.1.99.53.

## Phases

1. **TACACS+ for device administration** — AAA new-model, authentication/authorization/accounting via TACACS+ with local fallback. **Test AAA first:** Use `test aaa group tacacs+ [user] [pass] new-code` to verify server reachability before locking yourself out. Command accounting — log every command every admin types.
2. **Privilege level separation** — Level 15 (full admin), Level 7 (NOC read-only), Level 1 (basic). Configure custom privilege levels with specific commands allowed.
3. **Parser views (role-based CLI)** — Beyond privilege levels, create actual CLI views where a NOC operator can only see `show` commands and nothing else. `parser view NOC-VIEW` with explicit command inclusion.
4. **802.1X port authentication** — Radius config, dot1x on access switch ports, test authorized/unauthorized. Verify with `show dot1x all` and `show authentication sessions`.
5. **AAA accounting** — `aaa accounting exec` to track who logged in, when, from where. `aaa accounting commands 15` to log every privileged command. Verify accounting records appear in TACACS+ server logs.
6. **AAA failover testing** — Shut TACACS+ server (test local fallback works), shut Radius (test dot1x fail behavior), wrong credentials (test logging of failed attempts). This is critical — if AAA fails and fallback doesn't work, you're locked out of every device.

## Break/Fix Challenge
**The Fault:** Configure the TACACS+ server key wrong on HQ-RTR1 (mismatched shared secret).
**Symptom:** SSH login attempts fail with "authentication failed" even with correct credentials. Local fallback should still work.
**Diagnosis path:** `debug aaa authentication` (shows TACACS rejection), `show tacacs` (check server status), `test aaa group tacacs+` (quick test), verify local fallback login.
**Fix:** Correct the TACACS+ server key to match the server configuration.

## CCNA: AAA concepts (5.0), RADIUS vs TACACS+ (5.0), 802.1X concepts (5.0)
## Beyond CCNA: Full TACACS+ with command accounting, parser views (role-based CLI), privilege separation, 802.1X implementation, AAA failover, test aaa command, accounting records

## Decision Log Entries
- Why TACACS+ for device admin and RADIUS for user auth (not the reverse)
- Why local fallback is critical
- Why parser views over just privilege levels
- Why command accounting matters (audit trail)

## STAR
- **S:** Local credentials on every device. No centralized auth, no logging of admin actions, no role separation.
- **T:** Deploy centralized AAA — TACACS+ for admin, Radius for users, role-based access, full accounting.
- **A:** Configured TACACS+ on all devices with local fallback, privilege separation, parser views, 802.1X, command accounting, tested all failure scenarios including lockout prevention, diagnosed a mismatched TACACS key.
- **R:** Can implement centralized AAA, design role-based access with parser views, configure 802.1X, prevent lockouts, and maintain complete audit trails.

---

# Project 11 — QoS and Traffic Management

## Topology (20 nodes — adds Voice VLAN 500 config)

No new nodes. Adds VLAN 500 (Voice) on access switches. Alpine nodes simulate voice traffic.

## Phases

1. **Traffic classification with NBAR** — Use NBAR (Network-Based Application Recognition) to classify traffic by application, not just by IP/port. `match protocol http`, `match protocol dns`, etc. Understand what NBAR can identify that a simple ACL cannot.
2. **MQC classification and marking** — Class-maps (voice, signaling, bulk, default). Policy-map with DSCP marking (EF for voice, CS3 for signaling, AF11 for bulk). Apply as service-policy input.
3. **WAN edge queuing** — Output policy on WAN-facing interface: priority queue for voice (30% bandwidth guarantee), bandwidth for signaling (10%), fair queue for the rest. Shaping vs policing: configure traffic-shaping on the WAN edge and explain the difference.
4. **show policy-map interface — the #1 QoS verification command** — This is the single most important QoS command. Read class counters, offered rate, drop rate, queue depth. Practice interpreting the output for each class.
5. **Traffic generation and testing** — iperf/ping flooding from Alpine nodes. Compare voice-like traffic latency with and without QoS. Document before/after measurements.
6. **Voice VLAN on access switches** — `switchport voice vlan 500`, CoS-to-DSCP mapping, trust boundary at the access port.
7. **AutoQoS comparison** — Run `auto qos voip trust` on a test interface and examine what it generates with `show auto qos`. Compare the auto-generated MQC to your manual config. Understand what the "easy button" does under the hood and why manual config is better for non-default requirements.

## Break/Fix Challenge
**The Fault:** Misconfigure a class-map by omitting the `match` statement (empty class-map matches nothing).
**Symptom:** Voice traffic is not getting marked with DSCP EF — falls into default class.
**Diagnosis path:** `show policy-map interface [intf]` (voice class shows 0 packets matched), `show class-map` (empty match criteria).
**Fix:** Add the correct `match` statement to the class-map.

## CCNA: QoS concepts (4.0), DSCP (4.0), voice VLAN (2.0)
## Beyond CCNA: Full MQC config, NBAR classification, priority queuing with bandwidth guarantees, traffic shaping vs policing, traffic measurement, AutoQoS analysis, end-to-end QoS design, show policy-map interface mastery

## Decision Log Entries
- Why NBAR over simple ACL matching
- Why DSCP EF for voice specifically
- Why 30% priority for voice (oversubscription risk)
- Why shaping on WAN edge vs policing
- Why manual MQC over AutoQoS

## STAR
- **S:** All traffic treated equally. Voice-like traffic suffered during bulk transfers.
- **T:** Implement complete QoS — NBAR classification, MQC marking, priority queuing, and traffic measurement.
- **A:** Built NBAR classifiers, MQC policies with DSCP marking, configured priority/bandwidth queuing with traffic shaping, measured before/after, compared AutoQoS output, diagnosed an empty class-map.
- **R:** Can design end-to-end QoS, configure MQC with NBAR, prove improvement with real traffic data, and explain AutoQoS internals.

---

# Project 12 — Disaster Recovery Under Pressure

## Topology (20 nodes — no changes)

## The Exercise

**Rules:**
1. 90 minutes total
2. Wipe three devices to factory default: HQ-RTR1, HQ-DSW1, HQ-FW1 (recommended targets)
3. Rebuild using ONLY GitHub documentation (configs, decision log, diagrams)
4. Cannot look at running configs of other devices
5. Timer starts when first device is wiped

**Phases:**

1. **Preparation** — Review GitHub repo, open configs, write restoration plan with triage order. Verify your configuration archive (from Project 09) has backups available. If TFTP/SCP is configured, note the restore commands.
2. **Pre-wipe backup** — Practice TFTP/SCP config backup to a server. `copy running-config tftp:` or `copy running-config scp:`. This is your safety net. Practice the restore command too: `copy tftp: running-config`.
3. **The rebuild** — 90-minute timed exercise. Wipe → rebuild → verify per device. Use interface descriptions from your configs to trace connections without physical access. Use CDP from surviving devices to confirm what the wiped devices should be connected to.
4. **Password recovery procedure** — What if you forgot the enable secret? Walk through the rommon recovery process: `confreg 0x2142`, reboot, copy startup to running, reset password, `confreg 0x2102`, save. Practice this on one device.
5. **Verification checklist** — Run a standardized set of show commands on every rebuilt device:
   - `show cdp neighbors` — verify all neighbors present
   - `show interfaces trunk` — verify all trunks
   - `show ip ospf neighbor` — verify OSPF adjacencies
   - `show crypto session` — verify VPN
   - `show ip nat translations` — verify NAT
   - `show ntp status` — verify time sync
   - End-to-end ping from both sites
6. **After-action review** — What was rebuilt first and why, how long each device took, what was missing from docs, what to improve. Update GitHub docs with any gaps found.

## Break/Fix Challenge
The entire project IS the break/fix. Wiping three devices and rebuilding under time pressure
is the ultimate test of your documentation and engineering skills.

## CCNA: All topics — rebuilding complete network
## Beyond CCNA: DR planning, triage under pressure, TFTP/SCP backup and restore, password recovery, documentation validation, after-action review, config archive restore

## Decision Log Entries
- Why this triage order (core router → distribution switch → firewall)
- What the rebuild sequence should be and why
- What gaps in documentation were discovered

## STAR
- **S:** Complete enterprise network built across 11 projects, never tested if I could rebuild from documentation.
- **T:** Wipe three critical devices, rebuild in 90 minutes using only GitHub docs.
- **A:** Planned triage order, backed up configs via TFTP, wiped devices, rebuilt using documented configs and interface descriptions, used CDP from surviving devices for verification, practiced password recovery, ran full verification checklist.
- **R:** Proved documentation is rebuild-ready, identified gaps, demonstrated triage discipline, validated config backup/restore procedures.

---

# Project 13 — Network Automation (Bonus — Standalone Portfolio Piece)

## Purpose

This is NOT a networking project. This is a DevNet portfolio piece that sits alongside
the networking portfolio. The 12 projects prove you can design, build, and troubleshoot
network infrastructure. Project 13 proves you can automate it.

## Topology (21 nodes — adds 1)

| New Node | Image | Hostname | Role |
|----------|-------|----------|------|
| Alpine or Ubuntu | Linux | AUTOMATION1 | Automation workstation with Python/Netmiko |

### New Connections

| Side A | Side B | Purpose |
|--------|--------|---------|
| HQ-ASW1 Ethernet1/2 or 1/3 | AUTOMATION1 eth0 | Management VLAN 999 access |

## Phases

1. **Automation workstation setup** — Install Python3, pip, Netmiko, Paramiko on the Alpine/Ubuntu node. Verify SSH connectivity to all devices from this node. Document the setup in a script or requirements.txt.
2. **Inventory file** — Create a structured inventory of all 20 network devices: hostname, IP, platform, credentials. JSON or YAML format. This is your source of truth.
3. **Read-only automation** — Write a Python/Netmiko script that connects to every device and runs `show cdp neighbors`, `show ip interface brief`, and `show version`. Save outputs to files. This replaces manually logging into 20 devices.
4. **Configuration push** — Write a script that pushes your standard configs to all devices: SSH hardening, SNMP communities, syslog destination, NTP server, interface descriptions, banner. This is the "VTP for everything" — one script, all devices, consistent config.
5. **Compliance check** — Write a script that reads running configs from all devices and checks for: SSHv2 enabled, syslog pointing to correct server, NTP synchronized, no plaintext passwords. Report non-compliant devices.
6. **Ansible alternative** — If time allows, install Ansible and create playbooks that do the same as steps 3-5. Compare the Netmiko approach (Python scripting) vs Ansible approach (declarative YAML).

## Break/Fix Challenge
**The Fault:** Deliberately push a wrong SNMP community string to one device via the automation script.
**Symptom:** SNMP monitoring stops working for that device.
**Diagnosis path:** Run the compliance check script — it should flag the mismatch. Compare the pushed config against the intended config in the inventory.
**Fix:** Correct the inventory/template and re-run the push.

## CCNA: Not directly on exam — but CCNA questions reference automation concepts (6.0 Automation and Programmability)
## Beyond CCNA: Full Netmiko automation, inventory management, configuration compliance, Ansible basics, infrastructure-as-code thinking

## Decision Log Entries
- Why Netmiko over direct Paramiko
- Why JSON/YAML inventory over hardcoded IPs
- Why read-only scripts first before configuration push
- Why Ansible as a comparison, not a replacement

## STAR
- **S:** Managing 20+ devices manually — logging into each one for show commands, pushing configs individually, no way to verify consistency.
- **T:** Automate device management with Python/Netmiko and explore Ansible as an alternative.
- **A:** Built automation workstation, created structured device inventory, wrote read-only and configuration-push scripts, built compliance checker, compared Netmiko vs Ansible approaches, diagnosed an automated misconfiguration.
- **R:** Can automate network device management with Python, verify configuration compliance at scale, and articulate the difference between scripting and declarative automation.
