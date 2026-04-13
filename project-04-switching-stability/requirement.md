# Project 04 — Switching Layer Stability: Requirements

## Business Requirements

| ID | Requirement |
|----|-------------|
| BR-01 | The HQ distribution layer must maintain switching connectivity if a single inter-distribution link fails. |
| BR-02 | No access switch must be capable of disrupting root bridge placement. |
| BR-03 | Switch ports facing end devices must recover automatically from error events without manual intervention. |
| BR-04 | The network team must be able to trace any endpoint's forwarding path using standard show commands. |
| BR-05 | All Layer 2 protections must be documentable and reproducible from configuration files. |

## Technical Requirements

| ID | Requirement | Technology |
|----|-------------|------------|
| TR-01 | Bundle the two inter-distribution links into a single logical EtherChannel using LACP | LACP 802.3ad, `channel-group mode active` |
| TR-02 | Prevent STP from blocking one inter-distribution member link | Port-channel/EtherChannel |
| TR-03 | Enforce deliberate root bridge placement — DSW1 for VLANs 100/400/999, DSW2 for VLANs 200/300 | STP priority, Rapid-PVST |
| TR-04 | Prevent access switches from influencing root bridge elections | Root Guard on DSW downlinks to access switches |
| TR-05 | Protect against unidirectional link failure on inter-switch redundant paths | Loop Guard on Port-channel1 |
| TR-06 | Use 32-bit STP cost values | `spanning-tree pathcost method long` |
| TR-07 | Detect one-way link failures on inter-switch physical ports | UDLD (`udld enable`, `udld port`) |
| TR-08 | Automatically recover error-disabled ports after 300 seconds | `errdisable recovery` for bpduguard, dhcp-rate-limit, udld, security-violation |
| TR-09 | Demonstrate VTP v3 VLAN propagation and understand propagation risks | VTP v3, primary server, transparent mode |
| TR-10 | Trace an endpoint MAC address hop-by-hop through the switching topology | `show mac address-table` |
| TR-11 | Protect access ports from rogue STP participation | PortFast + BPDU Guard |
| TR-12 | Prevent STP interaction on the router-facing distribution uplink | BPDU Filter on HQ-DSW1 Et0/0 |

## Success Criteria

- [ ] `show etherchannel summary` shows Po1(SU) with both Et0/3(P) and Et1/0(P) on DSW1 and DSW2
- [ ] `show interfaces trunk` shows Port-channel1 trunking with native VLAN 1000 and allowed 100,200,300,400,999
- [ ] `show spanning-tree root` confirms DSW1 root for 100/400/999, DSW2 root for 200/300
- [ ] `show spanning-tree inconsistentports` shows only expected baseline Root Inconsistent entries (no unexpected inconsistencies)
- [ ] `show errdisable recovery` shows bpduguard, dhcp-rate-limit, udld, security-violation, psecure-violation Enabled at 300s
- [ ] VTP v3 VLAN 600 successfully propagated to all four HQ switches
- [ ] All switches returned to VTP transparent mode with VLAN 600 removed
- [ ] PC-ENG1 MAC traced to ASW1 Et0/2 → DSW1 Et0/1 path
- [ ] PortFast + BPDU Guard confirmed on all user-facing access ports
- [ ] BPDU Filter confirmed on HQ-DSW1 Et0/0 (router-facing)
- [ ] All three Phase 7 faults injected and diagnosed using show commands only
- [ ] All three Phase 7 faults corrected and verified clean
