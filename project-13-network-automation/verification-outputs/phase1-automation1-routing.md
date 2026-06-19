# Phase 1 — AUTOMATION1 Routing Verification

## Result

AUTOMATION1 is reachable at `10.1.99.54` and uses the correct routed model:

```text
default via 10.1.99.254 dev ens2 proto static
10.0.0.0/16 via 10.1.99.1 dev ens2
10.1.0.0/16 via 10.1.99.1 dev ens2
10.1.99.0/24 dev ens2 proto kernel scope link src 10.1.99.54
10.2.0.0/16 via 10.1.99.1 dev ens2
```

## Why It Matters

The default route points to `CML-EDGE1` so internet and homelab traffic leave
through the Route10 transit. Internal CML summaries point directly at
`10.1.99.1`, which removes ICMP redirect noise during automation runs.

## Ping Proof

All 10 inventory device IPs responded from AUTOMATION1:

```text
10.0.255.1
10.0.255.2
10.0.255.3
10.1.99.11
10.1.99.12
10.1.99.13
10.1.99.14
10.2.99.2
10.2.99.3
10.0.0.14
```
