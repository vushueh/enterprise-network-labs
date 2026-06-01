# Project 12 Phase 4 - Post-Recovery Verification

## Goal

Confirm every service that was operational in the Phase 0 baseline is fully restored after the timed rebuild. Run all checks from the baseline plan and compare.

## Verification Checklist

### 1. OSPF Full Mesh

From `HQ-RTR1`:

```ios
show ip ospf neighbor
```

Expected: All three WAN paths showing FULL.

```text
Neighbor ID   State  Interface
10.0.255.2    FULL   Tunnel0
10.0.255.2    FULL   Ethernet0/1
10.0.255.3    FULL   Ethernet0/2
```

### 2. End-To-End Reachability

From `HQ-RTR1` Loopback0:

```ios
ping 10.0.255.2 source Loopback0 repeat 20
ping 10.0.255.3 source Loopback0 repeat 20
ping 10.1.99.52 source Loopback0 repeat 5
ping 10.1.100.194 source Loopback0 repeat 5
```

All must be 100% success.

### 3. GRE + IPsec VPN

From `HQ-RTR1`:

```ios
show crypto isakmp sa
show crypto ipsec sa
```

Expected:

```text
IKEv2 SA: state = READY
IPsec SA: encaps incrementing, decaps incrementing
```

### 4. TACACS+ AAA

From `HQ-RTR1`:

```ios
test aaa group tacacs+ admin chongong new-code
test aaa group tacacs+ tacoper oper123 new-code
```

Both must return `User was successfully authenticated`.

### 5. HQ-DSW1 VLANs And Trunks

From `HQ-DSW1`:

```ios
show vlan brief
show interfaces trunk
show spanning-tree vlan 100 brief
```

Expected: VLANs 100, 200, 300, 500, 999, 1000 active. All expected trunks up. HQ-DSW1 is root bridge for all VLANs.

### 6. QoS Policy Restored

From `HQ-RTR1`:

```ios
show policy-map interface Ethernet0/0.100
show policy-map interface Ethernet0/1
```

Expected: `P11-MARK-IN` on Ethernet0/0.100, `P11-WAN-SHAPE-1M` nested on Ethernet0/1.

### 7. Syslog

From `HQ-RTR1`:

```ios
show logging
```

Expected: `Logging to 10.1.99.11 (udp port 514, informational), 0 message lines dropped`.

### 8. VLAN 100 Host Reachability

From `HQ-RTR1`:

```ios
ping 10.1.100.194 source Ethernet0/0.100 repeat 5
ping 10.1.100.170 source Ethernet0/0.100 repeat 5
```

Expected: 5/5 both hosts.

## Pass / Fail Gate

All 8 checks must pass before stopping the recovery timer. If any check fails, continue diagnosis and fix before stopping the clock.
