# Project 02 — Troubleshooting Log

All problems encountered during the Multi-Site Expansion + DHCP build.
Each entry follows the same format: Symptom → Investigation → Root Cause → Fix → Lesson.

---

## Issue P02-01 — BR-ASW1 Access Port Configured on Wrong Interface (Phase 1)

**Date:** 2026-04-05

**Symptom:** PC-BR1 had no network connectivity. No DHCP, no ping to gateway. Port was
configured but traffic not passing.

**Investigation:** `show vlan brief` showed Ethernet1/0 listed under VLAN 100.
Cross-referenced CML canvas — PC-BR1 cable was connected to Ethernet0/1, not Ethernet1/0.

**Root cause:** Interface naming transposition during config entry. Ethernet1/0 and Ethernet0/1
are visually similar names — easy to swap. Config was applied to the wrong interface.

**Fix:** Moved the PC-BR1 cable in CML from Ethernet0/1 to Ethernet1/0 to match the existing
config. No IOS changes needed.

**Lesson:** On IOL-L2, always cross-check interface names against the CML topology canvas.
Run `show cdp neighbors` or `show interfaces status` immediately after cabling to confirm
the correct interface is up before configuring.

---

## Issue P02-02 — BR-ASW1 ip default-gateway Insufficient for Remote-Subnet ICMP (Phase 2)

**Date:** 2026-04-05

**Symptom:** Ping from HQ-RTR1 (10.0.0.1) to BR-ASW1 (10.2.99.3) failed with 0% success.
Pings to BR-RTR1 (10.2.99.1) and BR-DSW1 (10.2.99.2) on the same subnet succeeded.

**Investigation:** Phase 1 ping from BR-RTR1 to 10.2.99.3 had worked (source was 10.2.99.1 —
same subnet, no gateway needed for reply). HQ-RTR1 sources from 10.0.0.1 — a remote subnet —
exposing the `ip default-gateway` limitation.

**Root cause:** `ip default-gateway` on IOL-L2 does not properly forward ICMP replies
destined to remote subnets. The reply from BR-ASW1 to 10.0.0.1 was dropped silently
because the management-plane handler cannot route beyond directly connected subnets.

**Fix:**
```
ip routing
ip route 0.0.0.0 0.0.0.0 10.2.99.1
no ip default-gateway
```

**Lesson:** `ip default-gateway` is only safe for same-subnet management access. Any device
that must respond to traffic from remote subnets needs `ip routing` + a default route.

---

## Issue P02-03 — Dnsmasq Container Failed to Start — bind-interfaces Crash (Phase 3)

**Date:** 2026-04-05

**Symptom:** CML error: "container failed to start" with code 30 when starting HQ-DHCP-DNS node.

**Investigation:** Reviewed dnsmasq.conf in CML CONFIG tab. `bind-interfaces` was present
as a hardening directive.

**Root cause:** `bind-interfaces` causes a race condition on CML Dnsmasq node versions —
dnsmasq starts before eth0 is fully ready and crashes when it cannot bind.

**Fix:** Removed `bind-interfaces` from dnsmasq.conf. Used the RESTORE button in CML
CONFIG tab to apply the corrected config.

**Lesson:** Avoid `bind-interfaces` on CML Dnsmasq nodes. The default wildcard binding
works correctly and does not have the timing dependency.

---

## Issue P02-04 — DHCP Relay Not Firing — Missing helper-address (Phase 3)

**Date:** 2026-04-05

**Symptom:** dnsmasq log showed `no address range available via eth0` continuously.
`debug ip dhcp server packet` on BR-RTR1 showed no output — relay not firing at all.

**Investigation:** Checked running configs on both routers. `ip helper-address` was missing
on all subinterfaces.

**Root cause:** `ip helper-address` had not been configured on either router. Without the
relay agent, DHCP broadcasts never leave the local subnet — the server never sees them.

**Fix:** Configured `ip helper-address 10.1.99.50` on all data VLAN subinterfaces on both
HQ-RTR1 and BR-RTR1:
```
interface Ethernet0/0.100
 ip helper-address 10.1.99.50
interface Ethernet0/0.200
 ip helper-address 10.1.99.50
! (repeated for all data VLANs)
```

**Lesson:** Centralized DHCP requires `ip helper-address` on every router subinterface
serving client subnets. Missing even one subinterface means that VLAN gets no DHCP service.

---

## Issue P02-05 — interface=eth0 in dnsmasq.conf Blocking Relay Packets (Phase 3)

**Date:** 2026-04-05

**Symptom:** Even after configuring helper-address, dnsmasq continued showing
`no address range available via eth0` — never showing `via 10.x.x.x` (relay indicator).

**Investigation:** Reviewed dnsmasq.conf. `interface=eth0` was present as a restriction.

**Root cause:** `interface=eth0` tells dnsmasq to only process requests arriving directly
on eth0 as broadcasts. Relayed DHCP packets arrive as unicast UDP on port 67 — this
directive caused dnsmasq to silently reject all relayed requests.

**Fix:** Removed `interface=eth0` from dnsmasq.conf.

