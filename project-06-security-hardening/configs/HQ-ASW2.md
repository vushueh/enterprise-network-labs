# HQ-ASW2 — Project 06 Security Hardening Configuration

**Device:** HQ-ASW2 (IOL-L2)
**Project:** 06 — Security Hardening
**Date:** 2026-05-02

This file covers all Project 06 security additions to HQ-ASW2. The base switching config was established in Projects 01–04. HQ-ASW2 hosts PC-SALES1 (VLAN 200, E0/2) and ATTACKER1 (VLAN 100, E0/3 — the attacker simulation node).

---

## Phase 1 — Port Security

```cisco
! ============================================================
! DEVICE: HQ-ASW2 | PROJECT: 06 | PHASE: 1 — Port Security
! ============================================================
enable
configure terminal

! --- Ethernet0/2: PC-SALES1, VLAN 200 ---
! WHY restrict: Sales user port — keep the legitimate user online; log violations
interface Ethernet0/2
 description ACCESS-PC-SALES1-VLAN200
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict

! --- Ethernet0/3: ATTACKER1, VLAN 100 ---
! WHY shutdown: Demonstrates visible err-disabled response on violation
! WHY maximum 1: One known attacker node — any MAC change is a violation event
interface Ethernet0/3
 description ACCESS-ATTACKER1-VLAN100
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown

end
write memory
```

**Sticky MACs learned:**
| Interface | Device | MAC Address |
|-----------|--------|-------------|
| Ethernet0/2 | PC-SALES1 | 5254.001E.FAAF |
| Ethernet0/3 | ATTACKER1 | 5254.0049.0158 |

---

## Phase 2 — DHCP Snooping

```cisco
! ============================================================
! DEVICE: HQ-ASW2 | PROJECT: 06 | PHASE: 2 — DHCP Snooping
! ============================================================
enable
configure terminal

ip dhcp snooping
no ip dhcp snooping information option
ip dhcp snooping vlan 100,200,300,999

interface Ethernet0/0
 ip dhcp snooping trust

interface Ethernet0/1
 ip dhcp snooping trust

interface Ethernet0/2
 ip dhcp snooping limit rate 15

interface Ethernet0/3
 ip dhcp snooping limit rate 15

! Static bindings (IOL-L2 platform workaround — see decision-log.md DL-08)
ip source binding 5254.001E.FAAF vlan 200 10.1.200.142 interface Ethernet0/2
ip source binding 5254.0049.0158 vlan 100 10.1.100.170 interface Ethernet0/3

end
write memory
```

---

## Phase 3 — Dynamic ARP Inspection

```cisco
! ============================================================
! DEVICE: HQ-ASW2 | PROJECT: 06 | PHASE: 3 — Dynamic ARP Inspection
! ============================================================
enable
configure terminal

! ATTACKER1 is included in ARP-VLAN100 so its REAL IP passes; only spoofed IPs are dropped
arp access-list ARP-VLAN100
 permit ip host 10.1.100.170 mac host 5254.0049.0158

arp access-list ARP-VLAN200
 permit ip host 10.1.200.142 mac host 5254.001E.FAAF

ip arp inspection vlan 100,200,300,999
ip arp inspection filter ARP-VLAN100 vlan 100
ip arp inspection filter ARP-VLAN200 vlan 200

interface Ethernet0/0
 ip arp inspection trust

interface Ethernet0/1
 ip arp inspection trust

end
write memory
```

---

## Phase 4 — IP Source Guard

```cisco
! ============================================================
! DEVICE: HQ-ASW2 | PROJECT: 06 | PHASE: 4 — IP Source Guard
! ============================================================
enable
configure terminal

interface Ethernet0/2
 ip verify source mac-check

interface Ethernet0/3
 ip verify source mac-check

end
write memory
```

---

## Phase 6 — Management Plane Hardening

```cisco
! ============================================================
! DEVICE: HQ-ASW2 | PROJECT: 06 | PHASE: 6 — Management Hardening
! ============================================================
enable
configure terminal

login block-for 120 attempt 3 within 60

line console 0
 exec-timeout 10 0

line vty 0 4
 exec-timeout 15 0

no service tcp-small-servers
no service udp-small-servers

end
write memory
```

---

## Phase 7 — Errdisable Recovery

```cisco
! ============================================================
! DEVICE: HQ-ASW2 | PROJECT: 06 | PHASE: 7 — Errdisable Recovery
! ============================================================
enable
configure terminal

errdisable recovery cause psecure-violation
errdisable recovery cause security-violation
errdisable recovery cause dhcp-rate-limit
errdisable recovery cause arp-inspection
errdisable recovery cause bpduguard
errdisable recovery interval 300

end
write memory
```
