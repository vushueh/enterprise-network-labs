# Project 03 — Requirements

## Business Requirements
1. Eliminate single points of failure in WAN routing — static routes do not self-heal
2. The network must automatically reroute traffic within 1 second of a WAN link failure
3. All inter-site routing must be authenticated — no unauthenticated routing updates on WAN links
4. A third WAN path through a transit router (WAN-RTR1) must be deployed as the preferred route
5. IPv6 inter-site routing must be dynamic — remove all IPv6 static routes from Project 02
6. A last-resort backup layer must exist even if the routing protocol itself fails

## Technical Requirements
- Routing protocol: OSPF (OSPFv2 for IPv4, OSPFv3 for IPv6)
- OSPF design: Multi-area — Area 0 (WAN backbone), Area 1 (HQ campus), Area 2 (Branch campus)
- ABR summarization: HQ-RTR1 summarizes 10.1.0.0/16 into Area 0; BR-RTR1 summarizes 10.2.0.0/16
- Authentication: MD5 on all WAN-facing OSPF interfaces (key: OSPF-WAN-KEY, key-id: 1)
- Path selection: WAN-RTR1 path preferred (cost 20) over direct HQ↔BR link (cost 100)
- BFD: interval 300ms, min_rx 300ms, multiplier 3 — bound to OSPF on all WAN interfaces
- IP SLA: ICMP probes to directly connected /30 neighbor IPs (not loopbacks)
- Floating static: AD 250 with object tracking — last resort if OSPF fails entirely
- WAN interface type: `ip ospf network point-to-point` on all /30 WAN links
- New device: WAN-RTR1 (IOL router) — transit router between HQ and Branch

## Success Criteria
- [ ] All three OSPF neighbors reach FULL/ - state with Pri=0 (point-to-point)
- [ ] WAN-RTR1 shows O IA 10.1.0.0/16 and O IA 10.2.0.0/16 (summarization working)
- [ ] Traceroute HQ → Branch hops through WAN-RTR1 first (10.0.0.6 → 10.0.0.10)
- [ ] After shutting HQ-RTR1 E0/2: route to Branch switches to backup path (metric 110)
- [ ] After restoring E0/2: traffic returns to preferred WAN-RTR1 path (metric 30)
- [ ] BFD sessions show Up/Up on all WAN interfaces
- [ ] IP SLA statistics show real success counters (not Unknown)
- [ ] Track object shows Reachability is Up, return code OK
- [ ] With OSPF shut down: floating static S 10.1.0.0/16 [250/0] installs and pings succeed
- [ ] OSPFv3 neighbor FULL/ - on direct HQ↔BR WAN link
- [ ] IPv6 ping: 2001:DB8:1:100::1 ↔ 2001:DB8:2:100::1 succeeds both directions
