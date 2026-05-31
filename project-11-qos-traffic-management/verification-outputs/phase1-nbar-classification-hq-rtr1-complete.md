# Project 11 Phase 1 - NBAR Classification Complete On HQ-RTR1

## Result

Phase 1 is complete on `HQ-RTR1`.

## Precheck

The IOL image accepted both protocol matches flagged for review:

```ios
match protocol rtp
match protocol ospf
```

The temporary precheck class-maps were removed before the final configuration was applied.

## Final Class-Maps

`P11-VOICE-LIKE`:

```ios
class-map match-any P11-VOICE-LIKE
 description P11 voice-like realtime traffic classification
 match protocol rtp
```

`P11-SIGNALING`:

```ios
class-map match-any P11-SIGNALING
 description P11 voice signaling and control traffic classification
 match protocol sip
```

`P11-NETWORK-CONTROL`:

```ios
class-map match-any P11-NETWORK-CONTROL
 description P11 routing and infrastructure control traffic
 match protocol ospf
 match protocol dns
```

`P11-BULK-DATA`:

```ios
class-map match-any P11-BULK-DATA
 description P11 bulk and lower-priority application traffic
 match protocol ftp
 match protocol http
```

## Verification

`show class-map` confirmed every class-map contains the expected match statements. No class-map was empty.

The configuration was saved with `write memory`.
