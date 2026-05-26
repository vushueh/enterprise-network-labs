# Project 10 Phase 3 - Parser View Pre-Check

## HQ-RTR1 Pre-Check

The prerequisite check passed:

```ios
show running-config | include ^aaa new-model|^enable secret|^parser view
```

Result:

```text
aaa new-model
enable secret 9 ...
```

Privilege before entering root view:

```ios
show privilege
```

Result:

```text
Current privilege level is 15
```

Root view entry succeeded:

```ios
enable view
Password:
HQ-RTR1#
```

## Review Adjustment

Before applying the Phase 3 pilot, the proposed configuration was revised to:

- Use `show parser view all` after configuration.
- Use `commands exec include all ping` so the permitted ping test can include `source` and `repeat` options.

