# Project 09 - Phase 1 Syslog Infrastructure

Status: CODEX-PROPOSED - pending Claude review
Session folder: C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09

Do not apply this to CML until Claude reviews and approves it.

## Phase Goal

Build centralized syslog visibility for the existing 20-node enterprise lab.

- Collector: HQ-SYSLOG at 10.1.99.51 on HQ Management VLAN 999
- Transport: UDP/514
- IOS/IOL features: timestamps, sequence numbers, remote logging, local buffer
- ASA features: logging enable, timestamp, host inside 10.1.99.51
- Tiered severity:
  - Core, WAN, ISP, distribution, firewall: warnings to the collector
  - Access switches: informational to the collector so user-edge events are visible

## Phase 1 Scope Correction After CML Testing

ISP-RTR1 is explicitly excluded from Project 09 Phase 1 internal syslog collection.
It sits on the simulated internet/outside side of the ASA, while HQ-SYSLOG lives on
inside management at `10.1.99.51`. Testing showed ISP-RTR1 could accept the logging
configuration but could not reach `10.1.99.51` from Loopback0. Bringing ISP-RTR1 into
the same collector would require a deliberate ASA outside-to-inside policy/NAT design,
which is out of scope for basic internal monitoring.

If ISP-RTR1 was configured during testing, remove it:

```text
enable
configure terminal
no logging host 10.1.99.51
no logging source-interface Loopback0
end
write memory
```

## Pre-Work Baseline - Run Before Applying

```text
! On HQ-RTR1:
show ip interface brief
ping 10.1.99.51 source 10.1.99.1
show logging | include 10.1.99.51|Trap|Logging

! On BR-RTR1:
show ip interface brief
ping 10.1.99.51 source 10.2.99.1
show logging | include 10.1.99.51|Trap|Logging

! On HQ-DSW1:
show cdp neighbors
show interfaces status | include Et1/1
show vlan brief | include 999
ping 10.1.99.51

! On HQ-FW1:
show route
ping inside 10.1.99.51
show logging
```

Expected baseline:
- HQ-SYSLOG is reachable at 10.1.99.51.
- HQ-DSW1 Ethernet1/1 is in VLAN 999 if it is still the HQ-SYSLOG switchport.
- No existing logging host points to the wrong address.

## [CODEX-PROPOSED] Project 09 / Phase 1 / Device: HQ-RTR1

```text
! ============================================================
! DEVICE: HQ-RTR1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 1 - Syslog Infrastructure
! ============================================================
enable
configure terminal

! --- Syslog timestamps and sequence numbers ---
! WHY: Every log needs an exact time and sequence number so later phases can
! correlate syslog, SNMP traps, NetFlow, and EEM events.
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service sequence-numbers

! --- Local logging buffer ---
! WHY: Keep local proof on the router even if the collector is temporarily down.
logging buffered 32768 informational
logging console warnings
logging monitor warnings

! --- Remote syslog collector ---
! WHY: HQ-RTR1 is a core routing device, so only warning-and-above events are
! sent remotely to avoid collector noise while still catching real problems.
logging host 10.1.99.51
logging source-interface Loopback0
logging trap warnings

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show logging | include 10.1.99.51|Trap|Logging
! show clock detail
! ping 10.1.99.51 source 10.0.255.1
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 1 / Device: BR-RTR1

```text
! ============================================================
! DEVICE: BR-RTR1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 1 - Syslog Infrastructure
! ============================================================
enable
configure terminal

! --- Syslog timestamps and sequence numbers ---
! WHY: Branch events must use the same timestamp and sequence format as HQ.
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service sequence-numbers

! --- Local logging buffer ---
! WHY: Keep a local event trail for Branch even if WAN or VPN transport fails.
logging buffered 32768 informational
logging console warnings
logging monitor warnings

! --- Remote syslog collector ---
! WHY: BR-RTR1 is a core Branch router, so warnings-and-above are forwarded
! to the central collector at HQ.
logging host 10.1.99.51
logging source-interface Loopback0
logging trap warnings

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show logging | include 10.1.99.51|Trap|Logging
! show clock detail
! ping 10.1.99.51 source 10.0.255.2
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 1 / Device: WAN-RTR1

```text
! ============================================================
! DEVICE: WAN-RTR1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 1 - Syslog Infrastructure
! ============================================================
enable
configure terminal

! --- Syslog timestamps and sequence numbers ---
! WHY: WAN transit events need the same log format as HQ and Branch.
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service sequence-numbers

! --- Local logging buffer ---
! WHY: Preserve local WAN evidence during path failures.
logging buffered 32768 informational
logging console warnings
logging monitor warnings

! --- Remote syslog collector ---
! WHY: WAN-RTR1 is infrastructure, so send warnings-and-above to HQ-SYSLOG.
logging host 10.1.99.51
logging source-interface Loopback0
logging trap warnings

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show logging | include 10.1.99.51|Trap|Logging
! show clock detail
! ping 10.1.99.51 source 10.0.255.3
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [SUPERSEDED] Project 09 / Phase 1 / Device: ISP-RTR1

Do not apply internal syslog collection to ISP-RTR1 in Phase 1. ISP-RTR1 is outside
the internal management/security boundary. Keep it excluded unless a later phase
intentionally designs outside-to-inside monitoring through the ASA.

## [CODEX-PROPOSED] Project 09 / Phase 1 / Devices: HQ-DSW1 and HQ-DSW2

Apply the same pattern to both HQ distribution switches. Change only the hostname prompt/device you are on.

```text
! ============================================================
! DEVICE: HQ-DSW1 / HQ-DSW2 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 1 - Syslog Infrastructure
! ============================================================
enable
configure terminal

