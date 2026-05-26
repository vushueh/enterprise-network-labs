# Project 10 Phase 1 - HQ-RTR1 TACACS+ Pilot Phase A

Apply this on `HQ-RTR1` only.

Phase A contains only AAA/TACACS+ configuration. It does not change `line vty 0 4`, so the current local VTY login remains in place while TACACS+ is tested.

## Pre-Checks

Run these on `HQ-RTR1` before applying Phase A:

```ios
show running-config | include ^username
show running-config | include ^crypto key|^ip domain|^hostname|^ip ssh
ping 10.1.99.52 source Loopback0 repeat 5
```

Expected:

- A local `username admin privilege 15 secret ...` exists.
- SSH prerequisites are present, or you stop and generate SSH keys before Phase B.
- The ping to `10.1.99.52` from `Loopback0` succeeds 5/5.

## Phase A Configuration

```ios
configure terminal
aaa new-model
!
tacacs server HQ-TACACS
 address ipv4 10.1.99.52
 key tacacs123
 exit
!
ip tacacs source-interface Loopback0
!
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+
end
write memory
```

Note: On `HQ-RTR1`, IOS rejected `source-interface Loopback0` inside the `tacacs server` block. The verified working syntax is the global command `ip tacacs source-interface Loopback0`.

## Tests Before Phase B

Run these on `HQ-RTR1` after Phase A:

```ios
test aaa group tacacs+ tacadmin admin123 new-code
test aaa group tacacs+ tacoper oper123 new-code
show tacacs
show aaa servers
```

Expected:

- Both `test aaa` commands return `User was successfully authenticated`.
- `show tacacs` shows requests going to `10.1.99.52`.
- `show aaa servers` shows the TACACS+ server as reachable/alive.

## Phase A Rollback

Use this if TACACS testing fails or the router behaves unexpectedly:

```ios
configure terminal
no aaa new-model
line vty 0 4
 login local
 transport input all
 no authorization exec default
end
write memory
```
