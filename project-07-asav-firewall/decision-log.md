# Project 07 — Decision Log

## Phase 1 — ASAv Insertion

### DL-01 — Insert HQ-FW1 instead of replacing HQ-RTR1

**Decision:** Keep HQ-RTR1 as the campus router and insert HQ-FW1 between HQ-RTR1 and ISP-RTR1.

**Alternatives considered:**
- Replace HQ-RTR1 with ASAv for both routing and firewall functions
- Keep the topology unchanged and add only stronger router ACLs

**Why this was chosen:**
- HQ-RTR1 already owns inter-VLAN routing, OSPF, and the campus routing table from earlier projects
- HQ-FW1 can focus on stateful policy, NAT, DMZ segmentation, inspection, and logging
- The resulting design matches production separation of duties: routers route, firewalls inspect
- The change is surgical and avoids rebuilding stable Projects 01-06 behavior

**Trade-offs:** Adds one more routed hop and one more device to manage. Acceptable because it creates a clean security boundary.

---

### DL-02 — Use ASA security levels 100, 50, and 0

**Decision:** Configure inside as 100, dmz as 50, and outside as 0.

**Alternatives considered:**
- Non-standard custom values such as 90, 40, and 0
- Equal security levels with ACL-only policy

**Why this was chosen:**
- 100/50/0 is the standard ASA trust model and is immediately readable
- Inside-to-outside and inside-to-DMZ traffic follows default high-to-low behavior
- Outside-to-DMZ and outside-to-inside traffic requires explicit ACL policy
- DMZ cannot initiate into inside by default, which limits pivot risk if HQ-SRV1 is compromised

**Trade-offs:** Requires explicit ACL entries for every lower-to-higher exception. That is the intended control.

---

### DL-03 — Move HQ-SRV1 into a firewall DMZ

**Decision:** Re-address HQ-SRV1 to 10.1.40.10/24 and connect it to HQ-FW1 GigabitEthernet0/2.

**Alternatives considered:**
- Leave HQ-SRV1 on the internal server VLAN and publish it through static NAT
- Put the server behind HQ-RTR1 with only router ACL protection

**Why this was chosen:**
- Public-facing services should not share a trust zone with internal campus systems
- A DMZ gives outside users a narrow path to the server without exposing the inside network
- Firewall connection tracking and logging are simpler when the server lives directly behind a firewall zone

**Trade-offs:** Requires server re-addressing and a default gateway change.

---

## Phase 2 — NAT Migration

### DL-04 — Move NAT from HQ-RTR1 to HQ-FW1

**Decision:** Remove HQ-RTR1 PAT/static NAT and rebuild NAT on HQ-FW1.

**Alternatives considered:**
- Keep NAT on HQ-RTR1 and pass translated traffic through the firewall
- Use transparent firewall mode and leave routing/NAT unchanged

**Why this was chosen:**
- Firewall policy should see original internal source addresses before translation
- ASA packet-tracer can show route lookup, NAT, ACL, and inspection in one decision path
- Static NAT for the DMZ server belongs on the same device enforcing outside access

**Trade-offs:** Requires a coordinated cutover. During migration, internet access depends on HQ-FW1 NAT being correct before router NAT is removed.

---

### DL-05 — Use per-VLAN PAT objects

**Decision:** Create separate PAT objects for Engineering, Sales, and Guest networks instead of one broad inside summary.

**Alternatives considered:**
- One large summary object for all 10.1.0.0/16 and 10.2.0.0/16 traffic
- Interface ACL-based NAT classification only

**Why this was chosen:**
- Per-VLAN objects make `show nat` and `show xlate` easier to read during verification
- Future projects can apply different NAT behavior to Guest or branch VLANs without redesign
- Management VLANs are intentionally excluded from outbound PAT

**Trade-offs:** More object definitions, but the operational clarity is worth it in a portfolio lab.

---

## Phase 3 — ACL and Inspection Policy

### DL-06 — Permit only HTTP from outside to the DMZ server

**Decision:** Allow outside TCP/80 to HQ-SRV1 static NAT and deny all other outside-originated traffic with logging.

**Alternatives considered:**
- Permit all outside-to-DMZ traffic for testing convenience
- Permit SSH/ICMP from outside to the firewall or server

**Why this was chosen:**
- The project objective is a minimum-exposure public web service
- Explicit deny logging proves unwanted traffic is blocked and visible
- SSH management remains restricted to the inside management VLAN

**Trade-offs:** External diagnostics are more constrained. Troubleshooting must use packet-tracer, logs, and controlled test flows.

---

### DL-07 — Inspect HTTP, DNS, and ICMP

**Decision:** Enable HTTP, DNS, and ICMP inspection in the ASA global policy.

**Alternatives considered:**
- Rely only on default TCP/UDP state tracking
- Enable broad inspection for every available protocol

**Why this was chosen:**
- HTTP inspection supports the public web-server use case
- DNS inspection validates common outbound name-resolution traffic
- ICMP inspection allows return echo-replies without broad inbound ACLs
- The scope is limited to protocols used in this project

**Trade-offs:** Inspection adds small processing overhead. In CML and this lab scale, that cost is negligible.

---

## Phase 5 — Logging and Visibility

### DL-08 — Send firewall logs to HQ-SYSLOG

**Decision:** Enable timestamped ASA logging to 10.1.99.51 and log ACL decisions.

**Alternatives considered:**
- Rely on local `show logging` only
- Log only critical events

**Why this was chosen:**
- Central syslog gives persistent evidence after live terminal buffers roll over
- ACL hit logging ties firewall decisions to specific traffic tests
- Visibility is part of the security control, not an optional extra

**Trade-offs:** Informational logging can be noisy in production. For this lab, it creates useful proof and troubleshooting context.

---

## Deferred Break/Fix

The planned break/fix challenge is an incorrect inside interface security level on HQ-FW1. It is reserved for a future video demonstration and is not marked complete in this project.
