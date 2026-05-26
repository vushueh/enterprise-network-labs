# Project 10 Phase 2 - Privilege Validation Progress

## Current Status

Phase 2 validates that the preferred administrator account uses TACACS+ at privilege level 15, while the operator account remains at privilege level 1 and cannot configure devices.

## Confirmed Accounts

```text
admin / chongong     -> TACACS+ netadmin, privilege 15
tacoper / oper123    -> TACACS+ netoper, privilege 1
```

## Validation Results

| Device | Admin SSH | Operator Privilege/Restriction | Status |
|---|---|---|---|
| HQ-RTR1 | `HQ-RTR1#` reached from HQ-DSW1 | Privilege 1; `configure terminal` denied | Complete |
| HQ-DSW1 | `HQ-DSW1#` reached from HQ-RTR1 | Privilege 1; `configure terminal` denied | Complete |
| WAN-RTR1 | `WAN-RTR1#` reached from HQ-RTR1 | Pending Phase 2 operator retest | In progress |
| BR-RTR1 | `BR-RTR1#` reached from HQ-RTR1 | Pending Phase 2 operator retest using preferred admin baseline | In progress |
| HQ-DSW2 | `HQ-DSW2#` reached from HQ-RTR1 | Pending Phase 2 operator retest | In progress |
| BR-DSW1 | `BR-DSW1#` reached from HQ-RTR1 | Pending Phase 2 operator retest | In progress |
| HQ-ASW1 | `HQ-ASW1#` reached from HQ-RTR1 | Pending Phase 2 operator retest | In progress |

## Console Safety Confirmation

The following TACACS-enabled devices now have local-only console authentication confirmed:

```ios
aaa authentication login CONSOLE local
line console 0
 login authentication CONSOLE
```

Devices confirmed:

```text
HQ-RTR1
WAN-RTR1
BR-RTR1
HQ-DSW1
HQ-DSW2
BR-DSW1
HQ-ASW1
```

## Address Correction

`BR-DSW1` is reached at:

```text
10.2.99.2
```

The attempted address `10.1.99.2` was not a target in this validation.

