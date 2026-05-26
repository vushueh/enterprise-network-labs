# Project 10 Phase 5 - AAA Accounting Verification On HQ-RTR1

## Goal

Verify that TACACS+ records administrator logins and privilege-15 commands from `HQ-RTR1`.

## Current Configuration Already Applied

Phase 1 already configured the accounting statements on `HQ-RTR1`:

```ios
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+
```

No new accounting configuration should be added unless the pre-check shows those lines are missing.

## Step 1 - Verify Accounting Configuration On HQ-RTR1 Console

Run on `HQ-RTR1` console:

```ios
enable
show running-config | include ^aaa accounting|^aaa authentication|^aaa authorization|^ip tacacs|^tacacs
show tacacs
```

Expected:

```ios
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+
```

and TACACS server status `Alive`.

## Step 2 - Generate An Accounted TACACS+ Admin Session

From `HQ-DSW1`, open a fresh SSH session to `HQ-RTR1`:

```ios
ssh -l admin 10.0.255.1
```

Password:

```text
chongong
```

Inside the SSH session on `HQ-RTR1`, run privileged read-only commands:

```ios
show privilege
show clock detail
show ip interface brief
show ip route
show tacacs
exit
```

This should generate:

- An exec accounting start record when `admin` logs in.
- Privilege-15 command accounting records for the commands.
- An exec accounting stop record when the SSH session closes.

Wait until the originating console displays the session-close confirmation:

```text
[Connection to 10.0.255.1 closed by foreign host]
```

Only after that confirmation proceed to accounting-log inspection, so both START and STOP records have had a chance to be written.

## Step 3 - Capture Supporting Router-Side TACACS Activity

Back on the `HQ-RTR1` console, run:

```ios
show tacacs
```

Record whether `Total Packets Sent` and `Total Packets Recv` increased after the SSH session.

This is supporting context only. TACACS counters combine authentication, authorization, and accounting traffic, so they do not prove accounting by themselves.

## Step 4 - Verify Accounting Records On HQ-TACACS

The TacPlus configuration names the accounting file:

```text
accounting file = /var/log/tacplus-acct.log
```

On the `HQ-TACACS` console, first confirm the available log path:

```sh
ls -la /var/log/tacplus*
```

Then read the configured accounting log:

```sh
cat /var/log/tacplus-acct.log
```

Optional live inspection for a second test:

```sh
tail -f /var/log/tacplus-acct.log
```

Look for:

```text
admin
HQ-RTR1 or 10.0.255.1
START
STOP
show clock detail
show ip interface brief
show ip route
```

On IOL, individual privilege-15 command records may not appear reliably. A matching exec session START/STOP record for `admin` is sufficient Phase 5 evidence; individual command records are additional evidence.

If the file does not exist, paste the result from `ls -la /var/log/tacplus*` so we can identify the actual path.

## Pass Criteria

Phase 5 passes if:

- The two `aaa accounting` lines are present on `HQ-RTR1`.
- `HQ-TACACS` accounting records show an `admin` exec START/STOP session or privilege-15 command records.
- TACACS packet counter change is retained only as supporting context.

## No-Risk Boundary

Use read-only commands for the accounting test. No production-style configuration changes are needed to prove command accounting.
