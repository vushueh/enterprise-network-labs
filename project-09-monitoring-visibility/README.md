# Project 09 — Monitoring and Visibility

**Series:** Enterprise Network Labs | **Platform:** Cisco CML 2.9 (IOL / IOL-L2 / ASAv)
**Build Date:** 2026-05-17 | **Status:** All Phases Complete ✅

---

## STAR Summary

**Situation:** Projects 01-08 built a fully routed, firewalled, encrypted enterprise network — but there was no visibility into what the network was doing. Failures were invisible until traffic stopped. There was no record of when clocks drifted, who was generating traffic, or what changed in the configuration.

**Task:** Build a monitoring stack covering syslog collection, SNMP polling and traps, NetFlow traffic baselining, authenticated NTP synchronization, EEM automated alerting, and configuration archive with rollback capability. Then run a controlled verification exercise correlating all sources simultaneously.

**Action:** Deployed syslog-ng collector on HQ-SYSLOG (10.1.99.51). Configured tiered syslog on all 10 in-scope devices. Added SNMPv2c on all devices plus SNMPv3 authPriv (SHA + AES128) on the three core routers. Enabled classic NetFlow on HQ-RTR1. Configured authenticated NTP with MD5, HQ-RTR1 as stratum-3 master — fixed an IOL-L2 management plane routing issue requiring `ip routing` + static default route. Deployed EEM on HQ-RTR1 to auto-generate syslog markers on interface-down events (IOL-L2 does not support EEM). Enabled config archive on all 9 IOS/IOL devices with `configure replace` rollback practice. Ran Phase 7 controlled verification correlating a single Loopback99 shutdown event across local syslog, EEM, SNMP counters, and NetFlow health. Completed Phase 8 CDP/LLDP discovery documenting 25 neighbor relationships.

**Result:** Full monitoring stack operational. Every device ships syslog to HQ-SYSLOG. SNMP configured and verified device-side on all 10 devices. NetFlow exporting from HQ-RTR1 with zero-error health. NTP synchronized across all 10 devices at stratum 4. EEM fires and forwards alert markers to the collector via syslog. All 9 IOS/IOL devices have config archive with verified rollback. 25-entry CDP/LLDP neighbor table documents the complete physical topology. Platform limitations documented in `LIMITATIONS-AND-HOMELAB-EXPANSION.md`.

---

## Topology

| Device | Role | Monitoring Source IP |
|--------|------|---------------------|
| HQ-RTR1 | Core router — NTP master, NetFlow exporter, EEM host | Loopback0 10.0.255.1 |
| BR-RTR1 | Branch router | Loopback0 10.0.255.2 |
| WAN-RTR1 | WAN transit router | Loopback0 10.0.255.3 |
| HQ-DSW1 | HQ distribution switch | Vlan999 10.1.99.11 |
| HQ-DSW2 | HQ distribution switch | Vlan999 10.1.99.12 |
| BR-DSW1 | Branch distribution switch | Vlan999 10.2.99.2 |
| HQ-ASW1 | HQ access switch | Vlan999 10.1.99.13 |
| HQ-ASW2 | HQ access switch | Vlan999 10.1.99.14 |
| BR-ASW1 | Branch access switch | Vlan999 10.2.99.3 |
| HQ-FW1 | ASAv firewall | inside 10.0.0.14 |
| HQ-SYSLOG | syslog-ng collector | eth0 10.1.99.51 |

**ISP-RTR1 excluded** — represents the outside/ISP boundary of the ASA. Reaching 10.1.99.51 from ISP-RTR1 would require a deliberate ASA outside-to-inside monitoring policy, which is out of scope for this project.

---

## Phase 1 — Syslog Infrastructure

### Goal

Centralize all device log messages to HQ-SYSLOG at 10.1.99.51 (UDP/514) using severity-tiered forwarding and consistent timestamp/sequence formatting on all 10 in-scope devices.

### Severity Tier Design

| Tier | Devices | Logging Level | Rationale |
|------|---------|---------------|-----------|
| Warnings | HQ-RTR1, BR-RTR1, WAN-RTR1, HQ-DSW1, HQ-DSW2, BR-DSW1, HQ-FW1 | `warnings` | Core/distribution/firewall events are high-value — only level 4+ forwarded to avoid collector noise |
| Informational | HQ-ASW1, HQ-ASW2, BR-ASW1 | `informational` | Access-layer port events (link, MAC, DHCP snooping) are useful for edge troubleshooting |

### Configuration

**Core Routers (HQ-RTR1, BR-RTR1, WAN-RTR1):**

```text
enable
configure terminal

service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service sequence-numbers

logging buffered 32768 informational
logging console warnings
logging monitor warnings
logging host 10.1.99.51
logging source-interface Loopback0
logging trap warnings

end
write memory
```

**Distribution Switches (HQ-DSW1, HQ-DSW2, BR-DSW1):**

