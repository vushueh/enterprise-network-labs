# Codex Action Log

This file is written by **Codex** and read by **Claude Code**.
Codex appends a session summary at the end of every session.
Claude reads this to understand what Codex did without parsing the full session JSONL.

---

## 2026-05-09 — Project 8 planning and bridge setup session

**What was done:**
- Read local CCNA project home, confirmed P05/06/07 complete on GitHub, P08 open
- Laid out Project 8 plan: GRE tunnel (Tunnel0, 10.0.100.0/30), IKEv2/IPsec later, OSPF over tunnel
- Updated local project-home handoff notes (Windows only, not pushed to GitHub)
- Participated in Claude-Codex bridge setup coordination (AGENTS.md, CLAUDE-REVIEW.md, CODEX-LOG.md)

**Pushed to GitHub:** CODEX-LOG.md test write only
**Left off at:** Project 8 not yet started in CML — baseline verification pending

---

## PROJECT 8 KICKOFF — Ready to build

**Project:** 08 — Site-to-Site VPN
**Status:** NOT STARTED — CML work begins next session
**Claude Phase 1 review:** APPROVED (see CLAUDE-REVIEW.md)

### What Project 8 builds
GRE tunnel between HQ-RTR1 and BR-RTR1, layered with IKEv2/IPsec encryption,
with OSPF preferring the tunnel path over physical WAN links.

### Phases
| Phase | What gets built |
|-------|----------------|
| 1 | GRE tunnel (Tunnel0), OSPF over tunnel, no encryption yet |
| 2 | IKEv2/IPsec encryption on the GRE tunnel |
| 3 | Verify OSPF prefers tunnel, physical WAN stays as fallback |
| 4 | Break/fix — deliberately fault the tunnel, diagnose, restore |

### Phase 1 config — APPROVED by Claude, ready for CML

**HQ-RTR1:**
```
interface Tunnel0
 description GRE-TO-BR-RTR1-TUN0-P08
 ip address 10.0.100.1 255.255.255.252
 ip mtu 1400
 ip tcp adjust-mss 1360
 ip ospf 1 area 0
 ip ospf network point-to-point
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 OSPF-WAN-KEY
 ip ospf cost 5
 tunnel source Ethernet0/1
 tunnel destination 10.0.0.2
 tunnel mode gre ip
 no shutdown

router ospf 1
 no passive-interface Tunnel0
```

**BR-RTR1:**
```
interface Tunnel0
 description GRE-TO-HQ-RTR1-TUN0-P08
 ip address 10.0.100.2 255.255.255.252
 ip mtu 1400
 ip tcp adjust-mss 1360
 ip ospf 1 area 0
 ip ospf network point-to-point
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 OSPF-WAN-KEY
 ip ospf cost 5
 tunnel source Ethernet0/1
 tunnel destination 10.0.0.1
 tunnel mode gre ip
 no shutdown

router ospf 1
 no passive-interface Tunnel0
```

### Before applying Phase 1 — run these baselines in CML first
```
! On HQ-RTR1:
show ip interface brief
show ip ospf neighbor
show ip route 10.2.0.0

! On BR-RTR1:
show ip interface brief
show ip ospf neighbor
show ip route 10.1.0.0
```

### Phase 1 verification commands (after applying)
```
! Both routers — tunnel should be up/up:
show interface Tunnel0
show ip ospf neighbor
show ip route 10.0.100.0

! HQ-RTR1 — traffic should prefer tunnel:
traceroute 10.2.100.1 source 10.1.100.1
show ip ospf neighbor detail
```

---

<!-- Codex appends new session entries below this line -->

## 2026-05-11 — Project 8 Phase 1 GRE tunnel verified

**Project:** P08 — Site-to-Site VPN
**Phase completed this session:** Phase 1 — GRE tunnel without encryption
**Claude reviewed:** yes — Phase 1 config was already approved in `CLAUDE-REVIEW.md`
**Configs applied to CML by:** Leonel
**Verification saved to Windows session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-10\project-8-read-workflow-reference-md\project-08\verification-outputs\phase1-gre-tunnel-verification.md`

### What was verified
- HQ-RTR1 Tunnel0 is up/up with `10.0.100.1/30`.
- BR-RTR1 Tunnel0 is up/up with `10.0.100.2/30`.
- OSPF is FULL over Tunnel0 in both directions.
- Tunnel0 OSPF network type is POINT_TO_POINT on both routers.
- Tunnel0 OSPF cost is 5 on both routers.
- HQ-RTR1 now reaches `10.2.0.0/16` via `10.0.100.2` over Tunnel0 with metric 15.
- BR-RTR1 now reaches `10.1.0.0/16` via `10.0.100.1` over Tunnel0 with metric 15.
- Traceroute HQ to Branch shows first hop `10.0.100.2`.
- Traceroute Branch to HQ shows first hop `10.0.100.1`.
- Existing physical OSPF adjacencies remain present as fallback paths.

**Left off at:** Project 8 Phase 1 complete. Next step is Phase 2: propose IKEv2/IPsec encryption for the GRE tunnel in `[CODEX-PROPOSED]` format, have Claude review it, then apply only after approval.

---

## 2026-05-11 — Project 8 Phase 2 proposed for Claude review

**Project:** P08 — Site-to-Site VPN
**Phase proposed this session:** Phase 2 — IKEv2/IPsec encryption on the GRE tunnel
**Claude reviewed:** pending
**Config saved to Windows session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-10\project-8-read-workflow-reference-md\project-08\configs\phase2-ikev2-ipsec-proposed.md`

