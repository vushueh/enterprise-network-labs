# Project 09 - Phase 1 Switch and Firewall Verification Summary

Date: 2026-05-16

## Result

Phase 1 syslog configuration is working on distribution switches, access switches, and HQ-FW1.

## Verified Devices

### Distribution Switches

- HQ-DSW1:
  - logging host `10.1.99.51` present
  - trap level `warnings`
  - ping to `10.1.99.51` succeeded 5/5
- HQ-DSW2:
  - logging host `10.1.99.51` present
  - trap level `warnings`
  - ping to `10.1.99.51` succeeded 4/5
  - first packet loss likely ARP resolution
- BR-DSW1:
  - logging host `10.1.99.51` present
  - trap level `warnings`
  - ping to `10.1.99.51` succeeded 5/5

### Access Switches

- HQ-ASW1:
  - logging host `10.1.99.51` present
  - trap level `informational`
  - ping to `10.1.99.51` succeeded 5/5
- HQ-ASW2:
  - logging host `10.1.99.51` present
  - trap level `informational`
  - ping to `10.1.99.51` succeeded 5/5
- BR-ASW1:
  - logging host `10.1.99.51` present
  - trap level `informational`
  - ping to `10.1.99.51` succeeded 5/5
  - `service timestamps debug datetime msec localtime show-timezone` verified in running config on 2026-05-17

### HQ-FW1

- ASA logging enabled
- timestamp logging enabled
- device ID set to hostname `HQ-FW1`
- buffered logging level `warnings`
- trap logging level `warnings`
- logging to inside `10.1.99.51`
- UDP TX counter increased to `142`
- ping inside `10.1.99.51` succeeded 5/5

## Correction Needed

On the switches, the intended command:

```text
service timestamps debug datetime msec localtime show-timezone
```

appears to have been mistyped as:

```text
$estamps debug datetime msec localtime show-timezone
```

The log timestamp command was applied successfully, so normal syslog timestamps are present. The debug timestamp command should still be corrected on the switches for consistency before closing Phase 1.

Correction completed:

- HQ-DSW1 verified
- HQ-DSW2 verified
- BR-DSW1 verified
- HQ-ASW1 verified
- HQ-ASW2 verified
- BR-ASW1 verified

## Notes

- `enable` on HQ-FW1 returned invalid input because the prompt was already privileged (`HQ-FW1#`). No issue.
- HQ-DSW2 `.!!!!` ping pattern is acceptable and consistent with first-packet ARP resolution.
