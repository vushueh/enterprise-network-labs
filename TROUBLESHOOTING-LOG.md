# Troubleshooting Log

Running log of every problem encountered across all projects.
This is the most valuable document in the repo.

---

## Project 01 - Campus Foundation

### Issue 1 - Interface Naming Mismatch (Phase 1/2)

**Date:** 2026-04-02

**Symptom:** Project template used GigabitEthernet0/0 and GigabitEthernet1/0 but those interfaces did not exist on CML nodes.

**Investigation:** Ran show ip interface brief after boot. IOL router showed Ethernet0/0 to Ethernet0/3 (administratively down). IOL-L2 showed Ethernet0/0 to Ethernet0/3 only, no slot 1.

**Root cause:** CML IOL images use Ethernet naming not GigabitEthernet. Nodes had one 4-port slot only, so Ethernet1/x ports did not exist.

**Fix:** Adapted all configs to Ethernet0/x. Remapped access ports: HQ-ASW1 E0/2=VLAN100, E0/3=VLAN999. HQ-ASW2 E0/2=VLAN200.

**Lesson:** Always run show ip interface brief on every node after boot. The live device output is the source of truth, not the template.

---

### Issue 2 - Native VLAN Mismatch During Trunk Build (Phase 2)

**Date:** 2026-04-03 approx 01:39-01:42 UTC

**Symptom:** CDP warnings on HQ-DSW1 console repeatedly:
  %CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on Ethernet0/3 (1000), with HQ-DSW2 Ethernet0/3 (1).
Same appeared for E0/1 (toward ASW1) and E0/2 (toward ASW2).

**How to read the message:**
  on Ethernet0/3 (1000) = local port and local native VLAN
  with HQ-DSW2 Ethernet0/3 (1) = remote device, remote port, remote native VLAN

**Investigation:** Checked timestamps on running configs. DSW2 was last changed at 01:43, ASW2 at 01:48. Warnings appeared while those switches were still being configured. After completing all switches, ran show interfaces trunk and all showed native VLAN 1000.

**Root cause:** Build-time mismatch. DSW1 was configured first with native VLAN 1000. The far-end switches were still on default native VLAN 1 while being configured. CDP detected and logged the temporary mismatch.

**Fix:** Completed trunk configuration on all remaining switches. Warnings stopped once both ends matched.

**Lesson:** Temporary CDP native VLAN mismatch warnings during one-side-at-a-time configuration are normal. They are not acceptable in the final state. Verify show interfaces trunk on ALL switches after completing the full build.

---

### Issue 3 - One-Way CDP Visibility on RTR1 (Phase 2/3)

**Date:** 2026-04-03

**Symptom:** HQ-DSW1 showed HQ-RTR1 as CDP neighbor. HQ-RTR1 showed zero CDP neighbors.

**Investigation:** DSW1 E0/0 trunk was operational. RTR1 Ethernet0/0 was up/up. CDP globally enabled on both. Ran show cdp neighbors multiple times on RTR1, still 0.

**Root cause:** Timing or CDP table refresh issue, possibly a CML IOL platform quirk. Physical link was up and trunk was operational.

**Fix:** Proceeded with Phase 3. After configuring subinterfaces and verifying routing with show ip route and successful ping, ran show cdp neighbors on RTR1 again and HQ-DSW1 appeared correctly.

**Lesson:** One-way CDP visibility does not always mean a connectivity failure. CDP is a verification aid not definitive proof. Final proof is: (1) show ip interface brief, (2) show ip route, (3) successful cross-VLAN ping.

---

### Issue 4 - STP Redundant Trunk Showing none for Forwarding VLANs (Phase 4)

**Date:** 2026-04-03

**Symptom:** show interfaces trunk on HQ-DSW2 and HQ-ASW2 showed some trunk ports with none in the Vlans in spanning tree forwarding state column.

**Investigation:** Trunk was operationally up and trunking. Native VLAN and allowed VLANs correct. CDP showed neighbors on those ports. All affected ports were redundant secondary uplink paths.

**Root cause:** Not a failure. Rapid-PVST+ was blocking the redundant path to prevent a Layer 2 loop. With dual distribution switches, STP must block one path per VLAN. A trunk can be physically up while STP blocks forwarding on it.

**Fix:** No fix required. Correct behavior. STP hardening confirmed expected root layout: HQ-DSW1 root for VLANs 100 and 999, HQ-DSW2 root for VLANs 200 and 300.

**Lesson:** Vlans in STP forwarding state = none does NOT mean the trunk is broken. A blocked port is STP doing its job. Always distinguish between link up/trunking (physical state) and STP forwarding (logical state).

