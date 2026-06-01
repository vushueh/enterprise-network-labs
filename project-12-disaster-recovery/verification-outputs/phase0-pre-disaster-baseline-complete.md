# Project 12 Phase 0 - Pre-Disaster Baseline Complete

## Result

All services confirmed operational. Baseline captured. Network is ready for disaster injection.

## OSPF Full Mesh

From `HQ-RTR1`:

```text
Neighbor ID   Pri  State    Dead Time  Address    Interface
10.0.255.2      1  FULL/DR  00:00:38   10.0.0.2   Ethernet0/1
10.0.255.3      1  FULL/DR  00:00:38   10.0.0.6   Ethernet0/2
10.0.255.2      1  FULL/-   00:00:31   10.0.100.2 Tunnel0
```

From `BR-RTR1`:

```text
Neighbor ID   Pri  State    Dead Time  Address    Interface
10.0.255.1      1  FULL/DR  00:00:35   10.0.0.1   Ethernet0/1
10.0.255.3      1  FULL/DR  00:00:39   10.0.0.10  Ethernet0/2
10.0.255.1      1  FULL/-   00:00:28   10.0.100.1 Tunnel0
```

## GRE + IPsec VPN

From `HQ-RTR1`:

```text
show crypto isakmp sa
IPv4 Crypto ISAKMP SA
dst             src             state     conn-id status
10.0.0.2        10.0.0.1        QM_IDLE        1 ACTIVE

show crypto ipsec sa interface Tunnel0
  #pkts encaps: 8241, #pkts encrypt: 8241, #pkts digest: 8241
  #pkts decaps: 8197, #pkts decrypt: 8197, #pkts verify: 8197
```

Encaps and decaps both incrementing — VPN active.

## TACACS+ AAA

From `HQ-RTR1`:

```text
test aaa group tacacs+ admin chongong new-code
Attempting authentication test to server-group tacacs+ using tacacs+
User was successfully authenticated.

test aaa group tacacs+ tacoper oper123 new-code
User was successfully authenticated.
```

## HQ-DSW1 VLANs

```text
show vlan brief

VLAN Name                             Status    Ports
1    default                          active
100  ENGINEERING                      active    Et0/2, Et0/3
200  SALES                            active    Et1/1, Et1/2
300  SERVERS                          active
500  VOICE                            active
999  MANAGEMENT                       active    Et0/0, Et0/1, Et0/2, Et0/3
1000 NATIVE-UNTAGGED                  active
```

## QoS Policy Baseline

From `HQ-RTR1`:

```text
show policy-map interface Ethernet0/0.100
Service-policy input: P11-MARK-IN
  Class-map: P11-VOICE-LIKE (match-any)
    0 packets, 0 bytes
  Class-map: P11-BULK-DATA-ACL (match-any)
    54 packets, 4410 bytes
    54 packets marked dscp af11
  Class-map: class-default (match-any)
    288 packets, 31152 bytes

show policy-map interface Ethernet0/1
Service-policy output: P11-WAN-SHAPE-1M
  shape (average) cir 1000000
  Service-policy : P11-WAN-QUEUE
    Class P11-DSCP-VOICE  priority 30% (300 kbps)
    class-default Fair-queue 17261 packets, 1220362 bytes
```

## Syslog

```text
show logging
Syslog logging: enabled (0 messages dropped, 0 flushes, 0 overruns)
    Console logging: level debugging, 412 messages logged
    Monitor logging: level debugging, 0 messages logged
    Buffer logging:  level debugging, 412 messages logged
    Logging Exception size (8192 bytes)
    Count and timestamp logging messages: disabled
    Logging to 10.1.99.11 (udp port 514, informational), 412 messages lines
```

## Baseline Latency

From `HQ-RTR1` Loopback0:

```text
ping 10.0.255.2 source Loopback0 repeat 20: 20/20, min/avg/max = 1/2/4 ms
ping 10.0.255.3 source Loopback0 repeat 20: 20/20, min/avg/max = 1/1/2 ms
ping 10.1.100.194 source Loopback0 repeat 5: 5/5, min/avg/max = 1/1/2 ms
ping 10.1.99.52 source Loopback0 repeat 5: 5/5, min/avg/max = 1/1/2 ms
```

## Baseline Summary

| Service | Status |
|---|---|
| OSPF full mesh (3 routers) | ✅ All FULL |
| GRE + IPsec VPN | ✅ Encaps/decaps incrementing |
| TACACS+ AAA | ✅ Both users authenticated |
| VLAN 100/200/300/500/999/1000 | ✅ All active on HQ-DSW1 |
| QoS marking + WAN shaping | ✅ Both policies active |
| Syslog to 10.1.99.11 | ✅ Active, 0 drops |
| VLAN 100 host reachability | ✅ 5/5 both hosts |
| Voice VLAN 500 at branch | ✅ BR-ASW1 Et1/0, Et1/1 |

**Baseline complete. Ready for disaster injection.**