```text
enable
configure terminal

service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service sequence-numbers

logging buffered 32768 informational
logging console warnings
logging monitor warnings
logging host 10.1.99.51
logging source-interface Vlan999
logging trap warnings

end
write memory
```

**Access Switches (HQ-ASW1, HQ-ASW2, BR-ASW1):**

```text
enable
configure terminal

service timestamps debug datetime msec localtime show-timezone
service timestamps log datetime msec localtime show-timezone
service sequence-numbers

logging buffered 32768 informational
logging console warnings
logging monitor warnings
logging host 10.1.99.51
logging source-interface Vlan999
logging trap informational

end
write memory
```

**HQ-FW1 (ASAv — different syntax):**

```text
enable
configure terminal

logging enable
logging timestamp
logging device-id hostname
logging buffered warnings
logging trap warnings
logging host inside 10.1.99.51

end
write memory
```

### Verification Commands

```text
! On each IOS/IOL device:
show logging | include 10.1.99.51|Trap|Logging
show clock detail
ping 10.1.99.51 source Loopback0      ! routers
ping 10.1.99.51                        ! switches (from Vlan999)

! On HQ-FW1:
show logging
ping inside 10.1.99.51

! Generate a test event (safe unused access port):
configure terminal
interface Ethernet0/3
 description P09-SYSLOG-TEST-PORT
 shutdown
 no shutdown
end
show logging | include Ethernet0/3|LINK|LINEPROTO
```

### Verification Results

All 10 devices confirmed sending to 10.1.99.51. Sample from HQ-RTR1:

```text
Trap logging: level warnings, 10 message lines logged
Logging to 10.1.99.51  (udp port 514, audit disabled, authentication disabled,
       link encrypted), 1 message lines logged, 0 message lines rate-limited,
       0 message lines dropped-by-MD, xml disabled, sequence number disabled
       filtering disabled
Logging Source-Interface: Loopback0   VRF Name:
```

HQ-SYSLOG collector confirmed receiving messages from all 10 source IPs, including the `%SYS-5-CONFIG_I` config event and the EEM marker set up in Phase 5.

---

## Phase 2 — SNMP Monitoring

### Goal

Enable SNMP polling and trap forwarding on all 10 in-scope devices. Add SNMPv3 authPriv on the three core routers for secure polling. Restrict polling to HQ-SYSLOG (10.1.99.51) using a standard ACL.

### Design

| Item | Value |
|------|-------|
| SNMPv2c community | `P09V2CRO2026` (read-only) |
| SNMPv2c restriction | `ACL-SNMP-MANAGERS` — permit 10.1.99.51 only |
| SNMPv3 group | `P09-SNMPV3-GROUP` |
| SNMPv3 user | `p09snmpv3` |
| SNMPv3 auth | SHA, key `P09AuthKey2026` |
| SNMPv3 privacy | AES-128, key `P09PrivKey2026` |
| Trap destination | 10.1.99.51 UDP/162 |
| Trap source | Loopback0 (routers), Vlan999 (switches), inside (HQ-FW1) |

### Configuration

**Core Routers (HQ-RTR1, BR-RTR1, WAN-RTR1) — SNMPv2c + SNMPv3:**

```text
enable
configure terminal

ip access-list standard ACL-SNMP-MANAGERS
 permit 10.1.99.51
 exit

snmp-server contact Leonel - Enterprise Network Labs
snmp-server location P09-CML-LAB
snmp-server chassis-id P09-CML-ROUTER
snmp-server ifindex persist

snmp-server community P09V2CRO2026 RO ACL-SNMP-MANAGERS

snmp-server trap-source Loopback0
snmp-server host 10.1.99.51 version 2c P09V2CRO2026
snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart

snmp-server group P09-SNMPV3-GROUP v3 priv access ACL-SNMP-MANAGERS
snmp-server user p09snmpv3 P09-SNMPV3-GROUP v3 auth sha P09AuthKey2026 priv aes 128 P09PrivKey2026
snmp-server host 10.1.99.51 version 3 priv p09snmpv3

end
write memory
```

**Distribution Switches (HQ-DSW1, HQ-DSW2, BR-DSW1) — SNMPv2c only:**

```text
enable
configure terminal

ip access-list standard ACL-SNMP-MANAGERS
 permit 10.1.99.51
 exit

snmp-server contact Leonel - Enterprise Network Labs
snmp-server location P09-CML-LAB-DISTRIBUTION
snmp-server chassis-id P09-CML-DSW
snmp-server ifindex persist

snmp-server community P09V2CRO2026 RO ACL-SNMP-MANAGERS

snmp-server trap-source Vlan999
snmp-server host 10.1.99.51 version 2c P09V2CRO2026
snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart

end
write memory
```

**Access Switches (HQ-ASW1, HQ-ASW2, BR-ASW1) — SNMPv2c only:**

