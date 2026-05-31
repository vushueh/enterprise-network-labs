# Project 11 Phase 4 - Policy Map Verification On HQ-RTR1

## Goal

Verify that both the input marking policy and the output WAN shaping/queuing policy are operating correctly on `HQ-RTR1`. Interpret counter output and confirm no drops.

## Verification Commands

```ios
show policy-map interface Ethernet0/0.100
show policy-map interface Ethernet0/1
show interfaces Ethernet0/1
```

## Expected Output

### Input Policy (Ethernet0/0.100)

```text
Service-policy input: P11-MARK-IN

Class-map: P11-VOICE-LIKE        match protocol rtp  -> set dscp ef
Class-map: P11-SIGNALING         match protocol sip  -> set dscp cs3
Class-map: P11-NETWORK-CONTROL   match ospf,dns      -> set dscp cs2
Class-map: P11-BULK-DATA         match ftp,http      -> set dscp af11
Class-map: class-default         match any
```

### Output Policy (Ethernet0/1)

```text
Service-policy output: P11-WAN-SHAPE-1M
  shape (average) cir 1000000
  Service-policy : P11-WAN-QUEUE
    Class P11-DSCP-VOICE           dscp ef   priority 30% (300 kbps)
    Class P11-DSCP-SIGNALING       dscp cs3  bandwidth 10% (100 kbps)
    Class P11-DSCP-NETWORK-CONTROL dscp cs2  bandwidth 5% (50 kbps)
    Class P11-DSCP-BULK            dscp af11 bandwidth 15% (150 kbps)
    Class class-default            fair-queue
```

## Counter Interpretation

- Zero counters on NBAR classes are expected at this stage — no matching protocol traffic generated yet.
- `class-default` counter increase confirms the policy is active and seeing traffic.
- `Queueing strategy: Class-based queueing` on `show interfaces Ethernet0/1` confirms HQoS is active.
- Zero drops confirms the shaper is not causing congestion under test conditions.
