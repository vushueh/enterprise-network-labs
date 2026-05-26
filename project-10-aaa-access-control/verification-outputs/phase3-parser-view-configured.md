# Project 10 Phase 3 - Parser View Configured

## Target

`HQ-RTR1`

## Root View Confirmation

```ios
show parser view
```

Result:

```text
Current view is 'root'
```

## NOC-VIEW Configuration

The parser view configuration was accepted:

```ios
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
```

## Informational Messages

IOS generated a warning because the CLI view password was entered as a type 0 secret:

```text
WARNING: CLI-VIEW secret command has been added to the configuration using a type 0 secret.
```

This does not block the Phase 3 functionality test.

IOS rejected this command:

```ios
commands exec include exit
```

with:

```text
% Addition/Deletion of default commands not possible
```

This is expected because `exit` is already available as a default parser-view command.

## View Presence Verification

```ios
show parser view all
```

Result:

```text
Views/SuperViews Present in System:
 NOC-VIEW
-------(*) represent superview-------
```

## Next Test

Enter `NOC-VIEW` and verify permitted monitoring commands work while configuration and sensitive commands are denied.

