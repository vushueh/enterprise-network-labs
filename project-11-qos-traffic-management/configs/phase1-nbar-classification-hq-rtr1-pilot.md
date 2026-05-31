# Project 11 Phase 1 - NBAR Classification Pilot On HQ-RTR1

## Goal

Configure classification only on `HQ-RTR1`. This phase creates class-maps that identify traffic types, but it does not mark, queue, shape, or apply a service-policy yet.

## Why HQ-RTR1 First

`HQ-RTR1` sees HQ LAN traffic, branch/WAN traffic, and firewall/default-route traffic. It is the best first router for proving the classification model.

## Configuration

Apply on `HQ-RTR1`:

```ios
configure terminal
!
class-map match-any P11-VOICE-LIKE
 description P11 voice-like realtime traffic classification
 match protocol rtp
!
class-map match-any P11-SIGNALING
 description P11 voice signaling and control traffic classification
 match protocol sip
!
class-map match-any P11-BULK-DATA
 description P11 bulk and lower-priority application traffic
 match protocol ftp
 match protocol http
!
class-map match-any P11-NETWORK-CONTROL
 description P11 routing and infrastructure control traffic
 match protocol ospf
 match protocol dns
!
end
```

## Verification

Run on `HQ-RTR1`:

```ios
show class-map
show running-config | section class-map
```

Expected:

- `P11-VOICE-LIKE` contains `match protocol rtp`
- `P11-SIGNALING` contains `match protocol sip`
- `P11-BULK-DATA` contains `match protocol ftp` and `match protocol http`
- `P11-NETWORK-CONTROL` contains `match protocol ospf` and `match protocol dns`

## Rollback

```ios
configure terminal
no class-map match-any P11-VOICE-LIKE
no class-map match-any P11-SIGNALING
no class-map match-any P11-BULK-DATA
no class-map match-any P11-NETWORK-CONTROL
end
```
