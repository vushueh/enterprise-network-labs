# Project 10 - Phase 1 TACACS Reachability Troubleshooting

Date: 2026-05-22

## Result

TACACS+ reachability is not ready.

`HQ-RTR1` has a connected route to `10.1.99.0/24`, but ARP for `10.1.99.52` is incomplete.

## Evidence

`HQ-RTR1`:

```text
show ip route 10.1.99.52
Routing entry for 10.1.99.0/24
Known via "connected" ... Ethernet0/0.999
```

```text
show ip arp 10.1.99.52
Internet  10.1.99.52  0  Incomplete  ARPA
```

```text
ping 10.1.99.52 source 10.1.99.1
Success rate is 0 percent (0/5)
```

`HQ-DSW1` and `HQ-DSW2` also failed to ping `10.1.99.52` from `Vlan999`.

## Interpretation

This is not a routing problem from `HQ-RTR1`.

The likely issue is one of:

- `HQ-TACACS` node is not powered on.
- `HQ-TACACS` is not connected.
- `HQ-TACACS` is connected to a switchport still in VLAN 1.
- `HQ-TACACS` does not have IP `10.1.99.52`.
- `HQ-TACACS` service is not running.

## Switch Observations

Known VLAN 999 server-facing ports:

- `HQ-DSW1 Et1/1`: `MGMT-HQ-SYSLOG-ETH0`, VLAN 999
- `HQ-DSW2 Et0/0`: `SERVER-HQ-DHCP-DNS`, VLAN 999

Several connected blank ports still show VLAN 1. These may be newly added Project 10 server nodes and should be investigated before configuring AAA.

Additional switch checks:

`show mac address-table vlan 1` returned no learned MAC addresses on both `HQ-DSW1` and `HQ-DSW2`.

Connected unlabeled VLAN 1 ports:

- `HQ-DSW1 Et1/2`
- `HQ-DSW1 Et1/3`
- `HQ-DSW2 Et1/1`
- `HQ-DSW2 Et1/2`
- `HQ-DSW2 Et1/3`

This confirms the physical links are up, but no endpoint is currently being learned in VLAN 1. The next step is to identify which of these ports connect to `HQ-TACACS` and `HQ-RADIUS`, then move those specific ports to VLAN 999.

## Next Step

Identify which switchport connects to `HQ-TACACS`, move that port to VLAN 999 if needed, then verify `10.1.99.52` answers ARP/ping.
