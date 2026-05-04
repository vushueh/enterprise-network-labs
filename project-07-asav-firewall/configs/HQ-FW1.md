# HQ-FW1 — Project 07 ASAv Perimeter Firewall Configuration

**Device:** HQ-FW1 (Cisco ASAv)
**Project:** 07 — ASAv Perimeter Firewall
**Platform note:** ASAv uses `GigabitEthernet0/x` interface names — NOT `Ethernet0/x` like IOL routers.
**Date:** 2026-05-04

This file covers the complete HQ-FW1 configuration across all phases. Phases are applied sequentially — each builds on the previous.

---

## Phase 1 — Identity, Interfaces, and Static Routes

```cisco
! ============================================================
! DEVICE: HQ-FW1 | PROJECT: 07 — ASAv Perimeter Firewall
! PHASE: 1 — Basic Setup and Cutover
! ============================================================
enable
configure terminal

! --- Identity ---
! WHY: Hostname makes logs, prompts, and screenshots readable.
hostname HQ-FW1
domain-name lab.local
enable password CMLenableP@ss!
username admin password CMLenableP@ss! privilege 15

! --- Inside interface (security-level 100 = most trusted) ---
! WHY: Inside faces the campus. Security level 100 = highest trust.
!      Traffic flows freely from higher to lower security levels by default.
interface GigabitEthernet0/0
 description INSIDE-TO-HQ-RTR1-E0/3
 nameif inside
 security-level 100
 ip address 10.0.0.14 255.255.255.252
 no shutdown

! --- Outside interface (security-level 0 = untrusted internet) ---
! WHY: Security level 0 = lowest trust. Outside-initiated traffic is blocked
!      unless explicitly permitted by an ACL (Phase 3).
interface GigabitEthernet0/1
 description OUTSIDE-TO-ISP-RTR1-E0/0
 nameif outside
 security-level 0
 ip address 203.0.113.1 255.255.255.252
 no shutdown

! --- DMZ interface (security-level 50 = semi-trusted) ---
! WHY: DMZ is between inside and outside. Server can be reached from inside
!      (100 → 50) and from outside with an ACL. DMZ cannot initiate to inside (50 ↛ 100).
interface GigabitEthernet0/2
 description DMZ-TO-HQ-SRV1-ETH0
 nameif dmz
 security-level 50
 ip address 10.1.40.1 255.255.255.0
 no shutdown

! --- Static routes ---
! WHY: Default route sends unknown traffic to ISP. Internal routes send
!      campus and branch traffic back through HQ-RTR1.
route outside 0.0.0.0 0.0.0.0 203.0.113.2 1
route inside 10.1.0.0 255.255.0.0 10.0.0.13 1
route inside 10.2.0.0 255.255.0.0 10.0.0.13 1
route inside 10.0.0.0 255.255.0.0 10.0.0.13 1

! --- SSH from management VLAN only ---
! WHY: Firewall management must not be reachable from untrusted interfaces.
crypto key generate rsa modulus 2048
ssh 10.1.99.0 255.255.255.0 inside
ssh timeout 10
ssh version 2
no http server enable

end
write memory

! --- VERIFICATION ---
! show interface ip brief    → Gi0/0, Gi0/1, Gi0/2 up/up with correct IPs
! show nameif               → inside 100, dmz 50, outside 0
! show route                → default via 203.0.113.2, internal routes via 10.0.0.13
! ping inside 10.0.0.13     → HQ-RTR1 responds
! ping outside 203.0.113.2  → ISP-RTR1 responds
! ping dmz 10.1.40.10       → HQ-SRV1 responds
```

---

## Phase 2 — NAT Migration