---

### Issue 5 - SSH Connection Refused Despite VTY Config Applied (Phase 5)

**Date:** 2026-04-03

**Symptom:** SSH from PC-MGMT1 to HQ-DSW1 failed with connection refused even though ping worked.
  ssh admin@10.1.99.11
  ssh: connect to host 10.1.99.11 port 22: Connection refused

**Investigation:** Ping to 10.1.99.11 succeeded, so IP reachability was not the issue. Ran show ip ssh on HQ-DSW1 and it showed: SSH Disabled - version 2.0, Please create EC or RSA keys, IOS Keys: NONE. RSA host keys were missing despite ip ssh version 2 being configured.

**Root cause:** crypto key generate rsa was not successfully completed during initial Phase 5 config. Likely because ip domain-name was not set first (required prerequisite). Without host keys, SSH port 22 never opens.

**Fix:** Re-ran on all devices in order:
  configure terminal
  ip domain-name lab.local
  crypto key generate rsa general-keys modulus 2048
IOS confirmed: %SSH-5-ENABLED: SSH 2.0 has been enabled

**Lesson:** ip ssh version 2 alone does NOT enable SSH. Three things required: (1) ip domain-name set first, (2) RSA keys generated, (3) verify with show ip ssh showing SSH Enabled. Connection refused means SSH not listening. Connection timed out means ACL block.

---

## Project 01 - Break/Fix Challenge

### Intentional Fault: VLAN 100 Removed from Trunk Allowed List

**Date:** 2026-04-03

---

#### Attempt 1 - Single Trunk Break (Unexpected Result)

**Break introduced on HQ-DSW1 Ethernet0/1:**
  interface Ethernet0/1
   switchport trunk allowed vlan 200,300,999
VLAN 100 removed from the trunk between HQ-DSW1 and HQ-ASW1.

**Expected symptom:** PC-ENG1 loses connectivity.

**Actual result:** PC-ENG1 ping STILL WORKED. No loss of connectivity.

**Why it still worked — Redundant Design Proof:**
The dual distribution switch design automatically protected against this single trunk failure.
When VLAN 100 was removed from HQ-DSW1 E0/1, STP and the redundant topology rerouted traffic:

  PC-ENG1 → HQ-ASW1 E0/1 → HQ-DSW2 E0/1 (VLAN 100 still allowed here)
           → HQ-DSW2 E0/3 → HQ-DSW1 E0/3 (inter-distribution trunk)
           → HQ-DSW1 E0/0 → HQ-RTR1 (router-on-a-stick)

The redundant uplink from HQ-ASW1 to HQ-DSW2 took over automatically.
This is EXACTLY what dual distribution switches are designed to do in production.

**Key engineering insight:** Removing one trunk link from a redundant L2 design does NOT
cause an outage — it causes a path shift. This is why enterprises use dual distribution
switches. A single link failure is survivable. Only removing ALL paths causes an outage.

---

#### Attempt 2 - Both ASW1 Uplinks Broken (Correct Break)

**Break introduced on HQ-ASW1 — both uplinks:**
  interface Ethernet0/0
   switchport trunk allowed vlan 200,300,999
  interface Ethernet0/1
   switchport trunk allowed vlan 200,300,999
VLAN 100 removed from BOTH uplinks on HQ-ASW1, eliminating all paths for PC-ENG1.

**Symptom observed:**
PC-ENG1 (10.1.100.10) lost all connectivity. PC-SALES1 and PC-MGMT1 continued working.
Both trunk links on ASW1 remained UP — no physical indication of failure.

**Diagnosis using show interfaces trunk on HQ-ASW1:**
  Et0/0  Vlans allowed on trunk: 200,300,999  (VLAN 100 missing)
  Et0/1  Vlans allowed on trunk: 200,300,999  (VLAN 100 missing)
VLAN 100 blocked on both uplinks. PC-ENG1 had no path to the router.

**Fix:**
  configure terminal
  interface Ethernet0/0
   switchport trunk allowed vlan 100,200,300,999
  interface Ethernet0/1
   switchport trunk allowed vlan 100,200,300,999
  end
  write memory
PC-ENG1 connectivity restored immediately.

**Lesson 1 - Redundancy works:** Removing VLAN 100 from ONE trunk in a redundant design
does NOT cause an outage. The standby path takes over automatically. This is the value
of dual distribution switches — single link failures are survivable.

**Lesson 2 - Subtle trunking failure:** A wrong allowed VLAN list is one of the most
common trunking failures. The trunk stays UP with no physical errors. The only way to
catch it is show interfaces trunk — check the Vlans allowed column carefully on both ends.

