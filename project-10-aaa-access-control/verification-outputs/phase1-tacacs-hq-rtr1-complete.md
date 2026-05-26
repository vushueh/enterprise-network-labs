# Project 10 Phase 1 - HQ-RTR1 TACACS+ Pilot Complete

## Status

Phase A and Phase B are both applied on `HQ-RTR1`. TACACS+ login is working.

## Final AAA Configuration

```ios
aaa new-model
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+
aaa session-id common
```

## Final TACACS+ Configuration

```ios
ip tacacs source-interface Loopback0
tacacs server HQ-TACACS
 address ipv4 10.1.99.52
 key tacacs123
```

Note: `HQ-RTR1` rejected `source-interface Loopback0` inside the `tacacs server` block. The accepted syntax is the global command `ip tacacs source-interface Loopback0`.

## Final VTY Configuration

```ios
line vty 0 4
 access-class 10 in
 exec-timeout 15 0
 logging synchronous
 transport input ssh
```

Phase B commands were applied:

```ios
line vty 0 4
 login authentication default
 authorization exec default
 transport input ssh
```

The running config does not display `login authentication default` or `authorization exec default` under the VTY section, but AAA login and exec authorization are active through the global default method lists.

## TACACS+ Test Results

`tacadmin` test:

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

`tacoper` test:

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
Tacacs+ Server -  public  :
               Server name: HQ-TACACS
            Server address: 10.1.99.52
               Server port: 49
              Socket opens:         12
             Socket closes:         12
             Socket aborts:          0
             Socket errors:          0
           Socket Timeouts:          0
   Failed Connect Attempts:          0
        Total Packets Sent:         18
        Total Packets Recv:         18
             Server Status: Alive
Continous Authc fail count:          0
Continous Authz fail count:          0
```

`show aaa servers` returned no visible output on this IOS image. `show tacacs` confirmed the TACACS+ server is alive and actively processing requests.

## SSH Login Verification

Test source: `HQ-DSW1`

Admin test:

```ios
ssh -l tacadmin 10.0.255.1
```

Result:

```text
HQ-RTR1#show privilege
Current privilege level is 15
```

Operator test:

```ios
ssh -l tacoper 10.0.255.1
```

Result:

```text
HQ-RTR1>show privilege
Current privilege level is 1
```

## Users Tested

| User | Password | TACACS+ Group | Expected Privilege | Verified Privilege |
|---|---|---|---|---|
| `tacadmin` | `admin123` | `netadmin` | 15 | 15 |
| `tacoper` | `oper123` | `netoper` | 1 | 1 |

## Local Fallback

Local fallback exists as a safety net:

```ios
username admin privilege 15 secret 9 ...
```

The active login method list is:

```ios
aaa authentication login default group tacacs+ local
```

If TACACS+ fails, IOS should fall back to the local `admin` account.

## Phase 1 Verdict

Project 10 Phase 1 TACACS+ pilot on `HQ-RTR1` is complete and verified.

