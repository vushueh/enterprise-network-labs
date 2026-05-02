# Project 05 — Internet Access and NAT: Requirements

## Business Requirements

| ID | Requirement |
|----|-------------|
| BR-01 | HQ and Branch users must reach the simulated internet through a single HQ edge exit. |
| BR-02 | Internal RFC 1918 addresses must never be exposed directly to the ISP segment. |
| BR-03 | The internal HQ server must be reachable from the outside through a stable public address. |
| BR-04 | Guest users must be allowed to reach the internet but blocked from internal HQ and Branch subnets. |
| BR-05 | NAT policy must be maintainable as the enterprise adds more internal subnets. |
| BR-06 | The ISP-facing edge must avoid TCP fragmentation problems during web transfers. |
| BR-07 | The design must be documented with the reason for each major configuration choice. |

## Technical Requirements

| ID | Requirement | Technology |
|----|-------------|------------|
| TR-01 | Add a simulated ISP router using an IOL image | ISP-RTR1 |
| TR-02 | Add an external web server using an Nginx image | EXT-WEB1 |
| TR-03 | Add an internal HQ web server using an Nginx image | HQ-SRV1 |
| TR-04 | Use HQ-RTR1 Ethernet0/3 as the ISP handoff | 203.0.113.1/30 |
| TR-05 | Use ISP-RTR1 Ethernet0/0 as the customer-facing ISP handoff | 203.0.113.2/30 |
| TR-06 | Use ISP-RTR1 Ethernet0/1 for the simulated internet segment | 203.0.113.97/28 |
| TR-07 | Place EXT-WEB1 on the simulated internet segment | 203.0.113.100/28, gateway 203.0.113.97 |
| TR-08 | Place HQ-SRV1 in the HQ server VLAN | 10.1.40.10/24, gateway 10.1.40.1 |
| TR-09 | Use HQ-DSW1 Ethernet1/1 for HQ-SRV1 | VLAN 400 access port, PortFast, BPDU Guard |
| TR-10 | Advertise a default route from HQ into OSPF | `default-information originate` |
| TR-11 | Translate HQ and Branch user subnets with PAT | `ip nat inside source list ... overload` |
| TR-12 | Exclude Management VLAN 999 from NAT | No NAT ACL permit and no NAT inside on E0/0.999 |
| TR-13 | Publish HQ-SRV1 with a one-to-one public address | Static NAT 10.1.40.10 to 203.0.113.10 |
| TR-14 | Route the static NAT public host address from ISP to HQ | ISP-RTR1 /32 route to 203.0.113.1 |
| TR-15 | Refactor NAT source matching with an object-group | `INSIDE-NAT-SOURCES` |
| TR-16 | Isolate HQ Guest VLAN from internal networks | `GUEST-RESTRICT` inbound on E0/0.300 |
| TR-17 | Clamp TCP MSS on the ISP-facing interface | `ip tcp adjust-mss 1452` |

## Lab Prerequisites

| Requirement | Detail |
|-------------|--------|
| ISP router node | `ISP-RTR1` using IOL router image |
| External server node | `EXT-WEB1` using Nginx image |
| Internal server node | `HQ-SRV1` using Nginx image |
| Free HQ router port | HQ-RTR1 Ethernet0/3 for ISP handoff |
| Free HQ switch port | HQ-DSW1 Ethernet1/1 for HQ-SRV1 |
| Public documentation range | 203.0.113.0/24 for all simulated public addresses |
| Existing baseline | Projects 01–04 complete and stable before adding internet/NAT |

## Success Criteria

- [ ] `show cdp neighbors` on HQ-RTR1 shows ISP-RTR1 on Ethernet0/3
- [ ] HQ-RTR1 can ping ISP-RTR1 at 203.0.113.2
- [ ] HQ-RTR1 can ping EXT-WEB1 at 203.0.113.100
- [ ] HQ-RTR1 has a static default route to 203.0.113.2
- [ ] HQ-RTR1 advertises a Type-5 OSPF default route
- [ ] BR-RTR1 learns O*E2 0.0.0.0/0 from HQ-RTR1
- [ ] PC-ENG1 reaches EXT-WEB1 through PAT using `wget -O - http://203.0.113.100`
- [ ] `show ip nat translations` shows PC-ENG1 translated to 203.0.113.1 with a unique port
- [ ] PC-BR1 reaches EXT-WEB1 through PAT
- [ ] `show ip nat translations` shows a Branch 10.2.100.x host translated to 203.0.113.1
- [ ] Static NAT entry for 203.0.113.10 to 10.1.40.10 is present with no traffic required
- [ ] Inbound ping from ISP-RTR1 to 203.0.113.10 succeeds
- [ ] NAT table shows inbound static NAT session entries during the ISP test
- [ ] NAT ACL is refactored to one object-group line
- [ ] Guest VLAN 300 can reach the internet and cannot reach internal HQ subnets
- [ ] `show running-config interface Ethernet0/3` shows `ip tcp adjust-mss 1452`
- [ ] Branch traceroute reaches EXT-WEB1 through BR-RTR1, WAN-RTR1, HQ-RTR1, ISP-RTR1, then EXT-WEB1
