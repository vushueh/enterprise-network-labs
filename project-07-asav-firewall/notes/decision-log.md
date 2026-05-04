# Project 07 — Design Decisions

## Why insert firewall between router and ISP (not replace the router)

**Choice:** Keep HQ-RTR1 as the campus router. Insert HQ-FW1 between HQ-RTR1 and ISP-RTR1.

**Alternatives considered:** Replace HQ-RTR1 with the ASA entirely. Run routing on the ASA.

**Rationale:** Separation of concerns. HQ-RTR1 handles OSPF, inter-VLAN routing, and WAN
routing. HQ-FW1 handles security policy, NAT, and stateful inspection. Combining both
on the ASA would require OSPF on the firewall, which increases attack surface and complexity.
In production, routers route and firewalls inspect — they are different tools for different jobs.

**Trade-offs:** One extra hop. More devices to manage.

---

## Why security levels 100 / 50 / 0

**Choice:** Inside = 100, DMZ = 50, Outside = 0.

**Alternatives considered:** All three at different non-standard values (e.g., 75/25/0).

**Rationale:** These are the ASA convention values. 100 = maximum trust (inside campus).
0 = no trust (internet). 50 = middle (DMZ servers are semi-trusted — they serve public
traffic but must not be able to pivot into campus). Using the convention values makes the
config immediately readable to any ASA engineer.

**Trade-offs:** None. These values are the de facto standard.

---

## Why DMZ at security level 50

**Choice:** DMZ = 50, between inside (100) and outside (0).

**Rationale:** A compromised DMZ server cannot initiate connections to the inside campus
(50 cannot initiate to 100 without an explicit ACL). Inside users can reach the DMZ server
(100 → 50 is permitted by default). Outside can reach the DMZ server only with an explicit
ACL permit. This gives the server exactly the access it needs and nothing more.

**Trade-offs:** Requires explicit ACL for outside → DMZ HTTP. That's the point.

---

## Why NAT moves from HQ-RTR1 to HQ-FW1

**Choice:** Remove all NAT from HQ-RTR1 and rebuild it on HQ-FW1.

**Alternatives considered:** Keep NAT on HQ-RTR1, have the firewall pass traffic transparently.

**Rationale:** NAT and firewall policy belong together. If NAT stays on the router, the
firewall sees already-translated addresses and cannot apply consistent policy. Moving NAT
to HQ-FW1 means the firewall sees original source IPs, applies policy, then translates —
the correct order of operations.

**Trade-offs:** More ASA config. Requires coordinated cutover to avoid losing internet access.

---

## Why per-VLAN NAT objects instead of summary /16

**Choice:** Individual objects per VLAN (P07-HQ-ENG, P07-HQ-SALES, etc.)

**Alternatives considered:** Single summary object covering 10.1.0.0/16 and 10.2.0.0/16.

**Rationale:** Per-VLAN objects make `show xlate` output readable — you can see exactly
which VLAN is translating. They also allow different NAT policies per VLAN in the future
(e.g., if Guest VLAN needs a different outside IP). Summary objects lose that granularity.

**Trade-offs:** More objects to define. No operational downside.

---

## Why management VLANs excluded from NAT

**Choice:** 10.1.99.0/24 and 10.2.99.0/24 not included in any PAT object.

**Rationale:** Management traffic should never go to the internet. Management VLANs hold
switch management IPs, DHCP/DNS servers, TACACS+, Radius, and Syslog. None of these
should initiate outbound internet connections. Excluding them from NAT enforces this.

**Trade-offs:** If a management device ever needs internet access, it requires explicit config change.

---

## Why application inspection for HTTP, DNS, and ICMP

**Choice:** inspect http, inspect dns, inspect icmp in the global policy.

**Alternatives considered:** Rely on stateful TCP/UDP inspection only.

**Rationale:** Application inspection goes beyond port/state tracking. DNS inspection
prevents DNS cache poisoning and enforces message format. HTTP inspection enables URL
filtering in future phases. ICMP inspection allows ICMP replies through without a
static ACL — the firewall tracks ICMP request/reply pairs the same way it tracks TCP sessions.

**Trade-offs:** Slight CPU overhead per connection. Negligible in a lab environment.

---

## Why syslog on the firewall

**Choice:** Send all deny events and ACL hits to HQ-SYSLOG at 10.1.99.51.

**Rationale:** Without logging, you have no visibility into what the firewall is blocking.
Logging deny events is the minimum for security monitoring. The `log` keyword on ACL deny
lines produces per-flow syslog messages — essential for troubleshooting and audit trails.

**Trade-offs:** Log volume can be high on a busy outside interface. Tune logging levels
per interface in production.
