# ISP-RTR1 — Project 07 Changes

**Device:** ISP-RTR1 (IOL router)
**Project:** 07 — ASAv Perimeter Firewall
**Date:** 2026-05-04

ISP-RTR1 IP addressing is unchanged. Only the interface description and a static host route for the DMZ server public IP are updated.

---

## Phase 1 — Update Interface Description

```cisco
! ============================================================
! DEVICE: ISP-RTR1 | PROJECT: 07 — ASAv Perimeter Firewall
! PHASE: 1 — ISP handoff now faces HQ-FW1
! ============================================================
enable
configure terminal

! --- Update description — IP 203.0.113.2/30 is unchanged ---
! WHY: E0/0 previously connected to HQ-RTR1. Now faces HQ-FW1 Gi0/1.
!      IP stays the same; only the far-end device changed.
interface Ethernet0/0
 description OUTSIDE-TO-HQ-FW1-GI0/1
 no shutdown

! --- Static route for HQ-SRV1 public IP ---
! WHY: ISP-RTR1 must know how to reach 203.0.113.10 (static NAT public IP).
!      Without this, inbound traffic to the DMZ server is black-holed at ISP
!      before it even reaches the firewall.
ip route 203.0.113.10 255.255.255.255 203.0.113.1

end
write memory

! --- VERIFICATION ---
! show ip route 203.0.113.10    → Static host route via 203.0.113.1 (HQ-FW1 outside)
! ping 203.0.113.1              → HQ-FW1 outside interface responds
! ping 203.0.113.10             → Reaches HQ-SRV1 in DMZ via static NAT (after Phase 3 ACL)
```
