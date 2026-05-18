# Project 09 - Phase 7 Monitoring Verification Exercise

Status: CODEX-PROPOSED - pending Claude review
Date: 2026-05-17

## Phase Goal

Simulate a controlled failure and correlate evidence from the monitoring stack:

- Syslog
- EEM
- SNMP device-side trap counters
- NetFlow device-side cache/export counters

## Known Collector Limitations

`HQ-SYSLOG` is a syslog-ng-only node from the Project 07 build.

It does not expose:

- `snmptrapd`
- net-snmp tools
- NetFlow collector tools

Therefore:

- Syslog/EEM collector-side proof is valid on HQ-SYSLOG.
- SNMP trap proof is device-side only.
- NetFlow proof is device-side only.

## Test Device

Use `HQ-RTR1`.

Why:

- It supports EEM.
- It already exports NetFlow to `10.1.99.51:2055`.
- It has SNMP traps configured.
- It has a safe test interface, `Loopback99`, from Phase 5.
- Shutting `Loopback99` does not interrupt production lab forwarding.

## Pre-Check

Run on `HQ-RTR1`:

```text
show running-config interface Loopback99
show running-config | section event manager
show logging | include 10.1.99.51|Trap|Logging
show snmp
show ip flow export
show ip cache flow
ping 10.1.99.51 source Loopback0
```

Expected:

- `Loopback99` exists with IP `10.255.99.99/32`.
- EEM applet `P09_EEM_LOOP99_DOWN` is registered.
- Syslog destination is `10.1.99.51`.
- SNMP trap destination is registered.
- NetFlow export is enabled to `10.1.99.51:2055`.
- Ping from Loopback0 to HQ-SYSLOG succeeds.

## Optional SNMP Link Trap Hardening

If supported, make sure SNMP link-status traps are enabled on `Loopback99`.

```text
configure terminal
interface Loopback99
 snmp trap link-status
end
write memory
```

If the command is rejected, document the platform limitation and continue. The EEM/syslog part remains valid.

## Generate NetFlow Baseline Traffic

Before the failure, generate traffic that appears in `show ip cache flow`.

```text
ping 10.2.100.1 source 10.1.100.1 repeat 20
show ip cache flow
show ip flow export
```

Expected:

- `show ip cache flow` shows ICMP/Tunnel traffic.
- `show ip flow export` counters increase and show zero export failures.

## Failure Trigger

Trigger the controlled failure:

```text
configure terminal
interface Loopback99
shutdown
end
```

Wait 5 seconds.

Restore the test interface:

```text
configure terminal
interface Loopback99
no shutdown
end
write memory
```

## Post-Failure Verification On HQ-RTR1

```text
show logging | include P09_PHASE5|Loopback99|HA_EM|LINEPROTO|LINK
show event manager history events
show snmp
show ip flow export
show ip cache flow
```

Expected:

- Local syslog shows Loopback99 down/up.
- Local syslog shows EEM marker:
  `P09_PHASE5_EEM_LINK_DOWN_DETECTED on HQ-RTR1 Loopback99`
- EEM history shows the applet completed successfully.
- SNMP trap counters may increment if Loopback99 link-status traps are supported by this image.
- NetFlow export counters remain healthy with zero export failures.

## HQ-SYSLOG Collector Check

On HQ-SYSLOG output, look for:

```text
10.0.255.1
P09_PHASE5_EEM_LINK_DOWN_DETECTED
Loopback99
```

Expected:

- The EEM marker should arrive from `10.0.255.1`.
- Interface down/up syslog may also appear depending on trap severity and logging configuration.

## Completion Criteria

Phase 7 is complete when:

- `HQ-RTR1` local logging shows Loopback99 down/up.
- `HQ-RTR1` local logging shows EEM marker.
- `show event manager history events` shows successful EEM applet execution.
- HQ-SYSLOG receives the EEM marker from `10.0.255.1`.
- `show ip flow export` remains healthy with no export failures.
- SNMP collector limitation is documented; device-side SNMP state is captured.

## Notes

Because HQ-SYSLOG does not have SNMP trap or NetFlow collector services, this phase cannot honestly prove collector-side SNMP/NetFlow ingestion. The correct engineering answer is to document the limitation and use device-side verification.
