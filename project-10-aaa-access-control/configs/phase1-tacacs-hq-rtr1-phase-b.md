# Project 10 Phase 1 - HQ-RTR1 TACACS+ Pilot Phase B

# Apply only after test aaa passes.

Phase B contains only `line vty 0 4` changes. Do not apply this file until Phase A has passed both TACACS+ authentication tests from the console session.

## Required Proof Before Applying

Run these on `HQ-RTR1` after Phase A and confirm both users authenticate:

```ios
test aaa group tacacs+ tacadmin admin123 new-code
test aaa group tacacs+ tacoper oper123 new-code
show tacacs
show aaa servers
```

Expected:

- `tacadmin / admin123` authenticates successfully and should receive privilege level 15.
- `tacoper / oper123` authenticates successfully and should receive privilege level 1.
- Keep the console session open before testing SSH.

## Phase B Configuration

```ios
configure terminal
line vty 0 4
 login authentication default
 authorization exec default
 transport input ssh
end
write memory
```

## Verification After Phase B

From a separate terminal/session, SSH to `HQ-RTR1` and test:

```text
ssh tacadmin@10.0.255.1
```

Then on `HQ-RTR1`, verify:

```ios
show users
show privilege
show running-config | section aaa
show running-config | section tacacs
show running-config | section line vty
show tacacs
show aaa servers
```

Also test local fallback from the console remains available:

```ios
show running-config | include ^username
```

## Rollback

Use this from the open console session if SSH login fails or TACACS+ behavior is not correct:

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

