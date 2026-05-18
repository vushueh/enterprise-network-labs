# Project 09 - Phase 7 Device-Side Verification Summary

Date: 2026-05-17

## Result

Phase 7 device-side verification is complete.

`HQ-RTR1` successfully generated a controlled monitoring event using `Loopback99`, and the event was visible across device-side syslog/EEM, SNMP trap counters, and NetFlow health counters.

## Pre-Check

`Loopback99` exists:

```text
interface Loopback99
 description P09-PHASE5-EEM-TEST-INTERFACE
 ip address 10.255.99.99 255.255.255.255
```

EEM applet exists:

```text
event manager applet P09_EEM_LOOP99_DOWN
 event syslog pattern "Line protocol on Interface Loopback99, changed state to down"
 action 1.0 syslog priority warnings msg "P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99"
```

Syslog destination:

```text
Logging to 10.1.99.51 (udp port 514)
Trap logging: level warnings
```

## NetFlow Baseline

Traffic was generated across the tunnel path:

```text
ping 10.2.100.1 source 10.1.100.1 repeat 20
Success rate is 100 percent (20/20)
```

Baseline NetFlow:

```text
5715 flows exported in 1459 udp datagrams
0 flows failed due to lack of export packet
0 export packets were dropped due to no fib
0 export packets were dropped due to adjacency issues
0 export packets were dropped due to fragmentation failures
0 export packets were dropped due to encapsulation fixup failures
```

## Controlled Failure

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

## Syslog And EEM Proof

Local logging:

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

## SNMP Device-Side Proof

SNMP trap counters increased from pre-check `6 sent, 0 dropped` to:

```text
10 SNMP packets output
10 Trap PDUs
Logging to 10.1.99.51.162, 0/10, 10 sent, 0 dropped.
```

This confirms the device transmitted additional SNMP traps during the event. Collector-side SNMP trap proof is not possible on the current HQ-SYSLOG node because no SNMP trap receiver is installed.

## NetFlow Device-Side Proof

Post-event NetFlow:

```text
5727 flows exported in 1463 udp datagrams
0 flows failed due to lack of export packet
0 export packets were dropped due to no fib
0 export packets were dropped due to adjacency issues
0 export packets were dropped due to fragmentation failures
0 export packets were dropped due to encapsulation fixup failures
```

Flow export remained healthy before, during, and after the monitoring event.

## Remaining Collector Check

Confirm on HQ-SYSLOG that the EEM marker appears from `10.0.255.1`:

```text
P09_PHASE5_EEM_LINK_DOWN_DETECTED
```

If present, Phase 7 is complete.
