# Project 09 - Phase 4 NTP Verification Summary

Date: 2026-05-17

## Current Status

Phase 4 NTP configuration is complete.

## HQ-RTR1

Configured as internal NTP master:

- `ntp authentication-key 9 md5 ...`
- `ntp authenticate`
- `ntp trusted-key 9`
- `ntp source Loopback0`
- `ntp master 3`

Verification:

- Time source: NTP
- NTP status shows stratum 3 with local reference `127.127.1.1`
- NTP association to local clock is selected

## Working Client Proof

BR-ASW1 successfully selected HQ-RTR1:

```text
*~10.0.255.1 127.127.1.1 st 3 reach 1
```

BR-ASW1 status:

- Reference: `10.0.255.1`
- Stratum: 4
- Last update received
- Ping to `10.0.255.1` succeeded 5/5

## Problem Found

HQ switches configured with:

```text
ntp source Vlan999
ntp server 10.0.255.1 key 9
```

but cannot ping `10.0.255.1`:

- HQ-DSW1 ping `10.0.255.1`: 0/5
- HQ-DSW2 ping `10.0.255.1`: 0/5
- HQ-ASW1 ping `10.0.255.1`: 0/5
- HQ-ASW2 ping `10.0.255.1`: 0/5

NTP associations on those devices show `.INIT.`, stratum 16, reach 0.

## Likely Root Cause

This matches the known IOL-L2 management routing issue from earlier projects:

- Same-subnet management works.
- Remote-subnet management traffic from switch SVI may fail unless `ip routing` and a default route are configured.
- `10.0.255.1` is HQ-RTR1 Loopback0, which is remote from the switch SVI subnet `10.1.99.0/24`.

## Recommended Fix

On HQ switches, verify routing state:

```text
show running-config | include ^ip routing|^ip default-gateway|^ip route
show ip route
show ip interface brief
```

Preferred fix if no default route exists:

```text
configure terminal
ip routing
ip route 0.0.0.0 0.0.0.0 10.1.99.1
end
write memory
```

Then re-test:

```text
ping 10.0.255.1
show ntp associations
show ntp status
```

Additional verification received:

- HQ-DSW1, HQ-DSW2, HQ-ASW1, and HQ-ASW2 have `ip default-gateway 10.1.99.1`.
- Their `show ip route` output says `Gateway of last resort is not set`.
- Each has only connected/local routes for `10.1.99.0/24`.

This confirms `ip default-gateway` is not sufficient for this IOL-L2 management plane. Use `ip routing` plus a static default route.

Routing fix applied and verified:

- HQ-DSW1 now has default route `0.0.0.0/0 via 10.1.99.1`; ping to `10.0.255.1` succeeds 5/5.
- HQ-DSW2 now has default route `0.0.0.0/0 via 10.1.99.1`; ping to `10.0.255.1` succeeds 5/5.
- HQ-ASW1 now has default route `0.0.0.0/0 via 10.1.99.1`; ping to `10.0.255.1` succeeds 5/5.
- HQ-ASW2 now has default route `0.0.0.0/0 via 10.1.99.1`; ping to `10.0.255.1` succeeds 5/5.

## Devices Still Needing Final Verification

Additional NTP verification received after the routing fix:

- HQ-DSW1 selected `10.0.255.1` as NTP peer: `*~10.0.255.1`, reach `77`, stratum `4`, reference `10.0.255.1`.
- HQ-DSW2 selected `10.0.255.1` as NTP peer: `*~10.0.255.1`, reach `77`, stratum `4`, reference `10.0.255.1`.
- HQ-ASW1 selected `10.0.255.1` as NTP peer: `*~10.0.255.1`, reach `77`, stratum `4`, reference `10.0.255.1`.
- HQ-ASW2 selected `10.0.255.1` as NTP peer: `*~10.0.255.1`, reach `77`, stratum `4`, reference `10.0.255.1`.

IOS still prints "Clock is unsynchronized" while the loop filter is in `FREQ` drift-measurement state, but the selected peer, nonzero reach, reference, and stratum prove the clients are receiving and selecting HQ-RTR1.

HQ-FW1 NTP configuration applied:

```text
ntp authentication-key 9 md5 *****
ntp authenticate
ntp trusted-key 9
ntp server 10.0.255.1 key 9 source inside
```

HQ-FW1 reachability to HQ-RTR1 is good: ping inside `10.0.255.1` succeeds 5/5.

HQ-FW1 is not yet fully synced:

- `show clock detail`: Time source is NTP.
- `show ntp associations`: configured peer `10.0.255.1`, but reach is `0`.
- `show ntp status`: stratum `16`, no reference clock, large offset.

## Devices Still Needing Final Verification

Final verification received:

- HQ-FW1 selected `10.0.255.1` as NTP peer: `*~10.0.255.1`, reach `177`, synchronized, stratum `4`, time source NTP.
- BR-DSW1 selected `10.0.255.1` as NTP peer: `*~10.0.255.1`, reach `377`, synchronized, stratum `4`, loopfilter `CTRL`, ping 5/5.
- WAN-RTR1 selected `10.0.255.1` as NTP peer: `*~10.0.255.1`, reach `377`, synchronized, stratum `4`, loopfilter `CTRL`, ping 5/5.
- BR-RTR1 selected `10.0.255.1` as NTP peer: `*~10.0.255.1`, reach `377`, synchronized, stratum `4`, loopfilter `CTRL`, ping 5/5.

## Phase 4 Completion Result

Phase 4 is complete.

NTP is configured and verified across the 10 in-scope internal devices:

- HQ-RTR1 operates as internal authenticated NTP master, stratum 3.
- Routers use `Loopback0` as NTP source.
- Switches use `Vlan999` as NTP source.
- HQ-FW1 uses ASA NTP with source `inside`.
- Clients select `10.0.255.1` and synchronize at stratum 4.
- HQ switch management routing issue was found and fixed with `ip routing` plus a static default route to `10.1.99.1`.
