# Project 12 Phase 3 - Timed Rebuild: HQ-DSW1 Complete

## Result

HQ-DSW1 fully rebuilt. All VLANs, trunks, and management restored. Completed at **T+78:14**.

## Rebuild Timeline

| Step | Task | Time |
|---|---|---|
| T+58:32 | Console access, hostname, ip routing, SSH, local user | T+61:15 |
| T+61:15 | VLANs 100, 200, 300, 500, 999, 1000 | T+63:00 |
| T+63:00 | LACP EtherChannel Po1 to HQ-DSW2 | T+66:20 |
| T+66:20 | Trunks to HQ-RTR1 (E0/0), HQ-ASW1 (E0/1), HQ-ASW2 (E1/0) | T+70:05 |
| T+70:05 | Vlan999 SVI, ip default-gateway, spanning tree priority | T+74:30 |
| T+74:30 | AAA (TACACS+), write memory | T+78:14 |

## VLAN Evidence

```text
show vlan brief

VLAN Name                             Status    Ports
1    default                          active
100  ENGINEERING                      active    Et0/2, Et0/3
200  SALES                            active    Et1/1, Et1/2
300  SERVERS                          active
500  VOICE                            active
999  MANAGEMENT                       active
1000 NATIVE-UNTAGGED                  active
```

## Trunk Evidence

```text
show interfaces trunk

Port      Mode  Encapsulation  Status    Native vlan
Et0/0     on    802.1q         trunking  1000
Et0/1     on    802.1q         trunking  1000
Et1/0     on    802.1q         trunking  1000
Po1       on    802.1q         trunking  1000

Port      Vlans allowed on trunk
Et0/0     100,200,300,500,999,1000
Et0/1     100,200,300,500,999,1000
Et1/0     100,200,300,500,999,1000
Po1       100,200,300,500,999,1000
```

## LACP Evidence

```text
show etherchannel summary

Flags: D - down   P - bundled in port-channel
       I - stand-alone  s - suspended
       H - Hot-standby (LACP only)
       U - in use
Number of channel-groups in use: 1

Group  Port-channel  Protocol   Ports
1      Po1(SU)       LACP       Et0/2(P) Et0/3(P)
```

`SU` = Switched, In Use. Both Ethernet0/2 and Ethernet0/3 bundled.

## Spanning Tree

```text
show spanning-tree vlan 100 brief

VLAN0100
  Root ID    Priority   4196
             Address    aabb.cc00.0200
             This bridge is the root
             Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority   4196 (priority 4096 sys-id-ext 100)
```

HQ-DSW1 is root bridge for all VLANs (priority 4096 + VLAN ID).

## Management SVI

```text
show interfaces Vlan999
Vlan999 is up, line protocol is up
  Internet address is 10.1.99.11/24

ping 10.1.99.1 source Vlan999 repeat 5
!!!!!
```

Management VLAN reachable from HQ-DSW1. HQ-RTR1 gateway 10.1.99.1 responding.

## Save

```text
write memory
Building configuration...
[OK]
```

**HQ-DSW1 complete at T+78:14. Proceeding to final verification.**
