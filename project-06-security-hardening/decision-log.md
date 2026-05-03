# Project 06 — Decision Log

## Phase 1 — Port Security

### DL-01 — Start configuration on HQ-ASW1 before HQ-ASW2

**Decision:** Configure and fully verify port security on HQ-ASW1 before touching HQ-ASW2.

**Alternatives considered:**
- Configure both switches in parallel
- Configure HQ-ASW2 first (closer to ATTACKER1 for attack testing)

**Why HQ-ASW1 first:**
- ASW1 has both a user endpoint (PC-ENG1, VLAN 100) and a management endpoint (MGMT1, VLAN 999), making it a more representative test of both violation modes in a single device
- Progressive approach — troubleshoot issues on one switch before multiplying them across two
- ASW1's E0/2 (restrict) and E0/3 (shutdown) cover both major violation modes in one go

**Trade-offs:** Slightly longer time before both switches are secured. Acceptable for a lab build.

---

### DL-02 — Sticky MAC learning vs manually configured static MACs

**Decision:** Use `switchport port-security mac-address sticky` to dynamically learn and lock endpoint MACs.

**Alternatives considered:**
- `switchport port-security mac-address XXXX.XXXX.XXXX` — manual static MAC per port
- Dynamic only (no sticky, no static) — allow up to maximum, no persistence

**Why sticky was chosen:**
- Eliminates need to pre-collect every endpoint MAC before deployment
- Learned MACs are written to running-config and survive reloads (unlike regular dynamic entries)
- Matches real-world enterprise deployment: push config, let legitimate devices lock the port
- Manual static entries require re-entry every time a NIC is replaced — operationally expensive at scale

**Trade-offs:** The first device to connect claims the sticky MAC slot. If policy requires pre-authorization of specific MACs before deployment, static entries are the correct choice.

---

### DL-03 — Restrict violation mode on user access ports (PC-ENG1, PC-SALES1)

**Decision:** Use `violation restrict` on Ethernet0/2 (user access port) on both HQ-ASW1 and HQ-ASW2.

**Alternatives considered:**
- `violation shutdown` — port goes err-disabled on first violation
- `violation protect` — silent drop with no logging

**Why restrict was chosen:**
- Engineering and Sales ports may temporarily see extra MACs (e.g., a test laptop briefly connected)
- Restrict drops frames from unknown MACs and logs the event without taking the port offline
- The legitimate user on the same port continues working uninterrupted
- A log event still generates a security alert even though the port stays up

**Trade-offs:** A persistent attacker can keep sending frames on a restrict port indefinitely without triggering a shutdown. DAI and IP Source Guard (Phases 3 and 4) layer additional controls on top.

---

### DL-04 — Shutdown violation mode on management and attacker ports

**Decision:** Use `violation shutdown` on Ethernet0/3 on both switches (MGMT1 on ASW1, ATTACKER1 on ASW2).

**Alternatives considered:**
- Restrict on management port for consistency with user ports

**Why shutdown on MGMT1 (ASW1 E0/3):**
- Management VLAN ports connect to a single known admin workstation — there is no legitimate reason for a second MAC to appear
- Any unauthorized MAC on a management port is a critical security event; the correct response is to take the port down immediately
- Err-disabled state provides a clear observable signal that a policy violation occurred

**Why shutdown on ATTACKER1 port (ASW2 E0/3):**
- Demonstrates the visible shutdown behavior in contrast to restrict on user ports
- Makes the attack demonstration unambiguous — port goes err-disabled on violation

**Trade-offs:** Shutdown requires manual intervention or errdisable recovery (Phase 7) to restore. Worth it for high-sensitivity ports.

---

### DL-05 — Maximum 2 MACs on user ports, maximum 1 on management and attacker ports

**Decision:** `maximum 2` on user access ports (Ethernet0/2), `maximum 1` on management and attacker ports (Ethernet0/3).

**Alternatives considered:**
- Maximum 1 everywhere (strictest)
- Maximum 3 (allows docking station with multiple devices)

**Why 2 on user ports:**
- Engineering and Sales users may have a workstation and an occasional secondary device (e.g., a phone or lab adapter)
- Maximum 2 provides operational flexibility without opening the port to arbitrary devices
- Voice VLAN work in future projects may require a phone MAC alongside the PC MAC

