# Project 10 Phase 2 - Admin Username and Privilege Separation

## Goal

Move into Phase 2 while keeping the remaining two access switches paused:

- `HQ-ASW2` paused
- `BR-ASW1` paused

Phase 2 focuses on privilege separation and making the normal `admin` username work with TACACS+.

## Why Local Admin Fails When TACACS+ Is Reachable

The active method list is:

```ios
aaa authentication login default group tacacs+ local
```

This means IOS checks TACACS+ first. If TACACS+ is reachable and rejects the username, IOS does not fall through to the local user database. Local fallback mainly helps when the TACACS+ server is unreachable.

To log in as `admin` while TACACS+ is healthy, the `admin` user must exist on `HQ-TACACS`.

## Update HQ-TACACS tac-plus.conf

Add this user to `tac-plus.conf` on `HQ-TACACS`:

```text
user = admin {
  login = cleartext admin123
  member = netadmin
}
```

This makes `admin` authenticate through TACACS+ and receive privilege level 15 through the existing `netadmin` group:

```text
group = netadmin {
  default service = permit
  service = exec {
    priv-lvl = 15
  }
}
```

Restart the TACACS+ service/node after editing the file.

## Test Admin Through TACACS+

Run on `HQ-RTR1`:

```ios
test aaa group tacacs+ admin admin123 new-code
test aaa group tacacs+ tacadmin admin123 new-code
test aaa group tacacs+ tacoper oper123 new-code
show tacacs
```

Expected:

- `admin / admin123` authenticates successfully
- `tacadmin / admin123` authenticates successfully
- `tacoper / oper123` authenticates successfully
- TACACS+ server remains `Alive`

## SSH Test Admin Username

From `HQ-RTR1`, test a TACACS-enabled device:

```ios
ssh -l admin 10.1.99.11
```

Password:

```text
admin123
```

Then run:

```ios
show privilege
exit
```

Expected:

```text
Current privilege level is 15
```

## Phase 2 Privilege Validation

Use these users:

| User | Password | Expected Privilege | Purpose |
|---|---|---:|---|
| `admin` | `admin123` | 15 | Normal admin username |
| `tacadmin` | `admin123` | 15 | TACACS admin test account |
| `tacoper` | `oper123` | 1 | Operator test account |

For each TACACS-enabled device, test:

```ios
ssh -l admin <device-ip>
show privilege
exit

ssh -l tacoper <device-ip>
show privilege
configure terminal
exit
```

Expected:

- `admin` receives privilege 15.
- `tacoper` receives privilege 1.
- `tacoper` cannot configure the device.

## Keep Console Local

Every TACACS-enabled IOS/IOL device should have:

```ios
aaa authentication login CONSOLE local
line console 0
 login authentication CONSOLE
```

This keeps console access local while SSH uses TACACS+.

