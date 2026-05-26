# Project 10 Phase 2 - Admin Username TACACS+ Fix

## Status

The normal username `admin` is now active in TACACS+ and authenticates successfully with password `chongong`.

## TACACS+ User Added

`HQ-TACACS` was updated with:

```text
user = admin {
  login = cleartext chongong
  member = netadmin
}
```

The `netadmin` group returns privilege level 15:

```text
group = netadmin {
  default service = permit
  service = exec {
    priv-lvl = 15
  }
}
```

## Restart Issue

After restarting `HQ-TACACS`, reachability temporarily failed because ARP entries were stale after the node came back with a new MAC address.

Recovery steps used:

```ios
clear arp 10.1.99.52
ping 10.1.99.52 source 10.1.99.1 repeat 5
ping 10.1.99.52 source Loopback0 repeat 5
```

Final ARP entry on `HQ-RTR1`:

```text
Internet  10.1.99.52  0  5254.004f.6105  ARPA  Ethernet0/0.999
```

## Final HQ-RTR1 TACACS+ Tests

```ios
test aaa group tacacs+ admin chongong new-code
```

Result:

```text
Sending password
User successfully authenticated

USER ATTRIBUTES

username             0   "admin"
reply-message        0   "Password: "
```

```ios
test aaa group tacacs+ tacadmin admin123 new-code
```

Result:

```text
Sending password
User successfully authenticated

USER ATTRIBUTES

username             0   "tacadmin"
reply-message        0   "Password: "
```

```ios
test aaa group tacacs+ tacoper oper123 new-code
```

Result:

```text
Sending password
User successfully authenticated

USER ATTRIBUTES

username             0   "tacoper"
reply-message        0   "Password: "
```

## TACACS+ Server Status

```text
Server name: HQ-TACACS
Server address: 10.1.99.52
Server port: 49
Socket errors: 0
Socket Timeouts: 0
Failed Connect Attempts: 0
Total Packets Sent: 62
Total Packets Recv: 62
Server Status: Alive
```

## Result

Phase 2 can continue using:

```text
Username: admin
Password: chongong
```

Expected privilege level: 15.

