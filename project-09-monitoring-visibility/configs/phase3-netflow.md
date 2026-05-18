# Project 09 - Phase 3 NetFlow Traffic Analysis

Status: CODEX-PROPOSED - pending Claude review
Session folder: C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09

Do not apply this to CML until Claude reviews and approves it.

## Phase Goal

Configure NetFlow on `HQ-RTR1` to baseline traffic patterns across the HQ campus, WAN, VPN tunnel, and firewall handoff.

This phase uses classic NetFlow syntax because the CML IOL router is more likely to support `ip flow ingress` and `ip flow-export` consistently than full Flexible NetFlow.

## Pre-Check Results Provided

Verified on `HQ-RTR1`:

- No existing flow/NetFlow config matched `show running-config | include flow|ip flow`.
- `Ethernet0/0.999` is up/up with `10.1.99.1`.
- `Ethernet0/1`, `Ethernet0/2`, `Ethernet0/3`, `Loopback0`, and `Tunnel0` are up/up.
- Route to `10.1.99.51` is directly connected via `Ethernet0/0.999`.
- `ping 10.1.99.51 source Loopback0` succeeded 5/5.

## Collector Caveat

`HQ-SYSLOG` is currently known to be syslog-ng-only from Phase 2. It may not have a NetFlow collector listening on UDP/2055.

That means:

- Device-side NetFlow can still be configured and verified on `HQ-RTR1`.
- Export can be aimed at `10.1.99.51:2055` as the intended collector.
- Collector-side proof may be blocked until a Linux/NMS collector node is added or rebuilt with NetFlow tooling.

## [CODEX-PROPOSED] Project 09 / Phase 3 / Device: HQ-RTR1

```text
! ============================================================
! DEVICE: HQ-RTR1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 3 - NetFlow Traffic Analysis
! ============================================================
enable
configure terminal

! --- NetFlow export destination ---
! WHY: Exports flow records toward the monitoring collector. UDP/2055 is a common
! NetFlow collector port. Even if HQ-SYSLOG cannot collect NetFlow today, this
! documents the intended collector path for the monitoring architecture.
ip flow-export destination 10.1.99.51 2055

! --- NetFlow export source ---
! WHY: Loopback0 is stable and already used for management identity. It makes
! exported flow records consistently appear from HQ-RTR1 as 10.0.255.1.
ip flow-export source Loopback0

! --- NetFlow export version ---
! WHY: Version 9 is template-based and more extensible than version 5. It is the
! better baseline for modern collectors while still using classic NetFlow config.
ip flow-export version 9

! --- NetFlow cache timing ---
! WHY: Shorter active timeout makes long-lived flows export periodically instead
! of waiting too long. Inactive timeout ages out quiet flows quickly during lab tests.
ip flow-cache timeout active 1
ip flow-cache timeout inactive 15

! --- NetFlow top talkers ---
! WHY: Gives local visibility even if the collector is not available. This is the
! built-in "who is using the network" view directly on HQ-RTR1.
ip flow-top-talkers
 top 10
 sort-by bytes
 exit

! --- HQ user VLANs ---
! WHY: Capture traffic entering HQ-RTR1 from major campus VLAN gateways so we can
! baseline Engineering, Sales, Guest, and Management traffic.
interface Ethernet0/0.100
 ip flow ingress

interface Ethernet0/0.200
 ip flow ingress

interface Ethernet0/0.300
 ip flow ingress

interface Ethernet0/0.999
 ip flow ingress

! --- WAN and firewall-facing paths ---
! WHY: Capture traffic arriving from direct Branch WAN, WAN-RTR1 transit, and
! firewall/inside handoff so we can compare internal, inter-site, and internet paths.
interface Ethernet0/1
 ip flow ingress

interface Ethernet0/2
 ip flow ingress

interface Ethernet0/3
 ip flow ingress

! --- VPN tunnel overlay ---
! WHY: Tunnel0 is the preferred encrypted inter-site path from Project 08. Capturing
! ingress on Tunnel0 shows traffic entering HQ from Branch over the VPN overlay.
interface Tunnel0
 ip flow ingress

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show running-config | include flow|ip flow
! show ip flow interface
! show ip flow export
! show ip cache flow
! show ip flow top-talkers
! ping 10.2.100.1 source 10.1.100.1 repeat 20
! show ip cache flow
! show ip flow top-talkers
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## Traffic Generation After Apply

Generate traffic that should create flows:

```text
! HQ Engineering toward Branch Engineering gateway:
ping 10.2.100.1 source 10.1.100.1 repeat 20

! HQ router toward collector:
ping 10.1.99.51 source Loopback0 repeat 20

! Optional if internet path is healthy:
ping 203.0.113.100 source 10.1.100.1 repeat 20
```

Then verify:

```text
show ip cache flow
show ip flow top-talkers
show ip flow export
```

Expected:

- `show ip flow interface` lists the configured interfaces with ingress flow enabled.
- `show ip cache flow` shows flows after traffic generation.
- `show ip flow top-talkers` shows source/destination pairs and byte counts.
- `show ip flow export` shows destination `10.1.99.51`, source `Loopback0`, version 9.
- Export packet counters may stay at 0 or show unreachable behavior if no NetFlow collector is listening on `10.1.99.51:2055`.

## Claude Review Prompt

```text
Read Codex's latest session and review Project 9 Phase 3 NetFlow config before I apply it to CML.
Config file:
C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\configs\phase3-netflow-proposed.md
Pay special attention to classic NetFlow syntax on IOS IOL and whether Tunnel0 should be included.
```