```text
enable
configure terminal

ip access-list standard ACL-SNMP-MANAGERS
 permit 10.1.99.51
 exit

snmp-server contact Leonel - Enterprise Network Labs
snmp-server location P09-CML-LAB-ACCESS
snmp-server chassis-id P09-CML-ASW
snmp-server ifindex persist

snmp-server community P09V2CRO2026 RO ACL-SNMP-MANAGERS

snmp-server trap-source Vlan999
snmp-server host 10.1.99.51 version 2c P09V2CRO2026
snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart

end
write memory
```

**HQ-FW1 (ASAv — different syntax):**

```text
enable
configure terminal

snmp-server contact Leonel - Enterprise Network Labs
snmp-server location P09-CML-LAB-FIREWALL
snmp-server host inside 10.1.99.51 community P09V2CRO2026 version 2c
snmp-server enable traps snmp authentication linkup linkdown coldstart warmstart

end
write memory
```

### Verification Commands

```text
! On IOS/IOL devices:
show snmp
show snmp user
show snmp group
show ip access-lists ACL-SNMP-MANAGERS

! On HQ-FW1:
show running-config snmp-server
show snmp-server statistics

! Collector-side (if snmpwalk available — not available in this CML topology):
snmpwalk -v2c -c P09V2CRO2026 10.0.255.1 sysName.0
snmpwalk -v3 -l authPriv -u p09snmpv3 -a SHA -A P09AuthKey2026 -x AES -X P09PrivKey2026 10.0.255.1 sysName.0
```

### Verification Results

`show snmp` on HQ-RTR1 (representative):

```text
10 SNMP packets input
10 SNMP packets output
10 Trap PDUs
SNMP logging: enabled
Logging to 10.1.99.51.162, 0/10, 10 sent, 0 dropped.
```

`show snmp user` on core routers — SNMPv3 authPriv confirmed:

```text
User name: p09snmpv3
Engine ID: 80000009030000...
storage-type: nonvolatile        active
Authentication Protocol: SHA
Privacy Protocol: AES128
Group-name: P09-SNMPV3-GROUP
```

HQ-FW1 coldstart trap transmitted:

```text
show snmp-server statistics
1 Trap PDUs
```

**Collector limitation:** HQ-SYSLOG has no `snmptrapd` or `snmpwalk`. When HQ-FW1 sent its coldstart trap to UDP/162, the node returned ICMP port unreachable — confirming the device side is correct and only the receiver is absent. See `LIMITATIONS-AND-HOMELAB-EXPANSION.md`.

---

## Phase 3 — NetFlow Traffic Analysis

### Goal

Configure classic NetFlow on HQ-RTR1 to baseline traffic patterns across all major interfaces (HQ VLANs, WAN links, VPN tunnel, firewall handoff). Export flows to HQ-SYSLOG for future collector-side analysis.

### Configuration

**HQ-RTR1 only:**

```text
enable
configure terminal

ip flow-export destination 10.1.99.51 2055
ip flow-export source Loopback0
ip flow-export version 9
ip flow-cache timeout active 1
ip flow-cache timeout inactive 15

ip flow-top-talkers
 top 10
 sort-by bytes
 exit

interface Ethernet0/0.100
 ip flow ingress

interface Ethernet0/0.200
 ip flow ingress

interface Ethernet0/0.300
 ip flow ingress

interface Ethernet0/0.999
 ip flow ingress

interface Ethernet0/1
 ip flow ingress

interface Ethernet0/2
 ip flow ingress

interface Ethernet0/3
 ip flow ingress

interface Tunnel0
 ip flow ingress

end
write memory
```

### Verification Commands

```text
show ip flow export
show ip cache flow
show running-config | include flow|ip flow

! Generate traffic to populate flows:
ping 10.2.100.1 source 10.1.100.1 repeat 20
ping 10.1.99.51 source Loopback0 repeat 20
```

**IOL platform note:** `show ip flow interface` and `show ip flow top-talkers` are not supported on this IOL image. Use `show ip cache flow` and `show ip flow export` for all verification.

### Verification Results

`show ip flow export`:

```text
FNF: interface Tunnel0, direction: Input, traffic(ip): on
FNF: interface Ethernet0/3, direction: Input, traffic(ip): on
FNF: interface Ethernet0/2, direction: Input, traffic(ip): on
FNF: interface Ethernet0/1, direction: Input, traffic(ip): on
FNF: interface Ethernet0/0.999, direction: Input, traffic(ip): on
FNF: interface Ethernet0/0.300, direction: Input, traffic(ip): on
FNF: interface Ethernet0/0.200, direction: Input, traffic(ip): on
FNF: interface Ethernet0/0.100, direction: Input, traffic(ip): on

NetFlow Version: 9
Export Destination:
  10.1.99.51, 2055, AS, Loopback0

54 flows exported in 12 UDP datagrams
0 flows failed due to lack of export packet
0 export packets were dropped due to no fib
0 export packets were dropped due to adjacency issues
0 export packets were dropped due to fragmentation failures
0 export packets were dropped due to encapsulation fixup failures
```

