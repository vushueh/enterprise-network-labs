# Project 09 - Phase 6 Archive BR-ASW1 Verification Summary

Date: 2026-05-17

## Result

`BR-ASW1` configuration archive is enabled and verified.

## Platform Discovery

`BR-ASW1` does not have a `flash:` filesystem. `show file systems` showed writable local filesystems including `unix:`, `disk0:`, and `disk1:`.

`archive path ?` confirmed that `unix:` is valid.

## Working Configuration

```text
archive
 path unix:/P09-ARCHIVE-$h-
 maximum 5
 write-memory
```

## Verification

`show archive`:

```text
The maximum archive configurations allowed is 5.
There are currently 2 archive configurations saved.
The next archive file will be named unix:/P09-ARCHIVE-BR-ASW1--<timestamp>-2
 Archive #  Name
   1        unix:/P09-ARCHIVE-BR-ASW1--May-17-23-28-37.582-UTC-0
   2        unix:/P09-ARCHIVE-BR-ASW1--May-17-23-28-38.309-UTC-1 <- Most Recent
```

`dir unix: | include P09-ARCHIVE`:

```text
P09-ARCHIVE-BR-ASW1--May-17-23-28-38.309-UTC-1
P09-ARCHIVE-BR-ASW1--May-17-23-28-37.582-UTC-0
```

## Lesson

Use `unix:/P09-ARCHIVE-$h-` for these CML IOL/IOL-L2 devices unless a device-specific `show file systems` output proves a different local filesystem should be used.
