# Project 10 Phase 4 - HQ-ASW1 802.1X Command Support Check

## Device

`HQ-ASW1` running IOL-L2 / IOS XE image used in the CML lab.

## Required Verification Commands

The Project 10 Phase 4 design calls for verification using:

```ios
show dot1x all
show authentication sessions
```

Both are unavailable on `HQ-ASW1`:

```text
HQ-ASW1#show dot1x all
                 ^
% Invalid input detected at '^' marker.

HQ-ASW1#show dot1x ?
% Unrecognized command

HQ-ASW1#show authentication sessions
                ^
% Invalid input detected at '^' marker.
```

`show dot1` is not an 802.1X alternative on this image. It displays dot1q-tunnel status:

```text
dot1q-tunnel mode LAN Port(s)
No ports have been configured as dot1q-tunnel
```

## Configuration Command Support

The switch does expose 802.1X configuration syntax:

```ios
aaa authentication dot1x ?
dot1x system-auth-control
interface Ethernet0/2
 authentication port-control ...
 authentication host-mode ...
 authentication open
 dot1x pae ...
```

## Finding

This image appears capable of accepting an 802.1X configuration but cannot provide the operational session verification commands required by the project acceptance test.

No Phase 4 RADIUS or access-port configuration has been applied yet.

## Final Alternative Command Checks

The following additional operational commands were tested and rejected:

```ios
show dot1x
show dot1x interface Ethernet0/2
show dot1x interface Ethernet0/2 detail
show authentication interface Ethernet0/2
show eap registrations
```

`show aaa sessions` is accepted, but it displays management AAA sessions rather than IEEE 802.1X port sessions:

```text
Total sessions since last reload: 6
Session Id: 13
   User Name: admin
   IP Address: 0.0.0.0
```

This output cannot verify an endpoint authentication state transition on `Ethernet0/2`.

## Recommendation

Do not claim a fully verified 802.1X implementation on this IOL-L2 image. Choose one of:

1. Use a CML switch image that supports `show dot1x all` or `show authentication sessions`.
2. Proceed with an explicitly evidence-limited open-auth configuration pilot, documenting that session authorization cannot be proven on this image.
