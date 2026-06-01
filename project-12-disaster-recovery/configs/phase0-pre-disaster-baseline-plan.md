# Project 12 Phase 0 - Pre-Disaster Baseline Documentation Plan

## Goal

Capture the complete operational state of the network before any disaster scenario is introduced. This baseline is the recovery target — every service must return to this state after the rebuild.

## Scope

All devices from Projects 01–11:

- `HQ-RTR1`, `BR-RTR1`, `WAN-RTR1`
- `HQ-DSW1`, `HQ-DSW2`
- `HQ-ASW1`, `HQ-ASW2`
- `BR-DSW1`, `BR-ASW1`
- `HQ-FW1` (ASAv)
- Supporting nodes: HQ-TACACS, HQ-RADIUS, Syslog

## Baseline Capture Commands

Run on all IOS/IOL devices:

```ios
show version
show ip interface brief
show interfaces description
show ip route
show ip ospf neighbor
show running-config
show vlan brief
show interfaces trunk
show crypto isakmp sa
show crypto ipsec sa
show policy-map interface
show class-map
show ip nbar protocol-discovery
show tacacs
show aaa sessions
show archive log config all
show cdp neighbors
show ip arp
show mac address-table
```

## Services That Must Be Operational (Pass Criteria)

| Service | Evidence |
|---|---|
| OSPF full mesh | All neighbors FULL on HQ-RTR1, BR-RTR1, WAN-RTR1 |
| GRE + IPsec VPN | `show crypto ipsec sa` — encaps/decaps incrementing |
| TACACS+ AAA | `test aaa group tacacs+` returns `successfully authenticated` |
| Syslog | HQ-RTR1 sending to 10.1.99.11 |
| SNMPv3 | Community/user configured on all routers |
| QoS | P11-MARK-IN on Ethernet0/0.100, P11-WAN-SHAPE-1M on Ethernet0/1 |
| NAT/PAT | Confirmed absent (removed in P07) — firewall handles internet |
| Voice VLAN | BR-ASW1 Ethernet1/0 and Ethernet1/1 showing Voice VLAN: 500 |
| VLANs | VLAN 100/200/999/500 active on all appropriate switches |

## Disaster Scenario

After baseline is confirmed, the following faults will be injected simultaneously to simulate a power-surge event:

1. `HQ-RTR1` — startup config erased, device reloaded to factory default
2. `HQ-DSW1` — startup config erased, device reloaded to factory default
3. `HQ-FW1` — simulated by removing NAT/ACL sections (less destructive given ASAv complexity)

The rebuild engineer must restore full network function within **90 minutes** using only this documentation.

## Runbook Location

Pre-disaster configs are archived in `show running-config` outputs in the verification-outputs folder. The rebuild engineer uses these as the recovery source.
