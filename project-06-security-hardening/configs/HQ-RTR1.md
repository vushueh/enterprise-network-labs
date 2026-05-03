# HQ-RTR1 — Project 06 Security Hardening Configuration

**Device:** HQ-RTR1 (IOL router)
**Project:** 06 — Security Hardening
**Date:** 2026-05-02

This file covers all Project 06 security additions to HQ-RTR1: inter-VLAN ACLs for OOB management protection and management plane hardening. The base router config (subinterfaces, OSPF, NAT) was established in Projects 01–05.

---

## Phase 5 — Inter-VLAN ACLs / OOB Management Protection

### Policy Overview

| ACL | Applied To | Key Policy |
|-----|-----------|------------|
| ACL-VLAN100-IN | Ethernet0/0.100 inbound | Block Engineering → Mgmt (log), allow → Sales/Servers/Internet |
| ACL-VLAN200-IN | Ethernet0/0.200 inbound | Block Sales → Mgmt (log), allow → Engineering/Servers/Internet |
| ACL-VLAN300-IN | Ethernet0/0.300 inbound | Block Guest → all internal 10.x.x.x, allow Internet |
| ACL-VLAN400-IN | Ethernet0/0.400 inbound | Allow Servers → Mgmt, permit established TCP to users, block new server-to-user sessions |

```cisco
! ============================================================
! DEVICE: HQ-RTR1 | PROJECT: 06 | PHASE: 5 — Inter-VLAN ACLs
! ============================================================
enable
configure terminal

! --- VLAN 100 (Engineering) — blocks mgmt access, permits inter-VLAN and internet ---
! WHY log on seq 10: Management access attempts are security events — audit trail required
ip access-list extended ACL-VLAN100-IN
 10 deny ip 10.1.100.0 0.0.0.255 10.1.99.0 0.0.0.255 log
 20 permit ip 10.1.100.0 0.0.0.255 10.1.200.0 0.0.0.255
 30 permit ip 10.1.100.0 0.0.0.255 10.1.40.0 0.0.0.255
 40 deny ip 10.1.100.0 0.0.0.255 10.1.44.0 0.0.0.255
 50 permit ip 10.1.100.0 0.0.0.255 any

! --- VLAN 200 (Sales) ---
ip access-list extended ACL-VLAN200-IN
 10 deny ip 10.1.200.0 0.0.0.255 10.1.99.0 0.0.0.255 log
 20 permit ip 10.1.200.0 0.0.0.255 10.1.100.0 0.0.0.255
 30 permit ip 10.1.200.0 0.0.0.255 10.1.40.0 0.0.0.255
 40 deny ip 10.1.200.0 0.0.0.255 10.1.44.0 0.0.0.255
 50 permit ip 10.1.200.0 0.0.0.255 any

! --- VLAN 300 (Guest) — internet only, block all enterprise subnets ---
! WHY deny 10.0.0.0/8: Covers all enterprise subnets (HQ, Branch, WAN, mgmt)
ip access-list extended ACL-VLAN300-IN
 10 deny ip 10.1.44.0 0.0.0.255 10.1.99.0 0.0.0.255 log
 20 deny ip 10.1.44.0 0.0.0.255 10.0.0.0 0.255.255.255
 30 permit ip 10.1.44.0 0.0.0.255 any

! --- VLAN 400 (Servers) ---
! WHY established on seq 20/30: Servers respond to user sessions; must not initiate to users
! WHY permit Servers → Mgmt (seq 10): Management VLANs need to push configs to servers
ip access-list extended ACL-VLAN400-IN
 10 permit ip 10.1.40.0 0.0.0.255 10.1.99.0 0.0.0.255
 20 permit tcp 10.1.40.0 0.0.0.255 10.1.100.0 0.0.0.255 established
 30 permit tcp 10.1.40.0 0.0.0.255 10.1.200.0 0.0.0.255 established
 40 deny ip 10.1.40.0 0.0.0.255 10.1.100.0 0.0.0.255
 50 deny ip 10.1.40.0 0.0.0.255 10.1.200.0 0.0.0.255
 60 deny ip 10.1.40.0 0.0.0.255 10.1.44.0 0.0.0.255
 70 permit ip 10.1.40.0 0.0.0.255 any

! --- Apply ACLs inbound on each VLAN subinterface ---
! WHY inbound: Filters traffic before routing — more efficient; policy bound to source VLAN
interface Ethernet0/0.100
 ip access-group ACL-VLAN100-IN in

interface Ethernet0/0.200
 ip access-group ACL-VLAN200-IN in

interface Ethernet0/0.300
 ip access-group ACL-VLAN300-IN in

interface Ethernet0/0.400
 ip access-group ACL-VLAN400-IN in

end
write memory
```

**Verification:**
```cisco
show ip access-lists ACL-VLAN100-IN
show ip access-lists ACL-VLAN200-IN
show ip access-lists ACL-VLAN300-IN
show ip access-lists ACL-VLAN400-IN
show ip interface Ethernet0/0.100
show ip interface Ethernet0/0.200
```

**Traffic tests:**
```cisco
! Engineering to Sales — should succeed (seq 20)
ping 10.1.200.1 source 10.1.100.1 repeat 5

! Engineering to Management — should fail with syslog (seq 10)
ping 10.1.99.1 source 10.1.100.1 repeat 5

! Sales to Management — should fail with syslog (seq 10)
ping 10.1.99.1 source 10.1.200.1 repeat 5

! Guest to internal — should fail (seq 20)
ping 10.1.100.1 source 10.1.44.1 repeat 5

! Guest to internet — should succeed (seq 30 + NAT from P05)
ping 203.0.113.100 source 10.1.44.1 repeat 5
```

---

## Phase 6 — Management Plane Hardening

```cisco
! ============================================================
! DEVICE: HQ-RTR1 | PROJECT: 06 | PHASE: 6 — Management Hardening
! ============================================================
enable
configure terminal

! --- Brute-force login protection ---
login block-for 120 attempt 3 within 60

! --- Remove CDP from ISP-facing interface ---
! WHY: CDP broadcasts device model, IOS version, and IP to untrusted external peers
interface Ethernet0/3
 no cdp enable

! --- Console session timeout ---
line console 0
 exec-timeout 10 0

! --- VTY session timeout ---
line vty 0 4
 exec-timeout 15 0

! --- Disable unnecessary services ---
no service tcp-small-servers
no service udp-small-servers
no ip bootp server
no ip http server
no ip http secure-server

end
write memory
```

**Verification:**
```cisco
show login
show cdp interface Ethernet0/3
show running-config | section line console
show running-config | section line vty
show running-config | include no service
```