**Lesson 3 - In production:** If only ONE of the two ASW1 uplinks had VLAN 100 removed,
it would look fine from the switch perspective but traffic would be asymmetric. This is
why allowed VLAN lists must be consistent across all redundant trunk pairs.

---

## Project 02 — Multi-Site Expansion + DHCP

### Issue P02-01 — BR-ASW1 Access Port Configured on Wrong Interface (Phase 1)

**Date:** 2026-04-05

**Symptom:** PC-BR1 had no network connectivity. No DHCP, no ping to gateway. Port was configured but traffic not passing.

**Investigation:** show vlan brief showed Ethernet1/0 listed under VLAN 100. Cross-referenced CML canvas — PC-BR1 cable was connected to Ethernet0/1, not Ethernet1/0.

**Root cause:** Interface naming transposition during config entry. Ethernet1/0 and Ethernet0/1 are visually similar names — easy to swap. Config was applied to the wrong interface.

**Fix:** Moved the PC-BR1 cable in CML from Ethernet0/1 to Ethernet1/0 to match the existing config. No IOS changes needed.

**Lesson:** On IOL-L2, always cross-check interface names against the CML topology canvas. Run show cdp neighbors or show interfaces status immediately after cabling to confirm the correct interface is up before configuring.

---

### Issue P02-02 — BR-ASW1 ip default-gateway Insufficient for Remote-Subnet ICMP (Phase 2)

**Date:** 2026-04-05

**Symptom:** Ping from HQ-RTR1 (10.0.0.1) to BR-ASW1 (10.2.99.3) failed with 0% success. Pings to BR-RTR1 (10.2.99.1) and BR-DSW1 (10.2.99.2) on the same subnet succeeded.

**Investigation:** Phase 1 ping from BR-RTR1 to 10.2.99.3 had worked (source was 10.2.99.1 — same subnet, no gateway needed for reply). HQ-RTR1 sources from 10.0.0.1 — a remote subnet — exposing the ip default-gateway limitation.

**Root cause:** ip default-gateway on IOL-L2 does not properly forward ICMP replies destined to remote subnets. The reply from BR-ASW1 to 10.0.0.1 was dropped silently because the management-plane handler cannot route beyond directly connected subnets.

**Fix:** Enabled ip routing on BR-ASW1. Added ip route 0.0.0.0 0.0.0.0 10.2.99.1. Removed ip default-gateway.

**Lesson:** ip default-gateway is only safe for same-subnet management access. Any device that must respond to traffic from remote subnets needs ip routing + a default route.

---

### Issue P02-03 — Dnsmasq Container Failed to Start — bind-interfaces Crash (Phase 3)

**Date:** 2026-04-05

**Symptom:** CML error: "container failed to start" with code 30 when starting HQ-DHCP-DNS node.

**Root cause:** bind-interfaces directive in dnsmasq.conf causes a race condition on some CML Dnsmasq node versions — dnsmasq starts before eth0 is fully ready.

**Fix:** Removed bind-interfaces from dnsmasq.conf. Restored both config files using the RESTORE button in CML CONFIG tab.

**Lesson:** Avoid bind-interfaces on CML Dnsmasq nodes. The default wildcard binding works correctly and does not have the timing dependency.

---

### Issue P02-04 — DHCP Relay Not Firing — Missing helper-address (Phase 3)

**Date:** 2026-04-05

**Symptom:** dnsmasq log showed "no address range available via eth0" continuously. debug ip dhcp server packet on BR-RTR1 showed no output — relay not firing at all.

**Root cause:** ip helper-address had not been configured on either router. Without the relay agent, DHCP broadcasts never leave the local subnet — the server never sees them.

**Fix:** Configured ip helper-address 10.1.99.50 on all data VLAN subinterfaces on both HQ-RTR1 and BR-RTR1.

**Lesson:** Centralized DHCP requires ip helper-address on every router subinterface serving client subnets. Missing even one subinterface means that VLAN gets no DHCP service.

---

### Issue P02-05 — interface=eth0 in dnsmasq.conf Blocking Relay Packets (Phase 3)

**Date:** 2026-04-05

**Symptom:** Even after configuring helper-address, dnsmasq continued showing "no address range available via eth0" — never showing "via 10.x.x.x" which indicates relay.

**Root cause:** interface=eth0 tells dnsmasq to only process requests arriving directly on eth0 as broadcasts. Relayed DHCP packets arrive as unicast UDP on port 67 — this line caused dnsmasq to reject them silently.

