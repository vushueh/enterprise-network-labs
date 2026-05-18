# Project 09 - Phase 3 NetFlow Verification Summary

Date: 2026-05-17

## Status

Project 09 Phase 3 - NetFlow Traffic Analysis is device-side verified on HQ-RTR1.

## Pre-Check

Verified before configuration:

- No existing NetFlow config matched `show running-config | include flow|ip flow`.
- `HQ-RTR1` interfaces were up/up:
  - `Ethernet0/0.100`
  - `Ethernet0/0.200`
  - `Ethernet0/0.300`
  - `Ethernet0/0.999`
  - `Ethernet0/1`
  - `Ethernet0/2`
  - `Ethernet0/3`
  - `Loopback0`
  - `Tunnel0`
- Route to `10.1.99.51` is directly connected via `Ethernet0/0.999`.
- `ping 10.1.99.51 source Loopback0` succeeded 5/5.

## Configuration Applied

Configured:

- `ip flow-export destination 10.1.99.51 2055`
- `ip flow-export source Loopback0`
- `ip flow-export version 9`
- `ip flow-cache timeout active 1`
- `ip flow-cache timeout inactive 15`
- `ip flow-top-talkers`
  - `top 10`
  - `sort-by bytes`
- `ip flow ingress` on:
  - `Ethernet0/0.100`
  - `Ethernet0/0.200`
  - `Ethernet0/0.300`
  - `Ethernet0/0.999`
  - `Ethernet0/1`
  - `Ethernet0/2`
  - `Ethernet0/3`
  - `Tunnel0`

## Verification

`show ip flow export` confirmed:

- NetFlow v9 enabled.
- Export source: `10.0.255.1` via `Loopback0`.
- Export destination: `10.1.99.51` UDP/2055.
- Initial check: 5 flows exported in 2 UDP datagrams.
- Later baseline check: 54 flows exported in 12 UDP datagrams.
- 0 export failures.
- 0 FIB drops.
- 0 adjacency drops.
- 0 fragmentation drops.
- 0 encapsulation fixup drops.

`show ip cache flow` confirmed:

- Flow cache active.
- Flows added before and after traffic generation.
- After `ping 10.2.100.1 source 10.1.100.1 repeat 20`, cache showed ICMP flow:

```text
Tu0 10.2.100.1 -> Local 10.1.100.1 protocol 01 packets 20
```

This proves NetFlow captured the Branch-to-HQ return traffic over Tunnel0.

Later `show ip cache flow` baseline confirmed:

- 2175 total packets observed in the packet size distribution.
- 13 active flows.
- 4083 inactive flows.
- 74 flows added.
- Protocol buckets included UDP-other, ICMP, and IP-other.
- Active OSPF/UDP/ICMP flows were visible from WAN-facing interfaces.

Additional traffic generated:

```text
ping 10.1.99.51 source Loopback0 repeat 20
```

Result:

- 20/20 successful.
- Round-trip min/avg/max = 1/1/2 ms.

## Platform Notes

This IOL image does not support:

```text
show ip flow interface
show ip flow top-talkers
show ip flow top talkers
```

Use these instead:

```text
show running-config | include flow|ip flow
show ip flow export
show ip cache flow
```

`show ip cache flow` provides the local top-flow evidence on this image.

## Collector Limitation

As documented in Phase 2, `HQ-SYSLOG` has no NetFlow collector. Collector-side proof is not expected for Phase 3. Device-side proof from `show ip flow export` and `show ip cache flow` is the success criteria.

## Remaining Optional Checks

To broaden the baseline, generate and capture additional flows:

```text
ping 10.1.99.51 source Loopback0 repeat 20
ping 203.0.113.100 source 10.1.100.1 repeat 20
show ip cache flow
show ip flow export
```
