# Phase 5 Compliance Check Summary

- Checked UTC: 2026-06-19T05:56:10.789634+00:00
- Devices attempted: 10
- Compliant: 0
- Non-compliant: 8
- Failed/unreachable: 2

| Device | Host | Platform | Status | Failing/Warned Checks | Error |
|--------|------|----------|--------|------------------------|-------|
| HQ-RTR1 | 10.0.255.1 | cisco_ios | non_compliant | SSHv2 enabled=fail, NTP points to core time source=fail |  |
| BR-RTR1 | 10.0.255.2 | cisco_ios | non_compliant | SSHv2 enabled=fail |  |
| WAN-RTR1 | 10.0.255.3 | cisco_ios | failed | none | NetmikoAuthenticationException: Authentication to device failed.

Common causes of this problem are:
1. Invalid username and password
2. Incorrect SSH-key file
3. Connecting to the wrong device

Device settings: cisco_ios 10.0.255.3:22


Authentication failed. |
| HQ-DSW1 | 10.1.99.11 | cisco_ios | non_compliant | SSHv2 enabled=fail |  |
| HQ-DSW2 | 10.1.99.12 | cisco_ios | non_compliant | SSHv2 enabled=fail |  |
| HQ-ASW1 | 10.1.99.13 | cisco_ios | non_compliant | SSHv2 enabled=fail |  |
| HQ-ASW2 | 10.1.99.14 | cisco_ios | non_compliant | SSHv2 enabled=fail |  |
| BR-DSW1 | 10.2.99.2 | cisco_ios | non_compliant | SSHv2 enabled=fail |  |
| BR-ASW1 | 10.2.99.3 | cisco_ios | non_compliant | SSHv2 enabled=fail |  |
| HQ-FW1 | 10.0.0.14 | cisco_asa | failed | none | NetmikoTimeoutException: TCP connection to device failed.

Common causes of this problem are:
1. Incorrect hostname or IP address.
2. Wrong TCP port.
3. Intermediate firewall blocking access.

Device settings: cisco_asa 10.0.0.14:22

 |

## Detailed Checks

### HQ-RTR1

| Check | Status | Evidence |
|-------|--------|----------|
| hostname matches inventory | pass | expected hostname HQ-RTR1 |
| SSHv2 enabled | fail | requires `ip ssh version 2` |
| syslog points to collector | pass | expected logging host 10.1.99.51 |
| NTP points to core time source | fail | expected ntp server 10.0.255.1 |
| SNMP read-only standard present | pass | expected standard read-only community; report stores only pass/fail |
| config archive present | pass | expected IOS archive path for rollback evidence |
| no obvious plaintext passwords | pass | checked for password type 0 and enable password |

### BR-RTR1

| Check | Status | Evidence |
|-------|--------|----------|
| hostname matches inventory | pass | expected hostname BR-RTR1 |
| SSHv2 enabled | fail | requires `ip ssh version 2` |
| syslog points to collector | pass | expected logging host 10.1.99.51 |
| NTP points to core time source | pass | expected ntp server 10.0.255.1 |
| SNMP read-only standard present | pass | expected standard read-only community; report stores only pass/fail |
| config archive present | pass | expected IOS archive path for rollback evidence |
| no obvious plaintext passwords | pass | checked for password type 0 and enable password |

### WAN-RTR1

- Error: `NetmikoAuthenticationException: Authentication to device failed.

Common causes of this problem are:
1. Invalid username and password
2. Incorrect SSH-key file
3. Connecting to the wrong device

Device settings: cisco_ios 10.0.255.3:22


Authentication failed.`

### HQ-DSW1

| Check | Status | Evidence |
|-------|--------|----------|
| hostname matches inventory | pass | expected hostname HQ-DSW1 |
| SSHv2 enabled | fail | requires `ip ssh version 2` |
| syslog points to collector | pass | expected logging host 10.1.99.51 |
| NTP points to core time source | pass | expected ntp server 10.0.255.1 |
| SNMP read-only standard present | pass | expected standard read-only community; report stores only pass/fail |
| config archive present | pass | expected IOS archive path for rollback evidence |
| no obvious plaintext passwords | pass | checked for password type 0 and enable password |

### HQ-DSW2

| Check | Status | Evidence |
|-------|--------|----------|
| hostname matches inventory | pass | expected hostname HQ-DSW2 |
| SSHv2 enabled | fail | requires `ip ssh version 2` |
| syslog points to collector | pass | expected logging host 10.1.99.51 |
| NTP points to core time source | pass | expected ntp server 10.0.255.1 |
| SNMP read-only standard present | pass | expected standard read-only community; report stores only pass/fail |
| config archive present | pass | expected IOS archive path for rollback evidence |
| no obvious plaintext passwords | pass | checked for password type 0 and enable password |

### HQ-ASW1

| Check | Status | Evidence |
|-------|--------|----------|
| hostname matches inventory | pass | expected hostname HQ-ASW1 |
| SSHv2 enabled | fail | requires `ip ssh version 2` |
| syslog points to collector | pass | expected logging host 10.1.99.51 |
| NTP points to core time source | pass | expected ntp server 10.0.255.1 |
| SNMP read-only standard present | pass | expected standard read-only community; report stores only pass/fail |
| config archive present | pass | expected IOS archive path for rollback evidence |
| no obvious plaintext passwords | pass | checked for password type 0 and enable password |

### HQ-ASW2

| Check | Status | Evidence |
|-------|--------|----------|
| hostname matches inventory | pass | expected hostname HQ-ASW2 |
| SSHv2 enabled | fail | requires `ip ssh version 2` |
| syslog points to collector | pass | expected logging host 10.1.99.51 |
| NTP points to core time source | pass | expected ntp server 10.0.255.1 |
| SNMP read-only standard present | pass | expected standard read-only community; report stores only pass/fail |
| config archive present | pass | expected IOS archive path for rollback evidence |
| no obvious plaintext passwords | pass | checked for password type 0 and enable password |

### BR-DSW1

| Check | Status | Evidence |
|-------|--------|----------|
| hostname matches inventory | pass | expected hostname BR-DSW1 |
| SSHv2 enabled | fail | requires `ip ssh version 2` |
| syslog points to collector | pass | expected logging host 10.1.99.51 |
| NTP points to core time source | pass | expected ntp server 10.0.255.1 |
| SNMP read-only standard present | pass | expected standard read-only community; report stores only pass/fail |
| config archive present | pass | expected IOS archive path for rollback evidence |
| no obvious plaintext passwords | pass | checked for password type 0 and enable password |

### BR-ASW1

| Check | Status | Evidence |
|-------|--------|----------|
| hostname matches inventory | pass | expected hostname BR-ASW1 |
| SSHv2 enabled | fail | requires `ip ssh version 2` |
| syslog points to collector | pass | expected logging host 10.1.99.51 |
| NTP points to core time source | pass | expected ntp server 10.0.255.1 |
| SNMP read-only standard present | pass | expected standard read-only community; report stores only pass/fail |
| config archive present | pass | expected IOS archive path for rollback evidence |
| no obvious plaintext passwords | pass | checked for password type 0 and enable password |

### HQ-FW1

- Error: `NetmikoTimeoutException: TCP connection to device failed.

Common causes of this problem are:
1. Incorrect hostname or IP address.
2. Wrong TCP port.
3. Intermediate firewall blocking access.

Device settings: cisco_asa 10.0.0.14:22

`
