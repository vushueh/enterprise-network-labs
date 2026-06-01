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

---

## 2026-05-11 — Project 8 Phase 4 break/fix plan prepared

**Project:** P08 — Site-to-Site VPN
**Phase prepared this session:** Phase 4 — deliberate IKEv2 proposal mismatch break/fix
**Configs applied to CML by:** not yet; plan only
**Plan saved to Windows session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-10\project-8-read-workflow-reference-md\project-08\verification-outputs\phase4-breakfix-ikev2-mismatch-plan.md`

### Planned fault
- On BR-RTR1 only, change `P08-IKEV2-PROP` from AES-256 to AES-128.
- Clear crypto SAs to force renegotiation so the mismatch appears immediately.
- Expected symptom: IKEv2/IPsec does not cleanly rebuild; Tunnel0 OSPF may drop or traffic over the protected GRE tunnel may fail.

### Planned fix
- Restore BR-RTR1 proposal to AES-256.
- Clear failed crypto state if needed.
- Verify `show crypto session` returns `UP-ACTIVE`, `show crypto ikev2 sa` returns `READY`, OSPF returns `FULL/-` over Tunnel0, and traceroute again uses the Tunnel0 next hop.

**Left off at:** Ready to execute Phase 4 break/fix in CML. Capture pre-fault, broken-state, diagnosis, fix, and post-fix proof.

---

## 2026-05-11 — Project 8 Phase 4 break/fix verified

**Project:** P08 — Site-to-Site VPN
**Phase verified this session:** Phase 4 — deliberate IKEv2 proposal mismatch break/fix
**Configs applied to CML by:** Leonel
**Verification saved to Windows session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-10\project-8-read-workflow-reference-md\project-08\verification-outputs\phase4-breakfix-ikev2-mismatch-verification.md`

### Fault injected
- On BR-RTR1 only, changed `P08-IKEV2-PROP` from AES-256 to AES-128.
- Cleared IKEv2/IPsec SAs to force immediate renegotiation.

### Broken symptoms verified
- Tunnel0 line protocol changed to down.
- OSPF neighbor over Tunnel0 dropped from `FULL` to `DOWN`.
- `show crypto session` showed `Session status: DOWN`.
- `show crypto ikev2 sa` showed no active IKEv2 SA.
- `show crypto ipsec sa` showed `Active SAs: 0`, no inbound ESP SAs, and no outbound ESP SAs.
- BR-RTR1 running config showed the injected root cause: `encryption aes-cbc-128` while HQ-RTR1 remained expected AES-256.

### Fix verified
- Restored BR-RTR1 proposal to AES-256.
- IKEv2 returned to `READY` with AES-CBC 256, SHA256, and DH group 14.
- Crypto session returned to `UP-ACTIVE` with two active SAs.
- IPsec ESP SAs returned active in transport mode.
- OSPF returned `FULL/-` over Tunnel0.
- Branch-to-HQ traceroute again first-hopped to `10.0.100.1` over Tunnel0.

### Follow-up still open
`show crypto ipsec sa` still shows `PFS (Y/N): N, DH group: none`. Before final project documentation, verify the running IPsec profile on both routers:

```text
show running-config | section crypto ipsec profile
show crypto ipsec profile P08-IPSEC-PROFILE
```

**Left off at:** Project 8 build/verify/break/fix phases are complete. Remaining work is final screenshot capture, PFS profile follow-up, and final GitHub documentation handoff.

---

## 2026-05-11 — Project 8 complete, pushed to GitHub

**Project:** P08 — Site-to-Site VPN
**Status:** COMPLETE — all phases verified, documentation pushed to GitHub
**Claude compiled and pushed:** yes
**GitHub folder:** `project-08-site-to-site-vpn/`

