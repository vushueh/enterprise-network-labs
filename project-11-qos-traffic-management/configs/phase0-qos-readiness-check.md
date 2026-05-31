# Project 11 - Phase 0 QoS Readiness Check

## Goal

Confirm the existing Project 10 network is healthy and that the router images support the QoS commands needed for Project 11 before applying any QoS policy.

## Scope

Primary pilot devices:

- `HQ-RTR1`
- `BR-RTR1`
- `WAN-RTR1`

The first QoS policy should be piloted on one WAN path before being expanded.

## Commands To Run First

Run these on `HQ-RTR1`, `BR-RTR1`, and `WAN-RTR1`.

```ios
show ip interface brief
show interfaces description
show cdp neighbors
show ip route
show ip ospf neighbor
show policy-map interface
show class-map
show policy-map
show running-config | include ^class-map|^policy-map|service-policy|bandwidth|priority|shape|fair-queue
```

## QoS Feature Checks

Run these on `HQ-RTR1` first. If supported, repeat on `BR-RTR1` and `WAN-RTR1`.

```ios
show ip nbar protocol-discovery
configure terminal
class-map match-any P11-TEST-NBAR
 match protocol http
 exit
no class-map match-any P11-TEST-NBAR
end
```

Expected:

- `match protocol http` is accepted.
- No permanent config remains after the test class-map is removed.

## Traffic Baseline

Before QoS, capture basic latency across the WAN paths.

On `HQ-RTR1`:

```ios
ping 10.0.255.2 source Loopback0 repeat 20
ping 10.0.255.3 source Loopback0 repeat 20
ping 10.2.99.2 source Loopback0 repeat 20
```

On `BR-RTR1`:

```ios
ping 10.0.255.1 source Loopback0 repeat 20
ping 10.1.99.11 source Loopback0 repeat 20
```

## Do Not Configure Yet

Do not apply `service-policy` in Phase 0. This phase only confirms:

- Topology still works after Project 10.
- QoS commands are supported.
- No previous QoS policy exists that would confuse the baseline.
