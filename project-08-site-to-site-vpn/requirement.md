# Project 08 — Site-to-Site VPN: Requirements

## Business Requirements

| # | Requirement |
|---|-------------|
| BR-01 | All inter-site traffic between HQ and Branch must be encrypted in transit. |
| BR-02 | The encryption solution must not require static routes — dynamic routing must continue working over the encrypted path. |
| BR-03 | If the primary encrypted path fails, inter-site routing must automatically fall back to unencrypted backup paths and recover when encryption is restored. |
| BR-04 | The team must be able to diagnose a VPN failure using structured, non-debug show commands before resorting to debug output. |

## Technical Requirements

| # | Requirement | Implementation |
|---|-------------|----------------|
| TR-01 | GRE tunnel between HQ-RTR1 and BR-RTR1 | Tunnel0 on each router, 10.0.100.0/30 |
| TR-02 | IKEv2 with AES-256, SHA-256, DH group 14 | `crypto ikev2 proposal P08-IKEV2-PROP` |
| TR-03 | IPsec ESP AES-256 / SHA-256 HMAC in transport mode | `crypto ipsec transform-set P08-IPSEC-TS` |
| TR-04 | Pre-shared key mutual authentication | `crypto ikev2 keyring P08-IKEV2-KEYRING` |
| TR-05 | OSPF over encrypted tunnel with cost 5 (preferred path) | `ip ospf cost 5` on Tunnel0 |
| TR-06 | Physical WAN and WAN-RTR1 paths remain as OSPF fallback | Existing adjacencies preserved, higher cost |
| TR-07 | MTU/MSS tuned to prevent fragmentation | `ip mtu 1400`, `ip tcp adjust-mss 1360` |
| TR-08 | Dead Peer Detection for faster crypto failure detection | `dpd 10 3 periodic` in IKEv2 profile |
| TR-09 | Perfect Forward Secrecy group 14 for rekey events | `set pfs group14` in IPsec profile |
| TR-10 | OSPF MD5 authentication on Tunnel0 | `ip ospf authentication message-digest` |

## Lab Prerequisites

| # | Prerequisite |
|---|--------------|
| LP-01 | Projects 01-07 baseline running in CML 2.9 |
| LP-02 | HQ-RTR1 Ethernet0/1 at 10.0.0.1, BR-RTR1 Ethernet0/1 at 10.0.0.2 (verified in Phase 1 baseline) |
| LP-03 | OSPF process 1 running on both routers with existing adjacencies over Ethernet0/1 and Ethernet0/2 |
| LP-04 | `no passive-interface` applied to Tunnel0 in router ospf 1 |

## Success Criteria

- [ ] Tunnel0 up/up on both routers
- [ ] OSPF `FULL/-` over Tunnel0 on both routers
- [ ] `show crypto session` shows `UP-ACTIVE` on both routers
- [ ] `show crypto ikev2 sa` shows `READY` with AES-CBC 256, SHA256, DH Grp:14
- [ ] `show crypto ipsec sa` shows active ESP SAs in transport mode with encaps/decaps counters increasing
- [ ] HQ-RTR1 route to 10.2.0.0/16 prefers Tunnel0 with metric 15
- [ ] BR-RTR1 route to 10.1.0.0/16 prefers Tunnel0 with metric 15
- [ ] Traceroute in both directions first-hops through Tunnel0 overlay IPs
- [ ] Break/fix: IKEv2 proposal mismatch causes tunnel failure; restoring matching proposal restores full VPN