**Fix:** Removed interface=eth0 from dnsmasq.conf.

**Lesson:** Never use interface= restriction on a centralized DHCP server that serves relayed requests.

---

### Issue P02-06 — HQ-DHCP-DNS eth0 NO-CARRIER — Missing VLAN Config on HQ-DSW2 (Phase 3)

**Date:** 2026-04-05

**Symptom:** ip link show eth0 on HQ-DHCP-DNS showed NO-CARRIER, state DOWN. Node had no network connectivity despite cable existing in CML.

**Root cause:** HQ-DSW2 E0/0 was physically connected but never configured as an access port in VLAN 999. Port was in VLAN 1 default state — HQ-DHCP-DNS had no valid Layer 2 path.

**Fix:** Configured HQ-DSW2 E0/0 as access port VLAN 999 with PortFast and BPDU Guard.

**Lesson:** Always configure the switchport before connecting a server. A cable without a VLAN assignment is the same as no cable from the server's perspective.

---

### Issue P02-07 — Wrong Console Open — udhcpc Run on HQ-DHCP-DNS (Phase 3)

**Date:** 2026-04-05

**Symptom:** udhcpc run on what appeared to be PC-BR1 failed. IOS debug commands typed on same device returned "not found".

**Root cause:** Multiple CML console tabs open. inserthostname-here hostname was the HQ-DHCP-DNS node (default hostname on CML Alpine/Dnsmasq nodes), not PC-BR1. Running udhcpc on the DHCP server asked the server to give itself an address.

**Fix:** Opened correct PC-BR1 console. Set hostnames on all nodes.

**Lesson:** Always verify hostname in the shell prompt before running any command. Run hostname on Alpine nodes to confirm which node you are on.

---

### Issue P02-08 — HQ-DHCP-DNS Loses IP on Every Restart (Phase 3/5)

**Date:** 2026-04-05

**Symptom:** After stopping and starting HQ-DHCP-DNS, ping to 10.1.99.50 from HQ-RTR1 failed immediately after node showed BOOTED in CML.

**Root cause:** CML shows node as BOOTED before the startup script finishes executing. The startup script sets the IP and default route — but pinging immediately catches the node before script completion.

**Fix:** Wait 15-20 seconds after BOOTED state appears before testing connectivity. Added ip addr show and ip route show to startup script output for visual confirmation on every boot.

**Lesson:** CML container BOOTED state does not equal startup script completed. Always wait before testing.

---

### Issue P02-09 — dnsmasq NXDOMAIN — domain= Without Address Records (Phase 5)

**Date:** 2026-04-05

**Symptom:** nslookup returning NXDOMAIN for all lab.local names even though dnsmasq was reachable and domain=lab.local + local=/lab.local/ were configured.

**Root cause:** domain= and local= are routing directives that tell dnsmasq where to look — they do not create any DNS records. Without address= entries or a populated hosts file, dnsmasq has nothing to return.

**Fix:** Added address= directives for all infrastructure hosts directly in dnsmasq.conf.

**Lesson:** Always pair domain= and local= with actual host records using address= directives.

---

### Issue P02-10 — pc-br1.lab.local NXDOMAIN — Dynamic IP in Static DNS Record (Phase 5)

**Date:** 2026-04-05

**Symptom:** nslookup pc-br1.lab.local returned NXDOMAIN even though address= entry existed in dnsmasq.conf.

**Root cause:** DHCP leases can change between restarts. The hardcoded IP in address= did not always match the current lease. Without a static reservation, the endpoint could get a different IP on each boot.

**Fix:** Added dhcp-host= static reservations using MAC addresses for both PC-BR1 and PC-BR2. This locks endpoints to permanent IPs regardless of restart order.

**Lesson:** Never hardcode dynamic DHCP IPs in DNS records. Always use static DHCP reservations for any device that needs a predictable DNS entry.

---

### Issue P02-11 — no ip domain lookup Blocking DNS on BR-RTR1 (Phase 5)

**Date:** 2026-04-05

**Symptom:** BR-RTR1 could ping 10.1.99.50 directly but ping hq-rtr1.lab.local returned "Unrecognized host or address". ip name-server 10.1.99.50 was configured.

**Root cause:** no ip domain lookup was configured in Phase 1 hardening to prevent the 30-second DNS timeout when mistyping IOS commands. This same setting blocks all DNS resolution from the router itself.

**Fix:** ip domain lookup re-enabled. ip name-server 10.1.99.50 confirmed. DNS resolution worked immediately.

**Lesson:** no ip domain lookup is double-edged — prevents mistyped command timeouts but also blocks legitimate DNS queries. The better approach is ip domain lookup with a valid name-server configured.

