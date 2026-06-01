# Project 12 Phase 2 - Timed Rebuild: HQ-RTR1 Complete

## Result

HQ-RTR1 fully rebuilt. All services restored. Completed at **T+58:32**.

## Rebuild Timeline

| Step | Task | Time |
|---|---|---|
| T+00:00 | Console access, hostname, SSH keys, local user | T+04:48 |
| T+04:48 | Interface addressing — Loopback0, all subinterfaces, WAN, Tunnel0 | T+11:55 |
| T+11:55 | OSPF configured, waiting for FULL adjacency | T+17:40 |
| T+17:40 | IKEv2/IPsec profile restored on Tunnel0 | T+27:12 |
| T+27:12 | TACACS+ AAA — Phase A applied, test aaa passed, Phase B applied | T+34:05 |
| T+34:05 | QoS — all class-maps, policy-maps, service-policy applied | T+49:30 |
| T+49:30 | Syslog, SNMP, write memory | T+55:10 |
| T+55:10 | Spot verification — OSPF, pings, VPN, TACACS | T+58:32 |

## OSPF Restoration Evidence

At T+17:40, adjacencies reformed:

```text
show ip ospf neighbor
Neighbor ID   Pri  State    Dead Time  Address    Interface
10.0.255.2      1  FULL/DR  00:00:38   10.0.0.2   Ethernet0/1
10.0.255.3      1  FULL/DR  00:00:35   10.0.0.6   Ethernet0/2
10.0.255.2      1  FULL/-   00:00:30   10.0.100.2 Tunnel0
```

All three adjacencies FULL.

## IPsec VPN Evidence

At T+27:12:

```text
show crypto isakmp sa
dst             src             state     conn-id status
10.0.0.2        10.0.0.1        QM_IDLE        1 ACTIVE

show crypto ipsec sa
#pkts encaps: 42, #pkts encrypt: 42
#pkts decaps: 38, #pkts decrypt: 38
```

Encaps and decaps incrementing after ping test. Tunnel0 operational.

## TACACS+ Evidence

At T+34:05:

```text
test aaa group tacacs+ admin chongong new-code
User was successfully authenticated.

test aaa group tacacs+ tacoper oper123 new-code
User was successfully authenticated.
```

Phase B applied (vty login authentication default). New SSH session confirmed at priv 15.

## QoS Evidence

At T+49:30:

```text
show policy-map interface Ethernet0/0.100
Service-policy input: P11-MARK-IN  -> present

show policy-map interface Ethernet0/1
Service-policy output: P11-WAN-SHAPE-1M
  shape (average) cir 1000000
  Service-policy : P11-WAN-QUEUE  -> nested correctly
```

## Save

```text
write memory
Building configuration...
[OK]
```

## HQ-RTR1 Status At T+58:32

| Service | Status |
|---|---|
| Interfaces up | ✅ All expected interfaces up/up |
| OSPF full mesh | ✅ 3 FULL adjacencies |
| GRE/IPsec VPN | ✅ QM_IDLE, encaps/decaps active |
| TACACS+ AAA | ✅ Both test aaa passed, SSH at priv 15 |
| QoS marking + shaping | ✅ Both service-policies applied |
| Syslog | ✅ Logging to 10.1.99.11 restored |
| write memory | ✅ Startup-config restored |

Proceeding to HQ-DSW1 rebuild.
