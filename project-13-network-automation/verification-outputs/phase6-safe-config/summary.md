# Phase 6 Gated Safe Config Push Summary

- Generated UTC: 2026-06-19T05:56:11.620668+00:00
- Devices: 10
- Applied mode: False

| Device | Host | Platform | Mode | Applied | Status | Error |
|--------|------|----------|------|---------|--------|-------|
| HQ-RTR1 | 10.0.255.1 | cisco_ios | deploy | False | planned |  |
| BR-RTR1 | 10.0.255.2 | cisco_ios | deploy | False | planned |  |
| WAN-RTR1 | 10.0.255.3 | cisco_ios | deploy | False | planned |  |
| HQ-DSW1 | 10.1.99.11 | cisco_ios | deploy | False | planned |  |
| HQ-DSW2 | 10.1.99.12 | cisco_ios | deploy | False | planned |  |
| HQ-ASW1 | 10.1.99.13 | cisco_ios | deploy | False | planned |  |
| HQ-ASW2 | 10.1.99.14 | cisco_ios | deploy | False | planned |  |
| BR-DSW1 | 10.2.99.2 | cisco_ios | deploy | False | planned |  |
| BR-ASW1 | 10.2.99.3 | cisco_ios | deploy | False | planned |  |
| HQ-FW1 | 10.0.0.14 | cisco_asa | deploy | False | skipped |  |

## Commands

### HQ-RTR1

```text
ip access-list standard P13-AUTOMATION-MARKER
 remark Project 13 automation safe marker on HQ-RTR1
 remark ACL is intentionally unused and has no packet-forwarding effect
```

### BR-RTR1

```text
ip access-list standard P13-AUTOMATION-MARKER
 remark Project 13 automation safe marker on BR-RTR1
 remark ACL is intentionally unused and has no packet-forwarding effect
```

### WAN-RTR1

```text
ip access-list standard P13-AUTOMATION-MARKER
 remark Project 13 automation safe marker on WAN-RTR1
 remark ACL is intentionally unused and has no packet-forwarding effect
```

### HQ-DSW1

```text
ip access-list standard P13-AUTOMATION-MARKER
 remark Project 13 automation safe marker on HQ-DSW1
 remark ACL is intentionally unused and has no packet-forwarding effect
```

### HQ-DSW2

```text
ip access-list standard P13-AUTOMATION-MARKER
 remark Project 13 automation safe marker on HQ-DSW2
 remark ACL is intentionally unused and has no packet-forwarding effect
```

### HQ-ASW1

```text
ip access-list standard P13-AUTOMATION-MARKER
 remark Project 13 automation safe marker on HQ-ASW1
 remark ACL is intentionally unused and has no packet-forwarding effect
```

### HQ-ASW2

```text
ip access-list standard P13-AUTOMATION-MARKER
 remark Project 13 automation safe marker on HQ-ASW2
 remark ACL is intentionally unused and has no packet-forwarding effect
```

### BR-DSW1

```text
ip access-list standard P13-AUTOMATION-MARKER
 remark Project 13 automation safe marker on BR-DSW1
 remark ACL is intentionally unused and has no packet-forwarding effect
```

### BR-ASW1

```text
ip access-list standard P13-AUTOMATION-MARKER
 remark Project 13 automation safe marker on BR-ASW1
 remark ACL is intentionally unused and has no packet-forwarding effect
```

### HQ-FW1

```text
! ASA safe-push intentionally skipped in Project 13 v1
! ASA syntax and SSH reachability are handled as a separate platform exception
```