---

### Issue P02-12 — Alpine PC Nodes Showing inserthostname-here (Phase 3/5)

**Date:** 2026-04-05

**Symptom:** Both PC-BR1 and PC-BR2 showed inserthostname-here as hostname. dnsmasq log showed "client provides name: localhost" for all DHCP leases.

**Root cause:** CML Alpine Linux nodes do not set a hostname by default. Every node boots with the placeholder inserthostname-here.

**Fix:** Ran hostname pc-br1 and hostname pc-br2 in each session. Added hostname command to each node's startup script in CML CONFIG tab for persistence.

**Lesson:** Set hostnames on all Alpine nodes immediately after adding them to the topology. Add the hostname command to the startup script so it survives every reboot.

---

## Project 02 — Break/Fix Challenge

### Three Simultaneous DHCP Faults

**Date:** 2026-04-05

**Symptom:** Two helpdesk tickets simultaneously: Branch Engineering VLAN 100 — no DHCP. HQ Sales VLAN 200 — no DHCP. DNS and management connectivity unaffected.

**Faults introduced:**
1. BR-RTR1 E0/0.100 helper-address changed to 10.1.99.99
2. HQ-RTR1 E0/0.200 helper-address changed to 10.1.99.99
3. BR-RTR1 ip route 10.1.99.0 255.255.255.0 Null0 added (black-hole)

**Investigation:**
Layer 1-2: show vlan brief and show interfaces trunk — clean, no issues.
Layer 3: show ip route 10.1.99.0 on BR-RTR1 revealed TWO routing entries — one via 10.0.0.1 (correct) and one via Null0 (black-hole). Ping succeeded intermittently due to IOS load-balancing between both paths — false positive. DHCP relay consistently hit the Null0 path causing silent drops.
Layer 3 relay: show running-config | section helper revealed wrong helper-address on BR-RTR1 E0/0.100 and HQ-RTR1 E0/0.200.

**Fix order (dependency critical):**
1. Removed Null0 route first — fixing helper-address without this would still fail
2. Corrected helper-address on BR-RTR1 E0/0.100 to 10.1.99.50
3. Corrected helper-address on HQ-RTR1 E0/0.200 to 10.1.99.50

**Lesson:** A successful ping does not prove a clean routing path. Always check show ip route for the specific destination. A Null0 black-hole with a competing legitimate route causes intermittent success that hides the real fault. Fix routing before fixing application-layer config — dependency order determines whether fixes actually take effect.

---

## Project 03 — OSPF Dynamic Routing

### Entry 1 — WAN-RTR1 Interface IP Mismatch

**Date:** 2026-04-12 | **Phase:** 1 (Pre-work)

**Symptom:** Pings from WAN-RTR1 to HQ-RTR1 (10.0.0.5) and BR-RTR1 (10.0.0.10) failing with 0% success rate immediately after configuring WAN-RTR1 interfaces. Same-subnet pings should never fail — no routing required, just ARP.

**Investigation:** `show cdp neighbors` revealed cables in CML were connected to opposite interfaces from the design document. WAN-RTR1 E0/1 connected to HQ-RTR1 but had the BR-side IP; E0/0 connected to BR-RTR1 but had the HQ-side IP. Additionally, `no ip address` without specifying the full mask cleared the address but the replacement command did not apply, leaving E0/0 unassigned.

**Root cause:** CML cable positions differed from design; IPs were assigned based on design rather than actual cable layout. Secondary issue: IOL `no ip address` behavior when full address/mask not specified.

**Fix:** Reassigned IPs to match actual cable positions confirmed by CDP. E0/1 = 10.0.0.6 (HQ side), E0/0 = 10.0.0.9 (BR side). Pings returned 100% after fix.

**Lesson:** Always run `show cdp neighbors` BEFORE assigning IPs to any new device. CDP reveals actual cable connections. Never assume CML cables are connected where the diagram shows.

---

### Entry 2 — DR/BDR Election on Point-to-Point WAN Links

**Date:** 2026-04-12 | **Phase:** 1

**Symptom:** `show ip ospf neighbor` showed FULL/DR and FULL/BDR on all WAN adjacencies instead of FULL/ - with Pri=0.

**Investigation:** `show ip ospf interface` confirmed network type was BROADCAST (IOL default for Ethernet). DR/BDR elections are unnecessary overhead on a /30 with only 2 endpoints and add delay during convergence.

**Root cause:** IOL Ethernet interfaces default to OSPF network type BROADCAST regardless of subnet mask.

