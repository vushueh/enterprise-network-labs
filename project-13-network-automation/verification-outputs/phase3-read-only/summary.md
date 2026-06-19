# Phase 3 Read-Only Netmiko Collection Summary

- Collected UTC: 2026-06-19T06:00:45.326119+00:00
- Devices attempted: 10
- Devices successful: 8
- Devices failed: 2

| Device | Host | Platform | Status | Commands | Error |
|--------|------|----------|--------|----------|-------|
| HQ-RTR1 | 10.0.255.1 | cisco_ios | ok | 9/9 |  |
| BR-RTR1 | 10.0.255.2 | cisco_ios | ok | 9/9 |  |
| WAN-RTR1 | 10.0.255.3 | cisco_ios | failed | 0/9 | NetmikoAuthenticationException: Authentication to device failed.

Common causes of this problem are:
1. Invalid username and password
2. Incorrect SSH-key file
3. Connecting to the wrong device

Device settings: cisco_ios 10.0.255.3:22


Authentication failed. |
| HQ-DSW1 | 10.1.99.11 | cisco_ios | ok | 9/9 |  |
| HQ-DSW2 | 10.1.99.12 | cisco_ios | ok | 9/9 |  |
| HQ-ASW1 | 10.1.99.13 | cisco_ios | ok | 9/9 |  |
| HQ-ASW2 | 10.1.99.14 | cisco_ios | ok | 9/9 |  |
| BR-DSW1 | 10.2.99.2 | cisco_ios | ok | 9/9 |  |
| BR-ASW1 | 10.2.99.3 | cisco_ios | ok | 9/9 |  |
| HQ-FW1 | 10.0.0.14 | cisco_asa | failed | 0/6 | NetmikoTimeoutException: TCP connection to device failed.

Common causes of this problem are:
1. Incorrect hostname or IP address.
2. Wrong TCP port.
3. Intermediate firewall blocking access.

Device settings: cisco_asa 10.0.0.14:22

 |