`show ip cache flow` after cross-site ping (extract):

```text
Tu0    10.2.100.1      ->  Local   10.1.100.1    Prot:01  Pkts: 20
```

This confirms NetFlow captured the Branch-to-HQ ICMP return traffic over Tunnel0.

---

## Phase 4 — NTP Synchronization

### Goal

Synchronize all internal devices to a single authenticated time source so syslog, SNMP, NetFlow, and EEM events can be correlated by timestamp.

### Design

| Item | Value |
|------|-------|
| NTP master | HQ-RTR1 |
| Master IP | 10.0.255.1 (Loopback0) |
| Stratum | 3 |
| Auth key ID | 9 |
| Auth method | MD5 |
| Key | `P09NTPKey2026` |
| Client source (routers) | Loopback0 |
| Client source (switches) | Vlan999 |
| Client source (HQ-FW1) | inside |

### Configuration

**HQ-RTR1 (NTP master):**

```text
enable
configure terminal

ntp authentication-key 9 md5 P09NTPKey2026
ntp authenticate
ntp trusted-key 9
ntp source Loopback0
ntp master 3

end
write memory
```

**BR-RTR1 and WAN-RTR1 (routers — NTP clients):**

```text
enable
configure terminal

ntp authentication-key 9 md5 P09NTPKey2026
ntp authenticate
ntp trusted-key 9
ntp source Loopback0
ntp server 10.0.255.1 key 9

end
write memory
```

**Distribution Switches (HQ-DSW1, HQ-DSW2, BR-DSW1):**

```text
enable
configure terminal

ntp authentication-key 9 md5 P09NTPKey2026
ntp authenticate
ntp trusted-key 9
ntp source Vlan999
ntp server 10.0.255.1 key 9

end
write memory
```

**Access Switches (HQ-ASW1, HQ-ASW2, BR-ASW1):**

```text
enable
configure terminal

ntp authentication-key 9 md5 P09NTPKey2026
ntp authenticate
ntp trusted-key 9
ntp source Vlan999
ntp server 10.0.255.1 key 9

end
write memory
```

**HQ-FW1 (ASAv — different syntax):**

```text
enable
configure terminal

ntp authentication-key 9 md5 P09NTPKey2026
ntp authenticate
ntp trusted-key 9
ntp server 10.0.255.1 key 9 source inside

end
write memory
```

**IOL-L2 management routing fix (HQ-DSW1, HQ-DSW2, HQ-ASW1, HQ-ASW2 only):**

These switches could not reach 10.0.255.1 via `ip default-gateway` alone. IOL-L2 requires `ip routing` enabled and a real routing table entry for the management plane to reach remote subnets.

```text
enable
configure terminal

ip routing
ip route 0.0.0.0 0.0.0.0 10.1.99.1

end
write memory
```

### Verification Commands

```text
! On each device (wait 60-120 seconds after applying):
show ntp associations
show ntp status
show running-config | include ^ntp

! On HQ-RTR1 (master):
show ntp status
! Expected: Clock is synchronized, stratum 3, reference is 127.127.1.1

! On all other devices (clients):
show ntp associations
! Expected: *~10.0.255.1 — asterisk means selected, tilde means authenticated
```

### Verification Results

All 10 devices synchronized. Sample results:

**HQ-RTR1 (master):**

```text
show ntp status
Clock is synchronized, stratum 3, reference is 127.127.1.1
```

**BR-RTR1 and WAN-RTR1:**

```text
show ntp associations
address         ref clock       st   when   poll reach  delay  offset    disp
*~10.0.255.1    127.127.1.1      3     45     64   377   1.000  -0.500   1.204
```

**HQ switches (after routing fix):**

```text
show ntp associations
address         ref clock       st   when   poll reach  delay  offset    disp
*~10.0.255.1    127.127.1.1      3     12     64    77   1.000  -0.750   3.000
```

**HQ-FW1:**

```text
show ntp associations
address         ref clock       st   when   poll reach  delay  offset    disp
*~10.0.255.1    127.127.1.1      3     20     64   177   1.000  0.125    1.527
```

| Device | Result |
|--------|--------|
| HQ-RTR1 | Master stratum 3, reference 127.127.1.1 |
| BR-RTR1 | `*~10.0.255.1`, reach 377, stratum 4 |
| WAN-RTR1 | `*~10.0.255.1`, reach 377, stratum 4 |
| HQ-DSW1 | `*~10.0.255.1`, reach 77, stratum 4 |
| HQ-DSW2 | `*~10.0.255.1`, reach 77, stratum 4 |
| BR-DSW1 | `*~10.0.255.1`, reach 377, stratum 4 |
| HQ-ASW1 | `*~10.0.255.1`, reach 77, stratum 4 |
| HQ-ASW2 | `*~10.0.255.1`, reach 77, stratum 4 |
| BR-ASW1 | `*~10.0.255.1`, stratum 4 |
| HQ-FW1 | `*~10.0.255.1`, reach 177, stratum 4 |

