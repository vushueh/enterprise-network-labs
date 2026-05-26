# Project 10 Phase 6 - AAA Failover And Break/Fix Complete On HQ-RTR1

## Scope

Phase 6 was performed on `HQ-RTR1` using a protected local console session. No intentional failure was saved to startup configuration.

## Safety Baseline

- Local privilege-15 fallback user `admin` exists and was explicitly set to the intended local password before testing.
- Console authentication uses the local-only list:

```ios
aaa authentication login CONSOLE local
line con 0
 login authentication CONSOLE
```

- Normal VTY authentication uses TACACS+ with local fallback:

```ios
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
ip tacacs source-interface Loopback0
tacacs server HQ-TACACS
 address ipv4 10.1.99.52
```

## Part A - TACACS Unreachable, Local Fallback Verified

The server address was temporarily changed to unused target `10.1.99.250`.

While the unreachable address was configured, `HQ-DSW1` successfully opened an SSH session to `HQ-RTR1` using local `admin / chongong`:

```text
HQ-RTR1#show privilege
Current privilege level is 15
```

This proves the `local` fallback method works when TACACS cannot be reached.

The IOL image retained last-known `show tacacs` server state and did not display increased timeout or failure counters during this test. This visibility limitation is documented; it does not change the observed local-fallback result.

The correct TACACS address was restored, authenticated successfully, and saved.

## Part B - Wrong Shared Key Break/Fix Verified

The TACACS shared key was deliberately changed to an incorrect value:

```ios
tacacs server HQ-TACACS
 key P10-WRONG-KEY
```

Observed failure:

```ios
test aaa group tacacs+ admin chongong new-code
```

```text
User rejected
Server Status: Alive
Continous Authc fail count: 1
```

This proves the server remained reachable while TACACS authentication failed due to the deliberate client/server secret mismatch.

The correct shared key was restored:

```ios
tacacs server HQ-TACACS
 key tacacs123
```

Post-repair verification:

```text
User successfully authenticated
Server address: 10.1.99.52
Total Packets Sent: 133
Total Packets Recv: 133
Server Status: Alive
```

Debugging was disabled and the corrected configuration was saved.

## Result

Phase 6 is complete on `HQ-RTR1`:

- TACACS unreachability was simulated without saving the fault.
- Local administrative fallback was verified.
- A wrong TACACS key was introduced and diagnosed.
- The correct key was restored and authentication recovered.
- Platform counter-display limitations were documented rather than overstated.

