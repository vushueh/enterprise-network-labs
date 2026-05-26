# Project 10 Phase 1 - HQ-RTR1 TACACS+ Phase A Passed

## Status

Phase A passed on `HQ-RTR1`.

## Safety Checks

- Local fallback user exists: `username admin privilege 15 secret ...`
- HQ-TACACS reachability from `Loopback0` passed: `10.1.99.52` returned 5/5 ICMP replies.
- SSH is enabled with RSA keys present:
  - SSH version: 2.0
  - RSA host key: `HQ-RTR1.lab.local`
  - RSA modulus: 2048 bits

## TACACS+ Configuration Notes

The original per-server command was rejected:

```ios
tacacs server HQ-TACACS
 source-interface Loopback0
```

The accepted IOS syntax is:

```ios
ip tacacs source-interface Loopback0
```

## Test Results

Both TACACS+ users authenticated successfully:

```ios
test aaa group tacacs+ tacadmin admin123 new-code
```

Result:

```text
User successfully authenticated
username 0 "tacadmin"
```

```ios
test aaa group tacacs+ tacoper oper123 new-code
```

Result:

```text
User successfully authenticated
username 0 "tacoper"
```

`show tacacs` confirmed:

- Server name: `HQ-TACACS`
- Server address: `10.1.99.52`
- Server port: `49`
- Server status: `Alive`
- Failed connect attempts: `0`
- Total packets sent: `8`
- Total packets received: `8`

## Phase B Decision

Safe to proceed to Phase B from the open console session.

