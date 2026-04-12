# Project 03 — Troubleshooting Log
### Enterprise Network Lab Series | OSPF Dynamic Routing

All troubleshooting entries from the Project 03 build session (2026-04-12).
Format: Symptom → Investigation → Root Cause → Fix → Lesson.

---

## Entry 1 — WAN-RTR1 Interface IP Mismatch

**Date:** 2026-04-12 | **Phase:** 1 (Pre-work)

**Symptom:**
Pings from WAN-RTR1 to HQ-RTR1 (10.0.0.5) and BR-RTR1 (10.0.0.10) failing
with 0% success rate immediately after configuring WAN-RTR1 interfaces.
Same-subnet pings should never fail — no routing required, just ARP.

**Expected:**
Directly connected /30 pings return !!!!! within seconds of interface configuration.

**Investigation:**
```
show ip interface brief
```
Showed WAN-RTR1 E0/0 = 10.0.0.6, E0/1 = 10.0.0.9. IPs looked right from the plan.

```
show cdp neighbors
```
Revealed the actual cable connections were opposite to the plan:
```
WAN-RTR1 Eth0/1  →  HQ-RTR1 Eth0/2   (expected: Eth0/0 → HQ)
WAN-RTR1 Eth0/0  →  BR-RTR1 Eth0/2   (expected: Eth0/1 → BR)
```
The IPs were configured based on the planned design, but the cables in CML
were connected to the opposite interfaces. E0/0 had the HQ-side IP but the
cable went to BR-RTR1. E0/1 had the BR-side IP but the cable went to HQ-RTR1.

During the correction attempt, `no ip address` cleared E0/0's IP but the
replacement command did not apply — E0/0 showed `unassigned` after the change.

**Root cause:**
Two issues occurred simultaneously:
1. CML cables were placed on opposite interfaces from the design document.
2. `no ip address` without specifying the full address/mask cleared the IP
   on IOL but the subsequent `ip address` command did not apply in the same
   sequence, leaving E0/0 unassigned.

**Fix:**
Rather than recabling in CML, IPs were reassigned to match the actual cable
positions as revealed by CDP:
```
interface Ethernet0/1
 description WAN-TO-HQ-RTR1-E0/2
 ip address 10.0.0.6 255.255.255.252

interface Ethernet0/0
 description WAN-TO-BR-RTR1-E0/2
 ip address 10.0.0.9 255.255.255.252
```
Ping results after fix:
- 10.0.0.5 (HQ-RTR1): 100% ✅
- 10.0.0.10 (BR-RTR1): 80% (first packet = ARP, normal) ✅

**Lesson:**
Always run `show cdp neighbors` BEFORE assigning IPs to any new device. CDP
reveals actual cable connections, which may differ from the design document in CML.
Never assume cables are connected where the diagram says they should be.

---

## Entry 2 — DR/BDR Election on Point-to-Point WAN Links

**Date:** 2026-04-12 | **Phase:** 1

**Symptom:**
After OSPF came up, `show ip ospf neighbor` showed FULL/DR and FULL/BDR
on all WAN adjacencies:
```
Neighbor ID     Pri   State           Dead Time   Address         Interface
10.0.255.3        1   FULL/DR         00:00:38    10.0.0.6        Ethernet0/2
10.0.255.2        1   FULL/BDR        00:00:38    10.0.0.2        Ethernet0/1
```

**Expected:**
On a point-to-point /30 WAN link with exactly two routers, there should be
no DR/BDR election. State should show `FULL/ -` with `Pri=0`.

**Investigation:**
```
show ip ospf interface Ethernet0/1
```
Confirmed network type was BROADCAST (IOS default for Ethernet interfaces).
DR/BDR elections exist for multi-access networks (many routers on the same
segment). On a /30 with only 2 endpoints the election is overhead with no benefit
and adds extra delay during convergence.

**Root cause:**
IOL Ethernet interfaces default to OSPF network type BROADCAST regardless of
the subnet mask. This triggers a DR/BDR election even on a /30 point-to-point link.

