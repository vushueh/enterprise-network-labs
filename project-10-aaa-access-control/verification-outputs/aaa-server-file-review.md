# Project 10 - AAA Server File Review

Date: 2026-05-22

## Finding

The `HQ-TACACS` and `HQ-RADIUS` CML service nodes exist, but their `boot.sh` files do not assign the required VLAN 999 IP addresses.

Current `boot.sh` on both nodes only contains commented examples and:

```sh
echo "READY" >/dev/console
exit 0
```

This explains why network devices cannot ARP or ping:

- `HQ-TACACS` expected: `10.1.99.52/24`
- `HQ-RADIUS` expected: `10.1.99.53/24`

## TACACS Configuration

`tac-plus.conf` has:

- key: `tacacs123`
- admin user: `tacadmin / admin123`
- operator user: `tacoper / oper123`
- enable password user: `$enab15$ / admin123`

This is enough to begin Phase 1 once IP reachability is fixed.

## RADIUS Configuration

`radiusd.conf` listens on UDP/1812.

`users` has:

- `testuser / testpassword`

`clients.conf` currently only permits localhost. It must be expanded to permit the network devices before 802.1X/RADIUS testing.

## Required Fix

Update `boot.sh` on each service node to assign its VLAN 999 IP address and default gateway.

Update `HQ-RADIUS clients.conf` to allow lab NAS/switch devices.
