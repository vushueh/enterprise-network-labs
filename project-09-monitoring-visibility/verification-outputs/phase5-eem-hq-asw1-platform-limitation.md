# Project 09 - Phase 5 EEM HQ-ASW1 Platform Limitation

Date: 2026-05-17

## Result

Initial Phase 5 EEM test on `HQ-ASW1` could not proceed because the IOL-L2 switch image does not support the `event manager` configuration command.

## Pre-Check Passed

`HQ-ASW1` was otherwise a good low-risk candidate:

- No existing EEM configuration.
- `Ethernet0/3` is a connected VLAN 999 test port.
- Syslog destination is `10.1.99.51`.
- Trap logging is informational.
- Ping to `10.1.99.51` succeeded 5/5.

## Failed Command

```text
HQ-ASW1(config)#event manager applet P09_EEM_ET0_3_LINK_DOWN
                 ^
% Invalid input detected at '^' marker.
```

Related commands also failed because EEM submode did not exist:

```text
event syslog pattern "Interface Ethernet0/3, changed state to down"
action 1.0 syslog msg "P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-ASW1 Ethernet0/3"
```

## Interpretation

This is a platform limitation, not a configuration mistake.

The switch still logged normal interface/config events, but it cannot run EEM applets in this image.

## Next Step

Move Phase 5 EEM pilot to an IOS router, preferably `HQ-RTR1`, where EEM is more likely to be supported.

Use a temporary loopback interface as the trigger target so the EEM test does not interrupt production lab forwarding.
