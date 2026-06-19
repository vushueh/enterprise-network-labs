# Wazuh Syslog Push Summary

- Generated UTC: 2026-06-19T06:39:19.019817+00:00
- Devices: 8
- Applied mode: True

| Device | Host | Platform | Source Interface | Server | Mode | Applied | Status | Error |
|--------|------|----------|------------------|--------|------|---------|--------|-------|
| HQ-RTR1 | 10.0.255.1 | cisco_ios | Loopback0 | 192.168.10.156 | deploy | True | ok |  |
| BR-RTR1 | 10.0.255.2 | cisco_ios | Loopback0 | 192.168.10.156 | deploy | True | ok |  |
| HQ-DSW1 | 10.1.99.11 | cisco_ios | Vlan999 | 192.168.10.156 | deploy | True | ok |  |
| HQ-DSW2 | 10.1.99.12 | cisco_ios | Vlan999 | 192.168.10.156 | deploy | True | ok |  |
| HQ-ASW1 | 10.1.99.13 | cisco_ios | Vlan999 | 192.168.10.156 | deploy | True | ok |  |
| HQ-ASW2 | 10.1.99.14 | cisco_ios | Vlan999 | 192.168.10.156 | deploy | True | ok |  |
| BR-DSW1 | 10.2.99.2 | cisco_ios | Vlan999 | 192.168.10.156 | deploy | True | ok |  |
| BR-ASW1 | 10.2.99.3 | cisco_ios | Vlan999 | 192.168.10.156 | deploy | True | ok |  |

## Commands

### HQ-RTR1

```text
service timestamps log datetime msec localtime show-timezone
logging origin-id hostname
logging facility local6
logging trap informational
logging source-interface Loopback0
logging host 192.168.10.156
```

### BR-RTR1

```text
service timestamps log datetime msec localtime show-timezone
logging origin-id hostname
logging facility local6
logging trap informational
logging source-interface Loopback0
logging host 192.168.10.156
```

### HQ-DSW1

```text
service timestamps log datetime msec localtime show-timezone
logging origin-id hostname
logging facility local6
logging trap informational
logging source-interface Vlan999
logging host 192.168.10.156
```

### HQ-DSW2

```text
service timestamps log datetime msec localtime show-timezone
logging origin-id hostname
logging facility local6
logging trap informational
logging source-interface Vlan999
logging host 192.168.10.156
```

### HQ-ASW1

```text
service timestamps log datetime msec localtime show-timezone
logging origin-id hostname
logging facility local6
logging trap informational
logging source-interface Vlan999
logging host 192.168.10.156
```

### HQ-ASW2

```text
service timestamps log datetime msec localtime show-timezone
logging origin-id hostname
logging facility local6
logging trap informational
logging source-interface Vlan999
logging host 192.168.10.156
```

### BR-DSW1

```text
service timestamps log datetime msec localtime show-timezone
logging origin-id hostname
logging facility local6
logging trap informational
logging source-interface Vlan999
logging host 192.168.10.156
```

### BR-ASW1

```text
service timestamps log datetime msec localtime show-timezone
logging origin-id hostname
logging facility local6
logging trap informational
logging source-interface Vlan999
logging host 192.168.10.156
```

