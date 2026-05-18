# Project 09 - Phase 6 Configuration Archive And Rollback

Status: CODEX-PROPOSED - pending Claude review
Date: 2026-05-17

## Phase Goal

Enable local IOS configuration archive so every `write memory` creates a recoverable configuration snapshot.

Then practice `configure replace` on `HQ-RTR1` using a harmless test change.

## In Scope

Apply IOS archive to:

- HQ-RTR1
- BR-RTR1
- WAN-RTR1
- HQ-DSW1
- HQ-DSW2
- BR-DSW1
- HQ-ASW1
- HQ-ASW2
- BR-ASW1

Documented exclusion:

- HQ-FW1 is ASAv. It does not use IOS `archive` / `configure replace` in the same way. For this phase, verify and save ASA config with `write memory`; ASA backup/restore can be handled separately in documentation.

## Why These Commands Matter

- `archive`: enters IOS configuration archive mode.
- `path unix:/P09-ARCHIVE-$h-`: stores local snapshots on the writable local `unix:` filesystem and includes the hostname in the filename.
- `write-memory`: automatically archives the config every time you save.
- `maximum 5`: keeps the most recent five snapshots so flash does not fill up.
- `archive config`: manually creates a snapshot on demand.
- `show archive`: proves archive is enabled and lists available rollback points.
- `configure replace ... force`: restores a saved snapshot without interactive prompts.

## Pre-Check On Each IOS Device

Run before configuring archive:

```text
show running-config | section archive
dir flash:
show file systems
```

Expected:

- No conflicting existing archive config, or document it before replacing.
- A writable local filesystem exists. In this CML IOL image, `flash:` is not present; use `unix:`.

## Shared IOS Configuration

Apply this to each in-scope IOS/IOL device:

```text
! ============================================================
! DEVICE: <DEVICE-NAME> | PROJECT: 09 - Monitoring and Visibility
! PHASE: 6 - Configuration Archive
! ============================================================
enable
configure terminal

! --- Local configuration archive ---
! WHY: Creates a local rollback point whenever the running config is saved.
! This gives us recovery insurance before future monitoring/AAA/QoS changes.
archive
 path unix:/P09-ARCHIVE-$h-
 write-memory
 maximum 5
 exit

end
write memory

! --- Manual baseline snapshot ---
! WHY: Forces an immediate archive file now instead of waiting for a future save.
archive config
```

## Verify On Each IOS Device

```text
show running-config | section archive
show archive
dir unix: | include P09-ARCHIVE
```

Expected:

- Archive path is `unix:/P09-ARCHIVE-$h-`.
- `write-memory` is present under archive.
- `maximum 5` is present.
- `show archive` lists at least one archived config.
- `dir unix:` shows at least one `P09-ARCHIVE-<hostname>-...` file.

## HQ-RTR1 Rollback Practice

Do this only after archive is verified on `HQ-RTR1`.

### 1. Identify Current Archive File

```text
show archive
```

Copy the newest archive path. It will look similar to:

```text
unix:/P09-ARCHIVE-HQ-RTR1-<number>
```

### 2. Make A Harmless Bad Change

```text
configure terminal
interface Loopback99
 description P09-PHASE6-BAD-CHANGE-ROLLBACK-TEST
end
show running-config interface Loopback99
```

Expected:

- Loopback99 description shows the temporary bad-change text.

### 3. Roll Back To The Archive

Replace `<ARCHIVE-FILE>` with the archive filename copied from `show archive`.

```text
configure replace <ARCHIVE-FILE> force
```

Example:

```text
configure replace unix:/P09-ARCHIVE-HQ-RTR1-1 force
```

### 4. Verify Rollback

```text
show running-config interface Loopback99
show archive
show logging | include CONFIG|ARCHIVE|P09
```

Expected:

- The temporary bad description is gone.
- The previous Loopback99 description is restored.
- Router remains reachable.
- Archive list still exists.

## Optional Cleanup After Rollback Practice

If `Loopback99` is only being kept for the EEM phase, leave it in place until Phase 7 correlation is complete. If you decide to remove it later:

```text
configure terminal
no interface Loopback99
end
write memory
archive config
```

Do not remove it before Phase 7 if you want to reuse the EEM trigger.

## HQ-FW1 Documentation Check

Run on the ASA:

```text
show running-config | include archive|configure replace
show startup-config | include hostname|logging|snmp-server|ntp
write memory
```

Expected:

- No IOS-style archive feature.
- Startup config includes saved Phase 1, 2, and 4 monitoring settings.