! --- Syslog timestamps and sequence numbers ---
! WHY: Distribution switches are the L2 control point for trunk, STP, and VLAN events.
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service sequence-numbers

! --- Local logging buffer ---
! WHY: Keep detailed local logs while sending only higher-severity items remotely.
logging buffered 32768 informational
logging console warnings
logging monitor warnings

! --- Remote syslog collector ---
! WHY: Distribution switches are core campus infrastructure, so only warnings-and-above
! are forwarded to reduce noise.
logging host 10.1.99.51
logging source-interface Vlan999
logging trap warnings

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show logging | include 10.1.99.51|Trap|Logging
! show clock detail
! ping 10.1.99.51
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 1 / Devices: HQ-ASW1 and HQ-ASW2

Apply the same pattern to both HQ access switches.

```text
! ============================================================
! DEVICE: HQ-ASW1 / HQ-ASW2 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 1 - Syslog Infrastructure
! ============================================================
enable
configure terminal

! --- Syslog timestamps and sequence numbers ---
! WHY: Access-layer events are noisy but useful during user-edge troubleshooting.
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service sequence-numbers

! --- Local logging buffer ---
! WHY: Keep local evidence for port-security, DHCP snooping, STP, and link events.
logging buffered 32768 informational
logging console warnings
logging monitor warnings

! --- Remote syslog collector ---
! WHY: Access switches send informational events so link changes, access-port events,
! and edge-security messages are visible centrally.
logging host 10.1.99.51
logging source-interface Vlan999
logging trap informational

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show logging | include 10.1.99.51|Trap|Logging
! show clock detail
! ping 10.1.99.51
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 1 / Devices: BR-DSW1 and BR-ASW1

BR-DSW1 uses the distribution-switch severity model. BR-ASW1 uses the access-switch severity model.

```text
! ============================================================
! DEVICE: BR-DSW1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 1 - Syslog Infrastructure
! ============================================================
enable
configure terminal

! --- Syslog timestamps and sequence numbers ---
! WHY: Branch distribution events must be timestamped and formatted like HQ.
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service sequence-numbers

! --- Local logging buffer ---
! WHY: Preserve Branch switch evidence locally if WAN/VPN reachability is impaired.
logging buffered 32768 informational
logging console warnings
logging monitor warnings

! --- Remote syslog collector ---
! WHY: Branch distribution is infrastructure, so warnings-and-above go to HQ-SYSLOG.
logging host 10.1.99.51
logging source-interface Vlan999
logging trap warnings

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show logging | include 10.1.99.51|Trap|Logging
! show clock detail
! ping 10.1.99.51
```

```text
! ============================================================
! DEVICE: BR-ASW1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 1 - Syslog Infrastructure
! ============================================================
enable
configure terminal

! --- Syslog timestamps and sequence numbers ---
! WHY: Branch access-layer events are useful for endpoint and security troubleshooting.
service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service sequence-numbers

! --- Local logging buffer ---
! WHY: Keep local access-layer evidence for DHCP, port, and edge-security events.
logging buffered 32768 informational
logging console warnings
logging monitor warnings

! --- Remote syslog collector ---
! WHY: Access switches send informational events so user-edge changes are visible.
logging host 10.1.99.51
logging source-interface Vlan999
logging trap informational

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show logging | include 10.1.99.51|Trap|Logging
! show clock detail
! ping 10.1.99.51
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 1 / Device: HQ-FW1

```text
! ============================================================
! DEVICE: HQ-FW1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 1 - Syslog Infrastructure
! Platform: ASAv
! ============================================================
enable
configure terminal

! --- ASA logging baseline ---
! WHY: Enable timestamped firewall logs and identify messages by firewall hostname.
logging enable
logging timestamp
logging device-id hostname

! --- Local and remote severity ---
! WHY: HQ-FW1 is a perimeter security device, so warnings-and-above are sent
! centrally. More detailed firewall inspection happens in later projects if needed.
logging buffered warnings
logging trap warnings

! --- Remote syslog collector ---
! WHY: The collector lives behind the ASA inside path at 10.1.99.51.
! Project 07 already proved logging host inside 10.1.99.51 is the correct ASA form.
logging host inside 10.1.99.51

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show logging
! ping inside 10.1.99.51
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## Post-Apply Verification

After Claude approves and you apply the configs, generate at least one test event.

Recommended low-risk event on an access switch:

```text
! On HQ-ASW1, use an unused access port if available:
configure terminal
interface Ethernet1/3
 description P09-SYSLOG-TEST-PORT
 shutdown
 no shutdown
end
```

Then verify:

```text
! On the device where the test event was generated:
show logging | include Ethernet1/3|LINK|LINEPROTO|SYS-5-CONFIG

! On HQ-SYSLOG:
! Confirm messages arrive from the device hostname/source IP.
```

## What To Capture For Phase 1

Save the following after applying:

- `show logging | include 10.1.99.51|Trap|Logging` from HQ-RTR1, BR-RTR1, one distribution switch, one access switch
- `show logging` from HQ-FW1
- Screenshot or terminal output from HQ-SYSLOG showing received logs
- One generated link/config event proving the collector receives messages

## Claude Review Prompt

```text
Read Codex's latest session and review Project 9 Phase 1 syslog config before I apply it to CML.
Config file:
C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\configs\phase1-syslog-proposed.md
```
