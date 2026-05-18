# Project 09 - Phase 5 EEM HQ-RTR1 Registration Summary

Date: 2026-05-17

## Result

`HQ-RTR1` supports EEM and the Phase 5 applet is registered.

## Registered Applet

```text
event manager applet P09_EEM_LOOP99_DOWN
 event syslog pattern "Interface Loopback99, changed state to administratively down"
 action 1.0 syslog priority warnings msg "P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99"
```

## Policy Registration Proof

```text
No.  Class     Type    Event Type          Trap  Time Registered           Name
1    applet    user    syslog              Off   Sun May 17 17:58:08 2026  P09_EEM_LOOP99_DOWN
 pattern {Interface Loopback99, changed state to administratively down}
 maxrun 20.000
 action 1.0 syslog priority warnings msg "P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99"
```

## Syslog Reachability

`HQ-RTR1` has logging host `10.1.99.51` configured and can ping HQ-SYSLOG from Loopback0.

## Next Step

Trigger the applet by shutting and restoring `Loopback99`, then verify the `P09_PHASE5_EEM_LINK_DOWN_DETECTED` marker appears locally and on HQ-SYSLOG.
