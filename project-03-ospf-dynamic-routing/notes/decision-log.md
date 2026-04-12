# Project 03 — Design Decision Log
### Enterprise Network Lab Series | OSPF Dynamic Routing

Records WHY each major design choice was made — not just what was configured.

---

## Decision 1 — WAN-RTR1 as Transit Router

**Choice:** Added a third router (WAN-RTR1) as a second WAN path between HQ and Branch.

**Alternatives considered:**
- Add a second direct link between HQ-RTR1 and BR-RTR1 (parallel to E0/1)
- Use a single WAN link and rely on static route failover

**Rationale:**
A transit router reflects real-world WAN architecture where sites connect through
a provider or hub device rather than directly to each other. It enables meaningful
cost manipulation — making one path preferred over another — and provides a
topology where OSPF multi-area design is actually necessary and logical.

**Trade-offs:**
Adds one node to the topology and two more WAN /30 subnets to manage.
IP SLA probe design becomes more complex (probe target must be carefully chosen).

---

## Decision 2 — Multi-Area OSPF (Areas 0, 1, 2) Instead of Single Area

**Choice:** Area 0 for WAN backbone, Area 1 for HQ campus, Area 2 for Branch campus.

**Alternatives considered:**
- Single-area OSPF (everything in Area 0) — simpler, but no summarization benefit
- Stub areas for Area 1 and Area 2 — reduces LSA types but restricts routing flexibility

**Rationale:**
Multi-area OSPF is the production standard for any network with multiple sites.
Each area maintains its own LSA database, and ABRs summarize between areas.
WAN-RTR1 only needs to know two summary routes (10.1.0.0/16 and 10.2.0.0/16)
instead of every /24 subnet at each site. As the network grows, new subnets
at HQ or Branch are automatically included in the existing summary — no changes
required on WAN-RTR1 or the other site.

**Trade-offs:**
ABR configuration adds complexity. Area boundary changes require careful
network statement management. In single-area OSPF, a misconfigured network
statement is obvious — in multi-area, you must verify which area each
interface belongs to.

---

## Decision 3 — Area 0 on WAN Links Only

**Choice:** All three WAN /30 subnets (10.0.0.0/30, 10.0.0.4/30, 10.0.0.8/30)
are in Area 0. Campus VLANs are in Areas 1 and 2.

**Alternatives considered:**
- Put all interfaces in Area 0 (catch-all `network 0.0.0.0 255.255.255.255 area 0`)
- Put campus VLANs in Area 0 and use stub for WAN

**Rationale:**
Area 0 (backbone) should contain only transit links — interfaces that carry
traffic between areas. Campus VLAN interfaces face endpoints, not other routers.
They should be in non-backbone areas so they can be summarized at the ABR.
Putting campus VLANs in Area 0 defeats the purpose of multi-area design.

**Trade-offs:**
Requires explicit network statements per area instead of a single catch-all.
More configuration lines, but far more control and clarity.

---

## Decision 4 — Explicit `ip ospf cost` Instead of Bandwidth Tuning

**Choice:** Applied `ip ospf cost 100` on direct WAN links and `ip ospf cost 10`
on WAN-RTR1 links. Did not rely on bandwidth/delay statements for cost calculation.

**Alternatives considered:**
- Use `bandwidth` statements and let IOS calculate costs from reference bandwidth
- Use `auto-cost reference-bandwidth` to adjust the reference bandwidth globally

**Rationale:**
Explicit cost values are deterministic and portable. When you read the config,
you immediately know the cost. With bandwidth-calculated costs, you must know
the reference bandwidth and do math to understand path selection. Explicit costs
are the recommended approach in production — they survive interface type changes
and reference bandwidth changes without unexpected side effects.

**Trade-offs:**
If the interface bandwidth is used for other purposes (QoS, traffic shaping),
overriding it via explicit cost means bandwidth no longer reflects the actual
link speed for those features. Requires separate cost statements per interface
instead of inheriting from bandwidth.

---

## Decision 5 — passive-interface default Strategy

**Choice:** `passive-interface default` under OSPF, then `no passive-interface`
only on WAN-facing interfaces.

**Alternatives considered:**
- List each passive interface individually
- No passive interfaces (OSPF hellos sent everywhere)

**Rationale:**
`passive-interface default` is the safest approach. It ensures any new interface
added to the router is passive by default — OSPF hellos never go to endpoints
accidentally. You must consciously un-passive a WAN interface, which forces
you to think about whether that link should have an OSPF neighbour.
Security: prevents OSPF hellos from reaching user VLANs where rogue devices
could attempt to form adjacencies.

**Trade-offs:**
If you forget to `no passive-interface` on a WAN link, OSPF will never form.
This is a benefit (forces intentional configuration) but can be confused with
a real problem during troubleshooting (`show ip ospf interface` will show passive).

