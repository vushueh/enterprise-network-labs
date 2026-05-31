# Project 11 Phase 4 - Policy Map Verification Complete On HQ-RTR1

## Result

Phase 4 is complete on `HQ-RTR1`.

## Input Marking Policy - Ethernet0/0.100

The input service-policy is visible:

```text
Service-policy input: P11-MARK-IN
```

Classes are present:

```text
P11-VOICE-LIKE       match protocol rtp  -> set dscp ef
P11-SIGNALING        match protocol sip  -> set dscp cs3
P11-NETWORK-CONTROL  match ospf,dns      -> set dscp cs2
P11-BULK-DATA        match ftp,http      -> set dscp af11
class-default        match any
```

Counters:

```text
P11-VOICE-LIKE       0 packets
P11-SIGNALING        0 packets
P11-NETWORK-CONTROL  0 packets
P11-BULK-DATA        0 packets
class-default        16 packets, 2052 bytes
```

Zero NBAR counters are expected — no matching protocol traffic generated from VLAN 100 yet. `class-default` counters prove the policy is active.

## Output WAN Policy - Ethernet0/1

Parent policy:

```text
Service-policy output: P11-WAN-SHAPE-1M
shape (average) cir 1000000
target shape rate 1000000
```

Child policy nested correctly:

```text
Service-policy : P11-WAN-QUEUE
P11-DSCP-VOICE            dscp ef   priority 30% (300 kbps)
P11-DSCP-SIGNALING        dscp cs3  bandwidth 10% (100 kbps)
P11-DSCP-NETWORK-CONTROL  dscp cs2  bandwidth 5% (50 kbps)
P11-DSCP-BULK             dscp af11 bandwidth 15% (150 kbps)
class-default             fair-queue
```

Counters:

```text
Parent class-default: 1568 packets, 111544 bytes
Parent drop rate: 0 bps
Queue depth/total drops/no-buffer drops: 0/0/0
Child class-default: 1568 packets, 111544 bytes
Child class-default drops/flowdrops: 0/0/0/0
```

No drops occurring. Normal traffic using class-default. Shaper active.

## Interface Queue Health

`show interfaces Ethernet0/1`:

```text
Queueing strategy: Class-based queueing
Input queue drops: 0
Total output drops: 0
Output queue drops: 0
5 minute input rate: 5000 bps
5 minute output rate: 4000 bps
```

`Class-based queueing` confirms HQoS is active on the interface.
