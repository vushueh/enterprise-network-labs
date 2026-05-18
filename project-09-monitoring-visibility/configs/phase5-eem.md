# Project 09 - Phase 5 EEM Proposed Configuration

Status: CODEX-PROPOSED - pending Claude review
Date: 2026-05-17

## Phase Goal

Use Embedded Event Manager (EEM) to create a small on-device automation trigger.

For this phase, `HQ-ASW1` is the pilot device. It is a good candidate because:

- It already sends informational syslog to `10.1.99.51`.
- It has a safe test interface, `Ethernet0/3`, previously labeled for Project 09 testing.
- A link-down test on an access switch is low risk compared with testing on a router uplink, trunk, firewall inside link, or WAN path.

## Why EEM Matters

Syslog tells you what happened. EEM lets the device react when it happens.

In this phase, the device watches for a link-down syslog event on `Ethernet0/3`, then emits a clear Project 09 marker message:

```text
P09_PHASE5_EEM_LINK_DOWN_DETECTED
```

That marker makes the event easy to find on HQ-SYSLOG and sets up the later multi-source monitoring verification phase.

## Pre-Check

Run on `HQ-ASW1`:

```text
show running-config | section event manager
show running-config interface Ethernet0/3
show logging | include 10.1.99.51|Trap|Logging
show interfaces status | include Et0/3
ping 10.1.99.51
```

Expected:

- No conflicting EEM applet for the same test.
- `Ethernet0/3` is safe to shut/no shut for testing.
- Syslog destination is still `10.1.99.51`.
- Trap level is informational.
- Ping to HQ-SYSLOG succeeds.

## HQ-ASW1 Configuration

```text
! ============================================================
! DEVICE: HQ-ASW1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 5 - EEM Link-Down Automation
! ============================================================
enable
configure terminal

! --- Test interface label ---
! WHY: This marks Ethernet0/3 as the intentional EEM test port so future
! troubleshooting notes do not confuse this with an accidental outage.
interface Ethernet0/3
 description P09-PHASE5-EEM-LINKDOWN-TEST
 exit

! --- EEM link-down detector ---
! WHY: Watches local syslog for Ethernet0/3 going down, then sends a clear
! Project 09 marker message into syslog. This proves the device can automate
! a response without relying on an external tool.
event manager applet P09_EEM_ET0_3_LINK_DOWN
 event syslog pattern "Interface Ethernet0/3, changed state to down"
 action 1.0 syslog msg "P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-ASW1 Ethernet0/3"
 exit

end
write memory
```

## Test

Run on `HQ-ASW1`:

```text
configure terminal
interface Ethernet0/3
shutdown
no shutdown
end
write memory
```

## Verification

Run on `HQ-ASW1`:

```text
show running-config | section event manager
show event manager policy registered
show logging | include P09_PHASE5|Ethernet0/3|LINK|LINEPROTO|HA_EM
show interfaces status | include Et0/3
```

Expected:

- EEM applet `P09_EEM_ET0_3_LINK_DOWN` is present.
- Registered policy shows the applet active.
- Local logging shows:
  - Ethernet0/3 link-down/up events.
  - EEM-generated marker: `P09_PHASE5_EEM_LINK_DOWN_DETECTED`.
- Interface returns to connected/up if a neighbor is attached, or returns to the expected lab state if unused.

On HQ-SYSLOG, look for:

```text
P09_PHASE5_EEM_LINK_DOWN_DETECTED
```

If the marker appears on HQ-SYSLOG, Phase 5 is complete.

## Rollback

If the applet misbehaves:

```text
configure terminal
no event manager applet P09_EEM_ET0_3_LINK_DOWN
interface Ethernet0/3
 description P09-SYSLOG-TEST-PORT
 no shutdown
end
write memory
```