**Lesson:** Never use `interface=` restriction on a centralized DHCP server that serves
relayed requests. Relay packets arrive as unicast, not broadcasts — interface binding
blocks them.

---

## Issue P02-06 — HQ-DHCP-DNS eth0 NO-CARRIER — Missing VLAN Config on HQ-DSW2 (Phase 3)

**Date:** 2026-04-05

**Symptom:** `ip link show eth0` on HQ-DHCP-DNS showed NO-CARRIER, state DOWN.
Node had no network connectivity despite cable existing in CML.

**Investigation:** Checked HQ-DSW2 running config. E0/0 (connected to HQ-DHCP-DNS)
had no switchport configuration — still in VLAN 1 default state.

**Root cause:** HQ-DSW2 E0/0 was physically connected but never configured as an
access port in VLAN 999. Port was in VLAN 1 default state — HQ-DHCP-DNS had no
valid Layer 2 path.

**Fix:**
```
interface Ethernet0/0
 description TO_HQ-DHCP-DNS
 switchport mode access
 switchport access vlan 999
 spanning-tree portfast
 spanning-tree bpduguard enable
```

**Lesson:** Always configure the switchport before connecting a server. A cable without
a VLAN assignment is the same as no cable from the server's perspective.

---

## Issue P02-07 — Wrong Console Open — udhcpc Run on HQ-DHCP-DNS (Phase 3)

**Date:** 2026-04-05

**Symptom:** `udhcpc` run on what appeared to be PC-BR1 failed. IOS debug commands
typed on same device returned "not found".

**Investigation:** Checked hostname prompt. Node showed `inserthostname-here` —
the default CML placeholder for Alpine/Dnsmasq nodes, not the IOS device name.

**Root cause:** Multiple CML console tabs open. The active tab was HQ-DHCP-DNS
(which also uses `inserthostname-here`), not PC-BR1. Running `udhcpc` on the
DHCP server asked the server to DHCP an address from itself.

**Fix:** Opened correct PC-BR1 console. Set hostnames on all nodes immediately.

**Lesson:** Always verify the hostname in the shell prompt before running any command.
Run `hostname` on Alpine nodes to confirm which node you are on. Never assume by tab order.

---

## Issue P02-08 — HQ-DHCP-DNS Loses IP on Every Restart (Phase 3/5)

**Date:** 2026-04-05

**Symptom:** After stopping and starting HQ-DHCP-DNS, ping to 10.1.99.50 from HQ-RTR1
failed immediately after node showed BOOTED in CML.

**Investigation:** Waited ~30 seconds and retried. Ping succeeded. Node was reachable
once startup script completed.

**Root cause:** CML shows node as BOOTED before the startup script finishes executing.
The startup script sets the static IP and default route — pinging immediately after
BOOTED catches the node before script completion.

**Fix:** Wait 15–20 seconds after BOOTED state appears before testing connectivity.
Added `ip addr show` and `ip route show` to startup script output for visual confirmation.

**Lesson:** CML container BOOTED state ≠ startup script completed. Always wait before
testing. Design startup scripts to print a completion banner as confirmation.

---

## Issue P02-09 — dnsmasq NXDOMAIN — domain= Without Address Records (Phase 5)

**Date:** 2026-04-05

**Symptom:** `nslookup` returning NXDOMAIN for all `lab.local` names even though
dnsmasq was reachable and `domain=lab.local` + `local=/lab.local/` were configured.

**Investigation:** Checked dnsmasq.conf — no `address=` directives and no hosts file
entries were present. Only routing directives existed.

**Root cause:** `domain=` and `local=` are routing directives — they tell dnsmasq
*where to look* for lab.local queries. They do not create DNS records. Without
`address=` entries or a populated `/etc/hosts`, dnsmasq has nothing to return.

**Fix:** Added `address=` directives for all infrastructure hosts in dnsmasq.conf:
```
address=/hq-rtr1.lab.local/10.1.99.1
address=/hq-dsw1.lab.local/10.1.99.11
address=/br-rtr1.lab.local/10.2.99.1
! (etc. for all devices)
```

**Lesson:** Always pair `domain=` and `local=` with actual host records using
`address=` directives. The routing config and the record config are separate steps.

---

## Issue P02-10 — pc-br1.lab.local NXDOMAIN — Dynamic IP in Static DNS Record (Phase 5)

**Date:** 2026-04-05

**Symptom:** `nslookup pc-br1.lab.local` returned NXDOMAIN even though an `address=`
entry existed in dnsmasq.conf.

**Investigation:** Checked current DHCP lease on PC-BR1 vs. the IP hardcoded in
`address=`. The IPs did not match — PC-BR1 had received a different lease.

**Root cause:** DHCP leases can change between restarts. The hardcoded IP in `address=`
did not match the current lease. Without a static reservation, the endpoint gets
whatever IP is next available.

**Fix:** Added `dhcp-host=` static reservations using MAC addresses:
```
dhcp-host=aa:bb:cc:dd:ee:01,pc-br1,10.2.100.10
dhcp-host=aa:bb:cc:dd:ee:02,pc-br2,10.2.200.10
```
Then updated `address=` entries to match the locked IPs.

