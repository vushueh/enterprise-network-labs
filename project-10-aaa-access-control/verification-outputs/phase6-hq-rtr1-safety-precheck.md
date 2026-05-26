# Project 10 Phase 6 - HQ-RTR1 Safety Pre-Check

## Result

Phase 6 pre-check passed with one platform syntax limitation. No failover fault has been introduced yet.

## Verified On HQ-RTR1

The local privilege-15 safety user exists:

```ios
username admin privilege 15 secret 9 ...
```

Console access is protected by a local-only AAA method list:

```ios
aaa authentication login CONSOLE local
line con 0
 login authentication CONSOLE
```

Remote administrative access currently uses TACACS+ with local fallback:

```ios
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
ip tacacs source-interface Loopback0
tacacs server HQ-TACACS
 address ipv4 10.1.99.52
```

## Healthy TACACS Baseline

Before failover testing:

```text
Server address: 10.1.99.52
Socket Timeouts: 0
Failed Connect Attempts: 0
Total Packets Sent: 105
Total Packets Recv: 105
Server Status: Alive
```

TACACS authentication succeeded:

```ios
test aaa group tacacs+ admin chongong new-code
```

```text
User successfully authenticated
```

## Local Test Syntax Limitation

The review-requested command is not supported on this IOL image:

```ios
test aaa local auth default admin chongong
```

```text
% Invalid input detected at '^' marker.
```

This is a command-support limitation, not an authentication failure. Before the temporary TACACS outage test, confirm that the successful console login used the intended local credential `admin / chongong`, or explicitly reset the local `admin` secret to `chongong`.

## Local Fallback Password Confirmed

The local safety credential was explicitly set on `HQ-RTR1` and saved:

```ios
configure terminal
username admin privilege 15 secret chongong
end
write memory
```

The unused fault target was checked from the router management source:

```ios
ping 10.1.99.250 source Loopback0 repeat 3
```

```text
Success rate is 0 percent (0/3)
```

`10.1.99.250` is suitable for the temporary unreachable-TACACS test.
