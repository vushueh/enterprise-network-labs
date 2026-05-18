# Project 09 - Phase 4 NTP Synchronization

Status: CODEX-PROPOSED - pending Claude review
Session folder: C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09

Do not apply this to CML until Claude reviews and approves it.

## Phase Goal

Synchronize time across the internal enterprise lab so syslog, SNMP, NetFlow, and later EEM/archive events can be correlated accurately.

- `HQ-RTR1` acts as the internal NTP master at stratum 3.
- Internal routers and switches use authenticated NTP to `HQ-RTR1` Loopback0: `10.0.255.1`.
- `HQ-FW1` uses `HQ-RTR1` as its NTP server through the inside path.
- `ISP-RTR1` remains excluded because it represents the outside/ISP side of the ASA.

## Shared Values

```text
NTP master: HQ-RTR1
NTP master IP: 10.0.255.1
NTP stratum: 3
NTP key ID: 9
NTP MD5 key: P09NTPKey2026
```

## Why NTP Matters Here

Syslog, SNMP traps, NetFlow exports, and EEM events are only useful if timestamps line up. Without NTP, you can still see events, but you cannot reliably prove event order during troubleshooting. NTP authentication prevents a rogue device from becoming a trusted time source.

## Pre-Work Checks

Run before applying Phase 4:

```text
! On HQ-RTR1:
show running-config | include ^ntp
show clock detail
show ntp status
show ntp associations

! On each IOS/IOL client device:
show running-config | include ^ntp
show clock detail
ping 10.0.255.1

! On HQ-FW1:
show running-config ntp
show clock detail
show ntp status
ping inside 10.0.255.1
```

Expected:

- No existing conflicting NTP config, or document it before replacing.
- Clients can reach `10.0.255.1`.
- Current clocks may show hardware calendar/manual time before NTP.

## [CODEX-PROPOSED] Project 09 / Phase 4 / Device: HQ-RTR1

```text
! ============================================================
! DEVICE: HQ-RTR1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 4 - NTP Synchronization
! ROLE: Internal NTP master
! ============================================================
enable
configure terminal

! --- NTP authentication key ---
! WHY: Defines the shared MD5 key used by trusted NTP clients. This prevents an
! unauthorized or mistyped NTP source from being accepted as trusted time.
ntp authentication-key 9 md5 P09NTPKey2026

! --- Require authenticated NTP ---
! WHY: Enables NTP authentication globally. Without this, the key exists but is
! not actually enforced for authenticated synchronization.
ntp authenticate

! --- Mark key 9 as trusted ---
! WHY: NTP only accepts authenticated updates from keys listed as trusted.
ntp trusted-key 9

! --- Stable NTP source identity ---
! WHY: Loopback0 is stable and already represents HQ-RTR1 management/router ID.
! Clients will point at 10.0.255.1 rather than a physical interface.
ntp source Loopback0

! --- Internal NTP master ---
! WHY: This lab is isolated from the internet, so HQ-RTR1 becomes the authoritative
! internal clock. Stratum 3 represents an internal upstream-like source without
! pretending to be a stratum-1 reference clock.
ntp master 3

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show running-config | include ^ntp
! show clock detail
! show ntp status
! show ntp associations
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 4 / Devices: BR-RTR1 and WAN-RTR1

Apply this on `BR-RTR1` and `WAN-RTR1`.

```text
! ============================================================
! DEVICE: BR-RTR1 / WAN-RTR1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 4 - NTP Synchronization
! ROLE: Authenticated NTP client
! ============================================================
enable
configure terminal

! --- NTP authentication key ---
! WHY: Must match HQ-RTR1 key ID and secret so the router can authenticate the
! NTP master before trusting its time.
ntp authentication-key 9 md5 P09NTPKey2026

! --- Require authenticated NTP ---
! WHY: Enforces authenticated NTP instead of accepting unauthenticated time.
ntp authenticate

! --- Trust key 9 ---
! WHY: Marks key 9 as valid for NTP updates from the configured server.
ntp trusted-key 9

! --- Stable NTP source identity ---
! WHY: Loopback0 makes NTP client traffic source from the router management ID,
! matching the syslog/SNMP/NetFlow source design.
ntp source Loopback0

! --- Authenticated NTP server ---
! WHY: Points to HQ-RTR1 Loopback0, not a physical interface. The key parameter
! requires the server response to authenticate with key 9.
ntp server 10.0.255.1 key 9

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output after 1-2 minutes:
! show running-config | include ^ntp
! show clock detail
! show ntp associations
! show ntp status
! ping 10.0.255.1 source Loopback0
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 4 / Devices: HQ-DSW1, HQ-DSW2, BR-DSW1

