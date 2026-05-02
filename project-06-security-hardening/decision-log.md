# Decision Log — Project 06 Security Hardening

Captures why each Project 06 security choice was made, not just what was configured.

---

## DL-01 — Use Sticky MAC for Port Security

**Decision:** Use sticky MAC learning with a maximum of 2 MAC addresses on the ATTACKER1 test port.

**Alternatives considered:**
- Manually configured static secure MAC addresses.
- Dynamic secure MAC addresses without saving them into the running config.

**Why sticky MAC was chosen:**
- It matches a realistic access-layer workflow where endpoints are learned automatically.
- It avoids typing endpoint MAC addresses by hand.
- It still creates visible configuration evidence after the switch learns a secure address.

**Impact:** Sticky MACs must be reviewed and cleared when a legitimate endpoint is replaced. This is a useful operational habit to practice.

---

## DL-02 — Start with Restrict Mode Before Shutdown Mode

**Decision:** Use `restrict` as the first port-security violation mode, then test `shutdown` after counters and logs are proven.

**Alternatives considered:**
- `protect`, which silently drops traffic without strong visibility.
- `shutdown`, which is realistic but more disruptive during first validation.

**Why restrict was chosen:**
- It drops violating frames and increments counters while keeping the port up.
- It gives better proof during early testing because the port remains available for repeated attempts.

**Impact:** The final lab should still test shutdown mode and errdisable recovery, but restrict mode makes Phase 1 cleaner.

---

## DL-03 — Trust Only Uplinks for DHCP Snooping

**Decision:** DHCP snooping trust belongs only on interfaces that lead toward the authorized DHCP server path.

**Alternatives considered:**
- Trusting all trunk and access ports to avoid DHCP drops.
- Trusting the attacker/test access port temporarily during testing.

**Why uplink-only trust was chosen:**
- DHCP replies should come from the infrastructure side, not from user endpoints.
- Trusting access ports defeats the purpose of DHCP snooping.
- This directly supports the Project 06 break/fix challenge.

**Impact:** Correct uplink identification matters. CDP/LLDP and trunk verification must be checked before enabling snooping.

---

## DL-04 — Build DAI and IP Source Guard on DHCP Snooping Bindings

**Decision:** Treat DHCP snooping as the foundation for DAI and IP Source Guard.

**Alternatives considered:**
- Static ARP ACLs for every endpoint.
- Router-only ACL filtering without switch-edge validation.

**Why binding-based validation was chosen:**
- DHCP snooping creates the MAC/IP/VLAN/interface truth table.
- DAI can use that truth table to reject spoofed ARP.
- IP Source Guard can use it to reject spoofed source IP traffic at the access port.

**Impact:** Static-address hosts may need static binding entries or special handling if they are tested under DAI/IP Source Guard.

---

## DL-05 — Simulate OOB Management with ACLs Around VLAN 999

**Decision:** Block user VLANs from initiating connections into Management VLAN 999 and log attempts.

**Alternatives considered:**
- Leave VLAN 999 reachable because it is only a lab.
- Fully redesign a physical out-of-band management network.

**Why ACL-based OOB simulation was chosen:**
- It teaches the operational principle without adding new hardware complexity yet.
- It protects infrastructure management access using the existing Project 01–05 topology.
- It gives clear CCNA-relevant ACL practice.

**Impact:** Management troubleshooting must start from approved management sources, not normal user VLANs.

---

## DL-06 — Keep Security Hardening Layered

**Decision:** Use multiple controls together instead of relying on one feature.

**Alternatives considered:**
- Only configure port security.
- Only configure router ACLs.

**Why layered hardening was chosen:**
- Port security limits MAC behavior.
- DHCP snooping protects address assignment.
- DAI protects ARP.
- IP Source Guard protects source IP behavior.
- ACLs enforce L3 policy.

**Impact:** Verification must prove each layer independently so failures are easier to isolate.

---

## DL-07 — Validate Errdisable Recovery Instead of Avoiding It

**Decision:** Intentionally trigger security-related errdisable behavior and confirm recovery.

**Alternatives considered:**
- Avoid shutdown-mode tests to keep the lab stable.
- Manually recover every port with `shutdown` / `no shutdown` only.

**Why recovery validation was chosen:**
- Project 04 introduced errdisable recovery; Project 06 proves it works under security events.
- Engineers need to know how the network behaves after a violation, not only during normal operation.

**Impact:** Timers and logs must be captured so recovery behavior is documented clearly.
