# Project 10 Phase 1 - TACACS+ Rollout Status

## Current Status

| Device | Phase A | Phase B | SSH Admin Test | SSH Operator Test | Notes |
|---|---|---|---|---|---|
| HQ-RTR1 | Passed | Passed | Passed | Passed | Pilot complete |
| WAN-RTR1 | Passed | Passed | Passed | Passed | SSH keys/domain fixed; console-local safeguard verified |
| BR-RTR1 | Passed | Passed | Passed | Passed | Verified from HQ-RTR1 |
| HQ-DSW1 | Passed | Passed | Passed | Passed | Console-local safeguard verified; tested from HQ-RTR1 |
| HQ-DSW2 | Passed | Passed | Passed | Passed | Console-local safeguard verified; tested from HQ-RTR1 |
| BR-DSW1 | Passed | Passed | Passed | Passed | Console-local safeguard added, verified from BR-RTR1 |
| HQ-ASW1 | Passed | Passed | Passed | Passed | Console-local safeguard verified; tested from HQ-RTR1 |
| HQ-ASW2 | Pending | Pending | Pending | Pending | Not started |
| BR-ASW1 | Pending | Pending | Pending | Pending | Not started |
| HQ-FW1 | Not included | Not included | Not included | Not included | ASA syntax is separate |

## WAN-RTR1 Evidence

WAN-RTR1 pre-check passed:

- Local fallback user exists: `username admin privilege 15 secret ...`
- Ping to `10.1.99.52` sourced from `Loopback0` passed 5/5

WAN-RTR1 TACACS+ tests passed:

```text
test aaa group tacacs+ tacadmin admin123 new-code
User successfully authenticated

test aaa group tacacs+ tacoper oper123 new-code
User successfully authenticated
```

WAN-RTR1 `show tacacs` confirmed:

- Server name: `HQ-TACACS`
- Server address: `10.1.99.52`
- Server status: `Alive`
- Socket errors: `0`
- Socket timeouts: `0`
- Failed connect attempts: `0`

Initial SSH failed because `WAN-RTR1` had no domain name and no RSA keys:

```text
SSH Disabled - version 2.0
Please create EC or RSA keys to enable SSH
IOS Keys in SECSH format(ssh-rsa, base64 encoded): NONE
```

Fix applied:

```ios
configure terminal
ip domain name lab.local
crypto key generate rsa general-keys modulus 2048
ip ssh version 2
end
write memory
```

WAN-RTR1 SSH tests passed from `HQ-RTR1`:

```text
ssh -l tacadmin 10.0.255.3
WAN-RTR1#show privilege
Current privilege level is 15
```

```text
ssh -l tacoper 10.0.255.3
WAN-RTR1>show privilege
Current privilege level is 1
```

## HQ-RTR1 Console Safeguard

HQ-RTR1 console also used the default TACACS+ method after `aaa new-model`, causing local `admin` console login to fail while TACACS login worked. Console was protected with:

```ios
aaa authentication login CONSOLE local
line con 0
 login authentication CONSOLE
```

## Console Safeguard Coverage

Local-only console authentication is confirmed on:

```text
HQ-RTR1
WAN-RTR1
BR-RTR1
HQ-DSW1
HQ-DSW2
BR-DSW1
HQ-ASW1
```

## Note

HQ-RTR1 was already complete. Reapplying the same Phase A and Phase B commands did not change the result, but it was not necessary.

## BR-RTR1 Evidence

BR-RTR1 pre-check passed:

- Local fallback user exists: `username admin privilege 15 secret ...`
- Ping to `10.1.99.52` sourced from `Loopback0` passed 5/5
- SSH was already enabled with RSA keys present

BR-RTR1 TACACS+ tests passed:

```text
test aaa group tacacs+ tacadmin admin123 new-code
User successfully authenticated

test aaa group tacacs+ tacoper oper123 new-code
User successfully authenticated
```

BR-RTR1 `show tacacs` confirmed:

- Server name: `HQ-TACACS`
- Server address: `10.1.99.52`
- Server status: `Alive`
- Socket errors: `0`
- Socket timeouts: `0`
- Failed connect attempts: `0`

