# Project 10 Phase 5 - Review Items Incorporated

## Status

Phase 5 plan updated based on review items P10-15 through P10-18.

## Adjustments

- TACACS packet-counter increases are supporting context only, not accounting proof.
- The SSH test session must be exited fully before checking for START/STOP accounting records.
- Accounting-log inspection should be performed directly on the `HQ-TACACS` console:

```sh
ls -la /var/log/tacplus*
cat /var/log/tacplus-acct.log
```

- On IOL, an exec accounting START/STOP record is sufficient proof if per-command accounting records do not appear.