**Fix:**
Applied `ip ospf network point-to-point` to all WAN-facing interfaces on all
three routers. The adjacencies briefly dropped and reformed — expected behavior
when changing the OSPF network type:
```
interface Ethernet0/1
 ip ospf network point-to-point
interface Ethernet0/2
 ip ospf network point-to-point
```
Applied on HQ-RTR1, BR-RTR1, and WAN-RTR1. During the one-sided change,
a transient NET_TYPE_MISMATCH warning appeared — this is normal and resolved
itself once both sides were updated.

Final state on all routers:
```
Neighbor ID     Pri   State     Dead Time   Address    Interface
10.0.255.3        0   FULL/ -   00:00:33    10.0.0.6   Ethernet0/2
10.0.255.2        0   FULL/ -   00:00:32    10.0.0.2   Ethernet0/1
```

**Lesson:**
Always set `ip ospf network point-to-point` on /30 WAN links in IOS/IOL.
Ethernet interfaces default to BROADCAST mode causing unnecessary DR/BDR
elections and slower convergence. This applies to both OSPFv2 and OSPFv3.

---

## Entry 3 — OSPF Failover and Reconvergence Test (Phase 5)

**Date:** 2026-04-12 | **Phase:** 5

**Symptom:**
Intentional outage. The preferred OSPF path through WAN-RTR1 was interrupted
by shutting HQ-RTR1 Ethernet0/2.

**Expected:**
OSPF should remove the WAN-RTR1 adjacency immediately (interface down, not dead
timer expiry), install the higher-cost direct HQ↔BR path (cost 110), and preserve
inter-site reachability. When the interface comes back, OSPF should return traffic
to the preferred WAN-RTR1 path.

**Investigation:**
Before failure:
```
show ip ospf neighbor → 2 neighbors FULL/ -
show ip route 10.2.100.1 → via 10.0.0.6 on E0/2, metric 30
traceroute 10.2.100.1 source 10.1.100.1 → Hop 1: 10.0.0.6 (WAN-RTR1)
```

After shutdown of E0/2:
```
%OSPF-5-ADJCHG: Process 1, Nbr 10.0.255.3 on Ethernet0/2 from FULL to DOWN
show ip ospf neighbor → Only BR-RTR1 (10.0.255.2) remaining
show ip route 10.2.100.1 → via 10.0.0.2 on E0/1, metric 110 ← backup path active
traceroute 10.2.100.1 source 10.1.100.1 → Hop 1: 10.0.0.2 (direct to BR-RTR1)
```

After `no shutdown` on E0/2:
```
%OSPF-5-ADJCHG: Nbr 10.0.255.3 on Ethernet0/2 from LOADING to FULL
show ip route 10.2.100.1 → back to 10.0.0.6 on E0/2, metric 30
```

**Root cause:**
Intentional test. No actual fault.

**Fix:**
Restored with `no shutdown` on Ethernet0/2.

**Lesson:**
OSPF cost manipulation worked correctly. The network failed over to the
direct backup link during outage (metric changed from 30 to 110) and reconverged
back to the optimal path when the preferred path returned. Interface-down events
trigger immediate adjacency loss — no need to wait for the dead timer.

---

## Entry 4 — IP SLA Probe Would Not Start (Threshold > Timeout)

**Date:** 2026-04-12 | **Phase:** 7

**Symptom:**
After configuring IP SLA, tracking, and a floating static route, the probe was
not running. The tracked route never became active.
```
show ip sla statistics → Number of successes: Unknown, failures: Unknown
show track 10 → Reachability is Down, return code: Unknown
show ip route static → empty (floating static not installed)
Operation time to live: 0
```

**Expected:**
IP SLA probe actively sending ICMP probes every 5 seconds. Track object showing
Reachability is Up. Floating static configured and standing by (not installed while
OSPF is preferred).

**Investigation:**
Manual ping to the probe target succeeded:
```
ping 10.0.255.3 source 10.0.0.5 → !!!!! 100%
```
Layer 3 reachability was not the problem. Checked SLA configuration:
```
show ip sla configuration 10
→ Next Scheduled Start Time: Pending trigger
→ Status of entry (SNMP RowStatus): notInService
→ Threshold (milliseconds): 5000
→ Operation timeout (milliseconds): 1000
```
The schedule command had been rejected with:
```
%Scheduling a probe with threshold 5000 ms greater than timeout 1000 ms is not allowed.
```

