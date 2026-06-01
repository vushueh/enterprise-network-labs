# Project 12 Phase 1 - Disaster Injection

## Scenario

Simulated power surge. Two core devices lose their startup configurations and reload to factory defaults. A third device loses critical service configuration.

## Devices Affected

| Device | Fault | Method |
|---|---|---|
| `HQ-RTR1` | Startup config erased, reloaded | `erase startup-config` + `reload` |
| `HQ-DSW1` | Startup config erased, reloaded | `erase startup-config` + `reload` |
| `HQ-FW1` | NAT/inspection policy removed | `clear configure nat` + `clear configure access-list` |

## Impact Assessment

**Immediate impact:**

- HQ-RTR1 loses all IP addressing, OSPF, TACACS+, QoS, GRE tunnel, AAA
- HQ-DSW1 loses all VLANs, trunks, inter-VLAN routing subinterface configs, OSPF
- HQ-FW1 loses NAT and access-list inspection rules — internet traffic blocked

**Cascading impact:**

- OSPF adjacencies collapse on all WAN links (no HQ-RTR1 router ID)
- HQ LAN becomes unreachable (HQ-DSW1 down reverts all access ports to VLAN 1)
- GRE/IPsec tunnel drops (HQ-RTR1 no longer has tunnel source config)
- TACACS+ authentication fails network-wide (HQ-RTR1 is the only AAA gateway for management traffic)
- QoS policy removed from WAN edge
- Syslog/SNMP from HQ-RTR1 stops

**Services still running:**

- BR-RTR1, WAN-RTR1 — still up with config (no fault injected)
- HQ-TACACS, HQ-RADIUS nodes — still running, but unreachable via management VLAN until HQ-RTR1 restores

## Injection Commands

### HQ-RTR1

```ios
enable
erase startup-config
reload
```

When prompted: `Proceed with reload? [confirm]` — press Enter.

### HQ-DSW1

```ios
enable
erase startup-config
reload
```

### HQ-FW1 (partial fault)

```
enable
configure terminal
clear configure nat
clear configure access-list
write memory
```

## Verification That Disaster Is In Effect

From BR-RTR1 after HQ-RTR1 reloads:

```ios
show ip ospf neighbor
```

Expected: No HQ-RTR1 neighbor (10.0.255.1 gone from table).

```ios
ping 10.0.255.1 source Loopback0 repeat 5
```

Expected: 0/5 — HQ-RTR1 not reachable.

## Recovery Start Gate

Once the above verification confirms the disaster is active, start the 90-minute rebuild timer.
