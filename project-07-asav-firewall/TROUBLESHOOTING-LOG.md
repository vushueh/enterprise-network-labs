# Troubleshooting Log — Project 07 ASAv Firewall

Project-local troubleshooting entries for Project 07.

---

## P07-T01 — Planned Break/Fix: Inside Interface Security Level Set to 0

**Phase:** Break/Fix Challenge

**Symptom:** All traffic from inside campus to internet is denied. Users cannot reach internet.
Inside-initiated pings to outside fail. No ACL deny messages — traffic drops silently.

**Diagnosis path:**
```
packet-tracer input inside tcp 10.1.100.10 12345 203.0.113.100 80
show nameif
show interface ip brief
```
`packet-tracer` shows implicit deny at security level check.
`show nameif` reveals inside interface security level is 0 instead of 100.

**Fix:**
```
interface GigabitEthernet0/0
 security-level 100
end
write memory
```

**Lesson:** ASA security level 100 = maximum trust (inside). Security level 0 = untrusted (outside).
Traffic flows from higher to lower by default — reversing inside to 0 means it cannot
initiate anything. Always verify `show nameif` immediately after interface configuration.

---

## Live Issues

No additional live Project 07 issues captured yet.