**Fix:** Applied `ip ospf network point-to-point` to all WAN-facing interfaces on all three routers. Adjacencies dropped and reformed — expected behavior when changing network type. Both sides must be changed; one-sided change produces transient NET_TYPE_MISMATCH.

**Lesson:** Always set `ip ospf network point-to-point` on /30 WAN links in IOS/IOL. Applies to both OSPFv2 and OSPFv3.

---

### Entry 3 — OSPF Failover and Reconvergence Test (Phase 5)

**Date:** 2026-04-12 | **Phase:** 5

**Symptom:** Intentional outage. HQ-RTR1 E0/2 shut to test failover to backup path.

**Result:** OSPF immediately removed WAN-RTR1 adjacency (interface-down event, not dead-timer expiry). Route to Branch switched from metric 30 (via WAN-RTR1) to metric 110 (direct backup). On `no shutdown`, traffic returned to preferred path. Cost manipulation worked correctly.

**Lesson:** Interface-down events trigger immediate adjacency loss — no need to wait for dead timer. OSPF cost engineering (cost 10 preferred vs cost 100 backup) produces predictable deterministic failover.

---

### Entry 4 — IP SLA Probe Would Not Start (Threshold > Timeout)

**Date:** 2026-04-12 | **Phase:** 7

**Symptom:** IP SLA probe not running. Track object showed Reachability Down, return code Unknown. Floating static never installed. `show ip sla statistics` showed Unknown counters. Operation time to live: 0.

**Investigation:** `show ip sla configuration` revealed `Next Scheduled Start Time: Pending trigger` and `Status: notInService`. Threshold was 5000ms (default), timeout was 1000ms. The `ip sla schedule` command had been silently rejected with: `%Scheduling a probe with threshold 5000 ms greater than timeout 1000 ms is not allowed.`

**Root cause:** IOS rejects `ip sla schedule` when threshold > timeout, leaving probe in `notInService`. No error is shown at the time of configuration — only at schedule time.

**Fix:** Removed and recreated SLA with `threshold 1000` and `timeout 1000` (threshold ≤ timeout). After fix, track showed Reachability is Up with RTT 1ms.

**Lesson:** When IP SLA won't start, check `show ip sla configuration` for `Pending trigger` and `notInService`. Always set threshold equal to or less than timeout.

---

### Entry 5 — IP SLA Probe Target Caused Track to Fail During OSPF Outage

**Date:** 2026-04-12 | **Phase:** 7

**Symptom:** When OSPF was shut down to test the floating static backup, the track object went Down instead of staying Up. Floating static never installed. Network lost all reachability — the exact failure the backup was designed to prevent.

**Investigation:** Probe target was 10.0.255.1 (HQ-RTR1 loopback) — reachable only via OSPF routes. When OSPF died, the route to the probe target disappeared, the ICMP probe failed, track went Down, and the floating static condition was never met.

**Root cause:** The probe target was reachable ONLY through the routing protocol it was designed to back up. When OSPF failed, both the primary routing and the backup mechanism failed simultaneously.

**Fix:** Changed probe target to directly connected /30 neighbor IP (10.0.0.2 on HQ-RTR1, 10.0.0.1 on BR-RTR1). A directly connected IP requires only ARP — it works regardless of OSPF state. After fix: with OSPF down, track stayed Up, floating static installed, pings succeeded 100%.

**Lesson:** IP SLA probe target must be reachable INDEPENDENTLY of the routing protocol it backs up. Always probe a directly connected IP on the backup link. The probe must survive the same failure scenario it is designed to detect.

---

## Project 04 — Switching Layer Stability

### P04-01 — Storm Control rejected on IOL-L2

**Phase:** Phase 6 — Access Port Protection
**Symptom:** `storm-control broadcast level 1.00 0.50` rejected with `% Invalid input detected at '^' marker`.
**Root cause:** CML IOL-L2 image does not implement storm control (ASIC-level hardware feature not available in software switch image).
**Fix:** Platform limitation. Applied available protections: PortFast, BPDU Guard, BPDU Filter.
**Lesson:** Always verify platform feature support with `show ?` before building a phase around a specific command.

---

### P04-02 — LACP member rejected when changing mode during fault injection

**Phase:** Phase 7 — Break/Fix
**Symptom:** `channel-group 1 mode on` rejected with `Command rejected: the interface can not be added to the channel group` on HQ-DSW2 Et1/0 during fault injection.
**Root cause:** Port retained internal LACP state after `no channel-group 1`. Attempting to re-add with incompatible mode `on` conflicted with the existing LACP bundle.
**Fix:** `default interface Ethernet1/0` to fully reset port state, then re-configured with `channel-group 1 mode active`.
**Lesson:** Use `default interface` as a clean reset before re-configuring a port that was removed from an EtherChannel.