BR-RTR1 SSH tests passed from `HQ-RTR1`:

```text
ssh -l tacadmin 10.0.255.2
BR-RTR1#show privilege
Current privilege level is 15
```

```text
ssh -l tacoper 10.0.255.2
BR-RTR1>show privilege
Current privilege level is 1
```

BR-RTR1 console safeguard added after discovering that the console used the default TACACS+ method after `aaa new-model`:

```ios
aaa authentication login CONSOLE local
line con 0
 login authentication CONSOLE
```

This keeps console access local while VTY SSH uses TACACS+.

## HQ-DSW1 Evidence

HQ-DSW1 pre-check passed:

- Local fallback user exists: `username admin privilege 15 secret ...`
- Ping to `10.1.99.52` sourced from `Vlan999` passed 5/5 after ARP warm-up
- SSH was already enabled with RSA keys present

HQ-DSW1 TACACS+ tests passed:

```text
test aaa group tacacs+ tacadmin admin123 new-code
User successfully authenticated

test aaa group tacacs+ tacoper oper123 new-code
User successfully authenticated
```

HQ-DSW1 `show tacacs` confirmed:

- Server name: `HQ-TACACS`
- Server address: `10.1.99.52`
- Server status: `Alive`
- Socket errors: `0`
- Socket timeouts: `0`
- Failed connect attempts: `0`

HQ-DSW1 SSH tests passed from `HQ-RTR1`:

```text
ssh -l tacadmin 10.1.99.11
HQ-DSW1#show privilege
Current privilege level is 15
```

```text
ssh -l tacoper 10.1.99.11
HQ-DSW1>show privilege
Current privilege level is 1
```

Note: `tacoper` showed an extra password prompt before successful login, but the final login and privilege result were correct.

## HQ-DSW2 Evidence

HQ-DSW2 pre-check passed:

- Local fallback user exists: `username admin privilege 15 secret ...`
- Ping to `10.1.99.52` sourced from `Vlan999` passed 5/5 after ARP warm-up
- SSH was already enabled with RSA keys present

HQ-DSW2 SSH tests passed from `HQ-RTR1`:

```text
ssh -l tacadmin 10.1.99.12
HQ-DSW2#show privilege
Current privilege level is 15
```

```text
ssh -l tacoper 10.1.99.12
HQ-DSW2>show privilege
Current privilege level is 1
```

Note: `tacoper` showed an extra password prompt before successful login, but the final login and privilege result were correct.

## BR-DSW1 Evidence

BR-DSW1 pre-check passed:

- Local fallback user exists: `username admin privilege 15 secret ...`
- Ping to `10.1.99.52` sourced from `Vlan999` passed 5/5
- SSH was already enabled with RSA keys present

BR-DSW1 console initially used the default TACACS+ method after `aaa new-model`, causing local `admin` console login to fail while TACACS login worked. Console was protected with:

```ios
aaa authentication login CONSOLE local
line con 0
 login authentication CONSOLE
```

BR-DSW1 `show tacacs` confirmed:

- Server name: `HQ-TACACS`
- Server address: `10.1.99.52`
- Server status: `Alive`
- Socket errors: `0`
- Socket timeouts: `0`
- Failed connect attempts: `0`

BR-DSW1 SSH tests passed from `BR-RTR1`:

```text
ssh -l tacadmin 10.2.99.2
BR-DSW1#show privilege
Current privilege level is 15
```

```text
ssh -l tacoper 10.2.99.2
BR-DSW1>show privilege
Current privilege level is 1
```

## HQ-ASW1 Evidence

HQ-ASW1 pre-check passed:

- Local fallback user exists: `username admin privilege 15 secret ...`
- Ping to `10.1.99.52` sourced from `Vlan999` passed 5/5 after ARP warm-up
- SSH was already enabled with RSA keys present

HQ-ASW1 SSH tests passed from `HQ-RTR1`:

```text
ssh -l tacadmin 10.1.99.13
HQ-ASW1#show privilege
Current privilege level is 15
```

```text
ssh -l tacoper 10.1.99.13
HQ-ASW1>show privilege
Current privilege level is 1
```
