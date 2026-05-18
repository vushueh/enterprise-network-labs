# Project 09 - Phase 6 Archive All IOS Devices Summary

Date: 2026-05-17

## Result

IOS configuration archive is enabled and verified on all nine in-scope IOS/IOL devices.

## Working Archive Configuration

```text
archive
 path unix:/P09-ARCHIVE-$h-
 maximum 5
 write-memory
```

## Device Verification

| Device | Archive Path | Saved Archives |
| --- | --- | --- |
| HQ-RTR1 | `unix:/P09-ARCHIVE-HQ-RTR1--<timestamp>` | 2 |
| BR-RTR1 | `unix:/P09-ARCHIVE-BR-RTR1--<timestamp>` | 2 |
| WAN-RTR1 | `unix:/P09-ARCHIVE-WAN-RTR1--<timestamp>` | 2 |
| HQ-DSW1 | `unix:/P09-ARCHIVE-HQ-DSW1--<timestamp>` | 2 |
| HQ-DSW2 | `unix:/P09-ARCHIVE-HQ-DSW2--<timestamp>` | 2 |
| BR-DSW1 | `unix:/P09-ARCHIVE-BR-DSW1--<timestamp>` | 2 |
| HQ-ASW1 | `unix:/P09-ARCHIVE-HQ-ASW1--<timestamp>` | 2 |
| HQ-ASW2 | `unix:/P09-ARCHIVE-HQ-ASW2--<timestamp>` | 2 |
| BR-ASW1 | `unix:/P09-ARCHIVE-BR-ASW1--<timestamp>` | 4 |

## Platform Lesson

The CML IOL/IOL-L2 images used here do not expose `flash:` as the local writable archive filesystem.

`show file systems` and `archive path ?` showed `unix:` as a valid writable local filesystem. The corrected archive path is:

```text
path unix:/P09-ARCHIVE-$h-
```

## Remaining Phase 6 Item

Practice rollback on `HQ-RTR1` with `configure replace` using the most recent archive file.
