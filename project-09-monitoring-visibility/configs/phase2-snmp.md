# Project 09 - Phase 2 SNMP Monitoring

Status: CODEX-PROPOSED - pending Claude review
Session folder: C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09

Do not apply this to CML until Claude reviews and approves it.

## Phase Goal

Build SNMP monitoring on top of the Phase 1 syslog foundation.

- SNMPv2c read-only baseline on all in-scope internal devices
- SNMP traps for link up/down, cold/warm start, and SNMP authentication failures
- SNMPv3 authPriv on core routers: `HQ-RTR1`, `BR-RTR1`, `WAN-RTR1`
- SNMP manager / trap receiver target: `10.1.99.51`

## Design Notes

- `10.1.99.51` is already proven reachable from Phase 1 and is treated as the monitoring collector for Project 09.
- SNMPv2c is intentionally used as a compatibility baseline, but it is community-string based and not encrypted.
- SNMPv3 authPriv is added on the core routers because it gives authentication plus privacy/encryption for management polling.
- `ISP-RTR1` remains excluded because it represents the outside/ISP side of the ASA.
- If `HQ-SYSLOG` does not have an SNMP trap daemon listening on UDP/162, device-side SNMP config can still be verified locally, but collector-side trap proof will require enabling or using an SNMP trap receiver.

## Shared Lab Values

```text
SNMP manager/trap target: 10.1.99.51
SNMPv2c RO community: P09V2CRO2026
SNMPv3 group: P09-SNMPV3-GROUP
SNMPv3 user: p09snmpv3
SNMPv3 auth: SHA, key P09AuthKey2026
SNMPv3 privacy: AES-128, key P09PrivKey2026
```

## Pre-Work Checks

Run these before applying Phase 2:

```text
! On HQ-SYSLOG:
! Confirm whether SNMP tools/trap receiver exist.
which snmpwalk
which snmptrapd
sudo ss -lunp | grep ':162'

! On routers/switches:
show running-config | include snmp-server
show ip access-lists ACL-SNMP-MANAGERS
ping 10.1.99.51

! On HQ-FW1:
show running-config snmp-server
ping inside 10.1.99.51
```

Expected:
- No old conflicting SNMP config, or if it exists, document it before replacing.
- In-scope devices can reach `10.1.99.51`.
- If UDP/162 is not listening on HQ-SYSLOG, plan to verify traps from device-side config first and enable trap collection later.

## [CODEX-PROPOSED] Project 09 / Phase 2 / Devices: HQ-RTR1, BR-RTR1, WAN-RTR1

Apply this on the three core routers. Keep the location line device-specific.

```text
! ============================================================
! DEVICE: HQ-RTR1 / BR-RTR1 / WAN-RTR1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 2 - SNMP Monitoring
! ============================================================
enable
configure terminal

! --- Restrict SNMP managers ---
! WHY: SNMPv2c uses a shared community string. Without an ACL, any reachable host
! that knows the string could poll the device. This limits polling to HQ-SYSLOG/NMS.
ip access-list standard ACL-SNMP-MANAGERS
 permit 10.1.99.51
 exit

! --- SNMP identity metadata ---
! WHY: Monitoring tools display contact and location fields so an alert tells you
! who owns the device and where it sits logically.
snmp-server contact Leonel - Enterprise Network Labs
snmp-server location P09-CML-LAB
snmp-server chassis-id P09-CML-ROUTER
snmp-server ifindex persist

! --- SNMPv2c read-only baseline ---
! WHY: SNMPv2c is widely supported and useful for basic polling, but it is not
! encrypted. We use read-only access and restrict it with ACL-SNMP-MANAGERS.
snmp-server community P09V2CRO2026 RO ACL-SNMP-MANAGERS

! --- SNMP trap source and trap receiver ---
! WHY: Trap source Loopback0 gives the collector a stable source identity even if
! a physical interface changes. This matches Phase 1 syslog source design.
snmp-server trap-source Loopback0
snmp-server host 10.1.99.51 version 2c P09V2CRO2026

! --- SNMP trap categories ---
! WHY: Link up/down proves interface events; coldstart/warmstart prove reload
! visibility; authentication traps prove bad SNMP attempts are visible.
snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart

! --- SNMPv3 authPriv for core routers ---
! WHY: SNMPv3 authPriv authenticates the manager and encrypts SNMP payloads.
! This is the secure model for production polling, unlike SNMPv2c community strings.
snmp-server group P09-SNMPV3-GROUP v3 priv access ACL-SNMP-MANAGERS
snmp-server user p09snmpv3 P09-SNMPV3-GROUP v3 auth sha P09AuthKey2026 priv aes 128 P09PrivKey2026
snmp-server host 10.1.99.51 version 3 priv p09snmpv3

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show running-config | include snmp-server|ACL-SNMP-MANAGERS
! show snmp
! show snmp user
! show snmp group
! show ip access-lists ACL-SNMP-MANAGERS
! ping 10.1.99.51 source Loopback0
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 2 / Devices: HQ-DSW1, HQ-DSW2, BR-DSW1

Apply this on the distribution switches.

```text
! ============================================================
! DEVICE: HQ-DSW1 / HQ-DSW2 / BR-DSW1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 2 - SNMP Monitoring
! ============================================================
enable
configure terminal

! --- Restrict SNMP managers ---
! WHY: Distribution switches expose useful interface, VLAN, and STP data through
! SNMP, so polling must be limited to the monitoring host.
ip access-list standard ACL-SNMP-MANAGERS
 permit 10.1.99.51
 exit

! --- SNMP identity metadata ---
! WHY: Location/contact fields make monitoring alerts readable and portfolio-ready.
snmp-server contact Leonel - Enterprise Network Labs
snmp-server location P09-CML-LAB-DISTRIBUTION
snmp-server chassis-id P09-CML-DSW
snmp-server ifindex persist

