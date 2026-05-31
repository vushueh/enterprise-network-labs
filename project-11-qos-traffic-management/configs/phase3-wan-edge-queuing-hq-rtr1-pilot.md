# Project 11 Phase 3 - WAN Edge Queuing And Shaping Pilot On HQ-RTR1

## Goal

Apply an outbound QoS policy on one WAN-facing interface of `HQ-RTR1` so marked traffic receives different treatment when leaving the router.

Pilot interface:

```ios
interface Ethernet0/1
 description WAN-TO-BR-RTR1-E0/1
```

## Design

Phase 2 marked traffic with DSCP values. Phase 3 uses those markings for outbound queuing.

| Output Class | Match | Treatment |
|---|---|---|
| `P11-DSCP-VOICE` | DSCP `ef` | Low-latency priority queue, 30% |
| `P11-DSCP-SIGNALING` | DSCP `cs3` | Bandwidth guarantee, 10% |
| `P11-DSCP-NETWORK-CONTROL` | DSCP `cs2` | Bandwidth guarantee, 5% |
| `P11-DSCP-BULK` | DSCP `af11` | Bandwidth guarantee, 15% |
| `class-default` | Everything else | Fair queue |

The child queuing policy is nested under a parent shaping policy:

```text
P11-WAN-SHAPE-1M
  shape average 1000000
  service-policy P11-WAN-QUEUE
```

## Phase 3A - Syntax Precheck Only

Run this first on `HQ-RTR1`. It creates and removes temporary policy components.

```ios
configure terminal
!
class-map match-any P11-PRECHECK-DSCP-EF
 match dscp ef
!
policy-map P11-PRECHECK-QUEUE
 class P11-PRECHECK-DSCP-EF
  priority percent 30
 class class-default
  fair-queue
!
policy-map P11-PRECHECK-SHAPE
 class class-default
  shape average 1000000
  service-policy P11-PRECHECK-QUEUE
!
no policy-map P11-PRECHECK-SHAPE
no policy-map P11-PRECHECK-QUEUE
no class-map match-any P11-PRECHECK-DSCP-EF
end
```

If any command is rejected, stop and paste the error.

## Phase 3B - Apply Pilot Policy

Only apply this after the precheck passes.

```ios
configure terminal
!
class-map match-any P11-DSCP-VOICE
 description P11 WAN queue match for DSCP EF
 match dscp ef
!
class-map match-any P11-DSCP-SIGNALING
 description P11 WAN queue match for DSCP CS3
 match dscp cs3
!
class-map match-any P11-DSCP-NETWORK-CONTROL
 description P11 WAN queue match for DSCP CS2
 match dscp cs2
!
class-map match-any P11-DSCP-BULK
 description P11 WAN queue match for DSCP AF11
 match dscp af11
!
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
!
policy-map P11-WAN-SHAPE-1M
 class class-default
  shape average 1000000
  service-policy P11-WAN-QUEUE
!
interface Ethernet0/1
 service-policy output P11-WAN-SHAPE-1M
!
end
```

## Verification

```ios
show policy-map
show running-config | section policy-map
show running-config interface Ethernet0/1
show policy-map interface Ethernet0/1
ping 10.0.255.2 source Loopback0 repeat 10
ping 10.0.255.3 source Loopback0 repeat 10
show policy-map interface Ethernet0/1
```

## Rollback

```ios
configure terminal
interface Ethernet0/1
 no service-policy output P11-WAN-SHAPE-1M
exit
no policy-map P11-WAN-SHAPE-1M
no policy-map P11-WAN-QUEUE
no class-map match-any P11-DSCP-VOICE
no class-map match-any P11-DSCP-SIGNALING
no class-map match-any P11-DSCP-NETWORK-CONTROL
no class-map match-any P11-DSCP-BULK
end
```
