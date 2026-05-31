# Project 11 Phase 2 - DSCP Marking Complete On HQ-RTR1

## Result

Phase 2 is complete on `HQ-RTR1`.

## Policy Applied

The input marking policy is attached to the VLAN 100 gateway interface:

```ios
interface Ethernet0/0.100
 service-policy input P11-MARK-IN
```

The policy-map contains the intended DSCP actions:

```ios
policy-map P11-MARK-IN
 class P11-VOICE-LIKE
  set dscp ef
 class P11-SIGNALING
  set dscp cs3
 class P11-NETWORK-CONTROL
  set dscp cs2
 class P11-BULK-DATA
  set dscp af11
```

`class-default` is not explicitly remarked. This avoids rewriting all unmatched traffic during the pilot.

## VLAN 100 Connectivity

Two VLAN 100 hosts were discovered:

```text
10.1.100.170
10.1.100.194
```

Both responded from the VLAN 100 gateway source:

```text
ping 10.1.100.170 source 10.1.100.1 repeat 5 -> 5/5, min/avg/max = 3/3/5 ms
ping 10.1.100.194 source 10.1.100.1 repeat 5 -> 5/5, min/avg/max = 4/4/6 ms
```

## Policy Counter Check

`show policy-map interface Ethernet0/0.100` displayed all configured classes.

NBAR class counters remained at zero because no matching RTP, SIP, DNS, FTP, or HTTP test traffic was generated yet. `class-default` saw traffic:

```text
class-default
  16 packets, 2052 bytes
```

This confirms the service-policy is active and seeing inbound traffic without breaking VLAN 100 connectivity.

## Save

The configuration was saved with `write memory`.
