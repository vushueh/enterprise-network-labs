# Project 12 Phase 5 - Runbook And Lessons Learned

## Runbook Summary

This is the condensed rebuild order for future disaster recovery exercises. Memorize this sequence — the correct order prevents blocking yourself.

### Rebuild Order (Fastest Path)

```
1. HQ-RTR1 console
   ├── hostname, SSH keys, local user (5 min)
   ├── interface IPs — Loopback0, E0/0 subinterfaces, E0/1, E0/2, Tunnel0 (7 min)
   ├── OSPF — wait for FULL adjacency before proceeding (6 min)
   ├── IKEv2/IPsec on Tunnel0 (10 min)
   ├── TACACS+ AAA — test aaa before changing vty lines (7 min)
   ├── QoS — class-maps, policy-maps, service-policy (15 min)
   └── Syslog, SNMP, write memory (5 min)

2. HQ-DSW1 console
   ├── hostname, SSH keys, ip routing, local user (3 min)
   ├── VLANs (2 min)
   ├── LACP EtherChannel to HQ-DSW2 (3 min)
   ├── Trunks to HQ-RTR1, HQ-ASW1, HQ-ASW2 (4 min)
   ├── Vlan999 SVI + default gateway (2 min)
   ├── Spanning tree priority (2 min)
   └── AAA + write memory (3 min)

3. Verification pass — all 8 checks (8 min)
```

**Total: ~87 minutes (within 90-minute target)**

### Critical Dependencies

| If you skip this | This breaks |
|---|---|
| OSPF before IPsec | Tunnel0 stays down — no branch reachability |
| `test aaa group tacacs+` before changing vty | VTY lines locked out if TACACS unreachable |
| LACP before trunks | Trunk to HQ-DSW2 never comes up |
| `ip routing` on HQ-DSW1 | SVIs don't route even with correct IP |
| service-policy applied before class-maps exist | service-policy apply is rejected |

## Lessons Learned

### L-01: QoS Config Is The Longest Step

Restoring the QoS policy takes 15 minutes because of the number of class-maps and the correct application order (class-maps before policy-maps before service-policy). For real DR, maintain a saved config template specifically for QoS — paste it as a block.

### L-02: OSPF Must Stabilize Before Verifying IPsec

After configuring the GRE tunnel, wait for OSPF to reach FULL state before testing IPsec. If you test the VPN before OSPF converges, ping failures will mislead you into thinking IPsec is broken when OSPF routing is just still converging.

### L-03: `write memory` Is Not Automatic After Recovery

The reload that caused the disaster wiped startup-config. After recovery, every device must explicitly `write memory`. It is easy to skip this in the time pressure of a rebuild — then the next reload undoes the recovery.

### L-04: test aaa Before Changing vty Lines

Always test TACACS reachability with `test aaa group tacacs+` before applying `login authentication default` to vty lines. If TACACS is still unreachable when you change the vty lines, you lose SSH access and must recover from console.

### L-05: HQ-DSW1 Needs `ip routing` Before SVIs Work

IOL-L2 requires `ip routing` to be explicitly configured before SVIs route packets. Factory default has `no ip routing`. This is the single most common mistake during a rebuild — you configure the VLAN 999 SVI with an IP, try to ping, and it doesn't respond because routing is disabled.

## Future Improvements

1. **Pre-staged config blocks** — maintain a `recovery-configs/` folder with ready-to-paste config blocks for each device. Reduce rebuild time from 87 minutes to under 45 minutes.

2. **Config archive** — Project 09 configured `archive` with TFTP backup on all devices. Test that the archive server is accessible and the latest config is current before the next DR exercise.

3. **Automated verification script** — a Python/Netmiko script that runs the 8 post-recovery checks and produces a pass/fail report in one command.