**Why 1 on management and attacker ports:**
- One specific known device per port — any additional device is by definition unauthorized

**Trade-offs:** Max 2 allows one unauthorized device after the legitimate sticky MAC is learned. DAI and IP Source Guard mitigate the remaining risk.

---

## Phase 2 — DHCP Snooping

### DL-06 — Trust only trunk uplinks, not access ports

**Decision:** Apply `ip dhcp snooping trust` only on Ethernet0/0 and Ethernet0/1 (trunk uplinks to HQ-DSW1).

**Alternatives considered:**
- Trust access ports connected to known servers
- Leave snooping enabled globally without trust configured (incorrect — would block all legitimate DHCP)

**Why uplinks-only trust:**
- Legitimate DHCP responses from Dnsmasq arrive via the trunk uplinks through HQ-DSW1
- DHCP Offer and Ack from Dnsmasq must arrive on a trusted port to pass through snooping
- Access ports connect to user endpoints which should never originate DHCP Offer or Ack messages
- Placing trust on an access port allows any user device to act as an authoritative DHCP server — exactly the attack snooping prevents

**Trade-offs:** If the DHCP server is ever moved to an access-connected segment, the trust designation must be updated.

---

### DL-07 — Rate limit access ports at 15 DHCP packets per second

**Decision:** Apply `ip dhcp snooping limit rate 15` on all untrusted access ports.

**Alternatives considered:**
- Higher limit (100 pps) — more lenient, less likely to trigger false positives
- Lower limit (5 pps) — stricter but could impact rapid DHCP failover
- No rate limiting

**Why 15 pps:**
- A single host DHCP exchange (Discover, Offer, Request, Ack) is 4 packets at startup
- 15 pps accommodates normal DHCP renewals plus some headroom
- A DHCP starvation attack (Gobbler-style) sends hundreds of packets per second — far above 15 pps
- This triggers errdisable on the attacking port without impacting legitimate clients

**Trade-offs:** On IOL-L2 the rate limit is configured correctly but snooping enforcement does not activate (see DL-08). On real hardware this rate limit enforces as designed.

---

### DL-08 — Static `ip source binding` entries as snooping binding table workaround

**Decision:** Add static MAC-VLAN-IP-interface bindings using `ip source binding` because IOL-L2 does not populate the DHCP snooping binding table from live traffic.

**Alternatives considered:**
- Skip DHCP snooping and leave Phases 3/4 without a binding table
- Use ARP ACLs only for DAI, skip IP Source Guard entirely
- Use a different simulation platform

**Why static bindings were added:**
- DAI (Phase 3) and IP Source Guard (Phase 4) both require a binding database to validate against
- `ip source binding` populates the same table that DHCP snooping would fill dynamically
- This preserves full DAI and IP Source Guard functionality despite the IOL-L2 limitation
- The configuration is identical to what would auto-populate on real hardware

**Trade-offs:** Static entries require manual updates when endpoints change MACs or IPs. On real hardware with working DHCP snooping, the table self-updates.

---

### DL-09 — Document the IOL-L2 snooping limitation rather than skip the phase

**Decision:** Configure DHCP snooping correctly, observe and document the limitation, and proceed with the static binding workaround.

**Alternatives considered:**
- Skip Phase 2 entirely and move to DAI
- Replace IOL-L2 with a different switch image

**Why document and proceed:**
- The configuration is correct; the limitation is in the IOL-L2 platform, not the config
- Discovering a platform limitation and documenting it is a professional troubleshooting outcome — it demonstrates understanding beyond just following a guide
- Any reviewer of this portfolio will understand that IOL-L2 is a simulation platform; what matters is knowing the correct config and being able to explain the behavior gap
- The static binding workaround shows adaptability: preserving dependent features within platform constraints

**Trade-offs:** DHCP snooping enforcement is not live on this platform. This is explicitly stated in the README and this decision log.

---

## Phase 3 — Dynamic ARP Inspection

### DL-10 — Use ARP ACLs as the DAI validation source instead of DHCP binding table

**Decision:** Create named ARP ACLs mapping each endpoint's MAC to its IP and apply them to DAI per VLAN.

**Alternatives considered:**
- Rely solely on DHCP snooping binding table (empty on IOL-L2 — would drop all ARP)
- Disable DAI since the binding table is empty
- Trust all ports and skip DAI