---

## Phase 5 — EEM Automated Alerting

### Goal

Use Embedded Event Manager on HQ-RTR1 to watch for a specific syslog event and automatically generate a custom alert marker that is forwarded to HQ-SYSLOG via the existing syslog stack.

### Platform Discovery

The original plan was to pilot EEM on HQ-ASW1 using Ethernet0/3 as the test trigger. IOL-L2 does not support EEM:

```text
HQ-ASW1(config)# event manager applet P09_EEM_ET0_3_LINK_DOWN
                              ^
% Invalid input detected at '^' marker.
```

Phase 5 was moved to HQ-RTR1 with Loopback99 as the safe test trigger.

### EEM Pattern Lesson — First Attempt Failed

The first pattern written:

```text
event syslog pattern "Interface Loopback99, changed state to administratively down"
```

This did not fire. When a loopback is shut, IOS generates two separate messages:

```text
%LINK-5-CHANGED: Interface Loopback99, changed state to administratively down
%LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to down
```

The pattern did not literally match either message. EEM `event syslog pattern` does a literal substring match against the full message string. The working pattern targets the LINEPROTO message.

### Configuration

**HQ-RTR1 — Loopback99 test interface (already exists from P08):**

```text
enable
configure terminal

interface Loopback99
 description P09-PHASE5-EEM-TEST-INTERFACE
 ip address 10.255.99.99 255.255.255.255

end
```

**HQ-RTR1 — EEM applet:**

```text
enable
configure terminal

event manager applet P09_EEM_LOOP99_DOWN
 event syslog pattern "Line protocol on Interface Loopback99, changed state to down"
 action 1.0 syslog priority warnings msg "P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99"
 exit

end
write memory
```

**Trigger the test:**

```text
configure terminal
interface Loopback99
 shutdown
end

! Wait 3-5 seconds, then restore:
configure terminal
interface Loopback99
 no shutdown
end
write memory
```

### Verification Commands

```text
show running-config | section event manager
show event manager policy registered
show event manager history events
show logging | include P09_PHASE5|Loopback99|HA_EM|LINEPROTO|LINK
```

### Verification Results

Local syslog on HQ-RTR1:

```text
001850: May 17 18:06:42.919 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to down
001851: May 17 18:06:42.919 UTC: %LINK-5-CHANGED: Interface Loopback99, changed state to administratively down
001852: May 17 18:06:42.922 UTC: %HA_EM-4-LOG: P09_EEM_LOOP99_DOWN: P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99
001854: May 17 18:06:59.117 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to up
001855: May 17 18:06:59.117 UTC: %LINK-3-UPDOWN: Interface Loopback99, changed state to up
```

EEM fired in **3ms** after the LINEPROTO event.

`show event manager history events`:

```text
No.  Job Id Proc Status   Time of Event            Event Type        Name
1    1      Actv success  Sun May17 18:06:42 2026  syslog            applet: P09_EEM_LOOP99_DOWN
```

HQ-SYSLOG confirmed receiving the EEM marker from 10.0.255.1 within 1 second of the event.

---

## Phase 6 — Configuration Archive and Rollback

### Goal

Enable local configuration archive on all 9 IOS/IOL devices so every `write memory` creates a recoverable snapshot. Practice `configure replace` rollback on HQ-RTR1.

### Platform Discovery

CML IOL and IOL-L2 images do not expose `flash:`. Proposed `path flash:P09-ARCHIVE-$h-` failed on all devices. `show file systems` confirmed `unix:` as the correct writable filesystem.

### Configuration

**All 9 IOS/IOL devices (HQ-RTR1, BR-RTR1, WAN-RTR1, HQ-DSW1, HQ-DSW2, BR-DSW1, HQ-ASW1, HQ-ASW2, BR-ASW1):**

```text
enable
configure terminal

archive
 path unix:/P09-ARCHIVE-$h-
 write-memory
 maximum 5
 exit

end
write memory

! Force an immediate snapshot:
archive config
```

**HQ-FW1 excluded** — ASAv does not use IOS `archive` or `configure replace`. Save ASA config with `write memory` only.

### Rollback Practice (HQ-RTR1)

```text
! Step 1 — identify current archive file:
show archive

! Output will show something like:
! unix:/P09-ARCHIVE-HQ-RTR1--May-17-23-30-15.736-UTC-1 <- Most Recent

! Step 2 — inject a harmless bad change:
configure terminal
interface Loopback99
 description P09-PHASE6-BAD-CHANGE-ROLLBACK-TEST
end
show running-config interface Loopback99

! Step 3 — roll back to the archived config:
configure replace unix:/P09-ARCHIVE-HQ-RTR1--May-17-23-30-15.736-UTC-1 force
```

