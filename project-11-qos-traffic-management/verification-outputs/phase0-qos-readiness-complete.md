# Project 11 Phase 0 - QoS Readiness Complete

## Result

Phase 0 is complete. `HQ-RTR1`, `BR-RTR1`, and `WAN-RTR1` are ready for Project 11 QoS work.

## OSPF Health

`HQ-RTR1` has full OSPF neighbors:

```text
10.0.255.2 FULL via Tunnel0
10.0.255.3 FULL via Ethernet0/2
10.0.255.2 FULL via Ethernet0/1
```

`BR-RTR1` has full OSPF neighbors:

```text
10.0.255.1 FULL via Tunnel0
10.0.255.3 FULL via Ethernet0/2
10.0.255.1 FULL via Ethernet0/1
```

`WAN-RTR1` has full OSPF neighbors:

```text
10.0.255.2 FULL via Ethernet0/0
10.0.255.1 FULL via Ethernet0/1
```

## NBAR Support

NBAR classification syntax was accepted on all three pilot routers:

```ios
class-map match-any P11-TEST-NBAR
 match protocol http
```

The temporary test class-map was removed after each test.

## Baseline Latency

`HQ-RTR1` Loopback0 source:

```text
To 10.0.255.2: 20/20, min/avg/max = 1/2/4 ms
To 10.0.255.3: 20/20, min/avg/max = 1/1/2 ms
To 10.2.99.2:  20/20, min/avg/max = 3/3/6 ms
```

`BR-RTR1` Loopback0 source:

```text
To 10.0.255.1: 20/20, min/avg/max = 1/2/6 ms
To 10.0.255.3: 20/20, min/avg/max = 1/1/2 ms
To 10.1.99.11: 20/20, min/avg/max = 2/3/5 ms
```

`WAN-RTR1` Loopback0 source:

```text
To 10.0.255.1: 20/20, min/avg/max = 1/1/2 ms
To 10.0.255.2: 20/20, min/avg/max = 1/1/2 ms
To 10.1.99.11: 20/20, min/avg/max = 2/2/3 ms
To 10.2.99.2:  20/20, min/avg/max = 1/2/3 ms
```

## Existing QoS State

No active MQC policy maps were present on the pilot routers before Project 11 configuration.