! --- SNMPv2c read-only baseline ---
! WHY: Distribution switches use SNMPv2c in this phase as the transition baseline.
! The community is read-only and protected by ACL-SNMP-MANAGERS.
snmp-server community P09V2CRO2026 RO ACL-SNMP-MANAGERS

! --- SNMP trap source and receiver ---
! WHY: Vlan999 is the stable management SVI for switch monitoring.
snmp-server trap-source Vlan999
snmp-server host 10.1.99.51 version 2c P09V2CRO2026

! --- SNMP trap categories ---
! WHY: Link traps are central to Phase 7 correlation; auth traps show bad community
! attempts; start traps show reload/restart visibility.
snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show running-config | include snmp-server|ACL-SNMP-MANAGERS
! show snmp
! show ip access-lists ACL-SNMP-MANAGERS
! ping 10.1.99.51
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 2 / Devices: HQ-ASW1, HQ-ASW2, BR-ASW1

Apply this on the access switches.

```text
! ============================================================
! DEVICE: HQ-ASW1 / HQ-ASW2 / BR-ASW1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 2 - SNMP Monitoring
! ============================================================
enable
configure terminal

! --- Restrict SNMP managers ---
! WHY: Access switches see edge-port state, port security, and client-facing
! failures. Polling should only come from the monitoring host.
ip access-list standard ACL-SNMP-MANAGERS
 permit 10.1.99.51
 exit

! --- SNMP identity metadata ---
! WHY: Monitoring should make it obvious whether an alert came from an access
! switch or a routing/core device.
snmp-server contact Leonel - Enterprise Network Labs
snmp-server location P09-CML-LAB-ACCESS
snmp-server chassis-id P09-CML-ASW
snmp-server ifindex persist

! --- SNMPv2c read-only baseline ---
! WHY: Access layer stays on SNMPv2c for the transition baseline. Read-only plus
! manager ACL keeps the blast radius low while showing the v2c security model.
snmp-server community P09V2CRO2026 RO ACL-SNMP-MANAGERS

! --- SNMP trap source and receiver ---
! WHY: Vlan999 is the management SVI and keeps trap source identity stable.
snmp-server trap-source Vlan999
snmp-server host 10.1.99.51 version 2c P09V2CRO2026

! --- SNMP trap categories ---
! WHY: Access-layer link up/down traps are the easiest proof for Phase 2 and become
! part of the later multi-source event correlation exercise.
snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show running-config | include snmp-server|ACL-SNMP-MANAGERS
! show snmp
! show ip access-lists ACL-SNMP-MANAGERS
! ping 10.1.99.51
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## [CODEX-PROPOSED] Project 09 / Phase 2 / Device: HQ-FW1

ASA SNMP syntax is different from IOS. Apply only after Claude confirms ASAv accepts this syntax in your image.

```text
! ============================================================
! DEVICE: HQ-FW1 | PROJECT: 09 - Monitoring and Visibility
! PHASE: 2 - SNMP Monitoring
! Platform: ASAv
! ============================================================
enable
configure terminal

! --- SNMP identity metadata ---
! WHY: ASA traps should identify the firewall clearly in the collector.
snmp-server contact Leonel - Enterprise Network Labs
snmp-server location P09-CML-LAB-FIREWALL

! --- SNMPv2c trap receiver ---
! WHY: The collector is reachable through the ASA inside interface. Community-based
! SNMPv2c is configured for baseline compatibility.
snmp-server host inside 10.1.99.51 community P09V2CRO2026 version 2c

! --- SNMP trap categories ---
! WHY: Authentication and link traps let the firewall participate in monitoring
! correlation without enabling broad management from the outside.
snmp-server enable traps snmp authentication linkup linkdown coldstart warmstart

end
write memory

! --- VERIFICATION ---
! Run these commands and paste the output:
! show running-config snmp-server
! show snmp-server statistics
! ping inside 10.1.99.51
```

PENDING-CLAUDE-REVIEW - do not apply to CML until Claude approves.

## Optional Collector-Side Verification

If SNMP tools exist on HQ-SYSLOG, test polling after Claude approval and device config:

```text
snmpwalk -v2c -c P09V2CRO2026 10.0.255.1 sysName.0
snmpwalk -v2c -c P09V2CRO2026 10.1.99.13 sysName.0
snmpwalk -v3 -l authPriv -u p09snmpv3 -a SHA -A P09AuthKey2026 -x AES -X P09PrivKey2026 10.0.255.1 sysName.0
```

Expected:
- SNMPv2c works against router loopbacks and switch VLAN 999 IPs from `10.1.99.51`.
- SNMPv3 works against `HQ-RTR1`, `BR-RTR1`, and `WAN-RTR1`.
- SNMPv3 should not be expected on access switches in this phase unless you intentionally extend it later.

## Trap Test After Apply

Use one low-risk access switch port:

```text
! On HQ-ASW1, use a known safe port:
configure terminal
interface Ethernet0/3
 shutdown
 no shutdown
end
write memory
```

Then verify on the device:

```text
show snmp
show logging | include Ethernet0/3|LINK|LINEPROTO
```

If an SNMP trap receiver is running on HQ-SYSLOG, verify it received linkDown/linkUp traps from the switch source IP.

## Claude Review Prompt

```text
Read Codex's latest session and review Project 9 Phase 2 SNMP config before I apply it to CML.
Config file:
C:\Users\CHONGONG\Documents\Codex\2026-05-16\title-it-something-like-project-9\project-09\configs\phase2-snmp-proposed.md
Pay special attention to IOS IOL SNMPv3 syntax and ASAv SNMP trap syntax.
```