Apply this on the distribution switches.

```text
! ============================================================
! DEVICE: HQ-DSW1 / HQ-DSW2 / BR-DSW1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 4 - NTP Synchronization
! ROLE: Authenticated NTP client
! ============================================================
enable
configure terminal

! --- NTP authentication key ---
! WHY: Uses the same key ID and secret as HQ-RTR1 so switch time cannot be set by
! an unauthenticated source.
ntp authentication-key 9 md5 P09NTPKey2026

! --- Require authenticated NTP ---
! WHY: Enables NTP authentication globally on the switch.
ntp authenticate

! --- Trust key 9 ---
! WHY: Allows the switch to accept authenticated NTP packets using key 9.
ntp trusted-key 9

! --- Stable NTP source identity ---
! WHY: Vlan999 is the management SVI and keeps NTP traffic in the management plane.
ntp source Vlan999

! --- Authenticated NTP server ---
! WHY: HQ-RTR1 Loopback0 is the internal time source for the whole lab.
ntp server 10.0.255.1 key 9

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output after 1-2 minutes:
! show running-config | include ^ntp
! show clock detail
! show ntp associations
! show ntp status
! ping 10.0.255.1
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 4 / Devices: HQ-ASW1, HQ-ASW2, BR-ASW1

Apply this on the access switches.

```text
! ============================================================
! DEVICE: HQ-ASW1 / HQ-ASW2 / BR-ASW1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 4 - NTP Synchronization
! ROLE: Authenticated NTP client
! ============================================================
enable
configure terminal

! --- NTP authentication key ---
! WHY: Edge/access logs must line up with core logs during incident correlation.
! Authenticated NTP prevents accepting time from an untrusted host.
ntp authentication-key 9 md5 P09NTPKey2026

! --- Require authenticated NTP ---
! WHY: Enables NTP authentication globally.
ntp authenticate

! --- Trust key 9 ---
! WHY: Allows authenticated NTP updates using this specific key.
ntp trusted-key 9

! --- Stable NTP source identity ---
! WHY: Vlan999 is the management SVI and matches the switch SNMP/syslog source.
ntp source Vlan999

! --- Authenticated NTP server ---
! WHY: Uses HQ-RTR1 Loopback0 as the internal time source.
ntp server 10.0.255.1 key 9

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output after 1-2 minutes:
! show running-config | include ^ntp
! show clock detail
! show ntp associations
! show ntp status
! ping 10.0.255.1
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 4 / Device: HQ-FW1

ASA NTP syntax is different from IOS. Apply only after Claude confirms syntax for your ASAv image.

```text
! ============================================================
! DEVICE: HQ-FW1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 4 - NTP Synchronization
! Platform: ASAv
! ROLE: Authenticated NTP client
! ============================================================
enable
configure terminal

! --- NTP authentication key ---
! WHY: Uses the same authenticated time key as the routers/switches.
ntp authentication-key 9 md5 P09NTPKey2026

! --- Require authenticated NTP ---
! WHY: Enables authenticated NTP on the ASA.
ntp authenticate

! --- Trust key 9 ---
! WHY: Marks the shared lab key as trusted for time synchronization.
ntp trusted-key 9

! --- Authenticated NTP server ---
! WHY: HQ-FW1 reaches HQ-RTR1 through the inside path. Source inside keeps the
! firewall's NTP traffic aligned with its internal management/security boundary.
ntp server 10.0.255.1 key 9 source inside

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output after 1-2 minutes:
! show running-config ntp
! show clock detail
! show ntp status
! show ntp associations
! ping inside 10.0.255.1
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## Expected Verification Notes

IOS/IOL devices may take 60-120 seconds before showing synchronized. Useful signs:

```text
show ntp associations
```

Expected:

- Client devices list `10.0.255.1` as the NTP server.
- The selected/active server is usually marked with `*`.

```text
show ntp status
```

Expected:

- HQ-RTR1 shows itself as an NTP master at stratum 3 or synchronized as master.
- Clients eventually show synchronized, with stratum one level below HQ-RTR1.

## Claude Review Prompt

```text
Read Codex's latest session and review Project 9 Phase 4 NTP config before I apply it to CML.
Config file:
C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\configs\phase4-ntp-proposed.md
Pay special attention to IOS IOL NTP authentication syntax and ASAv NTP server syntax.
```