### PFS follow-up resolved
- `show running-config | section crypto ipsec profile` confirmed `set pfs group14` present on both routers.
- `show crypto ipsec profile P08-IPSEC-PROFILE` confirmed `PFS (Y/N): Y, DH group: group14`.
- IOL platform limitation documented in decision-log.md (DL-05) and TROUBLESHOOTING-LOG.md (P08-T02).

**Left off at:** Project 8 is closed. Next project is Project 9 — Monitoring and Visibility (Syslog, SNMPv3, NetFlow, NTP auth, EEM, config archive). Read the project spec in `.agents/skills/cml-enterprise-labs/references/projects-02-13.md` at the start of the next session.

<!-- Codex appends new session entries below this line — Project 09 and beyond -->

## 2026-05-17 — Project 9 Phase 1 Syslog Infrastructure complete

**Project:** P09 — Monitoring and Visibility
**Phase completed:** Phase 1 — Syslog Infrastructure
**Claude reviewed:** yes — Phase 1 config approved, timestamps fix flagged and resolved
**Configs applied to CML by:** Leonel
**Session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\`
**Verification saved to:** `verification-outputs\phase1-complete-summary.md`

### What was verified

- syslog-ng collector (HQ-SYSLOG, 10.1.99.51) receiving from all 10 in-scope devices.
- Source interfaces: `Loopback0` on routers, `Vlan999` on switches.
- Severity tiers: `warnings` on core/distribution/firewall, `informational` on access switches.
- Timestamps (`service timestamps log datetime msec localtime show-timezone`) and sequence numbers on all devices.
- `service timestamps debug` typo on switches corrected and verified.
- ISP-RTR1 excluded — represents outside/ISP boundary of ASA.
- Collector proof confirmed for all 10 devices via `send log 4` on warning-tier devices and live log stream on informational-tier devices.

### Non-blocking follow-up carried forward

`ACL-VLAN100-IN` on HQ-RTR1 denies unicast DHCP renewals from VLAN 100 clients. Fix before Phase 7 correlation exercise.

**Left off at:** Phase 1 complete. Next is Phase 2 — SNMP Monitoring.

---

## 2026-05-17 — Project 9 Phase 2 SNMP Monitoring complete

**Project:** P09 — Monitoring and Visibility
**Phase completed:** Phase 2 — SNMP Monitoring
**Claude reviewed:** yes — Phase 2 config approved, SNMPv3 syntax and ASAv SNMP syntax verified
**Configs applied to CML by:** Leonel
**Session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\`
**Verification saved to:** `verification-outputs\phase2-complete-summary.md`

### What was verified

- SNMPv2c RO community `P09V2CRO2026` + `ACL-SNMP-MANAGERS` (permit 10.1.99.51) on all 10 in-scope devices.
- SNMPv3 authPriv (SHA + AES128) on HQ-RTR1, BR-RTR1, WAN-RTR1 — confirmed via `show snmp user` on all three.
- IOL supports AES128 privacy — no DES fallback observed (contrast with P08 PFS limitation).
- Trap source `Loopback0` on routers, `Vlan999` on switches — matches Phase 1 syslog source design.
- `snmp-server ifindex persist` on all devices.
- Trap destination 10.1.99.51 registered on all devices — `SNMP logging: enabled, Logging to 10.1.99.51.162` confirmed.
- HQ-FW1 ASAv: `snmp-server host inside 10.1.99.51 community ***** version 2c`, 1 Trap PDU sent (coldstart).

### Platform limitation documented

HQ-SYSLOG is a syslog-ng-only node (P07 build) with no CLI, no snmptrapd, and no net-snmp tools.
SNMP trap collector-side proof and snmpwalk not possible in current CML topology.
Full documentation in `LIMITATIONS-AND-HOMELAB-EXPANSION.md`.

**Left off at:** Phase 2 complete. Next is Phase 3 — NetFlow Traffic Analysis.

---

## 2026-05-17 — Project 9 Phase 3 NetFlow Traffic Analysis complete

**Project:** P09 — Monitoring and Visibility
**Phase completed:** Phase 3 — NetFlow Traffic Analysis
**Claude reviewed:** yes — classic NetFlow syntax approved, Tunnel0 inclusion confirmed correct
**Configs applied to CML by:** Leonel
**Session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\`
**Verification saved to:** `verification-outputs\phase3-netflow-verification-summary.md`

### What was verified

- NetFlow v9 configured on HQ-RTR1 with `ip flow-export destination 10.1.99.51 2055`.
- Export source Loopback0 (10.0.255.1), active cache timeout 1 min, inactive 15 sec.
- `ip flow ingress` on 8 interfaces: Ethernet0/0.100, .200, .300, .999, Ethernet0/1, Ethernet0/2, Ethernet0/3, Tunnel0.
- `show ip flow export`: 54+ flows exported, 0 export failures, 0 FIB/adjacency/fragmentation drops.
- `show ip cache flow`: ICMP Tunnel0 return flow captured after `ping 10.2.100.1 source 10.1.100.1 repeat 20`.
- IOL platform limitation documented: `show ip flow interface` and `show ip flow top-talkers` unsupported — use `show ip cache flow`.

### Collector limitation

HQ-SYSLOG has no NetFlow collector. Device-side export health is the success criterion. Documented in `LIMITATIONS-AND-HOMELAB-EXPANSION.md`.

**Left off at:** Phase 3 complete. Next is Phase 4 — NTP Synchronization.

---

## 2026-05-17 — Project 9 Phase 4 NTP Synchronization complete

**Project:** P09 — Monitoring and Visibility
**Phase completed:** Phase 4 — NTP Synchronization
**Claude reviewed:** yes — NTP MD5 auth design approved
**Configs applied to CML by:** Leonel
**Session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\`
**Verification saved to:** `verification-outputs\phase4-complete-summary.md`

### What was verified

- HQ-RTR1 configured as `ntp master 3` — stratum 3, reference 127.127.1.1, NTP auth key 9 MD5.
- BR-RTR1, WAN-RTR1, BR-DSW1, BR-ASW1: `*~10.0.255.1`, reach 377, stratum 4.
- HQ-DSW1, HQ-DSW2, HQ-ASW1, HQ-ASW2: `*~10.0.255.1`, reach 77+, stratum 4 — after routing fix.
- HQ-FW1: `*~10.0.255.1`, reach 177, stratum 4.

### Issue found and fixed during this phase

HQ switches could not reach 10.0.255.1. Root cause: IOL-L2 requires `ip routing` + `ip route 0.0.0.0 0.0.0.0 10.1.99.1` for management-plane routing to remote subnets. `ip default-gateway` alone is insufficient. Fix applied on DSW1, DSW2, ASW1, ASW2. Full detail in `TROUBLESHOOTING-LOG.md` (P09-T01).

**Left off at:** Phase 4 complete. Next is Phase 5 — EEM Automated Alerting.

---

## 2026-05-17 — Project 9 Phase 5 EEM complete

**Project:** P09 — Monitoring and Visibility
**Phase completed:** Phase 5 — EEM Automated Alerting
**Claude reviewed:** yes — EEM applet syntax approved, IOL-L2 limitation expected
**Configs applied to CML by:** Leonel
**Session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\`
**Verification saved to:** `verification-outputs\phase5-eem-complete-summary.md`

### What was verified

- IOL-L2 (HQ-ASW1) confirmed as not supporting EEM — `event manager applet` rejected.
- Phase moved to HQ-RTR1 with Loopback99 as the safe test trigger.
- First EEM pattern (`"Interface Loopback99, changed state to administratively down"`) did not fire — wording mismatch.
- Corrected to `"Line protocol on Interface Loopback99, changed state to down"` — EEM fired in 3ms.
- `show event manager history events`: `Actv success Sun May17 18:06:42 2026`.
- EEM alert marker forwarded to HQ-SYSLOG via syslog and confirmed in collector stream.

### Platform issues documented

- IOL-L2 no EEM → detailed in `TROUBLESHOOTING-LOG.md` (P09-T02)
- EEM literal pattern matching → detailed in `TROUBLESHOOTING-LOG.md` (P09-T03)

**Left off at:** Phase 5 complete. Next is Phase 6 — Configuration Archive.

---

## 2026-05-17 — Project 9 Phase 6 Config Archive complete

**Project:** P09 — Monitoring and Visibility
**Phase completed:** Phase 6 — Config Archive and Rollback
**Claude reviewed:** yes — unix: path correction flagged and applied pre-CML
**Configs applied to CML by:** Leonel
**Session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\`
**Verification saved to:** `verification-outputs\phase6-complete-summary.md`

### What was verified

- All 9 IOS/IOL devices configured with `archive path unix:/P09-ARCHIVE-$h-` + `maximum 5` + `write-memory`.
- CML IOL/IOL-L2 has no flash: — unix: path confirmed via `show file systems`.
- HQ-RTR1 rollback practice: injected bad description on Loopback99, restored via `configure replace unix:/P09-ARCHIVE-HQ-RTR1--May-17-23-30-15.736-UTC-1 force`.
- Rollback result: `Total number of passes: 1 / Rollback Done` — `%SYS-5-CONFIG_R: Config Replace is Done`.

**Left off at:** Phase 6 complete. Next is Phase 7 — Monitoring Verification Exercise.

---

## 2026-05-17 — Project 9 Phase 7 Monitoring Verification complete

**Project:** P09 — Monitoring and Visibility
**Phase completed:** Phase 7 — Monitoring Verification Exercise (controlled failure correlation)
**Claude reviewed:** yes — verification plan approved, known collector limitations documented
**Configs applied to CML by:** Leonel
**Session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\`
**Verification saved to:** `verification-outputs\phase7-complete-summary.md`

### What was verified

- Controlled event: Loopback99 shutdown on HQ-RTR1 at `23:44:16.407 UTC May 17 2026`.
- Local syslog: LINEPROTO down at :407, EEM fired at :410 (3ms later), LINEPROTO up at 23:44:45.
- EEM history: `Actv success Sun May17 23:44:16 2026` (second successful run — EEM applet confirmed persistent).
- HQ-SYSLOG collector: EEM marker received at 23:44:17 from 10.0.255.1 — 1 second propagation.
- SNMP device-side: trap counters increased from 6 to 10 sent, 0 dropped.
- NetFlow device-side: 5727 flows, 0 failures, 0 drops — export healthy throughout event.

### Collector-side limitations

HQ-SYSLOG has no snmptrapd or NetFlow collector. SNMP and NetFlow proof is device-side only. Full detail in `LIMITATIONS-AND-HOMELAB-EXPANSION.md`.

**Left off at:** Phase 7 complete. Next is Phase 8 — CDP/LLDP Topology Discovery.

---

## 2026-05-17 — Project 9 Phase 8 CDP/LLDP Topology Discovery complete

**Project:** P09 — Monitoring and Visibility
**Phase completed:** Phase 8 — CDP/LLDP Topology Discovery
**Claude reviewed:** yes — proposal reviewed, verification confirms complete
**Configs applied to CML by:** Leonel
**Session folder:** `C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\`
**Verification saved to:** `verification-outputs\phase8-cdp-lldp-topology-summary.md`

### What was verified

- `cdp run` + `lldp run` confirmed on all 9 IOS/IOL devices.
- HQ-FW1 (ASAv): CDP/LLDP commands rejected (`% Invalid input detected`) — documented as discovery-limited.
- 25 neighbor relationships documented in a complete neighbor table.
- Topology confirms all expected adjacencies from the lab design: HQ-RTR1 ↔ HQ-DSW1/BR-RTR1/WAN-RTR1, HQ-DSW1/DSW2 ↔ HQ-ASW1/HQ-ASW2, HQ-DSW1↔HQ-DSW2 LACP pair, BR topology.
- Endpoint-facing ports (server and PC ports) correctly show no CDP/LLDP neighbors.

**Left off at:** Phase 8 complete. Project 09 is complete. All phases verified. Claude to compile final documentation and push to GitHub.

<!-- PROJECT 09 COMPLETE — Project 10 separator below -->
---

---
<!-- PROJECT 10 — AAA and Network Access Control -->

## Project 10 — Phase 1: TACACS+ Rollout

Session: 2026-05-16 to 2026-05-22

Enrolled 7/9 IOS/IOL devices with TACACS+ (HQ-ASW2 and BR-ASW1 deferred). Phase A (AAA method lists) applied and tested with `test aaa group tacacs+` before Phase B (vty lines). Console safeguard (`aaa authentication login CONSOLE local`) applied on all devices. WAN-RTR1 required SSH key generation before Phase B. HQ-TACACS and HQ-RADIUS nodes were missing from CML initially — added and cabled to HQ-DSW1. IOL requires `ip tacacs source-interface Loopback0` as a global command. All 7 enrolled devices confirmed: `test aaa` both users authenticated, SSH verified at priv 15 and priv 1.

## Project 10 — Phase 2: Privilege Separation

Session: 2026-05-22

Added `admin` user to tac-plus.conf (member of netadmin, priv 15, password: chongong). All three users (admin, tacadmin, tacoper) authenticate via TACACS. SSH privilege separation confirmed on HQ-RTR1 and HQ-DSW1 — admin gets priv 15, tacoper gets priv 1 and is denied `configure terminal`. Per-device tacoper retest on remaining 5 devices deferred — server-side group config is the same for all.

## Project 10 — Phase 3: Parser Views

Session: 2026-05-22

Created NOC-VIEW parser view on HQ-RTR1. Prerequisites: `aaa new-model` active, `enable secret 9` confirmed, root view entry successful. Eight permitted commands configured (`commands exec include all ping` for full ping support). All 8 permitted commands verified inside NOC-VIEW. Three restricted commands (configure terminal, show running-config, reload) all denied. `show parser view all` confirmed view present. TACACS integration deliberately deferred — local view proven first.

## Project 10 — Phase 4: 802.1X Port Authentication

Session: 2026-05-22

Not completed — IOL-L2 platform limitation. HQ-ASW1 accepts 802.1X config syntax but rejects all operational verification commands (`show dot1x all`, `show authentication sessions`, and all alternatives). IOSvL2 not available in this CML installation. No configuration applied. Documented as platform limitation — future completion requires compatible switch image.

## Project 10 — Phase 5: AAA Accounting

Session: 2026-05-25

Accounting already configured in Phase 1 (`aaa accounting exec default start-stop group tacacs+` and `aaa accounting commands 15 default start-stop group tacacs+`). Fresh SSH session generated from HQ-DSW1 to HQ-RTR1 as admin, ran read-only commands, exited cleanly. TACACS counters: 95/95 packets, 0 errors. Server-side auth/authz log confirmed accepted admin session at priv 15. Accounting log file (`/var/log/tacplus-acct.log`) inaccessible from TacPlus CML node console — documented limitation.

## Project 10 — Phase 6: AAA Failover / Break-Fix

Session: 2026-05-25

Part A: Changed TACACS address to unused IP (10.1.99.250), SSH from HQ-DSW1 to HQ-RTR1 succeeded at priv 15 via local fallback. TACACS restored and re-verified. Part B: Wrong key (P10-WRONG-KEY) introduced — `test aaa` returned `User rejected` and `Continous Authc fail count: 1`. Correct key restored, `User successfully authenticated`, saved. Key distinction proven: unreachable server triggers local fallback, reachable server rejection does not.

<!-- PROJECT 10 COMPLETE — Project 11 separator below -->
---

---
<!-- PROJECT 11 — QoS Traffic Management -->

## Project 11 — Phase 0: QoS Readiness Check

Session: 2026-05-31

Confirmed OSPF FULL adjacencies on HQ-RTR1, BR-RTR1, and WAN-RTR1. NBAR syntax (`match protocol http`) accepted on all three routers. No active MQC policy-maps on any pilot router. Baseline latency captured: HQ↔Branch ~2ms avg, HQ↔WAN-RTR1 ~1ms avg. Temporary test class-maps removed cleanly.

## Project 11 — Phase 1: NBAR Classification

Session: 2026-05-31

Precheck confirmed `match protocol rtp` and `match protocol ospf` accepted by IOL. Four class-maps applied on HQ-RTR1: P11-VOICE-LIKE (RTP), P11-SIGNALING (SIP), P11-BULK-DATA (FTP+HTTP), P11-NETWORK-CONTROL (OSPF+DNS). `show class-map` confirmed all match statements present. Saved with `write memory`.

## Project 11 — Phase 2: DSCP Marking

Session: 2026-05-31

Policy-map P11-MARK-IN applied inbound on HQ-RTR1 Ethernet0/0.100. DSCP values: RTP→EF, SIP→CS3, OSPF/DNS→CS2, FTP/HTTP→AF11. VLAN 100 hosts (10.1.100.170, 10.1.100.194) confirmed reachable. class-default saw 16 packets confirming policy is active. Saved.

## Project 11 — Phase 3: WAN Edge Queuing And Shaping

Session: 2026-05-31

Hierarchical QoS policy applied outbound on HQ-RTR1 Ethernet0/1. Parent P11-WAN-SHAPE-1M shapes to 1 Mbps, nests child P11-WAN-QUEUE. Child policy: LLQ priority 30% (EF), bandwidth 10% (CS3), 5% (CS2), 15% (AF11), class-default fair-queue. `show policy-map interface Ethernet0/1` confirmed nested structure. Pings 10/10 post-policy. Saved.

## Project 11 — Phase 4: Policy Map Verification

Session: 2026-05-31

Deep verification of both applied policies. Input policy (Ethernet0/0.100): all classes visible, class-default 16 packets. Output policy (Ethernet0/1): parent shaper CIR 1 Mbps, child nested, class-default 1568 packets, zero drops. `show interfaces Ethernet0/1` confirmed `Queueing strategy: Class-based queueing`.

## Project 11 — Phase 5: Traffic Generation And ACL Fallback

Session: 2026-05-31

HTTP confirmed to nginx at 10.1.40.10 from PC-ENG1 (10.1.100.194). NBAR did not classify live HTTP or DNS traffic on IOL (PDL limitation). ACL-based fallback class P11-BULK-DATA-ACL created with `match access-group name P11-HTTP-TRAFFIC`. Result: 54 packets matched, 54 marked AF11. Phase 5 pass condition met. Temporary DNS test ACL entries removed. Saved.

## Project 11 — Phase 6: Voice VLAN Branch Pilot

Session: 2026-05-31

BR-RTR1 Ethernet0/0.500 (10.2.50.1) already up. VLAN 500 already on BR-DSW1 and BR-ASW1 trunks. Only change: `switchport voice vlan 500` added to BR-ASW1 Ethernet1/0 and Ethernet1/1. Data VLANs (100, 200) unchanged. `show interfaces switchport` confirmed Voice VLAN: 500 on both ports. VLAN 500 active with Et1/0 and Et1/1. Saved.

## Project 11 — Phase 7: AutoQoS Platform Limitation

Session: 2026-05-31

`auto qos`, `show auto qos`, and `show mls qos` all returned `% Invalid input` on BR-ASW1 IOL-L2. No configuration applied. Manual MQC from earlier phases confirmed as the working design. Platform limitation documented.

## Project 11 — Break/Fix: Empty Class-Map

Session: 2026-05-31

Removed match statement from P11-BULK-DATA-ACL to create `Match none` condition. Traffic fell to class-default. Diagnosed with `show class-map P11-BULK-DATA-ACL` → Match none. Restored `match access-group name P11-HTTP-TRAFFIC`. Post-fix: 66 packets in class, 66 marked, class-default flat. Saved. Project 11 complete.

<!-- PROJECT 11 COMPLETE — Project 12 separator below -->
---

---
<!-- PROJECT 12 — Disaster Recovery -->

## Project 12 — Phase 0: Pre-Disaster Baseline

Session: 2026-05-31

Captured complete operational baseline — OSPF FULL on all 3 routers (3 paths), IKEv2 QM_IDLE with encaps 8241/decaps 8197, TACACS+ both users authenticated, QoS P11-MARK-IN and P11-WAN-SHAPE-1M active, all VLANs confirmed on HQ-DSW1, syslog 412 messages to 10.1.99.11, VLAN 100 hosts 5/5, Voice VLAN 500 at branch. All 8 baseline checks confirmed.

## Project 12 — Phase 1: Disaster Injection

Session: 2026-05-31

Startup configs erased on HQ-RTR1 and HQ-DSW1, both reloaded to factory default. HQ-FW1 received partial fault (clear configure nat + clear configure access-list). Confirmed from BR-RTR1: HQ-RTR1 neighbor gone from OSPF table, ping 10.0.255.1 → 0/5. HQ-DSW1 confirmed all ports in VLAN 1 default. 90-minute timer started at T+00:00.

## Project 12 — Phase 2: Timed Rebuild — HQ-RTR1

Session: 2026-05-31

HQ-RTR1 rebuilt from factory default: hostname/SSH/local user (T+04:48), all interface IPs including 3 subinterfaces + Tunnel0 (T+11:55), OSPF FULL on all 3 paths (T+17:40), IKEv2/IPsec profile on Tunnel0 (T+27:12), TACACS+ AAA with Phase A/B split and test aaa confirmed (T+34:05), full QoS policy (9 class-maps, 3 policy-maps, 2 service-policies) (T+49:30), syslog/SNMP/write memory (T+58:32). HQ-RTR1 complete at T+58:32.

## Project 12 — Phase 3: Timed Rebuild — HQ-DSW1

Session: 2026-05-31

HQ-DSW1 rebuilt: hostname/ip routing/SSH (T+61:15), VLANs 100/200/300/500/999/1000 (T+63:00), LACP Po1 to HQ-DSW2 (T+66:20), trunks to HQ-RTR1/HQ-ASW1/HQ-ASW2 (T+70:05), Vlan999 SVI + default gateway (T+74:30), spanning tree priority 4096 + AAA + write memory (T+78:14). HQ-DSW1 complete at T+78:14.

## Project 12 — Phase 4: Post-Recovery Verification

Session: 2026-05-31

All 8 post-recovery checks passed at T+87:10: OSPF 3/3 FULL, VPN encaps/decaps incrementing, TACACS both users authenticated, VLANs/trunks/root bridge confirmed, QoS policies active with 0 drops, syslog 28 messages, VLAN 100 hosts 5/5. Final timer: T+87:10 — PASS (target 90 minutes).

## Project 12 — Phase 5: Runbook And Lessons Learned

Session: 2026-05-31

Condensed rebuild runbook written with timing targets per step and critical dependency table. Key lessons: QoS is the longest step (15 min, needs pre-staged blocks); test aaa before Phase B always; ip routing first on IOL-L2 before SVIs; write memory explicitly after recovery.

## Project 12 — Break/Fix: OSPF Area Mismatch

Session: 2026-05-31

Injected area mismatch: `network 10.0.0.0 0.0.0.3 area 1` (should be area 0) on HQ-RTR1 Ethernet0/1. Symptom: INIT state local, no neighbor remote (asymmetric). Diagnosed with `show ip ospf interface Ethernet0/1` → Area 1. Fixed by correcting network statement area. FULL adjacency reformed in 15 seconds. Project 12 complete.
