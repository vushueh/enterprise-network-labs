# Project 11 Phase 3 - WAN Edge Queuing Complete On HQ-RTR1

## Status

`P11-WAN-SHAPE-1M` was successfully applied outbound on `HQ-RTR1 Ethernet0/1`, verified, and saved.

## Policy Applied

Interface:

```ios
interface Ethernet0/1
 description WAN-TO-BR-RTR1-E0/1
 service-policy output P11-WAN-SHAPE-1M
```

Parent policy:

```ios
policy-map P11-WAN-SHAPE-1M
 class class-default
  shape average 1000000
  service-policy P11-WAN-QUEUE
```

Child policy:

```ios
policy-map P11-WAN-QUEUE
 class P11-DSCP-VOICE
  priority percent 30
 class P11-DSCP-SIGNALING
  bandwidth percent 10
 class P11-DSCP-NETWORK-CONTROL
  bandwidth percent 5
 class P11-DSCP-BULK
  bandwidth percent 15
 class class-default
  fair-queue
```

## Verification

`show policy-map interface Ethernet0/1` confirmed:

```text
Service-policy output: P11-WAN-SHAPE-1M
shape (average) cir 1000000
Service-policy : P11-WAN-QUEUE
P11-DSCP-VOICE priority 30% (300 kbps)
P11-DSCP-SIGNALING bandwidth 10% (100 kbps)
P11-DSCP-NETWORK-CONTROL bandwidth 5% (50 kbps)
P11-DSCP-BULK bandwidth 15% (150 kbps)
class-default Fair-queue
```

Connectivity remained healthy:

```text
ping 10.0.255.2 source Loopback0 repeat 10 -> 10/10
ping 10.0.255.3 source Loopback0 repeat 10 -> 10/10
```

`class-default` counters increased from 78 to 278 packets, confirming traffic traverses the output policy. DSCP-specific class counters remain zero until marked matching traffic is generated.

## Save

The configuration was saved with `write memory`.
