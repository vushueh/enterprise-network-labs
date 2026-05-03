# Project 06 — Troubleshooting Log

---

## 2026-05-02 — Project 06, Phase 1

### P06-T01 — Port security switchport commands entered at global config mode

**Symptom:** Commands like `switchport port-security maximum 2` returned `% Invalid input detected` when entered at the `HQ-ASW1(config)#` prompt.

**Expected:** Port security parameters should be accepted and configured on the target interface.

**Investigation:**
- Checked the prompt — showed `(config)#` rather than `(config-if)#`
- `switchport` commands are interface-context commands, not global config commands

**Root cause:** Switchport commands were entered at global config mode without first entering `interface Ethernet0/2`.

**Fix:**
```
interface Ethernet0/2
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation restrict
```

**Lesson:** `switchport` commands always require interface context. When you see `% Invalid input detected` on a switchport command, check the prompt first.

---

### P06-T02 — `switchport port-security` showing Status: Disabled despite parameters set

**Symptom:** `show port-security interface Ethernet0/2` showed `Port Status: Disabled` even though `maximum`, `mac-address sticky`, and `violation` parameters were visible in running-config.

**Expected:** Port should show `SecureUp` after parameters are configured.

**Investigation:**
- `show running-config interface Ethernet0/2` confirmed all parameters present
- Missing the bare `switchport port-security` activation command

**Root cause:** On IOS, `switchport port-security maximum X` and related commands configure parameters but do not activate the feature. The bare `switchport port-security` command (no arguments) is the activation trigger. Without it, port security is in a prepared-but-disabled state.

**Fix:**
```
interface Ethernet0/2
 switchport port-security
```

**Lesson:** Always enter `switchport port-security` (bare, no arguments) as the first port security command under an interface. Parameters without activation do nothing.

---

### P06-T03 — Net-Tools node has no interactive CLI

**Symptom:** Attempting to use the Net-Tools node as the ATTACKER1 simulation host produced no usable shell for running attack commands (arping, ip addr, etc.).

**Expected:** An interactive terminal with network tools for attack simulation.

**Investigation:**
- Net-Tools node in CML does not open an interactive terminal session
- Designed for limited automated testing, not interactive shell use

**Root cause:** Wrong node type for attacker simulation in CML.

**Fix:** Replaced Net-Tools with an Alpine Linux node. Alpine provides a full BusyBox shell with `arping`, `ip`, `ping`, `wget`, and `udhcpd` available.

**Lesson:** For attack simulation or any interactive command-line testing in CML, use Alpine or Ubuntu endpoints. Net-Tools is not a general-purpose attacker node.

---

### P06-T04 — Port went err-disabled after replacing attacker node (sticky MAC mismatch)

**Symptom:** HQ-ASW2 Ethernet0/3 went err-disabled immediately after the Alpine node replaced the Net-Tools node.

**Expected:** New node should connect normally and lock its MAC as the new sticky entry.

**Investigation:**
- `show port-security interface Ethernet0/3` showed `Secure-shutdown`
- `show port-security address` showed the old Net-Tools MAC still listed as `SecureSticky`
- Alpine's MAC (5254.0049.0158) did not match the locked entry — violation triggered immediately on first frame

**Root cause:** The old Net-Tools sticky MAC was locked in running-config. The Alpine node presented a different MAC, triggering the shutdown violation immediately.

**Fix:**
```
interface Ethernet0/3
 no switchport port-security mac-address sticky
 shutdown
 no shutdown
 switchport port-security mac-address sticky
```
Then connect Alpine and let it re-learn its MAC as the new sticky entry.

**Lesson:** When intentionally replacing an endpoint, remove the sticky MAC entry before connecting the new device. Sticky MACs are permanent until explicitly cleared or the feature is toggled.

---

### P06-T05 — `clear port-security sticky interface EthernetX/X` not supported on IOL-L2

**Symptom:** `clear port-security sticky interface Ethernet0/3` returned `% Invalid input detected`.

**Expected:** Command should clear the sticky MAC entry for the specified interface.

**Investigation:**
- `clear port-security sticky ?` — the `interface` keyword is not listed as a valid option on this IOL-L2 image
- Global `clear port-security sticky` (without interface) also unsupported in the same way

**Root cause:** IOL-L2 does not implement the per-interface variant of `clear port-security sticky`. Platform limitation.

