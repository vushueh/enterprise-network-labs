# HQ-DSW1 Read-Only Baseline

- Host: 10.1.99.11
- Platform: cisco_ios
- Role: distribution_switch
- Collected UTC: 2026-06-19T05:59:25.706847+00:00

## `show cdp neighbors`

```text
Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater, P - Phone,
                  D - Remote, C - CVTA, M - Two-port Mac Relay

Device ID        Local Intrfce     Holdtme    Capability  Platform  Port ID
HQ-ASW2.lab.local
                 Eth 0/2           124             R S I  Linux Uni Eth 0/0
HQ-ASW1.lab.local
                 Eth 0/1           178             R S I  Linux Uni Eth 0/0
HQ-DSW2.lab.local
                 Eth 1/0           141             R S I  Linux Uni Eth 1/0
HQ-DSW2.lab.local
                 Eth 0/3           161             R S I  Linux Uni Eth 0/3
HQ-RTR1.lab.local
                 Eth 0/0           131               R    Linux Uni Eth 0/0

Total cdp entries displayed : 5
```

## `show ip interface brief`

```text
Interface              IP-Address      OK? Method Status                Protocol
Ethernet0/0            unassigned      YES unset  up                    up
Ethernet0/1            unassigned      YES unset  up                    up
Ethernet0/2            unassigned      YES unset  up                    up
Ethernet0/3            unassigned      YES unset  up                    up
Ethernet1/0            unassigned      YES unset  up                    up
Ethernet1/1            unassigned      YES unset  up                    up
Ethernet1/2            unassigned      YES unset  up                    up
Ethernet1/3            unassigned      YES unset  up                    up
Port-channel1          unassigned      YES unset  up                    up
Vlan999                10.1.99.11      YES NVRAM  up                    up
```

## `show version`

```text
Cisco IOS Software [IOSXE], Linux Software (X86_64BI_LINUX_L2-ADVENTERPRISEK9-M), Version 17.16.1a, RELEASE SOFTWARE (fc1)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2024 by Cisco Systems, Inc.
Compiled Thu 19-Dec-24 17:53 by mcpre

ROM: Bootstrap program is Linux

HQ-DSW1 uptime is 7 hours, 33 minutes
System returned to ROM by unknown reload cause - suspect boot_data[BOOT_COUNT] 0x9, BOOT_COUNT 0, BOOTDATA 19
System restarted at 22:26:13 UTC Thu Jun 18 2026
System image file is "unix:/x86_64_crb_linux_l2-adventerprisek9-ms.iol"
Last reload reason: Unknown reason



This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.

Linux Unix (i686) processor with 794975K bytes of memory.
Processor board ID 131184650
8 Ethernet interfaces
1 Virtual Ethernet interface
256K bytes of NVRAM.

Configuration register is 0x0
```

## `show clock`

```text
05:59:38.925 UTC Fri Jun 19 2026
```

## `show ip ospf neighbor`

```text

```

## `show logging | last 30`

```text
                       ^
% Invalid input detected at '^' marker.
```

## `show ntp associations`

```text

  address         ref clock       st   when   poll reach  delay  offset   disp
*~10.0.255.1      127.127.1.1      3    767   1024   377  1.000  -3.384  1.985
 * sys.peer, # selected, + candidate, - outlyer, x falseticker, ~ configured
```

## `show lldp neighbors`

```text
Capability codes:
    (R) Router, (B) Bridge, (T) Telephone, (C) DOCSIS Cable Device
    (W) WLAN Access Point, (P) Repeater, (S) Station, (O) Other

Device ID           Local Intf     Hold-time  Capability      Port ID
HQ-DSW2.lab.local   Et0/3          120        B,R             Et0/3
HQ-ASW1.lab.local   Et0/1          120        B,R             Et0/0
HQ-DSW2.lab.local   Et1/0          120        B,R             Et1/0
HQ-ASW2.lab.local   Et0/2          120        B,R             Et0/0
HQ-RTR1.lab.local   Et0/0          120        R               Et0/0

Total entries displayed: 5
```

## `show running-config | include ^hostname|^ip ssh|logging host|ntp|snmp-server|archive|aaa|tacacs`

```text
hostname HQ-DSW1
aaa new-model
aaa authentication login default group tacacs+ local
aaa authentication login CONSOLE local
aaa authorization exec default group tacacs+ local
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+
aaa session-id common
archive
ip tacacs source-interface Vlan999
ip ssh bulk-mode 131072
ip ssh time-out 60
logging host 10.1.99.51
snmp-server community [REDACTED] RO ACL-SNMP-MANAGERS
snmp-server trap-source Vlan999
snmp-server location P09-CML-LAB-DISTRIBUTION
snmp-server contact Leonel - Enterprise Network Labs
snmp-server chassis-id P09-CML-DSW
snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart
snmp-server host 10.1.99.51 version 2c [REDACTED]
tacacs server HQ-TACACS
key [REDACTED]
ntp authenticate
key [REDACTED]
ntp source Vlan999
key [REDACTED]
```
