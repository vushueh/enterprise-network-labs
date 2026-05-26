# Project 10 Phase 3 - Parser View Pilot on HQ-RTR1

## Status Before Phase 3

Phase 2 was proven on `HQ-RTR1` and `HQ-DSW1`. Remaining Phase 2 per-device operator validation is deferred by choice while moving to Phase 3.

## Goal

Create a limited `NOC-VIEW` on `HQ-RTR1` that allows operational visibility commands without configuration access.

This first pilot does not modify TACACS+ user assignment. The current working logins remain:

```text
admin / chongong    -> TACACS+ administrator
tacoper / oper123   -> TACACS+ privilege 1 operator
```

## Pre-Check

Run on the `HQ-RTR1` console:

```ios
show running-config | include ^aaa new-model|^enable secret|^parser view
show privilege
```

Parser views require `aaa new-model` and an enable secret. If no `enable secret` is shown, stop and configure one before continuing.

## Enter Root View

Run on `HQ-RTR1`:

```ios
enable view
```

Enter the existing enable secret when prompted.

Verify:

```ios
show parser view
```

Expected result: root view is active.

## Configure NOC-VIEW

From root view on `HQ-RTR1`:

```ios
configure terminal
parser view NOC-VIEW
 secret 0 NOCview2026
 commands exec include show privilege
 commands exec include show version
 commands exec include show ip interface brief
 commands exec include show interfaces description
 commands exec include show ip route
 commands exec include show cdp neighbors
 commands exec include show lldp neighbors
 commands exec include all ping
 commands exec include exit
end
write memory
```

From root view, verify the configured view and permitted command list before entering it:

```ios
show parser view all
```

If IOS rejects an individual `commands exec include` command, stop and paste the error; parser view syntax support can vary by image.

## Test NOC-VIEW

From the open `HQ-RTR1` console:

```ios
enable view NOC-VIEW
```

Password:

```text
NOCview2026
```

Run permitted commands:

```ios
show privilege
show ip interface brief
show interfaces description
show ip route
show cdp neighbors
ping 10.1.99.52 source Loopback0 repeat 5
```

Run denied commands:

```ios
configure terminal
show running-config
reload
```

Expected:

- Permitted show/ping commands execute.
- Configuration, running configuration access, and reload are denied/unavailable.

Exit the view:

```ios
exit
```

## Important Boundary

Do not modify `HQ-TACACS` to assign `tacoper` to `NOC-VIEW` yet. First prove the local parser view works on this IOS image; TACACS-to-view integration is the next controlled step.

## Source Note

Cisco documents `show parser view all` for listing views from root view and the optional `all` keyword for including command sub-options in a CLI view:

- https://www.cisco.com/en/US/docs/ios/12_3t/12_3t7/feature/guide/gtclivws.html
