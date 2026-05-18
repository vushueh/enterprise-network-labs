# Project 09 - Phase 7 Complete Summary

Date: 2026-05-17

## Result

Phase 7 is complete.

The controlled monitoring event on `HQ-RTR1` was correlated across:

- Local syslog
- EEM
- HQ-SYSLOG collector
- SNMP device-side trap counters
- NetFlow device-side export/cache counters

## Controlled Event

Device: `HQ-RTR1`

Test interface:

```text
Loopback99
```

Trigger:

```text
interface Loopback99
 shutdown
```

Restore:

```text
interface Loopback99
 no shutdown
```

## Local Syslog And EEM Proof

```text
001908: May 17 23:44:16.407 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to down
001909: May 17 23:44:16.407 UTC: %LINK-5-CHANGED: Interface Loopback99, changed state to administratively down
001910: May 17 23:44:16.410 UTC: %HA_EM-4-LOG: P09_EEM_LOOP99_DOWN: P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99
001912: May 17 23:44:45.096 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to up
001913: May 17 23:44:45.096 UTC: %LINK-3-UPDOWN: Interface Loopback99, changed state to up
```

EEM history:

```text
No.  Job Id Proc Status   Time of Event            Event Type        Name
1    1      Actv success  Sun May17 18:06:42 2026  syslog            applet: P09_EEM_LOOP99_DOWN
2    2      Actv success  Sun May17 23:44:16 2026  syslog            applet: P09_EEM_LOOP99_DOWN
```

## HQ-SYSLOG Collector Proof

HQ-SYSLOG received the EEM marker from `HQ-RTR1` Loopback0 source `10.0.255.1`:

```text
May 17 23:44:17 10.0.255.1 001910: May 17 23:44:16.410 UTC: %HA_EM-4-LOG: P09_EEM_LOOP99_DOWN: P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99
May 17 23:44:46 10.0.255.1 001913: May 17 23:44:45.096 UTC: %LINK-3-UPDOWN: Interface Loopback99, changed state to up
```

## SNMP Device-Side Proof

SNMP trap counters increased during the event:

```text
10 SNMP packets output
10 Trap PDUs
Logging to 10.1.99.51.162, 0/10, 10 sent, 0 dropped.
```

Collector-side SNMP proof remains unavailable because HQ-SYSLOG does not run an SNMP trap receiver.

## NetFlow Device-Side Proof

NetFlow export remained healthy:

```text
5727 flows exported in 1463 udp datagrams
0 flows failed due to lack of export packet
0 export packets were dropped due to no fib
0 export packets were dropped due to adjacency issues
0 export packets were dropped due to fragmentation failures
0 export packets were dropped due to encapsulation fixup failures
```

NetFlow collector-side proof remains unavailable because HQ-SYSLOG does not run a NetFlow collector.

## Interpretation

The same controlled event was visible locally on `HQ-RTR1` and remotely on HQ-SYSLOG. Device-side SNMP and NetFlow counters confirm that the monitoring services remained active and healthy during the event.
