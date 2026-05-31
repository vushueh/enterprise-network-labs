# Project 11 Phase 7 - AutoQoS Comparison On Branch Test Port

## Goal

Attempt AutoQoS on an unused `BR-ASW1` port to compare Cisco's automatic QoS template against the manual MQC design built in earlier phases.

## Test Device

- Device: `BR-ASW1`
- Interface: `Ethernet1/2` (unused, shutdown)

## Pre-Test State

```ios
interface Ethernet1/2
 description UNUSED
 shutdown
```

No policy maps present. Only `class-default` in `show class-map`.

## AutoQoS Test Commands

```ios
show auto qos
show mls qos

interface Ethernet1/2
 auto qos ?
 auto qos
```

## Result

All AutoQoS commands rejected:

```text
show auto qos
              ^
% Invalid input detected at '^' marker.

show mls qos
             ^
% Invalid input detected at '^' marker.

auto qos
                   ^
% Invalid input detected at '^' marker.
```

## Conclusion

IOL-L2 does not support AutoQoS. Phase 7 is documented as a platform limitation.

The manual MQC design from Project 11 (NBAR/ACL classification, DSCP marking, HQoS shaping/queuing) is the working design and is more portable and transparent than AutoQoS for this lab platform.
