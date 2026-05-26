# Project 10 Phase 5 - AAA Accounting Verification Limited By TacPlus Node

## Status

AAA accounting is configured on `HQ-RTR1`, and an accounted administrator session was generated. Direct accounting-log verification cannot be performed because the `HQ-TACACS` TacPlus node in this CML topology does not provide an interactive console or runtime-log viewer.

## Accounting Configuration Verified

On `HQ-RTR1`:

```ios
aaa authentication login default group tacacs+ local
aaa authentication login CONSOLE local
aaa authorization exec default group tacacs+ local
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+
ip tacacs source-interface Loopback0
tacacs server HQ-TACACS
```

The required Phase 5 accounting statements are present:

```ios
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+
```

## Accounted Session Generated

From `HQ-DSW1`, a fresh TACACS+ SSH session was opened to `HQ-RTR1`:

```ios
ssh -l admin 10.0.255.1
```

Password used:

```text
chongong
```

The session received administrator privilege:

```text
HQ-RTR1#show privilege
Current privilege level is 15
```

Read-only commands executed in the session:

```ios
show privilege
show clock detail
show ip interface brief
show ip route
```

The session was closed fully:

```text
[Connection to 10.0.255.1 closed by foreign host]
```

This sequence was appropriate for generating exec START/STOP accounting records and, where supported by IOL/TacPlus, privilege-15 command accounting records.

## Supporting TACACS+ Status

After the accounted session, `HQ-RTR1` showed:

```text
Server name: HQ-TACACS
Server address: 10.1.99.52
Server port: 49
Socket opens: 81
Socket closes: 81
Socket errors: 0
Socket Timeouts: 0
Failed Connect Attempts: 0
Total Packets Sent: 95
Total Packets Recv: 95
Server Status: Alive
```

These counters confirm continued TACACS+ communication but are not accounting-specific proof.

## Server-Side Output Obtained

The available `HQ-TACACS` output shows that the `admin` user is being found and authorized for an exec shell at privilege level 15 from multiple network devices, including `HQ-RTR1`:

```text
login query for 'admin' port tty2 from 10.0.255.1 accepted
Start authorization request
do_author: user='admin'
exec authorization request for admin
server:priv-lvl=15 -> add priv-lvl=15
authorization query for 'admin' tty2 from 10.0.255.1 accepted
```

Similar accepted login/authorization activity appears from:

```text
10.0.255.3
10.0.255.2
10.1.99.12
10.2.99.2
10.1.99.13
```

This strengthens proof of centralized TACACS+ authentication and authorization, but the output does not show accounting `START`/`STOP` records or per-command accounting entries.

## Verification Limitation

The server configuration specifies:

```text
accounting file = /var/log/tacplus-acct.log
```

The accessible service output shows authentication and authorization debug messages, but no view of the accounting file from which to retrieve:

```sh
cat /var/log/tacplus-acct.log
```

Therefore, the expected accounting START/STOP or per-command records have not been directly retrieved from this node.

## Verdict

Phase 5 is documented as:

```text
Accounting configured and test activity generated; direct server-log proof unavailable due to TacPlus node console/log-access limitation.
```

The implementation is not misrepresented as fully log-verified.