---

## Decision 6 — MD5 Authentication on WAN Interfaces Only (Not LAN)

**Choice:** MD5 authentication on E0/1 and E0/2 (WAN-facing). Not on sub-interfaces
(LAN-facing) which are passive anyway.

**Alternatives considered:**
- Area-wide authentication (under `router ospf 1 area 0 authentication`)
- No authentication

**Rationale:**
Passive interfaces don't send OSPF hellos, so authentication on LAN interfaces
is meaningless — there are no neighbours to authenticate. WAN links are the
attack surface where a rogue device could be inserted. Interface-level MD5
is explicit and auditable — you can see it per-interface in `show running-config`.

**Trade-offs:**
Per-interface configuration is more verbose than area-wide authentication.
If a new WAN interface is added, authentication must be explicitly applied —
it is not inherited automatically.

---

## Decision 7 — BFD Interval 300ms / Multiplier 3

**Choice:** `bfd interval 300 min_rx 300 multiplier 3` on all WAN interfaces.

**Alternatives considered:**
- Faster BFD (50ms interval, multiplier 3 = 150ms detection)
- Slower BFD (500ms interval, multiplier 5 = 2500ms detection)
- No BFD (rely on OSPF dead timer = 40 seconds)

**Rationale:**
300ms * 3 = 900ms maximum detection time. This is aggressive enough to provide
sub-second failover while being conservative enough to avoid false positives
from transient packet loss in a simulated CML environment. 50ms BFD in a
virtualized lab often produces false flaps. 900ms is a good balance for
a CML lab that will be compared to production designs.

**Trade-offs:**
Faster BFD is more sensitive to packet loss and can cause unnecessary adjacency
flaps in unstable environments. 300ms is a common production starting point.

---

## Decision 8 — IP SLA Probe Target: Directly Connected IP

**Choice:** Probe the adjacent router's directly connected E0/1 IP (10.0.0.1 and
10.0.0.2 on the /30) rather than a loopback address.

**Alternatives considered:**
- Probe WAN-RTR1 loopback (10.0.255.3) — initial design, then corrected
- Probe a remote campus IP to test deeper reachability

**Rationale:**
Discovered during testing: probing a loopback reachable via OSPF means the
probe fails when OSPF fails — exactly when the floating static needs to install.
The probe must be reachable via a path that is INDEPENDENT of the routing
protocol it backs up. A /30 directly connected IP requires only ARP and L2
forwarding — it works regardless of OSPF state.

**Trade-offs:**
Probing a directly connected IP only verifies Layer 2/3 adjacency on the backup
link, not full end-to-end reachability to the remote site. A more sophisticated
design could use multiple probes, but for this lab the direct-link probe correctly
tracks whether the backup path is physically usable.

---

## Decision 9 — Floating Static AD 250 (Not 200 or 210)

**Choice:** Administrative distance 250 for the floating static routes.

**Alternatives considered:**
- AD 200 (higher than OSPF external type 2 = 170, still below 255)
- AD 210 (safe margin above OSPF = 110)
- AD 254 (just below the maximum of 255 = unreachable)

**Rationale:**
AD 250 is high enough to sit below any legitimate routing protocol (OSPF=110,
BGP=20/200, etc.) and high enough to make the intent unambiguous — this is
a last-resort route, not a preferred path. 250 is a common convention in
production networks for tracked floating statics.

**Trade-offs:**
No meaningful trade-off between 210 and 254 for this design. Convention chosen
for readability and alignment with common production practice.

---

## Decision 10 — IPv6 Redundancy Not Extended to WAN-RTR1

**Choice:** OSPFv3 configured only on the direct HQ↔BR WAN link (E0/1).
WAN-RTR1 backup path has no IPv6 addresses.

**Alternatives considered:**
- Add IPv6 to HQ-RTR1 E0/2, WAN-RTR1 E0/0/E0/1, BR-RTR1 E0/2 and run
  OSPFv3 with redundancy matching the IPv4 design

**Rationale:**
IPv6 addressing was only configured on the direct WAN link and VLAN 100
sub-interfaces during Project 02. Extending IPv6 to the WAN-RTR1 backup
path would require new address planning, new interface config, and OSPFv3
multi-path design — a full extension of the IPv6 scope. This was deferred
to keep Project 03 focused on OSPF architecture rather than expanding the
IPv6 addressing scheme mid-project.

**Trade-offs:**
IPv6 has a single point of failure at E0/1. If the direct HQ↔BR WAN link
fails, IPv6 connectivity between sites is completely lost even though IPv4
fails over successfully via WAN-RTR1. This is a known limitation documented
here for future resolution in a dedicated IPv6 hardening phase.
