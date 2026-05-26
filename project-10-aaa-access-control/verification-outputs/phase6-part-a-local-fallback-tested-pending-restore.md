# Project 10 Phase 6 Part A - Local Fallback Test Complete

## Fault Applied

On `HQ-RTR1`, only the TACACS server address was temporarily changed. The faulty state was not saved:

```ios
tacacs server HQ-TACACS
 address ipv4 10.1.99.250
 key 7 ...
```

The target `10.1.99.250` was confirmed unused before this test.

## Local Fallback Proof

While `HQ-RTR1` was pointed to unreachable TACACS target `10.1.99.250`, an SSH login was initiated from `HQ-DSW1`:

```ios
ssh -l admin 10.0.255.1
```

The session opened successfully and reached privilege 15:

```text
HQ-RTR1#show privilege
Current privilege level is 15
```

Because the local `admin` credential was explicitly set immediately before the test and the configured TACACS address was unreachable, this demonstrates successful local fallback for administrative access.

An initial failed SSH login entry was also observed before the successful login:

```text
%SEC_LOGIN-4-LOGIN_FAILED: Login failed [user: admin] [Source: 10.1.99.11] [localport: 22] ...
```

This is retained as observed evidence; the subsequent successful privilege-15 session is the pass condition.

## Counter Visibility Limitation

`show tacacs` was captured while the unreachable address remained configured:

```text
Server address: 10.1.99.250
Socket Timeouts: 0
Failed Connect Attempts: 0
Total Packets Sent: 111
Total Packets Recv: 111
Server Status: Alive
```

The IOL image retained last-known server status and did not expose timeout/failure counter activity for this fallback attempt. Claude review item P10-20 was attempted, but its desired counter proof is unavailable on this image.

## Restoration Verified

The TACACS server address and shared key were restored on `HQ-RTR1`:

```ios
tacacs server HQ-TACACS
 address ipv4 10.1.99.52
 key 7 ...
```

TACACS authentication was verified after restoration:

```ios
test aaa group tacacs+ admin chongong new-code
```

```text
User successfully authenticated
```

Healthy server status was confirmed:

```text
Server address: 10.1.99.52
Socket errors: 0
Socket Timeouts: 0
Failed Connect Attempts: 0
Total Packets Sent: 119
Total Packets Recv: 119
Server Status: Alive
```

The restored configuration was saved with `write memory`.

## Current Status

Part A is complete. Local fallback was proven during the unreachable TACACS condition, the server relationship has been restored, and `HQ-RTR1` is ready for Part B wrong-shared-key diagnosis.
