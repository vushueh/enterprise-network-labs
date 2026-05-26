# Project 10 Phase 3 - Parser View Pilot Complete

## Target

`HQ-RTR1`

## Objective

Create and verify a restricted CLI parser view named `NOC-VIEW` that allows operational visibility but blocks configuration and disruptive commands.

## Prerequisites Verified

```ios
aaa new-model
enable secret 9 ...
```

Root view access succeeded:

```ios
enable view
show parser view
```

Result:

```text
Current view is 'root'
```

## Parser View Configuration

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

The attempt to add `exit` was rejected because it is already a default parser-view command:

```text
% Addition/Deletion of default commands not possible
```

View presence was verified from root view:

```ios
show parser view all
```

Result:

```text
Views/SuperViews Present in System:
 NOC-VIEW
```

## NOC-VIEW Entry

```ios
enable view NOC-VIEW
show parser view
```

Result:

```text
Current view is 'NOC-VIEW'
```

## Permitted Commands Verified

The following commands executed successfully within `NOC-VIEW`:

```ios
show privilege
show version
show ip interface brief
show interfaces description
show ip route
show cdp neighbors
show lldp neighbors
ping 10.1.99.52 source Loopback0 repeat 5
```

Extended ping result:

```text
Success rate is 100 percent (5/5)
```

## Restricted Commands Verified

The following commands were denied inside `NOC-VIEW`:

```ios
configure terminal
show running-config
reload
```

Each returned an invalid-input result, confirming the restricted view blocks configuration access and disruptive reload operations.

## Verdict

Project 10 Phase 3 parser view pilot on `HQ-RTR1` is complete and verified.

The parser view is locally proven. Mapping a TACACS+ operator directly into `NOC-VIEW` remains a future integration step and was intentionally not introduced during this pilot.