**Fix (config-mode workaround):**
```
interface Ethernet0/3
 no switchport port-security mac-address sticky
 shutdown
 no shutdown
 switchport port-security mac-address sticky
```
The shutdown/no shutdown cycle resets port state. Re-adding the sticky command re-enables learning for the next connected device.

**Lesson:** On IOL-L2, use config-mode toggle of the sticky command plus shutdown cycling to clear sticky MACs. Always verify platform-specific exec commands with `?` before relying on them in a lab procedure.

---

## 2026-05-02 — Project 06, Phase 2

### P06-T06 — DHCP snooping binding table empty after client DHCP renewals

**Symptom:** `show ip dhcp snooping binding` returned no entries after PC-ENG1 and PC-SALES1 completed successful DHCP renewals from Dnsmasq.

**Expected:** Binding table should show MAC, VLAN, IP, interface for each DHCP client.

**Investigation:**
- `show ip dhcp snooping` confirmed snooping enabled on correct VLANs, uplinks marked trusted
- `show ip dhcp snooping statistics` showed 0 packets processed on all interfaces
- Reviewed IOL-L2 architecture: software-forwarding switch; DHCP snooping interception is normally an ASIC function
- No ASIC present in IOL — the snooping engine never activates

**Root cause:** IOL-L2 platform limitation. The DHCP snooping interception engine requires hardware ASIC support that does not exist in the IOL software image. Configuration is correct; the platform cannot execute the enforcement.

**Fix:** Added static `ip source binding` entries for each access port client to populate the binding database manually:
```
ip source binding 5254.00D7.CBBC vlan 100 10.1.100.194 interface Ethernet0/2
ip source binding 5254.00B2.8D53 vlan 999 10.1.99.100 interface Ethernet0/3
! (equivalent entries on HQ-ASW2)
```
These static entries serve as the binding database for Phase 3 (DAI) and Phase 4 (IP Source Guard).

**Lesson:** IOL-L2 DHCP snooping is a known platform limitation. Configure correctly for documentation and portfolio purposes, use static bindings to enable dependent features, and always test L2 security enforcement on real hardware when live behavior matters.

---

## 2026-05-02 — Project 06, Phase 3

### P06-T08 — `arping -U -s 10.1.100.1` returns `bind: Address not available`

**Symptom:** Running `arping -U -s 10.1.100.1 10.1.100.194` on ATTACKER1 failed with `bind: Address not available`.

**Expected:** `arping` should send a gratuitous ARP with a spoofed source IP.

**Investigation:**
- BusyBox `arping -U` (gratuitous/update mode) requires the source IP specified with `-s` to be assigned to a local interface, or the interface must be specified with `-I`
- ATTACKER1 had 10.1.100.170 assigned — not 10.1.100.1

**Root cause:** arping cannot bind to a source IP that is not present on any local interface.

**Fix:**
```sh
ip addr add 10.1.100.1/24 dev eth0
arping -U -c 3 -I eth0 10.1.100.1
ip addr del 10.1.100.1/24 dev eth0
```
Add the spoofed IP to the interface, send the gratuitous ARP, then remove it.

**Lesson:** Gratuitous ARP spoofing from BusyBox arping requires temporarily assigning the target IP to the attacking interface. Remove the spoofed IP after the test to restore normal network state.

---

## 2026-05-02 — Project 06, Phase 4

### P06-T07 — `ip verify source port-security` not supported on IOS 17.16

**Symptom:** `ip verify source port-security` was rejected under the interface with `% Invalid input detected`.

**Expected:** Command should enable IP Source Guard with port security integration.

**Investigation:**
- `ip verify source ?` output showed: `mac-check`, `vlan`
- `port-security` is not listed as a valid option on this IOS 17.16 IOL image

**Root cause:** The `ip verify source port-security` form is not implemented on IOS 17.16 (IOL). It may exist on older IOS versions or specific platform images.

**Fix:** Use `ip verify source mac-check` instead:
```
interface Ethernet0/2
 ip verify source mac-check
```
This validates both source IP and source MAC against the binding table — equivalent protection to the port-security variant.

**Lesson:** Check `?` help output before applying security commands on a new IOS version. `ip verify source mac-check` is the current and supported form for combined IP+MAC validation on this platform.
