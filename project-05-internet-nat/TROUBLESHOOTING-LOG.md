# Project 05 — Troubleshooting Log

## P05-T01 — Object-group network wildcard mask rejected

**Date:** 2026-05-02
**Phase:** Phase 4 — Object Groups for ACLs
**Symptom:** The object-group entries using wildcard format (`10.1.100.0 0.0.0.255`) were rejected by IOS/IOL.
**Root cause:** In the `object-group network` context, this IOL image expects subnet mask format, not wildcard mask format. Wildcards are valid in flat extended ACL lines, but not in this object-group input context.
**Fix:** Rebuilt the object-group using subnet mask format:

```cisco
object-group network INSIDE-NAT-SOURCES
 10.1.100.0 255.255.255.0
 10.1.200.0 255.255.255.0
 10.1.44.0 255.255.255.0
 10.1.40.0 255.255.255.0
 10.2.100.0 255.255.255.0
 10.2.200.0 255.255.255.0
 10.2.44.0 255.255.255.0
```

**Lesson:** Flat extended ACLs use wildcard masks. This IOL object-group context uses subnet masks. Always verify syntax from the exact IOS mode where the command will be entered.

---

## P05-T02 — `wget` to 203.0.113.97 returned connection refused

**Date:** 2026-05-02
**Phase:** Phase 2 — PAT
**Symptom:** `wget http://203.0.113.97` returned `Connection refused`. `curl` was also unavailable on the Alpine node (`curl: not found`).
**Root cause:** 203.0.113.97 is ISP-RTR1 Ethernet0/1, not the Nginx web server. The router had no HTTP service listening on TCP/80, so it rejected the connection. The Alpine endpoint image includes BusyBox `wget`, but not `curl`.
**Fix:** Test HTTP against EXT-WEB1 at 203.0.113.100 instead:

```sh
wget -O - http://203.0.113.100
```

**Lesson:** `Connection refused` is not the same as unreachable. It proves the TCP SYN reached the destination and was rejected by the host. For CML Alpine nodes, use `wget -O -` as the HTTP test tool.

---

## P05-T03 — No dedicated Branch Guest PC available for VLAN 300 ACL testing

**Date:** 2026-05-02
**Phase:** Phase 5 — Guest VLAN 300 ACL Isolation
**Symptom:** PC-ENG1 could not simulate Guest VLAN source traffic with `ping 10.1.100.1 source 10.1.44.1`; BusyBox ping does not use Cisco IOS `source` syntax, and PC-ENG1 is physically in VLAN 100.
**Root cause:** There was no dedicated Guest endpoint in VLAN 300. Also, router-generated pings from HQ-RTR1 do not traverse inbound on E0/0.300 the same way a real Guest host would.
**Fix:** Verified the ACL was present and bound inbound to E0/0.300, then used HQ-RTR1 sourced pings as a functional approximation:

```cisco
show ip access-lists GUEST-RESTRICT
show ip interface Ethernet0/0.300
ping 203.0.113.100 source 10.1.44.1 repeat 5
ping 10.1.100.1 source 10.1.44.1 repeat 5
ping 10.1.200.1 source 10.1.44.1 repeat 5
ping 10.1.40.1 source 10.1.44.1 repeat 5
```

**Lesson:** ACL placement can be verified without an endpoint, but true inbound ACL hit counters require traffic from an actual host on that VLAN. Add a dedicated Guest PC in a future validation pass if deeper proof is needed.

---

## P05-T04 — First inbound static NAT ping lost one packet

**Date:** 2026-05-02
**Phase:** Phase 3 — Static NAT for HQ-SRV1
**Symptom:** The first ping test toward the static NAT address returned `.!!!!` instead of `!!!!!`.
**Root cause:** The first packet was lost while HQ-RTR1 resolved ARP for HQ-SRV1 at 10.1.40.10. After ARP populated, packets 2–5 succeeded.
**Fix:** No configuration fix required. Re-running the ping after ARP cache population returns 100% success.
**Lesson:** One dropped first packet during initial connectivity testing is often ARP resolution, not a routing or NAT failure. Confirm with a second ping before changing config.
