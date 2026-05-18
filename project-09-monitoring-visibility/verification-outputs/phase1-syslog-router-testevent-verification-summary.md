# Project 09 - Phase 1 Router and Test Event Verification Summary

Date: 2026-05-16

## Router Verification

### WAN-RTR1

- Logging host `10.1.99.51` present.
- Trap logging level `warnings`.
- `ping 10.1.99.51 source Loopback0` succeeded 5/5.
- Source IP used: `10.0.255.3`.

### HQ-RTR1

- Logging host `10.1.99.51` present.
- Trap logging level `warnings`.
- `ping 10.1.99.51 source Loopback0` succeeded 5/5.
- Source IP used: `10.0.255.1`.

### BR-RTR1

- Logging host `10.1.99.51` present.
- Trap logging level `warnings`.
- `ping 10.1.99.51 source Loopback0` succeeded 5/5.
- Source IP used: `10.0.255.2`.

## HQ-ASW1 Test Event

HQ-ASW1 has only Ethernet0/x interfaces in this CML image. The intended test event was run on `Ethernet0/3`, not `Ethernet1/3`.

Commands applied:

```text
interface Ethernet0/3
 description P09-SYSLOG-TEST-PORT
 shutdown
 no shutdown
end
write memory
```

Local logging showed config events:

```text
%SYS-5-CONFIG_I: Configured from console by admin on console
```

No matching `%LINK` or `%LINEPROTO` messages appeared in the filtered local output for `Ethernet0/3`. This does not invalidate syslog configuration, but before closing Phase 1 the syslog collector should be checked directly for received messages from HQ-ASW1 and the routers.

## Remaining Checks

1. Confirm whether source-interface config is present in running config:

```text
show running-config | include logging host|logging source-interface|logging trap
```

Verified:

- HQ-RTR1: `logging trap warnings`, `logging source-interface Loopback0`, `logging host 10.1.99.51`
- BR-RTR1: `logging trap warnings`, `logging source-interface Loopback0`, `logging host 10.1.99.51`
- WAN-RTR1: `logging trap warnings`, `logging source-interface Loopback0`, `logging host 10.1.99.51`
- HQ-ASW1: `logging source-interface Vlan999`, `logging host 10.1.99.51`
- HQ-DSW1: `logging trap warnings`, `logging source-interface Vlan999`, `logging host 10.1.99.51`

HQ-ASW1 did not show `logging trap informational` in running config, but earlier `show logging` confirmed trap logging level informational. This is acceptable because IOS may omit default-equivalent running-config lines.

2. Confirm HQ-SYSLOG received messages from:

- HQ-RTR1
- BR-RTR1
- WAN-RTR1
- HQ-DSW1
- HQ-ASW1
- BR-ASW1
- HQ-FW1

Collector proof received:

- HQ-FW1 / ASA source `10.0.0.14` is sending logs to HQ-SYSLOG.
- HQ-ASW1 source `10.1.99.13` is sending logs to HQ-SYSLOG.
- HQ-ASW2 source `10.1.99.14` is sending logs to HQ-SYSLOG.
- BR-ASW1 source `10.2.99.3` is sending logs to HQ-SYSLOG.

Remaining nuance: routers and distribution switches use `logging trap warnings`, so normal config/login events at severity 5/6 are intentionally not forwarded. To prove those warning-tier devices send to HQ-SYSLOG without changing the design, generate a warning-level test message with `send log 4` if supported.

Warning-tier test proof received:

- HQ-DSW2 source `10.1.99.12` sent `%SYS-4-USERLOG_WARNING: P09_PHASE1_SYSLOG_TEST` to HQ-SYSLOG at 22:05:53 UTC.
- HQ-RTR1 source `10.0.255.1` sent `%SYS-4-USERLOG_WARNING: P09_PHASE1_SYSLOG_TEST` to HQ-SYSLOG at 15:26:16 UTC on 2026-05-17.
- BR-RTR1 source `10.0.255.2` sent `%SYS-4-USERLOG_WARNING: P09_PHASE1_SYSLOG_TEST` to HQ-SYSLOG at 15:26:26 UTC on 2026-05-17.
- WAN-RTR1 source `10.0.255.3` sent `%SYS-4-USERLOG_WARNING: P09_PHASE1_SYSLOG_TEST` to HQ-SYSLOG at 15:26:51 UTC on 2026-05-17.
- HQ-DSW1 source `10.1.99.11` sent `%SYS-4-USERLOG_WARNING: P09_PHASE1_SYSLOG_TEST` to HQ-SYSLOG at 15:27:08 UTC on 2026-05-17.
- BR-DSW1 source `10.2.99.2` sent `%SYS-4-USERLOG_WARNING: P09_PHASE1_SYSLOG_TEST` to HQ-SYSLOG at 15:27:18 UTC on 2026-05-17.

ISP-RTR1 exclusion verified:

- `no logging host 10.1.99.51` returned `Host 10.1.99.51 not found for logging`, confirming no active logging host remained.
- `show running-config | include logging host|logging source-interface` returned no output after removing the source-interface.

3. If a link event is still needed, test an active port and search broadly:

```text
show logging | include Ethernet0/3|LINK|LINEPROTO|CONFIG
```
