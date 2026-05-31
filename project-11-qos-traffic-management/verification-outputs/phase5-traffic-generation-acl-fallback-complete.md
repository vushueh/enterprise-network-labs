# Project 11 Phase 5 - Traffic Generation And ACL Fallback Complete

## Result

Phase 5 traffic testing proved:

- Real HTTP traffic can be generated from `PC-ENG1` to `10.1.40.10` (nginx).
- IOL/NBAR did not classify the generated HTTP or DNS traffic with `match protocol http` or `match protocol dns`.
- ACL-based classification successfully matched and marked the same traffic.

## HTTP Traffic

Source: `PC-ENG1` (`10.1.100.194`)
Destination: nginx web server at `10.1.40.10`

```sh
wget -O - http://10.1.40.10
Welcome to nginx!
```

Route from `HQ-RTR1` to `10.1.40.0/24`: via static, next-hop `10.0.0.14` (firewall path). Traffic exits via firewall, not `Ethernet0/1`. WAN output DSCP counters staying zero is expected for this destination.

## DNS Limitation

DNS traffic (12 ACL matches confirmed) did not increment `P11-NETWORK-CONTROL match protocol dns`. IOL NBAR PDL limitation — DNS packets were seen at the router but not classified by NBAR.

## ACL Fallback Configuration

```ios
ip access-list extended P11-HTTP-TRAFFIC
 permit tcp host 10.1.100.194 host 10.1.40.10 eq www

class-map match-any P11-BULK-DATA-ACL
 match access-group name P11-HTTP-TRAFFIC

policy-map P11-MARK-IN
 class P11-BULK-DATA-ACL
  set dscp af11
```

## Verification Evidence

`show policy-map interface Ethernet0/0.100`:

```text
Class-map: P11-BULK-DATA-ACL
  54 packets, 4410 bytes
  Match: access-group name P11-HTTP-TRAFFIC
    54 packets, 4410 bytes
  QoS Set
    dscp af11
      Packets marked 54
```

ACL hit count:

```text
Extended IP access list P11-HTTP-TRAFFIC
  10 permit tcp host 10.1.100.194 host 10.1.40.10 eq www (54 matches)
```

## Save

Configuration saved with `write memory`.
