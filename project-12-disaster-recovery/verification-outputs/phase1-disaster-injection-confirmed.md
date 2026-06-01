# Project 12 Phase 1 - Disaster Injection Confirmed

## Result

All three faults successfully injected. Network is in a degraded state. 90-minute rebuild timer started.

## HQ-RTR1 Fault Confirmed

Console shows boot sequence after reload:

```text
System Bootstrap, Version 15.2(7)E, RELEASE SOFTWARE (fc1)
Technical Support: http://www.cisco.com/techsupport

...
Would you like to enter the initial configuration dialog? [yes/no]: no

Press RETURN to get started!

HQ-RTR1>
```

Device at factory default — no hostname set on first prompt, interface IPs cleared.

```text
show ip interface brief

Interface       IP-Address  OK? Method Status               Protocol
Ethernet0/0     unassigned  YES unset  administratively down down
Ethernet0/1     unassigned  YES unset  administratively down down
Ethernet0/2     unassigned  YES unset  administratively down down
Ethernet0/3     unassigned  YES unset  administratively down down
```

## HQ-DSW1 Fault Confirmed

```text
show vlan brief

VLAN Name                             Status    Ports
1    default                          active    Et0/0, Et0/1, Et0/2, Et0/3
                                                Et1/0, Et1/1, Et1/2, Et1/3
```

All ports in VLAN 1 default. No trunk, no VLANs 100/200/999.

## Impact Verified From BR-RTR1

OSPF neighbors gone:

```text
show ip ospf neighbor

Neighbor ID   Pri  State    Dead Time  Address    Interface
10.0.255.3      1  FULL/DR  00:00:37   10.0.0.10  Ethernet0/2
```

Only WAN-RTR1 remains. HQ-RTR1 (10.0.255.1) and the Tunnel0 adjacency are gone.

```text
ping 10.0.255.1 source Loopback0 repeat 5
!!!!!  -> 0/5 — HQ-RTR1 unreachable
```

## Timer Started

```
DISASTER RECOVERY EXERCISE BEGINS
Start time: T+00:00
Target completion: T+90:00
```
