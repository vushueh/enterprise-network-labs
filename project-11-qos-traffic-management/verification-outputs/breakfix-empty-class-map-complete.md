# Project 11 Break/Fix - Empty Class-Map Complete

## Fault

The match statement was removed from the `P11-BULK-DATA-ACL` class-map:

```ios
class-map match-any P11-BULK-DATA-ACL
 no match access-group name P11-HTTP-TRAFFIC
```

This produced an empty class-map condition:

```text
Class Map match-any P11-BULK-DATA-ACL (id 9)
  Match none
```

## Broken Symptom

Working baseline (before break):

```text
P11-BULK-DATA-ACL: 60 packets, 4900 bytes
Packets marked: 60
P11-HTTP-TRAFFIC ACL matches: 60
```

After removing the match statement:

```text
P11-BULK-DATA-ACL: 60 packets, 4900 bytes  <- frozen, not increasing
class-default: 162 packets                  <- increasing instead
```

Key observable: ACL still incremented, but QoS class did not. Traffic was classified to class-default instead.

## Diagnosis

```ios
show class-map P11-BULK-DATA-ACL
```

Output: `Match none` — root cause visible immediately.

## Fix

```ios
configure terminal
class-map match-any P11-BULK-DATA-ACL
 match access-group name P11-HTTP-TRAFFIC
end
```

## Fixed Verification

After generating HTTP traffic again from `PC-ENG1` to `10.1.40.10`:

```text
P11-BULK-DATA-ACL: 66 packets, 5390 bytes   <- increasing again
Match access-group name P11-HTTP-TRAFFIC: 6 packets, 490 bytes
Packets marked: 66
P11-HTTP-TRAFFIC ACL matches: 66
class-default: 162 packets                   <- stayed flat
```

## Save

Configuration saved with `write memory` after verification.

## Key Lesson

QoS troubleshooting must check both the policy-map AND the class-map. A policy-map can reference a class successfully, but if the class-map has `Match none`, traffic bypasses that class entirely and falls through to `class-default`. When expected traffic is not matching a QoS class, always run `show class-map <name>` as the first diagnostic step.
