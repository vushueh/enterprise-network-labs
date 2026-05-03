# HQ-ASW1 — Project 06 Security Hardening Configuration

**Device:** HQ-ASW1 (IOL-L2)
**Project:** 06 — Security Hardening
**Date:** 2026-05-02

This file covers all Project 06 security additions to HQ-ASW1. The base switching config (VLANs, trunks, STP, SSH) was established in Projects 01–04.

---

## Phase 1 — Port Security

```cisco
! ============================================================
! DEVICE: HQ-ASW1 | PROJECT: 06 | PHASE: 1 — Port Security
! ============================================================
enable
configure terminal

! --- Ethernet0/2: PC-ENG1, VLAN 100 ---
! WHY maximum 2: Engineering may connect workstation + secondary device
! WHY restrict: Drops unknown MACs and logs; keeps port up for the legitimate user
interface Ethernet0/2
 description ACCESS-PC-ENG1-VLAN100
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict

! --- Ethernet0/3: MGMT1, VLAN 999 ---
! WHY maximum 1: One admin workstation — any second MAC is a policy violation
! WHY shutdown: Unauthorized MAC on a management port is a critical event
interface Ethernet0/3
 description ACCESS-MGMT1-VLAN999
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown

end
write memory
```

**Verification:**
```cisco
show port-security
show port-security address
show port-security interface Ethernet0/2
show port-security interface Ethernet0/3
```

---

## Phase 2 — DHCP Snooping

```cisco
! ============================================================
! DEVICE: HQ-ASW1 | PROJECT: 06 | PHASE: 2 — DHCP Snooping
! ============================================================
enable
configure terminal

! --- Enable snooping globally ---
ip dhcp snooping
no ip dhcp snooping information option

! --- Enable on all user VLANs ---
ip dhcp snooping vlan 100,200,300,999

! --- Trust trunk uplinks to HQ-DSW1 ---
! WHY: DHCP responses from Dnsmasq arrive via these trunk ports
interface Ethernet0/0
 ip dhcp snooping trust

interface Ethernet0/1
 ip dhcp snooping trust

! --- Rate limit access ports ---
! WHY 15 pps: Covers normal DHCP traffic; triggers errdisable on flood attacks
interface Ethernet0/2
 ip dhcp snooping limit rate 15

interface Ethernet0/3
 ip dhcp snooping limit rate 15

! --- Static bindings (IOL-L2 workaround) ---
! WHY: IOL-L2 snooping engine never populates the binding table from live DHCP
! These static entries provide the binding database for DAI (Phase 3) and IP Source Guard (Phase 4)
ip source binding 5254.00D7.CBBC vlan 100 10.1.100.194 interface Ethernet0/2
ip source binding 5254.00B2.8D53 vlan 999 10.1.99.100 interface Ethernet0/3

end
write memory
```

**Verification:**
```cisco
show ip dhcp snooping
show ip dhcp snooping binding
show ip source binding
show running-config interface Ethernet0/2
```

---

## Phase 3 — Dynamic ARP Inspection

```cisco
! ============================================================
! DEVICE: HQ-ASW1 | PROJECT: 06 | PHASE: 3 — Dynamic ARP Inspection
! ============================================================
enable
configure terminal

! --- ARP ACLs: static MAC-to-IP mappings for DAI validation ---
! WHY ARP ACLs: IOL-L2 binding table is empty; ARP ACLs are the validation source
arp access-list ARP-VLAN100
 permit ip host 10.1.100.194 mac host 5254.00D7.CBBC
 permit ip host 10.1.100.170 mac host 5254.0049.0158

arp access-list ARP-VLAN200
 permit ip host 10.1.200.142 mac host 5254.001E.FAAF

arp access-list ARP-VLAN999
 permit ip host 10.1.99.100 mac host 5254.00B2.8D53

! --- Enable DAI on user VLANs ---
ip arp inspection vlan 100,200,300,999

! --- Apply ARP ACLs ---
ip arp inspection filter ARP-VLAN100 vlan 100
ip arp inspection filter ARP-VLAN200 vlan 200
ip arp inspection filter ARP-VLAN999 vlan 999

! --- Trust uplink trunk ports ---
! WHY: Gateway ARP replies from HQ-RTR1 arrive via trunks; must pass without validation
interface Ethernet0/0
 ip arp inspection trust

interface Ethernet0/1
 ip arp inspection trust

end
write memory
```

**Verification:**
```cisco
show ip arp inspection vlan 100
show ip arp inspection interfaces
show ip arp inspection statistics vlan 100
show arp access-list
```

---

## Phase 4 — IP Source Guard

```cisco
! ============================================================
! DEVICE: HQ-ASW1 | PROJECT: 06 | PHASE: 4 — IP Source Guard
! ============================================================
enable
configure terminal

! --- Enable IP Source Guard with MAC check on access ports ---
! WHY mac-check: Validates both IP and MAC against binding table
! WHY NOT port-security variant: Not supported on IOS 17.16 (IOL)
interface Ethernet0/2
 ip verify source mac-check

interface Ethernet0/3
 ip verify source mac-check

end
write memory
```

**Verification:**
```cisco
show ip verify source
show ip source binding
```

---

## Phase 6 — Management Plane Hardening

```cisco
! ============================================================
! DEVICE: HQ-ASW1 | PROJECT: 06 | PHASE: 6 — Management Hardening
! ============================================================
enable
configure terminal

! --- Brute-force login protection ---
! WHY: Blocks password spray tools; 120s lockout is short enough for legitimate recovery
login block-for 120 attempt 3 within 60

! --- Console session timeout ---
line console 0
 exec-timeout 10 0

! --- VTY session timeout ---
line vty 0 4
 exec-timeout 15 0

! --- Disable unnecessary services ---
no service tcp-small-servers
no service udp-small-servers

end
write memory
```

**Verification:**
```cisco
show login
show running-config | section line console
show running-config | section line vty
```

---

## Phase 7 — Errdisable Recovery

```cisco
! ============================================================
! DEVICE: HQ-ASW1 | PROJECT: 06 | PHASE: 7 — Errdisable Recovery
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

**Verification:**
```cisco
show errdisable recovery
```
