# Project 10 - TACACS+ Server Configuration Review

Date: 2026-05-22

## Source Reviewed

Reviewed the `tac-plus.conf` content provided from the `HQ-TACACS` CML service node.

## Result

No TACACS+ group privilege fix is needed.

The provided `tac-plus.conf` already has the required `service = exec` blocks with `priv-lvl` inside each group.

## Relevant Configuration Found

```text
key = tacacs123
accounting file = /var/log/tacplus-acct.log
acl = default {
  permit = 0.0.0.0
}
host = 0.0.0.0 {
  prompt = "TACACS+ auth: "
}
group = netadmin {
  default service = permit
  service = exec {
    priv-lvl = 15
  }
}
group = netoper {
  default service = permit
  service = exec {
    priv-lvl = 1
  }
}
user = $enab15$ {
  login = cleartext admin123
}
user = tacadmin {
  login = cleartext admin123
  member = netadmin
}
user = tacoper {
  login = cleartext oper123
  member = netoper
}
```

## User/Group Privilege Mapping

| User | Password | Group | Expected Privilege |
| --- | --- | --- | --- |
| `tacadmin` | `admin123` | `netadmin` | 15 |
| `tacoper` | `oper123` | `netoper` | 1 |
| `$enab15$` | `admin123` | built-in enable user | enable authentication |

## Review Notes

- `netadmin` has `default service = permit` and `service = exec { priv-lvl = 15 }`.
- `netoper` has `default service = permit` and `service = exec { priv-lvl = 1 }`.
- The shared key is `tacacs123`, which matches the proposed IOS TACACS+ key.
- The accounting file is configured as `/var/log/tacplus-acct.log`.

## Before / After

No change was required based on the provided file content.

If the service node file on disk differs from the pasted content, update it to match the configuration shown above and restart the TacPlus service/node.
