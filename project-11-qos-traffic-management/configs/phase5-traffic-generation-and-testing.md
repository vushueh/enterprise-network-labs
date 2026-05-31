# Project 11 Phase 5 - Traffic Generation And Testing

## Goal

Generate real traffic that matches the QoS class-maps, then verify counters move under `show policy-map interface`.

## Known VLAN 100 Hosts

Discovered on `HQ-RTR1`:

```text
10.1.100.170  (PC-ENG1 or similar)
10.1.100.194  (PC-ENG1 — confirmed traffic source)
```

## Phase 5A - DNS Test

From a VLAN 100 host, generate DNS queries:

```sh
nslookup example.com 10.1.99.50
```

Expected: `P11-NETWORK-CONTROL` counter increases under `match protocol dns`.

**Actual result:** DNS traffic reached the router (ACL hit count confirmed 12 matches) but `match protocol dns` counter stayed at zero. IOL/NBAR limitation — DNS classification not reliable on this image.

## Phase 5B - HTTP Test

From `PC-ENG1`, generate HTTP traffic to the nginx server:

```sh
wget -O - http://10.1.40.10
```

Expected: `P11-BULK-DATA` counter increases under `match protocol http`.

**Actual result:** `wget` succeeded (nginx welcome page received), ACL toward `10.1.40.0/24` incremented, but `match protocol http` counter stayed at zero. Same IOL/NBAR limitation.

## Phase 5C - ACL Fallback Classification

Since NBAR did not classify live traffic, an ACL-based class was used as the working alternative:

```ios
ip access-list extended P11-HTTP-TRAFFIC
 permit tcp host 10.1.100.194 host 10.1.40.10 eq www

class-map match-any P11-BULK-DATA-ACL
 match access-group name P11-HTTP-TRAFFIC

policy-map P11-MARK-IN
 class P11-BULK-DATA-ACL
  set dscp af11
```

## Pass Condition

ACL-based class confirmed working — 54 packets, 4410 bytes, 54 packets marked DSCP af11. This proves end-to-end MQC marking with live traffic even without NBAR classification.
