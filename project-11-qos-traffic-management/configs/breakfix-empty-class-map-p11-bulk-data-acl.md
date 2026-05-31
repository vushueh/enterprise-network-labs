# Project 11 Break/Fix - Empty Class-Map (P11-BULK-DATA-ACL)

## Goal

Create and diagnose the Project 11 break/fix fault:

- **Fault:** QoS class-map exists but has no `match` statement.
- **Symptom:** Expected HTTP traffic no longer matches the class and falls into `class-default`.
- **Fix:** Restore the missing `match` statement.

## Target

Use the ACL fallback class from Phase 5:

```ios
class-map match-any P11-BULK-DATA-ACL
 match access-group name P11-HTTP-TRAFFIC
```

## Baseline (before break)

```ios
show class-map P11-BULK-DATA-ACL
show access-lists P11-HTTP-TRAFFIC
show policy-map interface Ethernet0/0.100
```

Generate HTTP traffic from `PC-ENG1`:

```sh
wget -O - http://10.1.40.10
```

## Break

```ios
configure terminal
class-map match-any P11-BULK-DATA-ACL
 no match access-group name P11-HTTP-TRAFFIC
end
```

Do not save.

## Broken Symptom

```text
show class-map P11-BULK-DATA-ACL
  Match none

show policy-map interface Ethernet0/0.100
  P11-BULK-DATA-ACL: count frozen, not increasing
  class-default: count increasing
```

## Diagnose

```ios
show class-map P11-BULK-DATA-ACL
```

Output: `Match none` — the class-map has no criteria.

## Fix

```ios
configure terminal
class-map match-any P11-BULK-DATA-ACL
 match access-group name P11-HTTP-TRAFFIC
end
```

## Verify Fix

Generate HTTP traffic again, then:

```ios
show class-map P11-BULK-DATA-ACL
show policy-map interface Ethernet0/0.100
show access-lists P11-HTTP-TRAFFIC
```

Expected: `P11-BULK-DATA-ACL` counter increases, `Packets marked` increases, ACL match count increases.

## Save After Fix

```ios
write memory
```

## Key Lesson

QoS troubleshooting must check both the policy-map and the class-map. A policy-map can reference a class correctly, but if the class-map has no match criteria (`Match none`), all traffic falls through to `class-default`. Always run `show class-map <name>` when a QoS class is not matching expected traffic.