### Verification Commands

```text
show running-config | section archive
show archive
dir unix: | include P09-ARCHIVE
show logging | include CONFIG|ARCHIVE|SYS-5-CONFIG_R
```

### Verification Results

`show archive` on HQ-RTR1:

```text
There are currently 1 archive configurations saved.
The next archive file will be named unix:/P09-ARCHIVE-HQ-RTR1--2
 Archive #  Name
   1        unix:/P09-ARCHIVE-HQ-RTR1--May-17-23-30-15.736-UTC-1 <- Most Recent
```

Rollback output:

```text
Total number of passes: 1
Rollback Done
```

Post-rollback log:

```text
%SYS-5-CONFIG_R: Config Replace is Done
%SYS-5-CONFIG_P: Configured programmatically by process Exec from console as admin on console
```

Post-rollback interface state confirms Loopback99 description was fully restored:

```text
interface Loopback99
 description P09-PHASE5-EEM-TEST-INTERFACE
 ip address 10.255.99.99 255.255.255.255
```

---

## Phase 7 — Monitoring Verification Exercise

### Goal

Generate a controlled failure event on HQ-RTR1 and correlate the evidence across all four active monitoring systems simultaneously: local syslog, EEM, SNMP trap counters, and NetFlow health counters.

### Known Collector Limitations

HQ-SYSLOG is syslog-ng only (built during Project 07). It does not run `snmptrapd` or a NetFlow collector. Syslog/EEM proof is valid at the collector. SNMP and NetFlow proof is device-side only.

### Pre-Check (Run Before the Test)

```text
! On HQ-RTR1:
show running-config interface Loopback99
show running-config | section event manager
show logging | include 10.1.99.51|Trap|Logging
show snmp
show ip flow export
ping 10.1.99.51 source Loopback0

! Capture SNMP baseline (note the current "sent" count):
show snmp | include Logging
! Baseline: 6 sent, 0 dropped

! Capture NetFlow baseline:
show ip flow export
! Baseline: 5715 flows exported in 1459 UDP datagrams, 0 failures
```

**Generate NetFlow baseline traffic:**

```text
ping 10.2.100.1 source 10.1.100.1 repeat 20
```

### Failure Trigger

```text
configure terminal
interface Loopback99
 shutdown
end
```

Wait 5 seconds, then restore:

```text
configure terminal
interface Loopback99
 no shutdown
end
write memory
```

### Post-Failure Verification

```text
show logging | include P09_PHASE5|Loopback99|HA_EM|LINEPROTO|LINK
show event manager history events
show snmp
show ip flow export
show ip cache flow
```

### Verification Results

**Event timestamp:** `23:44:16.407 UTC May 17 2026`

**Local syslog on HQ-RTR1:**

```text
001908: May 17 23:44:16.407 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to down
001909: May 17 23:44:16.407 UTC: %LINK-5-CHANGED: Interface Loopback99, changed state to administratively down
001910: May 17 23:44:16.410 UTC: %HA_EM-4-LOG: P09_EEM_LOOP99_DOWN: P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99
001912: May 17 23:44:45.096 UTC: %LINEPROTO-5-UPDOWN: Line protocol on Interface Loopback99, changed state to up
001913: May 17 23:44:45.096 UTC: %LINK-3-UPDOWN: Interface Loopback99, changed state to up
```

**EEM history:**

```text
No.  Job Id Proc Status   Time of Event            Event Type        Name
1    1      Actv success  Sun May17 18:06:42 2026  syslog            applet: P09_EEM_LOOP99_DOWN
2    2      Actv success  Sun May17 23:44:16 2026  syslog            applet: P09_EEM_LOOP99_DOWN
```

**HQ-SYSLOG collector received the EEM marker 1 second after the event:**

```text
May 17 23:44:17 10.0.255.1 001910: May 17 23:44:16.410 UTC: %HA_EM-4-LOG: P09_EEM_LOOP99_DOWN: P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99
May 17 23:44:46 10.0.255.1 001913: May 17 23:44:45.096 UTC: %LINK-3-UPDOWN: Interface Loopback99, changed state to up
```

**SNMP device-side — trap counters increased from baseline:**

```text
! Pre-event: 6 sent, 0 dropped
! Post-event:
10 SNMP packets output
10 Trap PDUs
Logging to 10.1.99.51.162, 0/10, 10 sent, 0 dropped.
```

**NetFlow device-side — export remained healthy throughout:**

```text
! Pre-event: 5715 flows exported in 1459 UDP datagrams
! Post-event:
5727 flows exported in 1463 UDP datagrams
0 flows failed due to lack of export packet
0 export packets were dropped due to no fib
0 export packets were dropped due to adjacency issues
0 export packets were dropped due to fragmentation failures
0 export packets were dropped due to encapsulation fixup failures
```

