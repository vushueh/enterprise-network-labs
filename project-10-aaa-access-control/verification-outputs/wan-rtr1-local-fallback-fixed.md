# Project 10 - WAN-RTR1 Local Fallback Fixed

Date: 2026-05-22

## Result

`WAN-RTR1` now has a local privilege 15 fallback user and VTY lines use `login local`.

## Configuration Proof

```text
username admin privilege 15 secret 9 ...
line vty 0 4
 login local
```

## Interpretation

This removes the main lockout risk found during the Project 10 Phase 1 pre-check.

AAA can now be piloted safely on `HQ-RTR1`, then expanded only after TACACS+ testing succeeds.
