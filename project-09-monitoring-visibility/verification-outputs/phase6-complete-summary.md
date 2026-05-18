# Project 09 - Phase 6 Complete Summary

Date: 2026-05-17

## Result

Phase 6 is complete.

Configuration archive is enabled and verified on all nine IOS/IOL devices, and rollback was successfully practiced on `HQ-RTR1`.

## Archive Configuration

All in-scope IOS/IOL devices use:

```text
archive
 path unix:/P09-ARCHIVE-$h-
 maximum 5
 write-memory
```

## Devices Verified

- HQ-RTR1
- BR-RTR1
- WAN-RTR1
- HQ-DSW1
- HQ-DSW2
- BR-DSW1
- HQ-ASW1
- HQ-ASW2
- BR-ASW1

Each device showed archive configuration under running config and saved archive files under `unix:`.

## Platform Discovery

The CML IOL/IOL-L2 images do not expose `flash:`. The correct local writable archive filesystem is `unix:`.

## HQ-RTR1 Rollback Practice

Archive used:

```text
unix:/P09-ARCHIVE-HQ-RTR1--May-17-23-30-15.736-UTC-1
```

Temporary bad change:

```text
interface Loopback99
 description P09-PHASE6-BAD-CHANGE-ROLLBACK-TEST
```

Rollback command:

```text
configure replace unix:/P09-ARCHIVE-HQ-RTR1--May-17-23-30-15.736-UTC-1 force
```

Rollback result:

```text
Total number of passes: 1
Rollback Done
```

Post-rollback interface state:

```text
interface Loopback99
 description P09-PHASE5-EEM-TEST-INTERFACE
 ip address 10.255.99.99 255.255.255.255
```

Log proof:

```text
%SYS-5-CONFIG_R: Config Replace is Done
%SYS-5-CONFIG_P: Configured programmatically by process Exec from console as admin on console
```

## Interpretation

The lab now has local rollback insurance before later monitoring verification and troubleshooting phases. `configure replace` was validated with a harmless interface description change, proving the archive can restore a known-good configuration.

## HQ-FW1 Note

HQ-FW1 is ASAv and was excluded from IOS `archive` / `configure replace`. ASA config should continue to be saved with `write memory` and documented separately.