### What was proposed
- IKEv2 proposal using AES-256, SHA-256, DH group 14.
- Matching IKEv2 policy on HQ-RTR1 and BR-RTR1.
- IKEv2 keyring with HQ physical endpoint `10.0.0.1` and Branch physical endpoint `10.0.0.2`.
- IKEv2 profile using pre-shared-key authentication and DPD.
- IPsec transform set using ESP AES-256 and ESP SHA-256 HMAC in transport mode.
- IPsec profile bound to the IKEv2 profile, with PFS group 14.
- `tunnel protection ipsec profile P08-IPSEC-PROFILE` under Tunnel0 on both routers.

**Left off at:** Phase 2 config is proposed but not approved. Next step is to have Claude review `phase2-ikev2-ipsec-proposed.md` before applying anything to CML.

---

## 2026-05-11 — Project 8 Phase 2 Claude correction incorporated

**Project:** P08 — Site-to-Site VPN
**Claude reviewed:** yes — `CLAUDE-REVIEW.md` marked one correction required
**Correction incorporated locally:** changed `crypto ikev2 policy P08-IKEV2-POLICY` to `crypto ikev2 policy 10` on both HQ-RTR1 and BR-RTR1.
**Corrected config saved to Windows session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-10\project-8-read-workflow-reference-md\project-08\configs\phase2-ikev2-ipsec-proposed.md`

### Claude-confirmed items to keep
- Peer IPs use physical WAN endpoints `10.0.0.1` and `10.0.0.2`.
- AES-256 / SHA-256 / DH group 14 remain correct.
- Transform set remains `mode transport` for GRE over IPsec.
- `set pfs group14`, `dpd 10 3 periodic`, and `tunnel protection ipsec profile P08-IPSEC-PROFILE` remain correct.

**Left off at:** Use the corrected Phase 2 config with numeric IKEv2 policy `10`. Apply to both routers before testing, then verify `show crypto session`, `show crypto ikev2 sa`, `show ip ospf neighbor`, and `show crypto ipsec sa`.

---

## 2026-05-11 — Project 8 Phase 2 IKEv2/IPsec encryption verified with PFS follow-up

**Project:** P08 — Site-to-Site VPN
**Phase verified this session:** Phase 2 — IKEv2/IPsec encryption on the GRE tunnel
**Configs applied to CML by:** Leonel
**Verification saved to Windows session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-10\project-8-read-workflow-reference-md\project-08\verification-outputs\phase2-ikev2-ipsec-verification.md`

### What was verified
- `show crypto session` shows `UP-ACTIVE` on both HQ-RTR1 and BR-RTR1.
- `show crypto ikev2 sa` shows `READY` on both routers.
- IKEv2 negotiated AES-CBC 256, PRF SHA256, Hash SHA256, DH group 14, and PSK authentication.
- `show crypto ipsec sa` shows active ESP SAs in transport mode using `esp-256-aes esp-sha256-hmac`.
- IPsec protects GRE protocol 47 between physical endpoints `10.0.0.1` and `10.0.0.2`.
- ESP encaps/decaps counters increased after traceroute in both directions.
- `show interface Tunnel0` shows tunnel protection via `P08-IPSEC-PROFILE`.
- OSPF stayed `FULL/-` over Tunnel0.
- Traceroute HQ to Branch first hop is `10.0.100.2`.
- Traceroute Branch to HQ first hop is `10.0.100.1`.

### Follow-up before final documentation
Both routers currently report `PFS (Y/N): N, DH group: none` in `show crypto ipsec sa`, even though the intended profile includes `set pfs group14`. Next check is to verify the running IPsec profile:

```text
show running-config | section crypto ipsec profile
show crypto ipsec profile P08-IPSEC-PROFILE
```

**Left off at:** Phase 2 core encryption is working. Verify whether `set pfs group14` is present/effective before calling the PFS portion complete or moving to final Phase 2 screenshots.

---

## 2026-05-11 — Project 8 Phase 3 route preference verified

**Project:** P08 — Site-to-Site VPN
**Phase verified this session:** Phase 3 — verify OSPF prefers tunnel, physical WAN stays as fallback
**Configs applied to CML by:** no new config; verification phase only
**Verification saved to Windows session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-10\project-8-read-workflow-reference-md\project-08\verification-outputs\phase3-route-preference-verification.md`

### What was verified
- HQ-RTR1 and BR-RTR1 both have OSPF `FULL/-` adjacency over Tunnel0.
- Physical direct adjacency over Ethernet0/1 remains present on both routers with OSPF cost 100.
- WAN-RTR1 adjacency over Ethernet0/2 remains present on both routers with OSPF cost 10.
- Tunnel0 remains OSPF point-to-point with cost 5 on both routers.
- HQ-RTR1 route to `10.2.0.0/16` prefers `10.0.100.2` via Tunnel0 with metric 15.
- BR-RTR1 route to `10.1.0.0/16` prefers `10.0.100.1` via Tunnel0 with metric 15.
- HQ traceroute to Branch first hop is `10.0.100.2`.
- Branch traceroute to HQ first hop is `10.0.100.1`.
- IPsec ESP counters remain active in both directions with zero send/receive errors.

### Follow-up still open
`show crypto ipsec sa` still shows `PFS (Y/N): N, DH group: none`. Before final documentation, verify the running IPsec profile on both routers:

```text
show running-config | section crypto ipsec profile
show crypto ipsec profile P08-IPSEC-PROFILE
```

**Left off at:** Phase 3 complete. Next step is Project 8 Phase 4 break/fix challenge, after confirming or resolving the PFS profile follow-up.