**Lesson:** Never hardcode dynamic DHCP IPs in DNS records. Always use static DHCP
reservations (`dhcp-host=`) for any device that needs a predictable DNS entry.

---

## Issue P02-11 — no ip domain lookup Blocking DNS on BR-RTR1 (Phase 5)

**Date:** 2026-04-05

**Symptom:** BR-RTR1 could ping 10.1.99.50 directly but `ping hq-rtr1.lab.local`
returned "Unrecognized host or address". `ip name-server 10.1.99.50` was configured.

**Investigation:** Checked running config — `no ip domain lookup` was present from
Phase 1 hardening.

**Root cause:** `no ip domain lookup` was configured in Phase 1 to prevent the
30-second DNS timeout when mistyping IOS commands. This same setting also blocks
all legitimate DNS resolution from the router itself.

**Fix:**
```
ip domain lookup
ip name-server 10.1.99.50
```
DNS resolution worked immediately.

**Lesson:** `no ip domain lookup` is double-edged — prevents mistyped command timeouts
but also blocks legitimate DNS queries. The better long-term approach is `ip domain lookup`
with a valid name-server configured. Hardening decisions have operational consequences.

---

## Issue P02-12 — Alpine PC Nodes Showing inserthostname-here (Phase 3/5)

**Date:** 2026-04-05

**Symptom:** Both PC-BR1 and PC-BR2 showed `inserthostname-here` as hostname.
dnsmasq log showed `client provides name: localhost` for all DHCP leases.

**Investigation:** Checked CML CONFIG tabs for both Alpine nodes. No startup script
had been configured.

**Root cause:** CML Alpine Linux nodes do not set a hostname by default. Every node
boots with the placeholder `inserthostname-here` — this flows into DHCP client
identification and makes distinguishing nodes in logs impossible.

**Fix:**
```bash
hostname pc-br1     # on PC-BR1 console
hostname pc-br2     # on PC-BR2 console
```
Added `hostname <name>` to each node's CML startup script for persistence across reboots.

**Lesson:** Set hostnames on all Alpine nodes immediately after adding them to the topology.
Add the `hostname` command to the startup script so it survives every reboot.
Never rely on prompt to identify nodes — always confirm with `hostname`.

---

## Break/Fix Challenge — Three Simultaneous DHCP Faults

**Date:** 2026-04-05

**Symptom:** Two helpdesk tickets simultaneously:
- Branch Engineering VLAN 100 — no DHCP
- HQ Sales VLAN 200 — no DHCP
- DNS and management connectivity unaffected

**Faults introduced (unknown at start):**
1. BR-RTR1 E0/0.100 `helper-address` changed to `10.1.99.99` (wrong server IP)
2. HQ-RTR1 E0/0.200 `helper-address` changed to `10.1.99.99` (wrong server IP)
3. BR-RTR1: `ip route 10.1.99.0 255.255.255.0 Null0` added (black-hole route)

**Investigation — OSI bottom-up:**

Layer 1–2:
```
show vlan brief           → VLANs 100, 200 active, clean
show interfaces trunk     → All uplinks trunking, native VLAN 1000 correct
```
No physical or data-link issues found.

Layer 3 — Routing:
```
show ip route 10.1.99.0 on BR-RTR1
```
Result: TWO entries — `via 10.0.0.1` (correct) AND `via Null0` (black-hole).
IOS load-balanced between both paths — intermittent ping SUCCESS masked the fault.
DHCP relay packets consistently hit Null0 → silent drop → client timeout.

Layer 3 — Relay config:
```
show running-config | section helper
```
Result: `ip helper-address 10.1.99.99` on BR-RTR1 E0/0.100 and HQ-RTR1 E0/0.200.
Wrong helper-address on both DHCP-failing subinterfaces.

**Fix order — dependency critical:**
```
! Step 1: Remove black-hole route FIRST
no ip route 10.1.99.0 255.255.255.0 Null0

! Step 2: Fix helper-address on BR-RTR1
interface Ethernet0/0.100
 ip helper-address 10.1.99.50

! Step 3: Fix helper-address on HQ-RTR1
interface Ethernet0/0.200
 ip helper-address 10.1.99.50
```
Fixing helper-address WITHOUT removing the Null0 route first would still fail — the
relay packets would still be black-holed on 50% of attempts.

**Lesson 1 — Intermittent ≠ working:** A successful ping does not prove a clean routing
path. Intermittent success with a Null0 competitor is a false positive. Always check
`show ip route <specific destination>` before trusting ping results.

**Lesson 2 — Fix dependencies matter:** When multiple faults exist at different layers,
fix the lowest-layer fault first. The Null0 black-hole at Layer 3 would have silently
sabotaged the helper-address fix at the application layer. Dependency order determines
whether fixes actually take effect.

**Lesson 3 — `show run | section`:** `show running-config | section helper` is the
fastest way to audit all helper-address config across all subinterfaces on one device.
Use this before `debug ip dhcp` for any DHCP relay issue.
