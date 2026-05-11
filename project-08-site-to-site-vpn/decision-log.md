# Project 08 — Decision Log

## DL-01 — GRE over IPsec vs. pure IPsec tunnel mode

**Decision:** Use GRE over IPsec (transport mode) rather than a pure IPsec tunnel-mode VTI.

**Alternatives considered:**
- Pure IPsec tunnel-mode VTI (no GRE, IPsec as the overlay directly)
- GRE over IPsec (GRE provides the tunnel, IPsec provides encryption in transport mode)

**Why GRE over IPsec was chosen:**
- GRE is multiprotocol — it can carry OSPF hellos, which are non-IP multicast-adjacent packets that IPsec tunnel mode cannot natively forward without GRE
- OSPF over a pure IPsec VTI requires additional configuration (static neighbors or virtual-template interfaces) that adds complexity not needed at this stage
- GRE over IPsec in transport mode is the foundational pattern used in enterprise WAN encryption before SD-WAN became dominant
- Transport mode is more efficient for GRE over IPsec: GRE already adds a tunnel header, so transport mode adds only ESP headers without a redundant second IP header

**Impact:** Tunnel0 uses `tunnel mode gre ip` with `tunnel protection ipsec profile` applied. OSPF hellos travel inside GRE, which travels inside ESP — no static neighbor or multicast workaround needed.

---

## DL-02 — IKEv2 over IKEv1

**Decision:** Use IKEv2 exclusively. IKEv1 was not configured.

**Alternatives considered:**
- IKEv1 with aggressive mode or main mode
- IKEv2

**Why IKEv2 was chosen:**
- IKEv2 is the current IETF standard (RFC 7296), replacing IKEv1
- IKEv2 reduces the number of round trips needed to establish an IKE SA (fewer messages than IKEv1 main mode)
- IKEv2 has built-in Dead Peer Detection, NAT traversal, and EAP support as standard features rather than extensions
- CCNA exam (5.0 VPN domain) expects knowledge of IKEv2 in modern deployments
- IKEv1 is still used in legacy environments but should not be introduced in new builds

**Impact:** All crypto config uses `crypto ikev2` hierarchy. `show crypto ikev2 sa` is the primary IKE health check command.

---

## DL-03 — AES-256 / SHA-256 / DH group 14 parameter selection

**Decision:** Use AES-256 for encryption, SHA-256 for integrity/PRF, and DH group 14 (2048-bit MODP) for key exchange.

**Alternatives considered:**
- AES-128 (weaker, sufficient for many enterprise scenarios)
- SHA-1 (deprecated, still common in legacy deployments)
- DH group 2 (1024-bit, considered weak)
- ECDH group 19/20 (stronger, not needed at lab scale)

**Why these parameters were chosen:**
- AES-256 provides 256-bit symmetric security with acceptable performance on IOL
- SHA-256 is the minimum recommended hash for new deployments per current NIST guidance
- DH group 14 is widely supported, provides 2048-bit MODP security, and avoids the compatibility concerns that occasionally affect ECDH groups on older IOL images
- These three together match current enterprise best-practice baselines and are the parameters tested in the Phase 4 break/fix scenario

**Impact:** `show crypto ikev2 sa` confirms: `Encr: AES-CBC, keysize: 256, PRF: SHA256, Hash: SHA256, DH Grp:14`

---

## DL-04 — OSPF over tunnel instead of static routes

**Decision:** Run OSPF over Tunnel0 rather than using static routes for inter-site reachability.

**Alternatives considered:**
- Static routes: `ip route 10.2.0.0 255.255.0.0 Tunnel0` on HQ-RTR1 and reverse on BR-RTR1
- OSPF over tunnel (Project 08 design)

**Why OSPF over tunnel was chosen:**
- Projects 01-07 already established OSPF as the routing protocol — adding a static route would create a hybrid routing design that is harder to maintain
- OSPF over GRE tunnel means route preference is controlled by OSPF cost (Tunnel0 cost 5 vs physical cost 100), not by static floating route administrative distance — the mechanism is transparent and consistent
- If the tunnel fails, OSPF automatically reconverges to the backup paths over Ethernet0/1 (cost 100) or through WAN-RTR1 (cost 10) without any manual intervention
- Static routes do not detect tunnel failure — OSPF dead-interval detection combined with DPD gives multi-layer failure detection

**Impact:** `ip ospf cost 5` on Tunnel0 produces route metric 15 to remote site, preferred over all backup paths. Recovery after tunnel failure is automatic via OSPF reconvergence.

---

## DL-05 — IOL platform caveat: PFS shown as N at SA level

**Decision:** Document but not work around the IOL PFS display inconsistency.

**Context:** After Phase 2 was verified working, `show crypto ipsec sa | include PFS` consistently showed `PFS (Y/N): N, DH group: none` on both routers even though `set pfs group14` was confirmed present in the running IPsec profile. This was investigated across Phases 2, 3, and 4.

**Root cause confirmed:** IOL (IOS on Linux) accepts and stores `set pfs group14` in the profile (visible in `show running-config | section crypto ipsec profile` and `show crypto ipsec profile P08-IPSEC-PROFILE` → `PFS (Y/N): Y, DH group: group14`). However, IOL does not perform the DH exchange during `CREATE_CHILD_SA` rekey, so the SA-level PFS field remains N. This is an IOL platform limitation, not a misconfiguration.

**Decision rationale:** The command is correct, the profile shows Y, and the behavior is an IOL limitation that does not exist on physical Cisco hardware or IOS XE. Adding a workaround would obscure the real platform behavior. The caveat is documented here and in both config files.

**Impact:** In a physical or IOS XE lab, `show crypto ipsec sa` would show `PFS (Y/N): Y` after a rekey that used the new DH keys.
