# Project 11 Phase 2 - DSCP Marking Pilot On HQ-RTR1

## Goal

Create an MQC policy-map on `HQ-RTR1` that marks traffic based on the Phase 1 class-maps.

This phase applies an input service-policy on the HQ LAN subinterface so traffic can be classified and marked as it enters `HQ-RTR1`.

## Marking Plan

| Class | Match | DSCP Marking | Why |
|---|---|---|---|
| `P11-VOICE-LIKE` | RTP | `ef` | Expedited Forwarding for realtime voice-like traffic |
| `P11-SIGNALING` | SIP | `cs3` | Common marking for call signaling/control |
| `P11-NETWORK-CONTROL` | OSPF, DNS | `cs2` | Infrastructure/control traffic should be identified |
| `P11-BULK-DATA` | FTP, HTTP | `af11` | Lower-priority assured forwarding |
| `class-default` | Everything else | no change | Avoid remarking unknown traffic |

## Important Pilot Choice

Apply the input policy to `Ethernet0/0.100` first, not the physical trunk. This limits the first test to Engineering VLAN 100 traffic and avoids touching every HQ VLAN at once.

## Configuration

Apply on `HQ-RTR1`:

```ios
configure terminal
!
policy-map P11-MARK-IN
 class P11-VOICE-LIKE
  set dscp ef
 class P11-SIGNALING
  set dscp cs3
 class P11-NETWORK-CONTROL
  set dscp cs2
 class P11-BULK-DATA
  set dscp af11
!
interface Ethernet0/0.100
 description GATEWAY-VLAN100-ENGINEERING
 service-policy input P11-MARK-IN
!
end
```

## Verification

Run on `HQ-RTR1`:

```ios
show policy-map
show running-config | section policy-map
show running-config interface Ethernet0/0.100
show policy-map interface Ethernet0/0.100
```

Expected:

- `P11-MARK-IN` exists with correct DSCP set actions per class.
- `Ethernet0/0.100` shows `service-policy input P11-MARK-IN`.
- `class-default` is not remarking unmatched traffic.

## Rollback

```ios
configure terminal
interface Ethernet0/0.100
 no service-policy input P11-MARK-IN
exit
no policy-map P11-MARK-IN
end
```
