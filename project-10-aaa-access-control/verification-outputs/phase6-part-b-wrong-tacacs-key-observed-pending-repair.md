# Project 10 Phase 6 Part B - Wrong TACACS Key Break/Fix Complete

## Fault Applied

On `HQ-RTR1`, the TACACS shared key was temporarily changed while the local-protected console remained open:

```ios
tacacs server HQ-TACACS
 key P10-WRONG-KEY
```

The fault has not been saved.

## Diagnostics Enabled

```ios
terminal monitor
debug aaa authentication
debug tacacs
```

The router reported:

```text
AAA Authentication debugging is on
TACACS access control debugging is on
```

## Failure Evidence

With the wrong key configured:

```ios
test aaa group tacacs+ admin chongong new-code
```

```text
User rejected
```

`show tacacs` reported:

```text
Server address: 10.1.99.52
Total Packets Sent: 127
Total Packets Recv: 127
Server Status: Alive
Continous Authc fail count: 1
```

The TACACS server remains reachable, but authentication fails after the deliberate key mismatch. This is consistent with a shared-key authentication fault and supplies the break evidence for Part B.

## Repair Verified

The correct key was restored from the open protected console:

```ios
configure terminal
tacacs server HQ-TACACS
 key tacacs123
 exit
end
undebug all
```

The router confirmed debugging was disabled:

```text
All possible debugging has been turned off
```

After repair, TACACS authentication passed:

```ios
test aaa group tacacs+ admin chongong new-code
```

```text
User successfully authenticated
```

Final TACACS status:

```text
Server address: 10.1.99.52
Socket errors: 0
Socket Timeouts: 0
Failed Connect Attempts: 0
Total Packets Sent: 133
Total Packets Recv: 133
Server Status: Alive
Continous Authc fail count: 1
```

`Continous Authc fail count: 1` remains as historical evidence of the deliberate wrong-key test; the successful authentication and `Alive` server status confirm the active configuration is repaired.

The corrected configuration was saved with `write memory`.

## Current Status

Part B is complete. The shared-key fault was introduced, identified through TACACS authentication failure evidence, repaired, retested successfully, and saved.