```cisco
! ============================================================
! DEVICE: HQ-FW1 | PROJECT: 07 — ASAv Perimeter Firewall
! PHASE: 2 — PAT per VLAN + Static NAT for DMZ Server
! ============================================================
enable
configure terminal

! --- HQ campus VLANs — dynamic PAT to outside interface ---
! WHY per-VLAN objects: show xlate output is VLAN-readable; future policy can differ per VLAN.
!      Management VLANs (10.1.99.0/24, 10.2.99.0/24) are excluded — mgmt never reaches internet.
object network P07-HQ-ENG
 subnet 10.1.100.0 255.255.255.0
 nat (inside,outside) dynamic interface

object network P07-HQ-SALES
 subnet 10.1.200.0 255.255.255.0
 nat (inside,outside) dynamic interface

object network P07-HQ-GUEST
 subnet 10.1.44.0 255.255.255.0
 nat (inside,outside) dynamic interface

! --- Branch VLANs — arrive via HQ-RTR1 inside, still need PAT ---
object network P07-BR-ENG
 subnet 10.2.100.0 255.255.255.0
 nat (inside,outside) dynamic interface

object network P07-BR-SALES
 subnet 10.2.200.0 255.255.255.0
 nat (inside,outside) dynamic interface

object network P07-BR-GUEST
 subnet 10.2.44.0 255.255.255.0
 nat (inside,outside) dynamic interface

! --- HQ-SRV1 static NAT — DMZ server keeps public IP 203.0.113.10 ---
! WHY: Static NAT is bidirectional — covers inbound from internet AND outbound from server.
object network P07-HQ-SRV1-STATIC
 host 10.1.40.10
 nat (dmz,outside) static 203.0.113.10

! --- MSS clamping ---
! WHY: Prevents TCP fragmentation through NAT. Replaces ip tcp adjust-mss that was on HQ-RTR1.
sysopt connection tcpmss 1452

end
write memory

! --- VERIFICATION ---
! show nat detail                                                → 7 rules (6 PAT + 1 static)
! show xlate                                                    → Active translations after traffic
! packet-tracer input inside tcp 10.1.100.194 12345 203.0.113.100 80 → Allow with NAT
! packet-tracer input outside tcp 203.0.113.2 12345 203.0.113.10 80  → Static NAT to 10.1.40.10
```

---

## Phase 3 — ACL Policy and Application Inspection

```cisco
! ============================================================
! DEVICE: HQ-FW1 | PROJECT: 07 — ASAv Perimeter Firewall
! PHASE: 3 — Outside ACL + Application Inspection
! ============================================================
enable
configure terminal

! --- Object for DMZ server (used in ACL permit) ---
object network OBJ-HQ-SRV1
 host 10.1.40.10

! --- Outside-to-DMZ: permit HTTP only, deny everything else (logged) ---
! WHY log on deny: Every blocked outside attempt is a security event — must be auditable.
access-list ACL-OUTSIDE-IN extended permit tcp any object OBJ-HQ-SRV1 eq 80 log
access-list ACL-OUTSIDE-IN extended deny ip any any log

access-group ACL-OUTSIDE-IN in interface outside

! --- Application inspection ---
! WHY inspect icmp: Allows ICMP reply through without a broad outside permit.
!      ASA tracks request/reply pairs — return traffic is state-matched automatically.
! WHY inspect dns: Validates DNS message format, prevents cache poisoning.
! WHY inspect http: Enables HTTP visibility; supports URL filtering in future phases.
policy-map global_policy
 class inspection_default
  inspect icmp
  inspect dns
  inspect http

end
write memory

! --- VERIFICATION ---
! show access-list ACL-OUTSIDE-IN                                         → Two entries present
! show service-policy global                                               → ICMP, DNS, HTTP inspection active
! packet-tracer input outside tcp 203.0.113.2 12345 203.0.113.10 80      → Allow
! packet-tracer input outside tcp 203.0.113.2 12345 10.0.0.14 22         → Drop
! packet-tracer input inside icmp 10.1.100.10 8 0 203.0.113.100          → Allow (inspection handles return)
```

---

## Phase 5 — Firewall Logging

```cisco
! ============================================================
! DEVICE: HQ-FW1 | PROJECT: 07 — ASAv Perimeter Firewall
! PHASE: 5 — Logging and Threat Detection
! ============================================================
enable
configure terminal

! --- Enable logging ---
! WHY informational: Captures permitted and denied flows; full visibility for lab.
logging enable
logging timestamp
logging trap informational
logging host inside 10.1.99.51
logging asdm informational

! --- Threat detection ---
! WHY: Provides host-level traffic statistics — identifies top talkers without external tools.
threat-detection basic-threat
threat-detection statistics

end
write memory

! --- VERIFICATION ---
! show logging                             → Logging enabled, host 10.1.99.51 configured
! show access-list ACL-OUTSIDE-IN         → Hit counters increment after traffic
! show threat-detection statistics host   → Host statistics visible after test traffic
```
