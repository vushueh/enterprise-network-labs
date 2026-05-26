# Project 10 Phase 2 - HQ-DSW1 Privilege Validation

## Status

Phase 2 privilege separation was validated on `HQ-DSW1`.

## Admin Test

Test from `HQ-RTR1`:

```ios
ssh -l admin 10.1.99.11
```

Password:

```text
chongong
```

Result:

```text
HQ-DSW1#
```

The `#` prompt confirms privilege level 15 for `admin`.

## Operator Test

Test from `HQ-RTR1`:

```ios
ssh -l tacoper 10.1.99.11
```

Password:

```text
oper123
```

Result:

```text
HQ-DSW1>show privilege
Current privilege level is 1
```

Configuration mode test:

```ios
HQ-DSW1>configure terminal
           ^
% Invalid input detected at '^' marker.
```

## Verdict

Privilege separation is working:

- `admin / chongong` receives privilege 15.
- `tacoper / oper123` receives privilege 1.
- `tacoper` cannot enter configuration mode.

