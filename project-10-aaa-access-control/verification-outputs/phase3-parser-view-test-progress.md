# Project 10 Phase 3 - NOC-VIEW Test Progress

## Target

`HQ-RTR1`

## View Entry

`NOC-VIEW` was entered successfully:

```ios
enable view NOC-VIEW
show parser view
```

Result:

```text
Current view is 'NOC-VIEW'
```

## Allowed Commands Verified

The following permitted commands executed successfully inside `NOC-VIEW`:

```ios
show privilege
show version
show interfaces description
show ip route
show lldp neighbors
ping 10.1.99.52 source Loopback0 repeat 5
```

Ping result:

```text
Success rate is 100 percent (5/5)
```

## Denied Commands Verified

The following restricted commands were denied inside `NOC-VIEW`:

```ios
configure terminal
show running-config
reload
```

Each returned invalid-input output at the command position, confirming it is not available within the restricted view.

## Pending Retest

These two intended permitted commands were entered without the leading `s`:

```text
how ip interface brief
how cdp neighbors
```

Their failures are typing errors, not view failures. Retest using:

```ios
show ip interface brief
show cdp neighbors
```