**Why ARP ACLs were chosen:**
- The DHCP snooping binding table is empty on IOL-L2 — without a validation source, DAI would drop all ARP packets on untrusted ports
- ARP ACLs provide an explicit MAC-to-IP whitelist that DAI processes before checking the binding table
- This is a standard Cisco-supported feature for statically addressed environments
- The ARP ACL approach produces observable drop behavior (confirmed via `show ip arp inspection statistics`)

**Trade-offs:** ARP ACLs must be manually maintained when endpoints change. On real networks with working DHCP snooping, ARP ACLs are only needed for static IP hosts.

---

### DL-11 — Trust DAI on uplink trunk ports only

**Decision:** Apply `ip arp inspection trust` on Ethernet0/0 and Ethernet0/1 (trunk uplinks) on both switches.

**Alternatives considered:**
- Trust no ports (all ARP validated — would break inter-VLAN routing)
- Trust access ports connected to known statically-addressed devices

**Why trunk uplinks are trusted:**
- HQ-RTR1 sends ARP responses for gateway IPs — those arrive on trunk ports
- If the uplink is not trusted, gateway ARP responses are dropped and all clients lose their default gateway
- Access ports should never be trusted — endpoints connect there, not routing devices

**Trade-offs:** An attacker who gains unauthorized trunk access would bypass DAI on that port. Preventing unauthorized trunking (DTP disable, BPDU guard) is a complementary control.

---

### DL-12 — Include ATTACKER1 MAC in ARP-VLAN100 on HQ-ASW1

**Decision:** Add ATTACKER1 (5254.0049.0158, 10.1.100.170) to ARP-VLAN100 on HQ-ASW1.

**Alternatives considered:**
- Exclude ATTACKER1 from all ARP ACLs (block all its ARP traffic)
- Create a separate attacker-specific ACL that only permits the real IP

**Why ATTACKER1 was included:**
- ATTACKER1 is an authorized lab node with a valid DHCP-assigned IP in VLAN 100
- Including it in the ARP ACL means legitimate ARP from ATTACKER1 passes; only spoofed ARPs (claiming a different IP) are dropped
- This demonstrates the key principle: DAI blocks spoofed bindings, not all traffic from an attacker host

**Trade-offs:** If the design goal were to block all network access from ATTACKER1, it would be excluded from the ARP ACL and port security would use shutdown to isolate it.

---

## Phase 4 — IP Source Guard

### DL-13 — `ip verify source mac-check` instead of `ip verify source port-security`

**Decision:** Apply `ip verify source mac-check` on access interfaces.

**Alternatives considered:**
- `ip verify source port-security` — validates source IP against port security MAC table
- `ip verify source` (IP-only, no MAC check)

**Why mac-check was chosen:**
- `ip verify source port-security` is not supported on IOS 17.16 (IOL) — command is rejected at the CLI
- `ip verify source mac-check` validates both source IP and source MAC against the binding table, providing equivalent combined IP+MAC protection
- IP-only verification would not catch an attacker who keeps their legitimate MAC but spoofs an IP

**Trade-offs:** The binding table must have entries for this to work — confirmed by static bindings from Phase 2.

---

### DL-14 — Apply IP Source Guard on access ports only, not uplinks

**Decision:** Apply `ip verify source mac-check` on Ethernet0/2 and Ethernet0/3 (access ports) only.

**Alternatives considered:**
- Apply on all interfaces including trunks

**Why access ports only:**
- Uplink trunk ports carry traffic from multiple VLANs and multiple hosts — applying source guard there would require bindings for every upstream host, unmanageable at scale
- The attack being mitigated (IP spoofing) originates from user access ports
- Routed traffic from HQ-DSW1 and HQ-RTR1 arrives on trusted uplinks and should not be validated by access-port bindings

**Trade-offs:** Source guard on access ports does not protect against an attacker with unauthorized trunk access. Physical security and trunk hardening address that layer.

---

## Phase 5 — Inter-VLAN ACLs / OOB Management Protection

### DL-15 — Apply ACLs inbound on router subinterfaces (source VLAN side)

**Decision:** Apply each VLAN ACL inbound on its corresponding subinterface at HQ-RTR1 (e.g., `ACL-VLAN100-IN in` on Ethernet0/0.100).

**Alternatives considered:**
- Apply outbound on the management VLAN subinterface (Ethernet0/0.999)
- Apply ACLs on HQ-DSW1 SVIs instead of the router