---

### P04-03 — Root Inconsistent on distribution downlinks (correct behavior)

**Phase:** Phase 2 — Advanced STP Controls
**Symptom:** `show spanning-tree inconsistentports` showed DSW1 Et0/1 and Et0/2 as Root Inconsistent for VLANs 200/300 after enabling Root Guard.
**Root cause:** Expected behavior in a split-root design. Access switches have uplinks to both distribution switches and advertise root-path BPDUs for all VLANs. Root Guard blocks the ones where the local switch is not the intended root.
**Fix:** No fix required. This is correct and intended.
**Lesson:** Cross-reference `show spanning-tree inconsistentports` with `show spanning-tree root` before treating inconsistency as a fault.

---

### P04-04 — VTP VLAN 600 persisted after returning to transparent mode

**Phase:** Phase 4 — VTP v3 Learning Lab
**Symptom:** VLAN 600 (VTP-Test) remained in `show vlan brief` on HQ-DSW2, HQ-ASW1, and HQ-ASW2 after switching back to `vtp mode transparent`.
**Root cause:** Changing from VTP client to transparent mode does not delete learned VLANs.
**Fix:** Manually ran `configure terminal → no vlan 600 → end → write memory` on each affected switch.
**Lesson:** Returning to VTP transparent mode is not a clean slate. Test VLANs must be removed explicitly.

---

## Project 05 — Internet Access and NAT

### P05-01 — Object-group network wildcard mask rejected

**Date:** 2026-05-02 | **Phase:** Phase 4 — Object Groups for ACLs

**Symptom:** Object-group entries using wildcard format (`10.1.100.0 0.0.0.255`) rejected with `% Mask 0.0.0.255 is not supported`.

**Root cause:** In the `object-group network` context, this IOL image expects subnet mask format, not wildcard mask. Wildcards are valid in flat extended ACL lines but not inside an object-group.

**Fix:** Rebuilt the object-group using subnet mask format (`255.255.255.0`).

**Lesson:** Flat extended ACLs use wildcard masks. Object-group network uses subnet masks on this IOL image. Always verify syntax from the exact IOS mode where the command will be entered.

---

### P05-02 — `wget` to 203.0.113.97 returned connection refused

**Date:** 2026-05-02 | **Phase:** Phase 2 — PAT

**Symptom:** `wget http://203.0.113.97` returned `Connection refused`. `curl` was also unavailable on Alpine (`curl: not found`).

**Root cause:** 203.0.113.97 is ISP-RTR1 Ethernet0/1 — a router interface with no HTTP service on TCP/80. The router rejected the connection. Target should have been EXT-WEB1 at 203.0.113.100. Alpine nodes include BusyBox `wget` but not `curl`.

**Fix:** Target EXT-WEB1 at 203.0.113.100. Use `wget -O - http://203.0.113.100` on all Alpine nodes.

**Lesson:** `Connection refused` proves TCP SYN reached the destination and was rejected. It is not a NAT failure. For CML Alpine nodes, always use `wget -O -` as the HTTP test tool — `curl` is not installed.

---

### P05-03 — No Guest PC available for VLAN 300 ACL inbound counter verification

**Date:** 2026-05-02 | **Phase:** Phase 5 — Guest VLAN 300 ACL Isolation

**Symptom:** BusyBox `ping` does not accept Cisco-style `source` keyword. PC-ENG1 is physically in VLAN 100 and cannot source traffic as a VLAN 300 host.

**Root cause:** No dedicated Guest endpoint in VLAN 300. Router-generated pings from HQ-RTR1 do not traverse inbound on E0/0.300 the same way a real host would — inbound ACL hit counters stayed at zero.

**Fix:** Verified ACL was present and bound inbound to E0/0.300 using `show ip access-lists` and `show ip interface`. Used HQ-RTR1 extended pings sourced from 10.1.44.1 as a functional approximation. A dedicated Guest PC would give true hit counter proof.

**Lesson:** ACL placement can be verified without an endpoint. Inbound ACL hit counters require traffic from an actual host on that VLAN. Add a dedicated Guest PC in a future validation pass.

---

### P05-04 — First inbound static NAT ping lost one packet

**Date:** 2026-05-02 | **Phase:** Phase 3 — Static NAT for HQ-SRV1

**Symptom:** First ping toward 203.0.113.10 returned `.!!!!` instead of `!!!!!`.