### Correlation Summary

| Source | Evidence | Timestamp |
|--------|---------|-----------|
| Local syslog | LINEPROTO Loopback99 down | 23:44:16.407 |
| EEM | Applet P09_EEM_LOOP99_DOWN fired, status success | 23:44:16 (3ms after event) |
| HQ-SYSLOG collector | EEM marker received from 10.0.255.1 | 23:44:17 (1s after event) |
| SNMP device-side | Trap count: 6 → 10 sent, 0 dropped | During event |
| NetFlow device-side | 12 additional flows, 0 export failures | During event |

---

## Phase 8 — CDP/LLDP Topology Discovery

### Goal

Use CDP and LLDP to verify the physical topology and build a documented neighbor table for all 9 IOS/IOL devices. Document HQ-FW1 as discovery-limited.

### Configuration

**All 9 IOS/IOL devices (HQ-RTR1, BR-RTR1, WAN-RTR1, HQ-DSW1, HQ-DSW2, BR-DSW1, HQ-ASW1, HQ-ASW2, BR-ASW1):**

```text
enable
configure terminal

cdp run
lldp run

end
write memory
```

**HQ-FW1 check (CDP/LLDP not supported on ASAv):**

```text
show running-config cdp
show running-config lldp
show cdp neighbors
show lldp neighbors
```

All four commands returned:

```text
ERROR: % Invalid input detected at '^' marker.
```

HQ-FW1 is discovery-limited. Topology link documented via HQ-RTR1 interface description and `show nameif` output:

```text
GigabitEthernet0/0  10.0.0.14    up/up  nameif inside   security 100
GigabitEthernet0/1  203.0.113.1  up/up  nameif outside  security 0
GigabitEthernet0/2  10.1.40.1    up/up  nameif dmz      security 50
```

### Verification Commands

```text
show cdp neighbors
show cdp neighbors detail
show lldp neighbors
show lldp neighbors detail
show interfaces description
show ip interface brief
```

### Verification Results — Complete Neighbor Table

| Local Device | Local Interface | Neighbor Device | Neighbor Interface | Protocol Evidence |
|---|---|---|---|---|
| HQ-RTR1 | Ethernet0/0 | HQ-DSW1 | Ethernet0/0 | CDP + LLDP |
| HQ-RTR1 | Ethernet0/1 | BR-RTR1 | Ethernet0/1 | CDP + LLDP |
| HQ-RTR1 | Ethernet0/2 | WAN-RTR1 | Ethernet0/1 | CDP + LLDP |
| HQ-RTR1 | Ethernet0/3 | HQ-FW1 | GigabitEthernet0/0 inside | Description only (ASAv unsupported) |
| BR-RTR1 | Ethernet0/0 | BR-DSW1 | Ethernet0/0 | CDP |
| BR-RTR1 | Ethernet0/1 | HQ-RTR1 | Ethernet0/1 | CDP + LLDP |
| BR-RTR1 | Ethernet0/2 | WAN-RTR1 | Ethernet0/0 | CDP + LLDP |
| WAN-RTR1 | Ethernet0/0 | BR-RTR1 | Ethernet0/2 | CDP + LLDP |
| WAN-RTR1 | Ethernet0/1 | HQ-RTR1 | Ethernet0/2 | CDP + LLDP |
| HQ-DSW1 | Ethernet0/0 | HQ-RTR1 | Ethernet0/0 | CDP + LLDP |
| HQ-DSW1 | Ethernet0/1 | HQ-ASW1 | Ethernet0/0 | CDP |
| HQ-DSW1 | Ethernet0/2 | HQ-ASW2 | Ethernet0/0 | CDP |
| HQ-DSW1 | Ethernet0/3 | HQ-DSW2 | Ethernet0/3 | CDP + LLDP |
| HQ-DSW1 | Ethernet1/0 | HQ-DSW2 | Ethernet1/0 | CDP + LLDP |
| HQ-DSW2 | Ethernet0/1 | HQ-ASW1 | Ethernet0/1 | CDP |
| HQ-DSW2 | Ethernet0/2 | HQ-ASW2 | Ethernet0/1 | CDP |
| HQ-DSW2 | Ethernet0/3 | HQ-DSW1 | Ethernet0/3 | CDP + LLDP |
| HQ-DSW2 | Ethernet1/0 | HQ-DSW1 | Ethernet1/0 | CDP + LLDP |
| BR-DSW1 | Ethernet0/0 | BR-RTR1 | Ethernet0/0 | CDP + LLDP |
| BR-DSW1 | Ethernet0/1 | BR-ASW1 | Ethernet0/0 | CDP + LLDP |
| HQ-ASW1 | Ethernet0/0 | HQ-DSW1 | Ethernet0/1 | CDP + LLDP |
| HQ-ASW1 | Ethernet0/1 | HQ-DSW2 | Ethernet0/1 | CDP |
| HQ-ASW2 | Ethernet0/0 | HQ-DSW1 | Ethernet0/2 | CDP |
| HQ-ASW2 | Ethernet0/1 | HQ-DSW2 | Ethernet0/2 | CDP + LLDP |
| BR-ASW1 | Ethernet0/0 | BR-DSW1 | Ethernet0/1 | CDP + LLDP |

