# Safe Standard Config Template

This is the approval-gated configuration standard for Project 13. The first
live push should use the unused marker ACL only. The broader standard is kept
as a reviewed template so automation does not blindly rewrite the lab.

## Phase 6A — Safe Marker Only

```ios
configure terminal
ip access-list standard P13-AUTOMATION-MARKER
 remark Project 13 automation safe marker on <DEVICE>
 remark ACL is intentionally unused and has no packet-forwarding effect
end
write memory
```

Rollback:

```ios
configure terminal
no ip access-list standard P13-AUTOMATION-MARKER
end
write memory
```

## Phase 6B — Proposed Standard IOS Config

Apply only after read-only collection, redacted backup, and compliance reports
are clean.

```ios
configure terminal
service timestamps log datetime msec localtime show-timezone
ip ssh version 2
logging host 10.1.99.51
logging trap warnings
ntp server 10.0.255.1
archive
 path unix:/P13-ARCHIVE-$h
 write-memory
end
write memory
```

## Why This Is Split

The reference project asks for a configuration push across the device fleet.
That is the correct skill to demonstrate, but the safe engineering sequence is:

1. prove inventory and reachability;
2. collect read-only baselines;
3. back up configs;
4. check compliance;
5. dry-run generated commands;
6. apply a low-risk marker;
7. expand to standards only after the reports are clean.

This makes the project credible because it shows automation discipline, not
just fast typing.
