# Project 07 — Troubleshooting Log

Project-local troubleshooting entries for the ASAv perimeter firewall lab.

---

## Current Status

Phases 1-6 completed without a live unresolved issue requiring a repair entry. Verification evidence is captured under [verification/screenshots/](verification/screenshots/), and the phase command flow is documented directly in [README.md](README.md).

---

## Deferred Break/Fix — Not Completed

### P07-BF-01 — Inside interface security level set to 0

**Status:** Deferred for future video demonstration. This fault has not been injected, fixed, or marked complete.

**Planned symptom:** Inside campus clients lose inside-to-outside connectivity because the ASA treats the inside interface as untrusted.

**Planned diagnosis path:**
```
packet-tracer input inside tcp 10.1.100.10 12345 203.0.113.100 80
show nameif
show interface ip brief
show running-config interface GigabitEthernet0/0
```

**Expected root cause when demonstrated:** `GigabitEthernet0/0` has `security-level 0` instead of `security-level 100`.

**Expected fix when demonstrated:**
```
interface GigabitEthernet0/0
 security-level 100
end
write memory
```

**Documentation rule:** Add a new dated entry after the future video demonstration is recorded. Do not convert this deferred plan into a completed troubleshooting entry until the fault is actually demonstrated and fixed.

---

## Live Issues — Discovered During Build

### P07-T01 — ICMP Pings Failing After Phase 1 Cutover

**Date:** 2026-05-04 | **Phase:** 1 — Basic Setup and Cutover

**Symptom:** After completing Phase 1, ping from PC-ENG1 (10.1.100.10) to EXT-WEB1 (203.0.113.100) succeeded but ping replies were not returned. Inside-to-outside ping showed 0% success. Packet-tracer showed Allow but live traffic dropped ICMP replies at the outside interface.

**Investigation:**
```
packet-tracer input inside icmp 10.1.100.10 8 0 203.0.113.100
show service-policy global
```
Packet-tracer showed Allow for the forward path but ICMP replies from outside were being dropped by the outside stateful inspection. `show service-policy global` showed no ICMP inspection in the class `inspection_default`.

**Root cause:** ASA stateful inspection does not track ICMP by default. Without `inspect icmp`, the ASA has no record of the outbound ICMP request and drops the reply as an uninitiated inbound flow. ICMP replies are silently dropped at the outside interface.

**Fix:** Added ICMP inspection under the global policy-map (done in Phase 3):
```
policy-map global_policy
 class inspection_default
  inspect icmp
```

**Lesson:** On an ASA, stateful tracking of ICMP requires explicit `inspect icmp`. Without it, ICMP replies from lower-security to higher-security zones are dropped even though the outbound request was permitted. This is the most common "ping works one way" complaint on ASA deployments. Always include `inspect icmp` in the global inspection policy.

---

### P07-T02 — Outside-to-DMZ HTTP Dropped Despite Static NAT Configured

**Date:** 2026-05-04 | **Phase:** 2 — NAT Migration

**Symptom:** After configuring static NAT for HQ-SRV1 (10.1.40.10 ↔ 203.0.113.10), `packet-tracer input outside tcp 203.0.113.2 12345 203.0.113.10 80` showed Drop. No traffic was reaching HQ-SRV1 from outside even though NAT was in place.

**Investigation:**
```
show nat detail
packet-tracer input outside tcp 203.0.113.2 12345 203.0.113.10 80
```
`show nat detail` confirmed the static NAT rule existed and the translation was correct (203.0.113.10 → 10.1.40.10). Packet-tracer output showed Phase 2 (NAT) passed successfully but Phase 3 (Access-List) showed Drop — the outside interface had no ACL permitting inbound traffic.

**Root cause:** On ASA, NAT and ACL are independent policies. NAT translates the address — it does NOT grant permission. Outside-initiated traffic to the DMZ also requires an explicit inbound ACL on the outside interface (`access-group ... in interface outside`) permitting the specific service. Without the ACL, ASA drops outside-initiated flows regardless of NAT.

**Fix:** Applied in Phase 3:
```
access-list P07-OUTSIDE-IN extended permit tcp any object OBJ-HQ-SRV1 eq 80 log
access-list P07-OUTSIDE-IN extended deny ip any any log
access-group P07-OUTSIDE-IN in interface outside
```

**Lesson:** ASA NAT ≠ permission. Static NAT makes the translation work but the security policy (ACL) controls whether the flow is actually allowed. This is the most critical conceptual difference from IOS NAT, where a static entry alone permits the traffic. On ASA, always configure both NAT and ACL for outside-initiated flows.

---

### P07-T03 — HQ-SYSLOG Unreachable After Phase 5 Logging Config

**Date:** 2026-05-04 | **Phase:** 5 — Logging and Threat Detection

**Symptom:** After configuring `logging host inside 10.1.99.51` on HQ-FW1, no syslog messages appeared on HQ-SYSLOG. `show logging` confirmed the logging host was configured and logging was enabled, but HQ-SYSLOG received nothing.

**Investigation:**
```
ping inside 10.1.99.51
show logging
show interface ip brief
```
Ping from HQ-FW1 to 10.1.99.51 (HQ-SYSLOG) failed. HQ-SYSLOG had an IP assigned but was completely unreachable. Checked HQ-DSW1 in CML — HQ-SYSLOG was connected to HQ-DSW1 Et1/1 which was configured as an access port in VLAN 400 instead of VLAN 999 (management VLAN).

**Root cause:** HQ-DSW1 Et1/1 (HQ-SYSLOG uplink) was placed in VLAN 400 during the original Project 06 build when HQ-SRV1 was still in that VLAN. When HQ-SRV1 moved to the firewall DMZ in Project 07, VLAN 400 on HQ-DSW1 was effectively orphaned but Et1/1 remained in it. HQ-SYSLOG should have been in VLAN 999 from the start.

**Fix:**
```
! On HQ-DSW1:
interface Ethernet1/1
 switchport access vlan 999
 no shutdown
end
write memory
```
After fix, ping from HQ-FW1 to 10.1.99.51 returned 100%. Syslog messages began appearing on HQ-SYSLOG immediately.

**Lesson:** When moving a server to a new segment (ASAv DMZ), audit all downstream switchport VLAN assignments for any remaining nodes connected to the old segment. A syslog collector silently receiving nothing is harder to notice than a broken ping — verify logging with `show logging` hit counters incrementing AND actual messages on the collector.
