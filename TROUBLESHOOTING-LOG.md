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

**Break introduced on HQ-DSW1 Ethernet0/1:**
  interface Ethernet0/1
   switchport trunk allowed vlan 200,300,999
VLAN 100 was deliberately removed from the allowed list on the trunk toward HQ-ASW1.

**Symptom observed:**
PC-ENG1 (10.1.100.10) lost all network connectivity immediately. PC-SALES1 and PC-MGMT1 continued working normally. The trunk on E0/1 remained UP with no interface errors and no CDP neighbor loss.

**Diagnosis using show interfaces trunk on HQ-DSW1:**
  Et0/1  Vlans allowed on trunk: 200,300,999
VLAN 100 was missing from the allowed list. The trunk link was still up.

**Key observation:** This is a subtle failure. One VLAN silently dropped from one trunk while everything else continued working. No physical indication of failure.

**Fix:**
  configure terminal
  interface Ethernet0/1
   switchport trunk allowed vlan 100,200,300,999
  end
  write memory
PC-ENG1 connectivity restored immediately after fix.

**Lesson:** Wrong allowed VLAN is one of the most common and subtle trunking failures. Characteristics: one VLAN loses connectivity while others work, trunk link stays up with no physical errors. The show interfaces trunk command is the key diagnostic. Always verify the allowed VLAN list on BOTH ends of every trunk.
