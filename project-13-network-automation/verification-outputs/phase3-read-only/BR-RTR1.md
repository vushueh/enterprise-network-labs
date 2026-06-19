# BR-RTR1 Read-Only Baseline

- Host: 10.0.255.2
- Platform: cisco_ios
- Role: branch_router
- Collected UTC: 2026-06-19T05:59:02.453741+00:00

## `show cdp neighbors`

```text
Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater, P - Phone,
                  D - Remote, C - CVTA, M - Two-port Mac Relay

Device ID        Local Intrfce     Holdtme    Capability  Platform  Port ID
WAN-RTR1.lab.local
                 Eth 0/2           169               R    Linux Uni Eth 0/0
BR-DSW1.lab.local
                 Eth 0/0           178             R S I  Linux Uni Eth 0/0
HQ-RTR1.lab.local
                 Eth 0/1           163               R    Linux Uni Eth 0/1

Total cdp entries displayed : 3
```

## `show ip interface brief`

```text
Interface              IP-Address      OK? Method Status                Protocol
Ethernet0/0            unassigned      YES NVRAM  up                    up
Ethernet0/0.100        10.2.100.1      YES NVRAM  up                    up
Ethernet0/0.200        10.2.200.1      YES NVRAM  up                    up
Ethernet0/0.300        10.2.44.1       YES NVRAM  up                    up
Ethernet0/0.500        10.2.50.1       YES NVRAM  up                    up
Ethernet0/0.999        10.2.99.1       YES NVRAM  up                    up
Ethernet0/0.1000       unassigned      YES unset  up                    up
Ethernet0/1            10.0.0.2        YES NVRAM  up                    up
Ethernet0/2            10.0.0.10       YES NVRAM  up                    up
Ethernet0/3            unassigned      YES NVRAM  administratively down down
Loopback0              10.0.255.2      YES NVRAM  up                    up
Tunnel0                10.0.100.2      YES NVRAM  up                    up
```

## `show version`

```text
Cisco IOS Software [IOSXE], Linux Software (X86_64BI_LINUX-ADVENTERPRISEK9-M), Version 17.16.1a, RELEASE SOFTWARE (fc1)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2024 by Cisco Systems, Inc.
Compiled Thu 19-Dec-24 17:54 by mcpre

ROM: Bootstrap program is Linux

BR-RTR1 uptime is 7 hours, 33 minutes
System returned to ROM by unknown reload cause - suspect boot_data[BOOT_COUNT] 0x9, BOOT_COUNT 0, BOOTDATA 19
System restarted at 22:25:29 UTC Thu Jun 18 2026
System image file is "unix:/x86_64_crb_linux-adventerprisek9-ms.iol"
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

Linux Unix (i686) processor with 799831K bytes of memory.
Processor board ID 131184656
4 Ethernet interfaces
256K bytes of NVRAM.

Configuration register is 0x0
```

## `show clock`

```text
05:59:15.494 UTC Fri Jun 19 2026
```

## `show ip ospf neighbor`

```text

Neighbor ID     Pri   State           Dead Time   Address         Interface
10.0.255.3        0   FULL/  -        00:00:36    10.0.0.9        Ethernet0/2
10.0.255.1        0   FULL/  -        00:00:34    10.0.0.1        Ethernet0/1
10.0.255.1        0   FULL/  -        00:00:30    10.0.100.1      Tunnel0
```

## `show logging | last 30`

```text
                       ^
% Invalid input detected at '^' marker.
```

## `show ntp associations`

```text

  address         ref clock       st   when   poll reach  delay  offset   disp
*~10.0.255.1      127.127.1.1      3     80    512   377  2.000   2.308  2.007
 * sys.peer, # selected, + candidate, - outlyer, x falseticker, ~ configured
```

## `show lldp neighbors`

```text
Capability codes:
    (R) Router, (B) Bridge, (T) Telephone, (C) DOCSIS Cable Device
    (W) WLAN Access Point, (P) Repeater, (S) Station, (O) Other

Device ID           Local Intf     Hold-time  Capability      Port ID
HQ-RTR1.lab.local   Et0/1          120        R               Et0/1
WAN-RTR1.lab.local  Et0/2          120        R               Et0/0

Total entries displayed: 2
```

## `show running-config | include ^hostname|^ip ssh|logging host|ntp|snmp-server|archive|aaa|tacacs`

```text
hostname BR-RTR1
aaa new-model
aaa authentication login default group tacacs+ local
aaa authentication login CONSOLE local
aaa authorization exec default group tacacs+ local
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+
aaa session-id common
archive
ip tacacs source-interface Loopback0
ip ssh bulk-mode 131072
ip ssh time-out 60
logging host 10.1.99.51
snmp-server group P09-SNMPV3-GROUP v3 priv access ACL-SNMP-MANAGERS
snmp-server community [REDACTED] RO ACL-SNMP-MANAGERS
snmp-server trap-source Loopback0
snmp-server location P09-CML-LAB
snmp-server contact Leonel - Enterprise Network Labs
snmp-server chassis-id P09-CML-ROUTER
snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart
snmp-server host 10.1.99.51 version 2c [REDACTED]
snmp-server host 10.1.99.51 version 3 [REDACTED] p09snmpv3
tacacs server HQ-TACACS
key [REDACTED]
ntp authenticate
key [REDACTED]
ntp source Loopback0
key [REDACTED]
```
