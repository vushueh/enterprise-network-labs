# Network Requirement Document — Project 06 Security Hardening

## Background

The enterprise lab now has multi-site routing, stable switching, internet access, NAT, and basic guest isolation. Project 06 hardens the network so endpoint-facing ports, DHCP, ARP, IP source behavior, inter-VLAN access, and device management are controlled intentionally.

---

## Business Requirements

| ID | Requirement | Reason |
|----|-------------|--------|
| BR-01 | Reduce risk from rogue devices at the access layer | Unauthorized endpoints should not be able to freely join or spoof the enterprise network |
| BR-02 | Protect DHCP service integrity | Clients must receive addresses only from the authorized DHCP infrastructure |
| BR-03 | Prevent common LAN spoofing attacks | ARP and IP spoofing can redirect or disrupt user traffic |
| BR-04 | Protect management access | VLAN 999 should behave like an out-of-band management network, not a normal user-reachable subnet |
| BR-05 | Preserve the Project 05 internet/NAT baseline | Security hardening must not break known-good routing or internet access |
| BR-06 | Prove controls through active testing | A security feature is not complete until it has been tested against a realistic failure or attack |

---

## Technical Requirements

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| TR-01 | Configure port security on selected access ports | Sticky MAC enabled, max 2 addresses, restrict-mode proof captured, shutdown-mode test documented |
| TR-02 | Enable DHCP snooping | Snooping enabled on user VLANs, only uplinks trusted, access ports rate-limited to 15 pps |
| TR-03 | Enable Dynamic ARP Inspection | DAI enabled on VLANs 100/200/300 and uplinks trusted appropriately |
| TR-04 | Enable IP Source Guard | Access ports enforce DHCP snooping bindings where supported by the IOL-L2 image |
| TR-05 | Build inter-VLAN ACL policy | Engineering and Sales can communicate as intended, Guest reaches internet only, users cannot initiate to VLAN 999 |
| TR-06 | Harden device management plane | VTY ACLs, SSH-only access, disabled unused services, login block-for, and warning banners configured |
| TR-07 | Validate errdisable recovery | Port security and DHCP rate-limit triggers recover after the Project 04 recovery interval |
| TR-08 | Capture verification evidence | Screenshots and command output prove each phase before moving forward |

---

## Lab Prerequisites

| Prerequisite | Expected State |
|--------------|----------------|
| Project 05 baseline | Internet/NAT, OSPF default, Guest ACL, HQ-SRV1 static NAT all verified |
| New node | ATTACKER1 Net-Tools node added to CML |
| New connection | HQ-ASW2 Ethernet1/1 connected to ATTACKER1 eth0 |
| Access switch baseline | HQ-ASW2 trunk uplink stable and no ports unexpectedly errdisabled |
| Screenshots folder | `verification/screenshots/` ready for captured proof |

---

## Success Criteria

- [ ] ATTACKER1 connected to HQ-ASW2 Ethernet1/1 and visible in interface status.
- [ ] Port security learns sticky MAC addresses and increments violation counters when a third MAC is used.
- [ ] DHCP snooping trusts only trunk uplinks and builds expected bindings.
- [ ] Rogue DHCP behavior is blocked or counted by DHCP snooping statistics.
- [ ] Dynamic ARP Inspection blocks spoofed ARP attempts.
- [ ] IP Source Guard blocks source IP/MAC mismatches where supported.
- [ ] Guest VLAN 300 remains internet-only and cannot reach internal or management ranges.
- [ ] User VLANs cannot initiate sessions into VLAN 999.
- [ ] Management VLAN 999 can still administer infrastructure devices.
- [ ] Errdisable recovery works for security-related triggers.
- [ ] DHCP snooping trusted-port break/fix challenge completed and documented.
