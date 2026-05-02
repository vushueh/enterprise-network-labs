# Project 05 — Decision Log

## DL-01 — PAT instead of a dynamic NAT pool

**Decision:** Use PAT overload on HQ-RTR1 Ethernet0/3: `ip nat inside source list NAT-PAT-SOURCES interface Ethernet0/3 overload`.

**Alternatives considered:**
- Dynamic NAT pool using multiple public addresses
- Static one-to-one NAT for every inside host
- No NAT and private routing on the ISP router

**Why PAT was chosen:**
- The lab has one customer-facing public IP on HQ-RTR1: 203.0.113.1
- PAT allows many inside hosts to share one public address by tracking sessions with unique source ports
- This matches real small/medium enterprise edge behavior: users browse outbound through a single public edge address
- Dynamic NAT without overload would need a public address pool and would exhaust public IPs quickly
- Static NAT for every user device is wasteful and not how user internet access is normally built

**Impact:** All HQ and Branch user VLANs can reach the simulated internet through a single public IP. Server publishing is handled separately with static NAT.

---

## DL-02 — Exclude VLAN 999 Management from NAT

**Decision:** Do not include 10.1.99.0/24 or 10.2.99.0/24 in `INSIDE-NAT-SOURCES`, and do not mark HQ-RTR1 Ethernet0/0.999 as `ip nat inside`.

**Alternatives considered:**
- Allow Management VLAN 999 through PAT like normal user VLANs
- Permit management outbound but control it later with firewall policy

**Why exclusion was chosen:**
- Management interfaces are for administration traffic: SSH, SNMP, syslog, NTP, and monitoring
- Management hosts should not browse or initiate general internet sessions
- Excluding Management from NAT enforces the policy at the routing/NAT layer before future firewall work
- It is a belt-and-suspenders control: the VLAN is absent from the NAT ACL and the subinterface is not a NAT inside interface

**Impact:** If a management host tries to reach the internet, it is not translated and therefore cannot use the simulated ISP path. User VLANs still work normally.

---

## DL-03 — Object-groups over individual ACL permit lines

**Decision:** Replace seven separate NAT ACL permit lines with one object-group reference: `permit ip object-group INSIDE-NAT-SOURCES any`.

**Alternatives considered:**
- Keep individual ACL lines for every subnet
- Use a broad summary like 10.0.0.0/8
- Use multiple ACLs per site

**Why object-groups were chosen:**
- Object-groups make ACLs easier to maintain as the lab grows
- The NAT policy references one named group instead of repeating every subnet in every ACL
- Adding a new NAT-eligible subnet becomes one change inside the object-group
- A broad 10.0.0.0/8 match would accidentally include infrastructure and management ranges that should stay private

**Impact:** NAT behavior stayed the same, but the ACL became production-style and easier to audit. IOL requires subnet masks inside `object-group network`, so entries use `255.255.255.0` rather than wildcard format.

---

## DL-04 — TCP MSS clamp of 1452 on the NAT outside interface

**Decision:** Apply `ip tcp adjust-mss 1452` on HQ-RTR1 Ethernet0/3, the ISP-facing outside interface.

**Alternatives considered:**
- Leave TCP MSS at the default 1460 bytes
- Lower the interface MTU
- Apply MSS clamping on every inside interface

**Why 1452 was chosen:**
- Ethernet MTU is 1500 bytes
- Standard IPv4 + TCP headers consume 40 bytes, leaving a normal MSS of 1460
- Setting MSS to 1452 gives 8 bytes of headroom for NAT/PAT and possible upstream encapsulation
- Clamping at the ISP boundary protects both HQ and Branch outbound TCP sessions without touching every user-facing subinterface

**Impact:** Web traffic is less likely to fragment or black-hole across the simulated ISP link. The running config on Ethernet0/3 is the authoritative verification on IOL.
