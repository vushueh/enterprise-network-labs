# Project 10 Phase 2 - HQ-RTR1 Privilege Separation

## Goal

Validate TACACS+ privilege separation on `HQ-RTR1`.

The TACACS+ server already has the required group behavior:

- `tacadmin` is a member of `netadmin`, which returns `priv-lvl = 15`
- `tacoper` is a member of `netoper`, which returns `priv-lvl = 1`

This phase proves the difference from SSH before expanding AAA to more devices.

## Devices Used

- Source device for SSH test: `HQ-DSW1`
- Target device: `HQ-RTR1`
- TACACS+ server: `HQ-TACACS` at `10.1.99.52`

## Pre-Check on HQ-RTR1

Run from the open `HQ-RTR1` console:

```ios
show running-config | include ^aaa|^ip tacacs|^tacacs
show tacacs
show users
```

Expected:

- `aaa authentication login default group tacacs+ local`
- `aaa authorization exec default group tacacs+ local`
- `ip tacacs source-interface Loopback0`
- `HQ-TACACS` status is `Alive`

## Test 1 - Admin User Gets Privilege 15

Run from `HQ-DSW1`:

```ios
ssh -l tacadmin 10.0.255.1
```

Password:

```text
admin123
```

Then run:

```ios
show privilege
show running-config | include ^hostname
configure terminal
do show privilege
end
exit
```

Expected:

- Prompt is `HQ-RTR1#`
- `show privilege` returns `Current privilege level is 15`
- `configure terminal` is allowed

## Test 2 - Operator User Gets Privilege 1

Run from `HQ-DSW1`:

```ios
ssh -l tacoper 10.0.255.1
```

Password:

```text
oper123
```

Then run:

```ios
show privilege
show running-config
configure terminal
enable
exit
```

Expected:

- Prompt is `HQ-RTR1>`
- `show privilege` returns `Current privilege level is 1`
- `show running-config` is denied or unavailable
- `configure terminal` is denied or unavailable
- `enable` should not grant privilege 15 unless the enable password is known and accepted

## Post-Test on HQ-RTR1

Run from the `HQ-RTR1` console:

```ios
show users
show tacacs
show logging | include TACACS|AAA|LOGIN|SEC_LOGIN|AUTHEN|AUTHZ
```

## Pass Criteria

Phase 2 passes if:

- `tacadmin` logs in through TACACS+ and receives privilege level 15
- `tacadmin` can enter configuration mode
- `tacoper` logs in through TACACS+ and receives privilege level 1
- `tacoper` cannot enter configuration mode
- `HQ-TACACS` remains alive with no failed connects or socket errors

## No New Configuration Required Yet

Do not add command authorization in this phase. `aaa authorization commands ...` will be safer after privilege separation is proven and local fallback behavior is documented.

