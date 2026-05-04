# HQ-RTR1 — Project 07 Changes

**Device:** HQ-RTR1 (IOL router)
**Project:** 07 — ASAv Perimeter Firewall
**Date:** 2026-05-04

This file covers only the Project 07 changes to HQ-RTR1. The base config (subinterfaces, OSPF, ACLs, port security) was established in Projects 01–06.

---

## Phase 1 — Re-IP E0/3, Update Default Route, Shut VLAN 400 Gateway

```cisco
! ============================================================
! DEVICE: HQ-RTR1 | PROJECT: 07 — ASAv Perimeter Firewall
! PHASE: 1 — Cutover E0/3 from ISP to firewall inside
! ============================================================
enable
configure terminal

! --- Re-purpose E0/3 from ISP handoff to firewall inside link ---
! WHY: HQ-RTR1 no longer connects directly to ISP. Internet-bound traffic
!      now goes to HQ-FW1 first, which handles stateful inspection and NAT.
interface Ethernet0/3
 description INSIDE-TO-HQ-FW1-GI0/0
 no ip address
 no ip nat outside
 no ip tcp adjust-mss 1452
 ip address 10.0.0.13 255.255.255.252
 no shutdown

! --- Shut VLAN 400 gateway subinterface ---
! WHY: HQ-SRV1 moved to firewall DMZ. HQ-RTR1 must stop acting as server VLAN gateway.
interface Ethernet0/0.400
 description OLD-GATEWAY-VLAN400-MOVED-TO-HQ-FW1-DMZ
 shutdown

! --- Update default route to point to firewall ---
! WHY: HQ-FW1 is now the perimeter. All internet-bound traffic routes to its inside IP.
no ip route 0.0.0.0 0.0.0.0 203.0.113.2
ip route 0.0.0.0 0.0.0.0 10.0.0.14

! --- Add DMZ route via firewall ---
! WHY: Internal VLANs still use HQ-RTR1 as gateway. HQ-RTR1 needs a route to DMZ
!      so it can forward internal traffic destined for 10.1.40.0/24 to HQ-FW1.
ip route 10.1.40.0 255.255.255.0 10.0.0.14

! --- Redistribute DMZ route into OSPF so Branch can reach DMZ ---
! WHY: Prefix-list restricts redistribution to only 10.1.40.0/24 — not all statics.
!      Without this, Branch-RTR1 has no path to the DMZ server.
ip prefix-list P07-DMZ-ONLY seq 5 permit 10.1.40.0/24

route-map P07-REDIST-DMZ permit 10
 match ip address prefix-list P07-DMZ-ONLY

router ospf 1
 redistribute static subnets route-map P07-REDIST-DMZ

end
write memory

! --- VERIFICATION ---
! show ip interface brief              → E0/3 = 10.0.0.13/30
! show ip route 0.0.0.0               → Default route via 10.0.0.14
! show ip route 10.1.40.0             → Static via 10.0.0.14
! show ip ospf database external | include 10.1.40 → DMZ route in OSPF LSA
! ping 10.0.0.14                       → HQ-FW1 inside responds
```

---

## Phase 2 — Remove NAT

```cisco
! ============================================================
! DEVICE: HQ-RTR1 | PROJECT: 07 — ASAv Perimeter Firewall
! PHASE: 2 — Remove NAT (migrated to HQ-FW1)
! ============================================================
enable
configure terminal

! --- Remove PAT statement ---
! WHY: NAT boundary is now HQ-FW1. HQ-RTR1 must stop translating.
no ip nat inside source list NAT-PAT-SOURCES interface Ethernet0/3 overload

! --- Remove static NAT for HQ-SRV1 ---
! WHY: Server moved to DMZ. Static NAT rebuilt on HQ-FW1 under Phase 2.
no ip nat inside source static 10.1.40.10 203.0.113.10

! --- Remove ip nat inside from all subinterfaces ---
interface Ethernet0/0.100
 no ip nat inside
interface Ethernet0/0.200
 no ip nat inside
interface Ethernet0/0.300
 no ip nat inside
interface Ethernet0/0.400
 no ip nat inside
interface Ethernet0/1
 no ip nat inside
interface Ethernet0/2
 no ip nat inside
interface Ethernet0/3
 no ip nat outside

! --- Remove NAT source ACL and object group ---
! WHY: These were router NAT helpers — no longer needed here.
no ip access-list extended NAT-PAT-SOURCES
no object-group network INSIDE-NAT-SOURCES

clear ip nat translation *

end
write memory

! --- VERIFICATION ---
! show running-config | include ip nat    → No output (all NAT removed)
! show ip nat translations                → Empty table
```
