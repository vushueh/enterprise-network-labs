# Project 09 - Phase 4 Complete Summary

Date: 2026-05-17

## Result

Phase 4 is complete.

Authenticated NTP is configured and verified across all 10 in-scope internal devices.

## Design

- NTP master: HQ-RTR1
- NTP master address: `10.0.255.1`
- NTP master stratum: `3`
- Authentication key ID: `9`
- Authentication method: MD5
- Routers source NTP from `Loopback0`
- Switches source NTP from `Vlan999`
- HQ-FW1 sources NTP from `inside`

## Verified Devices

| Device | Status | Key Proof |
| --- | --- | --- |
| HQ-RTR1 | Master active | Local NTP master, stratum 3, reference `127.127.1.1` |
| BR-RTR1 | Synced | `*~10.0.255.1`, reach `377`, stratum 4 |
| WAN-RTR1 | Synced | `*~10.0.255.1`, reach `377`, stratum 4 |
| HQ-DSW1 | Synced | `*~10.0.255.1`, reach `77`, stratum 4 |
| HQ-DSW2 | Synced | `*~10.0.255.1`, reach `77`, stratum 4 |
| BR-DSW1 | Synced | `*~10.0.255.1`, reach `377`, stratum 4 |
| HQ-ASW1 | Synced | `*~10.0.255.1`, reach `77`, stratum 4 |
| HQ-ASW2 | Synced | `*~10.0.255.1`, reach `77`, stratum 4 |
| BR-ASW1 | Synced | `*~10.0.255.1`, stratum 4 |
| HQ-FW1 | Synced | `*~10.0.255.1`, reach `177`, stratum 4 |

## Issue Found And Fixed

The HQ switches initially could not reach HQ-RTR1 Loopback0 at `10.0.255.1`.

Root cause:

- The IOL-L2 switches had `ip default-gateway 10.1.99.1`.
- Their routing table still showed no gateway of last resort.
- Remote management traffic to `10.0.255.1` failed even though same-subnet management worked.

Fix applied on HQ-DSW1, HQ-DSW2, HQ-ASW1, and HQ-ASW2:

```text
ip routing
ip route 0.0.0.0 0.0.0.0 10.1.99.1
```

After the fix, all four HQ switches could ping `10.0.255.1` and selected HQ-RTR1 as their NTP peer.

## Notes

- IOS may briefly show "Clock is unsynchronized" while the loop filter is still in `FREQ` drift-measurement state. For this phase, selected peer `*~10.0.255.1`, nonzero reach, reference `10.0.255.1`, and stratum 4 are valid proof of NTP operation.
- HQ-FW1 initially showed reach `0` and stratum 16, then converged successfully to synchronized stratum 4.