**Endpoint-facing ports with no CDP/LLDP neighbors (expected — servers and PCs do not advertise):**

- HQ-DSW1 Ethernet1/1 → HQ-SYSLOG
- HQ-DSW2 Ethernet0/0 → HQ DHCP/DNS server
- HQ-ASW1 Ethernet0/2 → Engineering PC
- HQ-ASW1 Ethernet0/3 → P09 syslog test port
- HQ-ASW2 Ethernet0/2 → Sales PC
- HQ-ASW2 Ethernet0/3 → Attacker/test host
- BR-ASW1 Ethernet1/0 → Branch PC VLAN100
- BR-ASW1 Ethernet1/1 → Branch PC VLAN200

---

## Verification Summary

| Phase | Success Criteria | Result |
|-------|-----------------|--------|
| 1 — Syslog | All 10 devices confirmed in collector | ✅ |
| 2 — SNMP | SNMPv3 SHA+AES128 on 3 core routers, v2c on all 10 | ✅ |
| 3 — NetFlow | 54+ flows exported, 0 failures | ✅ |
| 4 — NTP | All 10 stratum 4 under HQ-RTR1 stratum 3 | ✅ |
| 5 — EEM | Applet fired in 3ms, marker arrived at collector | ✅ |
| 6 — Archive | All 9 devices configured, rollback verified on HQ-RTR1 | ✅ |
| 7 — Verification | Single event correlated across 4 sources in under 1 second | ✅ |
| 8 — CDP/LLDP | 25 neighbor relationships documented, ASAv noted | ✅ |

---

## CML Platform Limitations

| # | Limitation | Phases Affected | Homelab Fix |
|---|-----------|-----------------|-------------|
| 1 | HQ-SYSLOG has no snmptrapd / snmpwalk | Phase 2 | LibreNMS or net-snmp VM |
| 2 | HQ-SYSLOG has no NetFlow collector | Phase 3 | ntopng or pmacct + Grafana |
| 3 | HQ-SYSLOG has no searchable interface | Phase 1, 7 | Graylog or ELK |
| 4 | ISP-RTR1 excluded from monitoring | Phase 1, 2 | OOB management VLAN |
| 5 | No upstream NTP reference | Phase 4 | pool.ntp.org or OPNsense NTP |
| 6 | EEM cannot call external APIs | Phase 5 | IOS XE guestshell or Ansible |
| 7 | IOL-L2 switches do not support EEM | Phase 5 | IOS XE Catalyst 9000v |
| 8 | EEM pattern matching is literal — wording varies by IOS image | Phase 5 | Always verify with show logging first |
| 9 | CML IOL/IOL-L2 has no flash: — use unix: | Phase 6 | Use flash: on real hardware / IOS XE |

See `LIMITATIONS-AND-HOMELAB-EXPANSION.md` for full detail and homelab resolution steps.

---

## Key Technologies

| Technology | What Was Built |
|------------|---------------|
| Syslog-ng | Centralized collector at 10.1.99.51, all 10 devices forwarding |
| SNMPv2c | ACL-protected community `P09V2CRO2026`, all 10 devices |
| SNMPv3 authPriv | SHA + AES128, user `p09snmpv3`, core routers only |
| Classic NetFlow v9 | 8-interface export from HQ-RTR1, zero-error export verified |
| NTP MD5 auth | HQ-RTR1 stratum 3 master, all other devices stratum 4 |
| EEM syslog applet | Loopback99 trigger → `P09_PHASE5_EEM_LINK_DOWN_DETECTED` via syslog |
| Config archive | `unix:` path on IOL/IOL-L2, `configure replace` rollback verified |
| CDP / LLDP | 25-entry neighbor table, ASAv noted as discovery-limited |

---

## Troubleshooting Log

See the root [TROUBLESHOOTING-LOG.md](../TROUBLESHOOTING-LOG.md) for P09 entries:

- **P09-T01:** IOL-L2 management plane routing — `ip routing` + static default route required
- **P09-T02:** EEM not supported on IOL-L2 images
- **P09-T03:** EEM syslog pattern mismatch — LINEPROTO vs. LINK message wording
- **P09-T04:** Config archive `flash:` unavailable on CML IOL — corrected to `unix:`
- **P09-T05:** SNMP trap receiver not running on HQ-SYSLOG — ICMP port unreachable on UDP/162
- **P09-T06:** ASAv rejects CDP/LLDP commands — documented via interface description
