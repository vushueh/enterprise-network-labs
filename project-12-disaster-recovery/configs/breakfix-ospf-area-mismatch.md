# Project 12 Break/Fix - OSPF Area Mismatch After Rebuild

## Goal

Demonstrate a common rebuild mistake: configuring an OSPF network statement with the wrong area number. This causes a one-sided adjacency that never reaches FULL state.

## Fault To Inject

On `HQ-RTR1`, change the Ethernet0/1 network statement to area 1 instead of area 0:

```ios
configure terminal
router ospf 1
 no network 10.0.0.0 0.0.0.3 area 0
 network 10.0.0.0 0.0.0.3 area 1
end
```

This simulates a typo during a rushed rebuild — typing `area 1` instead of `area 0`.

## Broken Symptom

From `HQ-RTR1`:

```ios
show ip ospf neighbor
```

Expected broken output:

```text
Neighbor ID     Pri  State     Dead Time  Address    Interface
10.0.255.2        1  INIT/DROTHER  00:00:39  10.0.0.2   Ethernet0/1
```

`INIT` state means HQ-RTR1 sees BR-RTR1's hellos but BR-RTR1 does not accept HQ-RTR1's hellos — because the area number in HQ-RTR1's hellos is 1 but BR-RTR1 expects area 0.

From `BR-RTR1`:

```ios
show ip ospf neighbor
```

Expected: No HQ-RTR1 entry via Ethernet0/1 (BR-RTR1 drops mismatched-area hellos silently).

Syslog shows on BR-RTR1:

```text
%OSPF-4-BADLSATYPE: Received LSA with mismatch area information from HQ-RTR1
```

## Diagnosis

```ios
show ip ospf interface Ethernet0/1
```

Expected output showing wrong area:

```text
Ethernet0/1 is up, line protocol is up
  Internet Address 10.0.0.1/30, Area 1, Attached via Network Statement
```

`Area 1` confirms the mismatch. BR-RTR1 Ethernet0/1 is in `Area 0`.

Cross-check from BR-RTR1:

```ios
show ip ospf interface Ethernet0/1
```

```text
  Internet Address 10.0.0.2/30, Area 0, Attached via Network Statement
```

Area mismatch confirmed: HQ-RTR1 is sending area 1 hellos on the link where BR-RTR1 expects area 0.

## Fix

```ios
configure terminal
router ospf 1
 no network 10.0.0.0 0.0.0.3 area 1
 network 10.0.0.0 0.0.0.3 area 0
end
```

## Verify Fix

```ios
show ip ospf neighbor
```

Expected restored:

```text
10.0.255.2   FULL  Ethernet0/1
```

Wait for Dead timer to expire and adjacency to reform — typically 10–40 seconds.

## Save

```ios
write memory
```

## Key Lesson

OSPF area mismatches cause `INIT` state on the local router (you see the neighbor's hellos) with no neighbor entry on the far end (it silently discards mismatched-area packets). Always run `show ip ospf interface <int>` to confirm the area number assigned to each interface — it must match on both sides.
