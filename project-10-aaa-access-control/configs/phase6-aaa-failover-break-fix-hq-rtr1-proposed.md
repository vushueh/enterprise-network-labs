# Project 10 Phase 6 - AAA Failover And Break/Fix Pilot On HQ-RTR1

## Review Status

Proposed plan only. Review before applying in CML.

## Scope

Perform Phase 6 on `HQ-RTR1` only while keeping its local-protected console session open.

Do not shut down `HQ-TACACS` globally because multiple completed devices depend on it. Do not test RADIUS failure behavior because Phase 4 802.1X was not implemented due to the IOL-L2 platform limitation.

## Important AAA Behavior

The active VTY authentication list is:

```ios
aaa authentication login default group tacacs+ local
```

Cisco IOS uses `local` only when the TACACS+ method returns an error or does not respond. If a reachable TACACS+ server explicitly rejects a login, authentication stops and does not fall back to the local user.

Therefore:

- Use an unreachable TACACS target to prove local fallback.
- Use a wrong TACACS shared key as a separate break/fix diagnosis test.

## Safety Preconditions

Run these on the `HQ-RTR1` console before introducing any fault:

```ios
enable
show running-config | include ^username|^aaa authentication|^aaa authorization|^ip tacacs
show running-config | section line con
show running-config | section tacacs
show tacacs
test aaa group tacacs+ admin chongong new-code
test aaa local auth default admin chongong
```

Expected:

```ios
username admin privilege 15 secret ...
aaa authentication login default group tacacs+ local
aaa authentication login CONSOLE local
aaa authorization exec default group tacacs+ local
ip tacacs source-interface Loopback0
line con 0
 login authentication CONSOLE
```

And:

```text
User successfully authenticated
Server Status: Alive
```

The last command is an additional local-password pre-check suggested during review:

```ios
test aaa local auth default admin chongong
```

If `HQ-RTR1` rejects this command syntax, paste the error and do not treat that as a credential failure. In that case, the console login itself is the local-password proof, but only if the console login was performed using `admin / chongong` after applying:

```ios
aaa authentication login CONSOLE local
line console 0
 login authentication CONSOLE
```

If a different local password was used at the console prompt, set the local fallback password to the intended credential before beginning Part A:

```ios
configure terminal
username admin privilege 15 secret chongong
end
write memory
```

Keep the console open for the whole exercise. Do not `write memory` while the deliberate failure is present.

## Part A - Prove Local Fallback With An Unreachable TACACS Target

### A1. Introduce A Fault Only On HQ-RTR1

On the open `HQ-RTR1` console, temporarily change the TACACS server target to an unused management address:

```ios
configure terminal
tacacs server HQ-TACACS
 no address ipv4 10.1.99.52
 address ipv4 10.1.99.250
 exit
end
show running-config | section tacacs
show tacacs
```

Do not save this fault.

### A2. Test Local Fallback From HQ-DSW1

From `HQ-DSW1`, SSH to `HQ-RTR1` using the local `admin` account credentials:

```ios
ssh -l admin 10.0.255.1
```

Password:

```text
chongong
```

Inside `HQ-RTR1`, run:

```ios
show privilege
exit
```

Expected:

```text
Current privilege level is 15
```

This is the local fallback proof because the configured TACACS target on `HQ-RTR1` cannot respond.

### A3. Capture Failed TACACS Status Before Restoring

Back on the still-open `HQ-RTR1` console, run before repairing the address:

```ios
show tacacs
```

Expected if supported by the image: `Socket Timeouts` and/or `Failed Connect Attempts` have increased, proving that IOS tried the unreachable TACACS server before falling back locally.

Observed on this IOL image: an SSH login can fall back successfully while `show tacacs` continues displaying the last-known `Alive` state and zero timeout/failure counters. If this occurs, document the limitation and use the active unreachable server address plus successful privilege-15 SSH session as the fallback evidence.

### A4. Restore TACACS Address Immediately

On the still-open `HQ-RTR1` console:

```ios
configure terminal
tacacs server HQ-TACACS
 no address ipv4 10.1.99.250
 address ipv4 10.1.99.52
 key tacacs123
 exit
end
test aaa group tacacs+ admin chongong new-code
show tacacs
```

Expected:

```text
User successfully authenticated
Server Status: Alive
```

Do not begin Part B unless TACACS authentication is restored.

## Part B - Break/Fix Challenge: Wrong TACACS Shared Key

### B1. Turn On Diagnostic Output

On the `HQ-RTR1` console:

```ios
terminal monitor
debug aaa authentication
debug tacacs
```

If either debug command is rejected, continue using `test aaa` and `show tacacs`, and paste the error.

### B2. Introduce The Wrong Key

On `HQ-RTR1`:

```ios
configure terminal
tacacs server HQ-TACACS
 key P10-WRONG-KEY
 exit
end
test aaa group tacacs+ admin chongong new-code
show tacacs
```

Expected:

- The TACACS test does not authenticate successfully.
- Debug or TACACS status output indicates the TACACS exchange failed.

Do not use this wrong-key test as proof that local fallback works.

### B3. Repair The Shared Key

On the same console:

```ios
configure terminal
tacacs server HQ-TACACS
 key tacacs123
 exit
end
undebug all
test aaa group tacacs+ admin chongong new-code
show tacacs
write memory
```

Expected:

```text
User successfully authenticated
Server Status: Alive
```

## Phase 6 Evidence To Capture

Paste:

1. Safety-precheck output.
2. Local credential pre-check result, or unsupported-command output with existing console-local proof.
3. Part A temporary TACACS server address output.
4. SSH local fallback proof at privilege 15.
5. `show tacacs` before restoring, showing timeout/failure activity.
6. Restored TACACS test after Part A.
7. Wrong-key failing `test aaa` output and any useful debug lines.
8. Corrected-key successful `test aaa` output and final `show tacacs`.

## Rollback

If you lose confidence during either test, from the open local-protected console run:

```ios
configure terminal
tacacs server HQ-TACACS
 no address ipv4 10.1.99.250
 address ipv4 10.1.99.52
 key tacacs123
 exit
end
undebug all
test aaa group tacacs+ admin chongong new-code
show tacacs
write memory
```

## Source Rationale

Cisco documentation distinguishes an authentication `FAIL` from an `ERROR`: the next method such as `local` is attempted only if the prior method does not respond or returns an error, not when a reachable server rejects authentication.

- https://www.cisco.com/c/en/us/support/docs/security-vpn/terminal-access-controller-access-control-system-tacacs-/200606-aaa-authentication-login-default-local.html
- https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_usr_aaa/configuration/xe-3s/sec-usr-aaa-xe-3s-book/sec-cfg-authentifcn.html
