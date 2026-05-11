# Project 08 — Troubleshooting Log

---

## P08-T01 — IKEv2 policy name rejected by IOL

**Date:** 2026-05-11
**Phase:** Phase 2 — IKEv2/IPsec configuration
**Symptom:** Codex-proposed config used `crypto ikev2 policy P08-IKEV2-POLICY` (a named string). Claude-review flagged this before it was applied to CML.
**Root cause:** IOS IOL requires a numeric priority integer for `crypto ikev2 policy <1-65535>`. Named strings are not valid on this platform, unlike some IOS XE releases that accept an optional name after the number.
**Fix:** Changed to `crypto ikev2 policy 10` on both HQ-RTR1 and BR-RTR1 before applying to CML.
**Lesson:** Always check platform-specific syntax. The Codex proposal was otherwise correct — only the policy identifier syntax needed correction. This is why the Claude-review step exists before any config touches CML.

---

## P08-T02 — PFS shows N in show crypto ipsec sa on IOL

**Date:** 2026-05-11
**Phase:** Phase 2 verification / Phase 3 / Phase 4 follow-up
**Symptom:** After Phase 2 verification, `show crypto ipsec sa | include PFS` showed `PFS (Y/N): N, DH group: none` on both routers, even though `set pfs group14` was confirmed in the running IPsec profile.
**Investigation:**
- Verified `set pfs group14` present in `show running-config | section crypto ipsec profile` — confirmed on both routers.
- Ran `show crypto ipsec profile P08-IPSEC-PROFILE` — showed `PFS (Y/N): Y, DH group: group14`.
- Tried `clear crypto session` to force rekey — SA came back with PFS still showing N at SA level.
**Root cause:** IOL platform limitation. IOL accepts and correctly stores `set pfs group14` in the profile configuration, but does not perform the Diffie-Hellman exchange during `CREATE_CHILD_SA` rekey events. The profile-level check (`show crypto ipsec profile`) reports Y; the SA-level check (`show crypto ipsec sa`) reports N because no DH exchange actually occurred at rekey time.
**Fix:** No fix required — this is a known IOL platform behavior, not a misconfiguration. On physical Cisco hardware or IOS XE, the SA-level output would correctly show Y after a PFS-enabled rekey.
**Lesson:** Always distinguish between profile-level configuration state and SA-level negotiation state. `show crypto ipsec profile` shows what is configured; `show crypto ipsec sa` shows what was actually negotiated. In this case, IOL does not enforce what it claims to configure at the SA level.

---

## P08-T03 — Phase 4 break/fix: IKEv2 proposal mismatch

**Date:** 2026-05-11
**Phase:** Phase 4 — Deliberate break/fix challenge
**Fault injected:** On BR-RTR1 only, changed `P08-IKEV2-PROP` from `encryption aes-cbc-256` to `encryption aes-cbc-128`. Cleared IKEv2 and IPsec SAs to force immediate renegotiation.
**Symptom observed:**
- Console: `%LINEPROTO-5-UPDOWN: Line protocol on Interface Tunnel0, changed state to down`
- Console: `%OSPF-5-ADJCHG: Process 1, Nbr 10.0.255.1 on Tunnel0 from FULL to DOWN`
- `show crypto session` → `Session status: DOWN`, `Active SAs: 0`
- `show crypto ikev2 sa` → no output (no IKEv2 SA present)
- `show ip ospf neighbor` → Tunnel0 neighbor missing, Ethernet0/1 and Ethernet0/2 still FULL
- `show crypto ipsec sa` → all encaps/decaps counters 0, no inbound or outbound ESP SAs
**Diagnosis path:**
1. `show crypto session` → confirmed DOWN
2. `show crypto ikev2 sa` → confirmed no IKE SA (not just no traffic — the control plane itself failed)
3. `show running-config | section crypto ikev2 proposal` on BR-RTR1 → showed `encryption aes-cbc-128` (root cause visible without debug)
4. Same command on HQ-RTR1 → showed `encryption aes-cbc-256` (confirmed mismatch)
**Fix:** Restored BR-RTR1 proposal to `encryption aes-cbc-256`. Cleared failed crypto state with `clear crypto ikev2 sa` and `clear crypto sa`. Both routers renegotiated successfully.
**Recovery verified:**
- Tunnel0 came back up/up
- OSPF reconverged from DOWN → INIT → 2WAY → EXSTART → EXCHANGE → LOADING → FULL (all within one second)
- `show crypto session` → UP-ACTIVE, Active SAs: 2
- `show crypto ikev2 sa` → READY, AES-CBC 256, SHA256, DH Grp:14
- `show crypto ipsec sa` → ACTIVE(ACTIVE), transport mode, encaps/decaps counters incrementing
- Traceroute from Branch to HQ first-hopped to 10.0.100.1 (Tunnel0 path restored)
**Lesson:** A mismatched IKEv2 proposal is one of the most common site-to-site VPN failures. The key diagnostic insight is that `show crypto ikev2 sa` returning empty (no SA at all) means the control-plane negotiation itself failed — not a data-plane or routing problem. Always compare `show running-config | section crypto ikev2 proposal` on both peers before reaching for debug.
