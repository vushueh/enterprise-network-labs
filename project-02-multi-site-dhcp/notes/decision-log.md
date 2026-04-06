# Project 02 — Design Decisions

## Router-on-a-Stick on BR-RTR1 vs L3 switching on BR-DSW1
**Choice:** Inter-VLAN routing via subinterfaces on BR-RTR1
**Alternative:** Enable ip routing on BR-DSW1 and create per-VLAN SVIs
**Rationale:** Keeps all routing decisions at the router. BR-DSW1 stays L2-focused in Phase 1. OSPF in Project 03 will use BR-RTR1 as the ABR — centralizing routing there now avoids a redesign.
**Trade-off:** All inter-VLAN traffic hairpins through BR-RTR1. Suboptimal for heavy east-west traffic but acceptable at lab scale.

## VLAN 1000 as Native VLAN
**Choice:** VLAN 1000 native on all trunks, no IP assigned
**Alternative:** Leave VLAN 1 as native (IOS default)
**Rationale:** VLAN 1 carries CDP, STP, VTP, and DTP by default. Separating native from management avoids untagged control-plane traffic mixing with data. Industry best practice — VLAN 1 should never carry user traffic.
**Trade-off:** Must configure native VLAN explicitly on every trunk — easy to miss one port.

## BR-DSW1 as STP Root for All VLANs
**Choice:** spanning-tree vlan 100,200,300,500,999,1000 priority 4096 on BR-DSW1
**Alternative:** Let STP auto-elect (lowest MAC wins)
**Rationale:** Single distribution switch at branch — only one device to be root. Auto-election is unpredictable; a random MAC could make BR-ASW1 the root, which would cause a forwarding black-hole.
**Trade-off:** Manual priority — must remember to set this on any future distribution switch added.

## ip routing on BR-ASW1 (not ip default-gateway)
**Choice:** ip routing + ip route 0.0.0.0 0.0.0.0 10.2.99.1
**Alternative:** ip default-gateway 10.2.99.1 (original Phase 1 config)
**Rationale:** ip default-gateway on IOL-L2 cannot route replies to remote-subnet sources. When HQ-RTR1 (10.0.0.1) pings BR-ASW1, the reply must be routed back to a remote subnet — this requires the routing engine, not the management-plane handler.
**Trade-off:** Technically enables routing on an access switch — not standard in production. Acceptable for lab management-plane reachability.

## Centralized DHCP on HQ vs Distributed per-site DHCP
**Choice:** Single Dnsmasq server at HQ serving all 8 VLANs via relay
**Alternative:** Separate DHCP server at each site
**Rationale:** Demonstrates ip helper-address relay — a core CCNA topic. Single server is easier to manage. Also realistic — many enterprises use centralized DHCP with relay rather than distributed servers.
**Trade-off:** Branch DHCP depends on WAN link. If WAN fails, branch endpoints cannot renew leases (mitigated by 24h lease time).

## bandwidth and delay set on WAN interfaces
**Choice:** bandwidth 1000 and delay 1000 on both E0/1 WAN interfaces
**Alternative:** Leave IOL defaults (10 Mbps bandwidth, default delay)
**Rationale:** OSPF calculates cost from bandwidth. Without explicit bandwidth, IOL defaults to 10 Mbps making the WAN look identical to LAN links. Setting 1 Mbps now ensures Project 03 OSPF cost calculations are realistic.
**Trade-off:** Values are arbitrary (lab-only) but self-consistent.

## Static DHCP Reservations for Endpoints
**Choice:** dhcp-host= MAC-to-IP binding for PC-BR1 and PC-BR2
**Alternative:** Dynamic DHCP with no reservation
**Rationale:** DNS A records hardcode IPs. If an endpoint gets a different IP after a restart, the DNS entry becomes stale. Static reservations ensure DNS and DHCP always agree.
**Trade-off:** Must update dnsmasq.conf if endpoint MAC changes.