**Root cause:**
The IP SLA operation had threshold set to 5000ms (default) while timeout was 1000ms.
IOS rejects the `ip sla schedule` command when threshold > timeout, leaving the
probe in `notInService` state. The probe was created but never started.

**Fix:**
Removed and recreated the SLA with matching threshold and timeout values:
```
no ip sla 10
ip sla 10
 icmp-echo 10.0.255.3 source-ip 10.0.0.5
 timeout 1000
 threshold 1000    ← must be <= timeout
 frequency 5
exit
ip sla schedule 10 life forever start-time now
```
After fix, router reported:
```
%TRACK-6-STATE: 10 ip sla 10 reachability Down -> Up
show track 10 → Reachability is Up, return code: OK, RTT: 1ms
```

**Lesson:**
When IP SLA will not start, check `show ip sla configuration` for
`Pending trigger` and `notInService`. Compare threshold against timeout.
IOS silently rejects the schedule command if threshold > timeout. Always
set threshold equal to or less than timeout.

---

## Entry 5 — IP SLA Probe Target Caused Track to Fail During OSPF Outage

**Date:** 2026-04-12 | **Phase:** 7

**Symptom:**
When OSPF was shut down to test the floating static backup, the track object went
Down instead of staying Up. The floating static never installed. The network lost
all reachability to HQ — exactly what the backup was designed to prevent.

Console output during OSPF shutdown on BR-RTR1:
```
%OSPF-5-ADJCHG: Nbr 10.0.255.3 from FULL to DOWN
%TRACK-6-STATE: 10 ip sla 10 reachability Up -> Down  ← should NOT happen
show ip route 10.1.100.1 → % Subnet not in table
ping 10.1.100.1 source 10.2.100.1 → ..... 0%
```

**Expected:**
Track should remain Up when OSPF fails. The IP SLA probe runs independently of
OSPF routing. The floating static (AD 250) should install automatically and
maintain connectivity via the direct backup link.

**Investigation:**
Examined the probe target. The probe was configured to reach `10.0.255.1`
(HQ-RTR1 loopback) — a non-directly-connected address that exists only in the
OSPF routing table. When OSPF died, the route to the probe target disappeared
from the routing table. Without a route to reach the probe target, the ICMP
probe failed. The track object went Down. The floating static (with `track 10`
condition) never installed.

The probe was dependent on the exact routing protocol it was designed to back up.

**Root cause:**
The IP SLA probe target was reachable ONLY through OSPF. When OSPF failed:
1. OSPF routes removed from table
2. Route to probe target (loopback) disappeared
3. ICMP probe failed — no path to destination
4. Track object went Down
5. Floating static condition not met — never installed
6. Network had zero reachability to remote site

**Fix:**
Changed the probe target to the directly connected IP on the backup WAN link.
A /30 directly connected IP requires no routing — just ARP on the same subnet:

```
! BR-RTR1 — probe HQ-RTR1's directly connected E0/1 IP
ip sla 10
 icmp-echo 10.0.0.1 source-ip 10.0.0.2   ← same /30 subnet, no routing needed
 timeout 1000
 threshold 1000
 frequency 5

! HQ-RTR1 — probe BR-RTR1's directly connected E0/1 IP
ip sla 10
 icmp-echo 10.0.0.2 source-ip 10.0.0.1   ← same /30 subnet, no routing needed
```

After fix — with OSPF shut down:
```
show track → Reachability is Up  ✅ (probe still works via direct link)
show ip route static → S 10.1.0.0/16 [250/0] via 10.0.0.1  ✅ (installed)
ping 10.1.100.1 source 10.2.100.1 → !!!!!  100%  ✅ (network never went dark)
```

After OSPF restored:
```
show ip route 10.1.100.1 → O IA [110/30] via 10.0.0.9  ✅ (OSPF preferred again)
show ip route static → empty  ✅ (floating static suppressed by OSPF AD 110)
```

**Lesson:**
An IP SLA probe target must be reachable INDEPENDENTLY of the routing protocol
it backs up. Always probe a directly connected address on the backup path —
never a loopback or remote IP that requires dynamic routing to reach. The probe
must survive the same failure scenario it is designed to detect. If the probe
relies on the protocol it monitors, the entire tracking mechanism fails at the
worst possible moment.
