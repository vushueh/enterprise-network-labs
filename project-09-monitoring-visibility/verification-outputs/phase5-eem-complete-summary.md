# Project 09 - Phase 5 EEM Complete Summary

Date: 2026-05-17

## Result

Phase 5 is complete from the device side.

`HQ-RTR1` successfully used Embedded Event Manager (EEM) to react to a syslog event and generate a custom syslog marker.

## Platform Lesson

The original low-risk pilot target, `HQ-ASW1`, could not run EEM because the IOL-L2 image does not support the `event manager` configuration command.

The phase was moved to `HQ-RTR1`, where EEM is supported.

## Working Applet

```text
event manager applet P09_EEM_LOOP99_DOWN
 event syslog pattern "Line protocol on Interface Loopback99, changed state to down"
 action 1.0 syslog priority warnings msg "P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99"
```

## Test Method

A temporary loopback was used so no production lab link had to be interrupted:

```text
interface Loopback99
 shutdown
 no shutdown
```

## Device-Side Proof

Local log output:

```text
001850: May 17 18:06:42.919 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to down
001851: May 17 18:06:42.919 UTC: %LINK-5-CHANGED: Interface Loopback99, changed state to administratively down
001852: May 17 18:06:42.922 UTC: %HA_EM-4-LOG: P09_EEM_LOOP99_DOWN: P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99
001854: May 17 18:06:59.117 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to up
001855: May 17 18:06:59.117 UTC: %LINK-3-UPDOWN: Interface Loopback99, changed state to up
```

EEM history:

```text
No.  Job Id Proc Status   Time of Event            Event Type        Name
1    1      Actv success  Sun May17 18:06:42 2026  syslog            applet: P09_EEM_LOOP99_DOWN
```

## Interpretation

The first EEM pattern was too specific and did not match this IOS image's actual syslog format.

The working pattern matches the actual emitted message:

```text
Line protocol on Interface Loopback99, changed state to down
```

This confirms that EEM pattern matching is literal and platform message wording matters.

## Remaining Optional Collector Check

On HQ-SYSLOG, confirm the marker appears from `10.0.255.1`:

```text
P09_PHASE5_EEM_LINK_DOWN_DETECTED
```