**Why inbound on source subinterfaces:**
- Inbound filtering stops traffic before routing — dropped packets never consume routing table lookups (more efficient)
- Per-VLAN inbound ACLs mean the policy is bound to the source VLAN, making auditing straightforward
- Outbound on the management subinterface would require one large ACL blocking all user VLANs
- HQ-DSW1 is an IOL-L2 switch — extended ACLs must live on the routed gateway (HQ-RTR1)

**Trade-offs:** One ACL per VLAN means more ACLs to maintain. The clarity and efficiency benefits outweigh the management overhead for this topology size.

---

### DL-16 — `log` keyword on all deny-to-management ACL entries

**Decision:** Add `log` to every ACL sequence that denies traffic destined to 10.1.99.0/24.

**Alternatives considered:**
- Log all denies across all ACLs
- No logging on deny rules
- Log only to a dedicated syslog server

**Why log specifically on management denies:**
- Management access violations are high-priority security events — they indicate either misconfiguration or an active attacker
- Logging only management denies avoids filling syslog with routine inter-VLAN policy drops
- Log output timestamps each event and shows source IP, unlike a hit counter alone
- The same output will forward to the Syslog server in Project 09

**Trade-offs:** The `log` keyword adds CPU overhead per matched packet. A high-volume attack against the management VLAN could cause log flooding; rate-limiting syslog (Project 09) handles this.

---

### DL-17 — Deny Engineering and Sales access to Guest VLAN 300

**Decision:** Add explicit deny rules in VLAN 100 and VLAN 200 ACLs blocking access to 10.1.44.0/24 (Guest VLAN).

**Alternatives considered:**
- Allow Engineering to Guest (for support scenarios)
- Only block Guest-to-internal, not internal-to-Guest

**Why bidirectional Guest isolation:**
- Guest VLAN is untrusted — enterprise users initiating sessions into an untrusted segment creates risk
- An infected Guest device can accept inbound connections from internal hosts if the internal-to-Guest direction is permitted
- Full bidirectional isolation is the correct Guest VLAN design regardless of direction

**Trade-offs:** IT support requiring access to Guest devices for troubleshooting would need a dedicated OOB access path.

---

### DL-18 — `established` keyword for VLAN 400 (Servers) return traffic to users

**Decision:** In ACL-VLAN400-IN, use `permit tcp ... established` for server-to-user return traffic.

**Alternatives considered:**
- Full permit (servers can initiate any connection to users)
- Block all server-to-user traffic

**Why established:**
- Servers should respond to connections initiated by users, not initiate new TCP connections to user workstations
- `established` matches TCP with ACK or RST flags — these are responses, not new sessions
- Prevents a compromised server from scanning or attacking user endpoints directly

**Trade-offs:** `established` is TCP-specific. UDP and ICMP from servers to users are handled by separate permit/deny rules. Stateful inspection (Project 07 ASAv) will provide more granular control.

---

## Phase 6 — Management Plane Hardening

### DL-19 — login block-for 120 attempts 3 within 60

**Decision:** Block logins for 120 seconds after 3 failed attempts within 60 seconds on all HQ devices.

**Alternatives considered:**
- Shorter block (30 seconds) — faster recovery for legitimate lockouts
- More lenient threshold (10 attempts) — fewer false lockouts
- No login protection

**Why these values:**
- 3 attempts in 60 seconds: A legitimate user fat-fingering a password might fail twice but rarely three times in under a minute
- 120-second block: Enough to defeat password spray tools; short enough that a legitimate locked-out admin can retry promptly
- Values align with CIS Benchmark and NIST 800-53 device hardening baselines

**Trade-offs:** During an emergency, the 120-second lockout adds delay for SSH access. A physical console connection bypasses this protection (acceptable — requires physical access).

---

### DL-20 — exec-timeout 15 0 on VTY, exec-timeout 10 0 on console

**Decision:** VTY sessions timeout after 15 minutes idle; console sessions timeout after 10 minutes idle.

**Alternatives considered:**
- Uniform 10 minutes on both
- Shorter VTY timeout (5 minutes) — more aggressive
- `exec-timeout 0 0` (no timeout) — explicitly avoided

