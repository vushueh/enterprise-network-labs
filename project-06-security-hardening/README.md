# Project 06 — Security Hardening

**Series:** Enterprise Network Labs | **Platform:** Cisco CML 2.9 (IOL, IOL-L2, Net-Tools)
**Build Date:** 2026-05-02 | **Status:** 🔄 Started; Phase 1 ready to build

---

## STAR Summary

**Situation:** Projects 01–05 built a routed, multi-site enterprise network with OSPF, switching stability, internet access, PAT/static NAT, and Guest isolation. The access layer still needed deliberate security controls, and the management VLAN was not yet protected like an out-of-band network.

**Task:** Harden the switching edge and management plane by adding port security, DHCP snooping, Dynamic ARP Inspection, IP Source Guard, inter-VLAN ACL policy, strict management VLAN protection, and active attack testing with a rogue endpoint.

**Action:** Seven structured phases — port security → DHCP snooping → Dynamic ARP Inspection → IP Source Guard → inter-VLAN ACL and OOB management protection → management-plane hardening → errdisable recovery validation. ATTACKER1 is used to prove the controls actually stop bad behavior instead of only existing in the running config.

**Result:** Target outcome: access ports enforce MAC limits, DHCP replies are trusted only from uplinks, ARP/IP spoofing attempts are blocked at the switch edge, Guest remains internet-only, user VLANs cannot initiate connections into Management VLAN 999, and the network can recover cleanly from security-triggered errdisable events.

---

## Topology

![CML Topology — Project 06 Security Hardening](verification/screenshots/P06-Ph0-cml-topology.png)
> Project 06 adds ATTACKER1 on HQ-ASW2 Ethernet1/1 as a rogue endpoint for security-control testing. Capture this screenshot after the Net-Tools node is added in CML.

---

## Topology Changes

Project 06 keeps the Project 05 routed/NAT baseline and adds one test host.

| Node | Image | Role |
|------|-------|------|
| ATTACKER1 | Net-Tools | Rogue endpoint used to test port security, DHCP snooping, DAI, and IP Source Guard |

### New Connection

| Local Device | Local Port | Remote Device | Remote Port | Purpose |
|--------------|------------|---------------|-------------|---------|
| HQ-ASW2 | Ethernet1/1 | ATTACKER1 | eth0 | Rogue/test access port for security hardening |

**Why HQ-ASW2 Ethernet1/1:** Project 06 needs an isolated access-layer port where security violations can be triggered without disrupting the known-good Project 05 production paths.

---

## Security Design

### Layered Control Matrix

| Layer | Control | Where Applied | Why |
|-------|---------|---------------|-----|
| L2 access edge | Port security with sticky MAC | User-facing access ports | Limits unauthorized MAC addresses on a port |
| DHCP control | DHCP snooping | VLANs 100/200/300/400/999 | Blocks rogue DHCP servers and builds the binding table |
| ARP control | Dynamic ARP Inspection | VLANs 100/200/300 | Blocks ARP spoofing using DHCP snooping bindings |
| IP spoofing control | IP Source Guard | User-facing access ports | Drops source IPs that do not match the binding table |
| L3 segmentation | Inter-VLAN ACL policy | Router subinterfaces / SVIs as appropriate | Enforces who can initiate traffic between VLANs |
| Management protection | VTY ACLs and VLAN 999 deny rules | Routers and switches | Simulates out-of-band management by blocking user VLAN access |
| Recovery | Errdisable recovery | Access switches | Confirms security events do not leave ports permanently down |

### Policy Intent

| Source Zone | Allowed Destinations | Blocked Destinations |
|-------------|----------------------|----------------------|
| Engineering VLAN 100 | Sales VLAN 200, Servers VLAN 400, internet | Management VLAN 999 |
| Sales VLAN 200 | Engineering VLAN 100, Servers VLAN 400, internet | Management VLAN 999 |
| Guest VLAN 300 | Internet only | Internal 10.1.x.x, 10.2.x.x, Management VLAN 999 |
| Servers VLAN 400 | Replies to allowed sessions, required infrastructure | Unsolicited user access where not required |
| Management VLAN 999 | All infrastructure as needed | None by default; this is the admin source zone |

---

## Pre-Work Checklist

Before configuring Project 06, verify the Project 05 baseline is stable and the new rogue-device cabling is correct.

```cisco
! On HQ-RTR1
show ip ospf neighbor
show ip route 0.0.0.0
show ip nat translations
show ip access-lists GUEST-RESTRICT

! On HQ-ASW2
show cdp neighbors
show interfaces status
show interfaces trunk
show vlan brief
show running-config interface Ethernet1/1
```

**Expected baseline:**
- Project 05 NAT and Branch internet access still work
- HQ-ASW2 trunk uplink remains stable before security features are added
- HQ-ASW2 Ethernet1/1 is available for ATTACKER1
- CDP/LLDP and interface descriptions match the intended topology
- No ports are already errdisabled before security testing begins

---

## Phase 1 — Port Security

### Why This Phase Exists

Port security is the first access-layer control because it limits which source MAC addresses can appear on a user-facing port. Sticky MAC learning keeps the configuration realistic: the switch learns the first legitimate addresses automatically, then blocks unexpected MAC churn.

