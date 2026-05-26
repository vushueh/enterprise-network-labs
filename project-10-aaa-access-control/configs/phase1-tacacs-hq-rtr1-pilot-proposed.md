# Project 10 - Phase 1 TACACS+ HQ-RTR1 Pilot Proposed Configuration

Status: CODEX-PROPOSED - pending test on HQ-RTR1 only
Date: 2026-05-22

## Phase Goal

Enable TACACS+ for network device administration with local fallback.

Start with `HQ-RTR1` only. Do not apply to the other devices until `HQ-RTR1` passes `test aaa` and login verification.

## TACACS+ Server

- Server name: `HQ-TACACS`
- IP: `10.1.99.52`
- TACACS+ key: `tacacs123`
- Test admin user: `tacadmin`
- Test admin password: `admin123`
- Test operator user: `tacoper`
- Test operator password: `oper123`

## Why Local Fallback Matters

The method list will be:

```text
aaa authentication login default group tacacs+ local
```

That means:

1. Try TACACS+ first.
2. If TACACS+ is unreachable, use the local username database.

This only protects the device if a local privilege 15 user exists before AAA is enabled.

## HQ-RTR1 Pre-Check

Run first:

```text
show running-config | include ^username|^aaa|^tacacs|line vty|login
ping 10.1.99.52 source 10.1.99.1
show users
```

Expected:

- Local `admin privilege 15` exists.
- `ping 10.1.99.52 source 10.1.99.1` succeeds.
- You are on console or have a safe active session.

## HQ-RTR1 Pilot Configuration

```text
! ============================================================
! DEVICE: HQ-RTR1 | PROJECT: 10 - AAA and Network Access Control
! PHASE: 1 - TACACS+ Device Administration Pilot
! ============================================================
enable
configure terminal

! --- Enable AAA ---
! WHY: Turns on IOS AAA method lists. This changes login behavior, so local
! fallback must already exist before this command is applied.
aaa new-model

! --- TACACS+ server definition ---
! WHY: Defines the central admin authentication server. The source interface
! makes TACACS traffic come from HQ-RTR1 Loopback0 for stable identity.
tacacs server HQ-TACACS
 address ipv4 10.1.99.52
 key tacacs123
 exit

ip tacacs source-interface Loopback0

! --- Login authentication ---
! WHY: Try TACACS+ first, then fall back to local user database if the server
! is unreachable. This prevents lockout during server failure.
aaa authentication login default group tacacs+ local

! --- Exec authorization ---
! WHY: Lets TACACS+ assign privilege level after login. Local fallback remains
! available if TACACS+ is unreachable.
aaa authorization exec default group tacacs+ local

! --- Command accounting for privilege 15 ---
! WHY: Sends privileged command audit records to TACACS+. This creates an
! admin action trail for troubleshooting and accountability.
aaa accounting commands 15 default start-stop group tacacs+

! --- Exec/session accounting ---
! WHY: Logs when admins start and stop device sessions.
aaa accounting exec default start-stop group tacacs+

! --- VTY lines use default AAA method list ---
! WHY: The default login method list above now controls VTY access.
line vty 0 4
 login authentication default
 authorization exec default
 transport input ssh
 exit

end
write memory
```

## Immediate Test

Run from `HQ-RTR1`:

```text
test aaa group tacacs+ tacadmin admin123 new-code
test aaa group tacacs+ tacoper oper123 new-code
show tacacs
show aaa servers
show running-config | include ^aaa|^tacacs|ip tacacs|line vty|authorization|accounting
```

Expected:

- `tacadmin` test succeeds.
- `tacoper` test succeeds.
- TACACS server shows reachable/activity.

## Login Test

Open a new SSH session to `HQ-RTR1` from a management host if available.

Test:

- `tacadmin / admin123` should receive privilege 15.
- Local `admin` should still work if TACACS is unreachable later.

Keep the console session open while testing.

## Emergency Rollback

If login behavior breaks while you still have console access:

```text
configure terminal
no aaa new-model
line vty 0 4
 login local
 no authorization exec default
end
write memory
```

This returns the device to local login behavior.
