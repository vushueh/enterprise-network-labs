# Project 10 - AAA Server Reachability Fixed

Date: 2026-05-22

## Result

`HQ-TACACS` and `HQ-RADIUS` are now reachable from `HQ-RTR1` on VLAN 999.

## HQ-TACACS

Ping from `HQ-RTR1` source `10.1.99.1`:

```text
ping 10.1.99.52 source 10.1.99.1
Success rate is 100 percent (5/5)
```

ARP resolved:

```text
Internet  10.1.99.52  0  5254.002b.752e  ARPA  Ethernet0/0.999
```

## HQ-RADIUS

Ping from `HQ-RTR1` source `10.1.99.1`:

```text
ping 10.1.99.53 source 10.1.99.1
Success rate is 80 percent (4/5)
```

ARP resolved:

```text
Internet  10.1.99.53  0  5254.0012.8975  ARPA  Ethernet0/0.999
```

## Interpretation

The original incomplete ARP issue is fixed. The service nodes now have working VLAN 999 IP addresses.

## Next Step

Verify service availability:

- TACACS+ TCP/49 using `test aaa group tacacs+` after IOS server definition.
- RADIUS UDP/1812 later during the RADIUS/802.1X phase.

Before applying AAA, verify local fallback users exist on every device, especially `WAN-RTR1`.
