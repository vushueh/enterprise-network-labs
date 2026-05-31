# Project 11 Phase 7 - AutoQoS Platform Limitation Complete

## Result

Phase 7 was completed as a platform limitation. No AutoQoS configuration was applied.

## Test Device And Port

- Device: `BR-ASW1`
- Interface: `Ethernet1/2` (unused, shutdown)

## AutoQoS Test Output

```text
show auto qos
              ^
% Invalid input detected at '^' marker.

show mls qos
             ^
% Invalid input detected at '^' marker.

interface Ethernet1/2
 auto qos
                   ^
% Invalid input detected at '^' marker.
```

## Verdict

The IOL-L2 image does not support AutoQoS commands.

## Phase 7 Objective Met

- Verified AutoQoS is not available on this platform.
- Avoided applying unverified configuration to active links.
- Confirmed why manual MQC QoS is more portable and transparent in this lab.

## Manual QoS Summary (Working Design)

| Component | Device | Config |
|---|---|---|
| NBAR/ACL classification | HQ-RTR1 | 4 NBAR class-maps + 1 ACL fallback class-map |
| DSCP marking (inbound) | HQ-RTR1 | P11-MARK-IN on Ethernet0/0.100 |
| WAN shaping | HQ-RTR1 | P11-WAN-SHAPE-1M on Ethernet0/1 (1 Mbps) |
| WAN queuing (child) | HQ-RTR1 | P11-WAN-QUEUE nested under shaper |
| Voice VLAN | BR-ASW1 | switchport voice vlan 500 on Ethernet1/0, Ethernet1/1 |
