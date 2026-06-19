# Phase 4 Redacted Config Backup Summary

- Collected UTC: 2026-06-19T06:02:11.390660+00:00
- Devices attempted: 10
- Devices successful: 8
- Devices failed: 2

| Device | Host | Platform | Status | File | Error |
|--------|------|----------|--------|------|-------|
| HQ-RTR1 | 10.0.255.1 | cisco_ios | ok | outputs/phase4-redacted-backups/HQ-RTR1-running-config-redacted.txt |  |
| BR-RTR1 | 10.0.255.2 | cisco_ios | ok | outputs/phase4-redacted-backups/BR-RTR1-running-config-redacted.txt |  |
| WAN-RTR1 | 10.0.255.3 | cisco_ios | failed |  | NetmikoAuthenticationException: Authentication to device failed.

Common causes of this problem are:
1. Invalid username and password
2. Incorrect SSH-key file
3. Connecting to the wrong device

Device settings: cisco_ios 10.0.255.3:22


Authentication failed. |
| HQ-DSW1 | 10.1.99.11 | cisco_ios | ok | outputs/phase4-redacted-backups/HQ-DSW1-running-config-redacted.txt |  |
| HQ-DSW2 | 10.1.99.12 | cisco_ios | ok | outputs/phase4-redacted-backups/HQ-DSW2-running-config-redacted.txt |  |
| HQ-ASW1 | 10.1.99.13 | cisco_ios | ok | outputs/phase4-redacted-backups/HQ-ASW1-running-config-redacted.txt |  |
| HQ-ASW2 | 10.1.99.14 | cisco_ios | ok | outputs/phase4-redacted-backups/HQ-ASW2-running-config-redacted.txt |  |
| BR-DSW1 | 10.2.99.2 | cisco_ios | ok | outputs/phase4-redacted-backups/BR-DSW1-running-config-redacted.txt |  |
| BR-ASW1 | 10.2.99.3 | cisco_ios | ok | outputs/phase4-redacted-backups/BR-ASW1-running-config-redacted.txt |  |
| HQ-FW1 | 10.0.0.14 | cisco_asa | failed |  | NetmikoTimeoutException: TCP connection to device failed.

Common causes of this problem are:
1. Incorrect hostname or IP address.
2. Wrong TCP port.
3. Intermediate firewall blocking access.

Device settings: cisco_asa 10.0.0.14:22

 |
