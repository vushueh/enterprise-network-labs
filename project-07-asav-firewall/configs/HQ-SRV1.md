# HQ-SRV1 — Project 07 DMZ Migration

**Device:** HQ-SRV1 (Nginx/Alpine)
**Project:** 07 — ASAv Perimeter Firewall
**Date:** 2026-05-04

HQ-SRV1 moves from VLAN 400 (connected to HQ-DSW1) to the ASAv DMZ (connected to HQ-FW1 Gi0/2). New IP: 10.1.40.10/24. New gateway: 10.1.40.1 (HQ-FW1 DMZ interface).

---

## Phase 1 — Re-IP for DMZ Segment

```bash
# ============================================================
# DEVICE: HQ-SRV1 | PROJECT: 07 — ASAv Perimeter Firewall
# PHASE: 1 — Move from VLAN 400 to Firewall DMZ
# ============================================================

# Flush old VLAN 400 address
ip addr flush dev eth0

# Set new DMZ address
ip address add 10.1.40.10/24 dev eth0
ip link set dev eth0 up

# Set default gateway to HQ-FW1 DMZ interface
ip route replace default via 10.1.40.1

# VERIFICATION
ip addr show eth0
# Expected: inet 10.1.40.10/24

ip route show
# Expected: default via 10.1.40.1

ping -c 3 10.1.40.1
# Expected: 100% success (HQ-FW1 DMZ interface responds)
```
