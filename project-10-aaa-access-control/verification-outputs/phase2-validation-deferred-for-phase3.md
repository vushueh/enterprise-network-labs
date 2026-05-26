# Project 10 Phase 2 - Deferred Validation Note

Phase 2 privilege separation was fully demonstrated on the pilot path:

- `admin / chongong` received administrator access through TACACS+.
- `tacoper / oper123` received privilege level 1.
- `tacoper` could not enter configuration mode on `HQ-DSW1`.
- `HQ-RTR1` operator behavior was also validated.

Per-device operator restriction re-tests for `WAN-RTR1`, `BR-RTR1`, `HQ-DSW2`, `BR-DSW1`, and `HQ-ASW1` were deferred while proceeding to Phase 3.

This is an evidence gap only; TACACS+ Phase 1 authentication and SSH rollout on those devices was already verified.

