# Project 10 - Phase 1 TACACS+ Pre-Check Summary

Date: 2026-05-22

## Result

Do not enable TACACS+ yet.

All tested network devices failed to reach the planned TACACS+ server at `10.1.99.52`.

## Reachability Test

`ping 10.1.99.52` failed from:

- HQ-RTR1
- BR-RTR1
- WAN-RTR1
- HQ-DSW1
- HQ-DSW2
- BR-DSW1
- HQ-ASW1
- HQ-ASW2
- BR-ASW1

## AAA State

Most devices currently show:

```text
no aaa new-model
line vty 0 4
 login local
```

Local fallback user `admin privilege 15` exists on most devices.

Exception/risk:

- WAN-RTR1 shows `line vty 0 4` with `login` but no local username in the pasted filter output. Before any AAA work, WAN-RTR1 needs a local fallback user and `login local`.

## Interpretation

TACACS+ server reachability is not ready. The likely causes are:

- HQ-TACACS node is not added, powered on, or connected.
- HQ-TACACS is not on VLAN 999.
- HQ-TACACS does not have IP `10.1.99.52`.
- Switch access port/VLAN for HQ-TACACS is missing or wrong.
- The TacPlus service is not running on the server.

## Next Step

Troubleshoot HQ-TACACS server/node reachability before applying AAA.