### HQ-ASW2 ATTACKER1 Port

```cisco
interface Ethernet1/1
 description ACCESS-ATTACKER1-VLAN100-SECURITY-TEST
 switchport mode access
 switchport access vlan 100
 switchport nonegotiate
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
 no shutdown
```

**Why maximum 2:** The first two MAC addresses establish the sticky baseline. A third source MAC from the same port should trigger the violation so the test is controlled and repeatable.

**Why `restrict` first:** Restrict mode drops violating traffic and increments counters while keeping the port up. That gives clean proof before testing the more disruptive `shutdown` mode.

**Why PortFast and BPDU Guard stay enabled:** This is still an edge port. A rogue endpoint should not participate in spanning tree, and a rogue switch should be shut down immediately if it sends BPDUs.

### ATTACKER1 Test Flow

```sh
ip link show eth0
udhcpc -i eth0

ip link set eth0 down
ip link set eth0 address 02:06:06:06:00:01
ip link set eth0 up
udhcpc -i eth0

ip link set eth0 down
ip link set eth0 address 02:06:06:06:00:02
ip link set eth0 up
udhcpc -i eth0
```

If `udhcpc` is not available on the Net-Tools image, use whatever DHCP client the node provides, or simply generate traffic after changing the MAC address.

### Verification

| Test | Command | Expected / Observed Result |
|------|---------|----------------------------|
| Port-security status | `show port-security interface Ethernet1/1` | Enabled, maximum 2, violation mode restrict |
| Sticky MACs | `show port-security address interface Ethernet1/1` | Learned sticky MAC entries appear |
| Violation counters | `show port-security interface Ethernet1/1` | Security violation count increments after the third MAC |
| Syslog proof | `show logging | include PSECURE` | Port-security violation messages appear |
| Port state | `show interfaces Ethernet1/1 status` | Port remains connected in restrict mode |

Add screenshots under `verification/screenshots/` as each proof is captured:

![P06 Phase 1 Port Security Status](verification/screenshots/P06-Ph1-port-security-interface-e1-1.png)
![P06 Phase 1 Sticky MAC Table](verification/screenshots/P06-Ph1-port-security-addresses.png)

---

## Phase Roadmap

| Phase | Focus | Primary Proof |
|-------|-------|---------------|
| 1 | Port security | Violation counters and sticky MAC table |
| 2 | DHCP snooping | Trusted uplinks, binding table, drop counters |
| 3 | Dynamic ARP Inspection | ARP inspection statistics and spoof test failure |
| 4 | IP Source Guard | Source mismatch drops on access ports |
| 5 | Inter-VLAN ACL + OOB protection | Management VLAN access blocked from user VLANs |
| 6 | Management-plane protection | VTY ACL, login hardening, unused services disabled |
| 7 | Errdisable integration | Recovery timer and post-recovery port behavior |

---

## Break/Fix Challenge — DHCP Snooping Trust in the Wrong Place

### Fault Injection

Set DHCP snooping trust on an access port instead of the trunk uplink.

### Expected Symptom

Legitimate clients behind the switch fail to obtain DHCP leases, while the apparent configuration looks close enough to be misleading.

### Diagnosis Commands

```cisco
show ip dhcp snooping
show ip dhcp snooping binding
show ip dhcp snooping statistics
show running-config | include dhcp snooping trust
show interfaces trunk
```

### Root Cause

The switch trusts DHCP messages from the wrong interface. The real DHCP server's replies arrive through the uplink, but that uplink is untrusted, so valid DHCP offers are dropped.

### Fix

Remove trust from the access port and place it only on the correct trunk uplink.

---

## Verification Summary

| Control | Required Evidence | Status |
|---------|-------------------|--------|
| Port security | Sticky MACs, violation counter, PSECURE log | Pending |
| DHCP snooping | Binding table, trusted uplinks only, drop counters | Pending |
| DAI | ARP inspection enabled, spoof blocked | Pending |
| IP Source Guard | IP/MAC binding enforcement on access ports | Pending |
| Inter-VLAN ACLs | Each policy rule tested and logged | Pending |
| Management plane | VTY ACL and login hardening verified | Pending |
| Errdisable recovery | Security violation recovery confirmed | Pending |

---

## Troubleshooting Log

Project-level troubleshooting entries are in [TROUBLESHOOTING-LOG.md](TROUBLESHOOTING-LOG.md). The planned break/fix drill is the DHCP snooping trusted-port mistake.

---

## Key Technologies

| Technology | Command / Feature | Purpose |
|------------|-------------------|---------|
| Port security | `switchport port-security` | Limit MAC addresses on access ports |
| Sticky MAC | `switchport port-security mac-address sticky` | Learn expected MACs automatically |
| DHCP snooping | `ip dhcp snooping` | Block rogue DHCP and build binding database |
| DAI | `ip arp inspection vlan` | Validate ARP packets against bindings |
| IP Source Guard | `ip verify source` | Prevent IP spoofing at the access edge |
| Extended ACLs | `ip access-list extended` | Enforce inter-VLAN policy |
| VTY ACL | `access-class` | Restrict SSH management sources |
| Login protection | `login block-for` | Slow brute-force login attempts |
| Errdisable recovery | `errdisable recovery cause` | Restore ports after controlled security events |