**Root cause:** First packet lost while HQ-RTR1 resolved ARP for HQ-SRV1 at 10.1.40.10. After ARP cache populated, packets 2–5 succeeded.

**Fix:** No configuration fix required. Second ping returns 100%.

**Lesson:** One dropped first packet during initial testing is almost always ARP resolution, not a routing or NAT failure. Always run a second ping before changing config.

---

## Project 06 — Security Hardening

### P06-T01 — Planned Break/Fix: DHCP Snooping Trust on Wrong Port

**Date:** 2026-05-02 | **Phase:** Break/Fix Challenge — DHCP Snooping

**Symptom:** Legitimate clients fail to receive DHCP leases after DHCP snooping is enabled.

**Root cause:** DHCP snooping trust is placed on an access port instead of the real trunk/uplink toward the authorized DHCP server path. Valid DHCP offers arrive on an untrusted interface and are dropped.

**Fix:** Remove `ip dhcp snooping trust` from the access port and apply it only to the correct uplink/trunk interface. Clear counters, renew DHCP, and verify the binding table.

**Lesson:** DHCP snooping trust is a directional trust decision. Trust the path to the real DHCP server, never the user edge.

---

### P06-01 — ACL-VLAN200-IN Blocking DHCP Renewals and DNS to 10.1.99.50 (Discovered During Project 07 Pre-work)

### P06-01 — ACL-VLAN200-IN Blocking DHCP Renewals and DNS to 10.1.99.50

**Date:** 2026-05-03 | **Phase:** Post-build review

**Symptom:** Console on HQ-RTR1 flooded with repeated syslog messages:
```
%SEC-6-IPACCESSLOGDP: list ACL-VLAN200-IN denied icmp 10.1.200.142 -> 10.1.99.1 (8/0), 360 packets
%SEC-6-IPACCESSLOGP: list ACL-VLAN200-IN denied udp 10.1.200.142(68) -> 10.1.99.50(67), 1 packet
```
ICMP denials appeared every ~5 minutes. DHCP renewal denial appeared intermittently.

**Investigation:** `show ip access-lists ACL-VLAN200-IN` confirmed line 10 had 97,067+ matches — a Sales VLAN device (10.1.200.142 = PC-SALES1) continuously pinging the Management VLAN gateway (10.1.99.1). That is correct behavior — the ACL is working as designed from Project 06. The critical finding was the UDP deny: source port 68 (DHCP client) to destination port 67 (DHCP server at 10.1.99.50). This is a DHCP lease renewal — not a DHCP discover.

**Root cause:** DHCP discover packets are broadcasts (0.0.0.0 → 255.255.255.255) processed by `ip helper-address` before the inbound ACL sees them — so initial DHCP works fine. DHCP renewals however are unicast (client IP → server IP) and DO hit the inbound ACL. The broad deny line `deny ip 10.1.200.0 0.0.0.255 10.1.99.0 0.0.0.255` blocks unicast renewal packets to 10.1.99.50 before they can reach the relay. Same problem exists for DNS UDP/TCP 53 to 10.1.99.50. Without a fix, VLAN 200 devices will fail to renew leases and eventually lose their IPs.

**Fix:** Added three permit lines BEFORE the management deny on ACL-VLAN200-IN:
```
ip access-list extended ACL-VLAN200-IN
 5 permit udp 10.1.200.0 0.0.0.255 eq 68 host 10.1.99.50 eq 67
 6 permit udp 10.1.200.0 0.0.0.255 host 10.1.99.50 eq 53
 7 permit tcp 10.1.200.0 0.0.0.255 host 10.1.99.50 eq 53
```
Line 5 permits DHCP renewals (source port 68 client → destination port 67 server).
Lines 6 and 7 permit DNS over UDP and TCP to the DHCP/DNS server specifically.
The broad management deny at line 10 still blocks everything else to 10.1.99.0/24.

**Verification:**
```
show ip access-lists ACL-VLAN200-IN
show logging | include 10.1.200.142
```
Lines 5/6/7 appear above line 10. DHCP renewal denials stop. ICMP denials to 10.1.99.1 continue (correct).

**Lesson:** DHCP discovers are broadcasts handled by ip helper-address before ACLs — initial DHCP always works. DHCP renewals are unicast and hit inbound ACLs directly. Any ACL that blocks a VLAN from the management range will silently break DHCP renewals if the DHCP server lives in that management range. Always permit UDP port 67/68 and UDP/TCP 53 to the specific DHCP/DNS server host BEFORE the broad management deny. Apply the same correction to ACL-VLAN100-IN and ACL-VLAN300-IN.
