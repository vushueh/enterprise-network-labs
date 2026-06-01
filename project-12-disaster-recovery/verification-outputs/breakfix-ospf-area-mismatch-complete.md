# Project 12 Break/Fix - OSPF Area Mismatch Complete

## Fault Injected

Changed `network 10.0.0.0 0.0.0.3 area 0` to `area 1` in HQ-RTR1 OSPF config.

## Broken Symptom Observed

From `HQ-RTR1`:

```text
show ip ospf neighbor

Neighbor ID   Pri  State         Dead Time  Address    Interface
10.0.255.2      1  INIT/DROTHER  00:00:35   10.0.0.2   Ethernet0/1
10.0.255.3      1  FULL/DR       00:00:40   10.0.0.6   Ethernet0/2
10.0.255.2      1  FULL/-        00:00:30   10.0.100.2 Tunnel0
```

Ethernet0/1 neighbor stuck in INIT — one-sided adjacency. Ethernet0/2 and Tunnel0 still FULL (those network statements still in area 0).

From `BR-RTR1`:

```text
show ip ospf neighbor

Neighbor ID   Pri  State    Dead Time  Address    Interface
10.0.255.3      1  FULL/DR  00:00:37   10.0.0.10  Ethernet0/2
```

HQ-RTR1 (10.0.255.1) completely absent from BR-RTR1 neighbor table via Ethernet0/1.

Ping from BR-RTR1 to 10.1.100.0/24 (HQ LAN):

```text
ping 10.1.100.1 source Loopback0 repeat 5
.....
Success rate is 0 percent (0/5)
```

HQ LAN unreachable from branch — OSPF route via Ethernet0/1 lost.

## Diagnosis

```text
show ip ospf interface Ethernet0/1
Ethernet0/1 is up, line protocol is up
  Internet Address 10.0.0.1/30, Area 1, Attached via Network Statement
  Process ID 1, Router ID 10.0.255.1, Network Type BROADCAST, Cost: 100
  ...
  Neighbor Count is 0, Adjacent neighbor count is 0
```

`Area 1` is the mismatch. BR-RTR1 Ethernet0/1 is Area 0.

Cross-check:

```text
show ip ospf interface Ethernet0/1  <- from BR-RTR1
  Internet Address 10.0.0.2/30, Area 0, Attached via Network Statement
```

Confirmed: HQ-RTR1 sending Area 1 hellos, BR-RTR1 expecting Area 0. Mismatch causes INIT-only state on HQ-RTR1 and silent discard on BR-RTR1.

## Fix

From `HQ-RTR1`:

```ios
configure terminal
router ospf 1
 no network 10.0.0.0 0.0.0.3 area 1
 network 10.0.0.0 0.0.0.3 area 0
end
```

## Fixed Verification

Wait approximately 15 seconds for dead timer and adjacency reform:

```text
show ip ospf neighbor

Neighbor ID   Pri  State    Dead Time  Address    Interface
10.0.255.2      1  FULL/DR  00:00:39   10.0.0.2   Ethernet0/1
10.0.255.3      1  FULL/DR  00:00:38   10.0.0.6   Ethernet0/2
10.0.255.2      1  FULL/-   00:00:27   10.0.100.2 Tunnel0
```

All three adjacencies FULL. Ethernet0/1 back to FULL.

Ping from BR-RTR1 to HQ LAN restored:

```text
ping 10.1.100.1 source Loopback0 repeat 5
!!!!!
Success rate is 100 percent (5/5)
```

## Save

```ios
write memory
```

## Key Lesson

OSPF area mismatch produces an asymmetric symptom: the local router sees the neighbor in INIT state (it hears the far-end hellos), but the far-end shows no neighbor at all (it silently discards mismatched-area packets). The mismatch is visible on the local side with `show ip ospf interface <int>` — the Area field will not match the topology design. Always verify the area assignment on both sides of a link before concluding the physical link or OSPF process is at fault.