**Why different values:**
- Console sessions are physically accessible — a forgotten open console session at an exposed workstation is a higher risk
- VTY (SSH) sessions are remote — 15 minutes is standard and gives engineers enough time to work between commands
- `exec-timeout 0 0` leaves an indefinitely open administrative session — unacceptable on any production device

**Trade-offs:** Shorter timeouts are more secure but frustrating for engineers running long verification sessions.

---

### DL-21 — `no cdp enable` on HQ-RTR1 Ethernet0/3 (ISP-facing) only

**Decision:** Disable CDP specifically on the WAN/ISP-facing interface of HQ-RTR1, not globally.

**Alternatives considered:**
- `no cdp run` globally on HQ-RTR1 (disable all CDP)
- Leave CDP enabled on all interfaces

**Why interface-level CDP disable:**
- CDP advertises device type, IOS version, platform, and management IP to directly connected neighbors
- ISP-RTR1 is a simulated external party — broadcasting device information to an external peer is reconnaissance data for an attacker
- Disabling CDP only on E0/3 preserves internal CDP on all campus interfaces (valuable for topology verification throughout the series)
- Global `no cdp run` would eliminate the CDP neighbor discovery used in every project's pre-work checklist

**Trade-offs:** Internal CDP remains enabled and is still a potential information disclosure risk. Future hardening could replace internal CDP with LLDP and enforce role-based CDP policy.

---

### DL-22 — Disable tcp-small-servers, udp-small-servers, http server, bootp server

**Decision:** Explicitly disable all listed unnecessary services on HQ-RTR1, HQ-ASW1, and HQ-ASW2.

**Alternatives considered:**
- Rely on defaults (some services are off by default on newer IOS)
- Disable only on the router, not the switches

**Why explicit disable on all three devices:**
- `tcp-small-servers` and `udp-small-servers` (echo, chargen, daytime) are legacy debug services usable in amplification attacks
- `ip http server` and `ip http secure-server` — web management is not used in this lab; HTTP management is unencrypted
- `ip bootp server` — obsolete IP assignment mechanism; Dnsmasq handles all DHCP
- Applying to all three devices creates a consistent hardening posture; inconsistency is a common audit finding

**Trade-offs:** If HTTP device management (WebUI) is ever needed, `ip http secure-server` would need re-enabling explicitly.

---

## Phase 7 — Errdisable Recovery

### DL-23 — Enable recovery for 5 specific causes, not all causes

**Decision:** Enable errdisable recovery for psecure-violation, security-violation, dhcp-rate-limit, arp-inspection, and bpduguard.

**Alternatives considered:**
- `errdisable recovery cause all` — automatic recovery for every possible cause
- Manual recovery only (no auto-recovery configured)
- Only psecure-violation (narrowest scope)

**Why these 5 causes:**
- **psecure-violation / security-violation:** Port security violations from endpoint changes should auto-recover; not all violations mean an active attack
- **dhcp-rate-limit:** A briefly misbehaving DHCP client should auto-recover without a manual port bounce
- **arp-inspection:** An intermittent ARP mismatch (e.g., transient IP assignment issue) should recover automatically
- **bpduguard:** An accidental switch connection to a PortFast port (common in labs and during maintenance) should recover without requiring an engineer to be dispatched

**Why not `cause all`:**
- Some err-disabled causes (loopback detection, link-flap) warrant investigation before auto-recovery
- Blanket recovery can mask persistent faults that should trigger remediation, not just automatic restart

**Trade-offs:** Automatic recovery means a persistent attacker could trigger a violation, wait 300 seconds, and attempt again. Monitoring (Project 09 SNMP/Syslog) provides the detection layer on top.

---

### DL-24 — Recovery interval of 300 seconds

**Decision:** Set `errdisable recovery interval 300` (5 minutes).

**Alternatives considered:**
- 30 seconds — faster recovery but enables rapid attack cycling
- 600 seconds — stronger deterrence but longer user downtime

**Why 300 seconds:**
- 300 seconds is the IOS default and widely referenced in CIS and NSA hardening baselines
- Long enough to slow scripted attack cycling; short enough that a legitimate endpoint change recovers within 5 minutes
- Consistent behavior expectation across both access switches

**Trade-offs:** A patient attacker can cycle violations every 5 minutes. Rate-limiting (Phase 2) and monitoring (Project 09) are the detection layers; errdisable recovery is not a standalone security control.
