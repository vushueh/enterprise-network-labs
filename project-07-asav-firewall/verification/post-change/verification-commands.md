# Project 07 — Verification Commands

## Phase 1 — ASAv Basic Setup

```
! HQ-FW1
show interface ip brief
show nameif
show route
ping inside 10.0.0.13
ping outside 203.0.113.2
ping dmz 10.1.40.10
show cdp neighbors

! HQ-RTR1
show ip interface brief
show ip route 0.0.0.0
ping 10.0.0.14

! ISP-RTR1
ping 203.0.113.1
```

**Expected:**
- HQ-FW1 Gi0/0 = inside, security 100, 10.0.0.14
- HQ-FW1 Gi0/1 = outside, security 0, 203.0.113.1
- HQ-FW1 Gi0/2 = dmz, security 50, 10.1.40.1
- All neighbor pings succeed
- HQ-RTR1 default route points to 10.0.0.14

---

## Phase 2 — NAT Migration

```
! HQ-FW1
show nat detail
show xlate
packet-tracer input inside tcp 10.1.100.194 12345 203.0.113.100 80
packet-tracer input outside tcp 203.0.113.2 12345 203.0.113.10 80

! HQ-RTR1
show running-config | include ip nat
show ip nat translations

! ISP-RTR1
show ip route 203.0.113.10
ping 203.0.113.10

! Endpoints
wget -O - http://203.0.113.100    (from PC-ENG1 and PC-BR1)
```

**Expected:**
- HQ-RTR1: no ip nat entries, no active translations
- HQ-FW1 show nat: 7 NAT rules (6 PAT objects + 1 static)
- packet-tracer inside→outside: allow with NAT translation shown
- packet-tracer outside→203.0.113.10: static NAT to 10.1.40.10 visible

---

## Phase 3 — ACL Policy and Inspection

```
! HQ-FW1
show access-list ACL-OUTSIDE-IN
show service-policy global
packet-tracer input outside tcp 203.0.113.2 12345 203.0.113.10 80
packet-tracer input outside tcp 203.0.113.2 12345 10.0.0.14 22
packet-tracer input inside icmp 10.1.100.10 8 0 203.0.113.100
```

**Expected:**
- outside→DMZ HTTP: allow (ACL permits, static NAT translates)
- outside→inside SSH: drop (implicit deny)
- inside→outside ICMP: allow (ICMP inspection tracks return traffic)

---

## Phase 5 — Logging

```
! HQ-FW1
show logging
show threat-detection statistics host
show access-list ACL-OUTSIDE-IN

! HQ-SYSLOG (verify messages arriving)
tail -f /var/log/syslog | grep 10.0.0.14
```

**Expected:**
- Deny events appear in syslog within seconds of blocked traffic
- ACL hit counters increment on each denied flow
- threat-detection shows top talkers

---

## Phase 6 — show conn

```
! HQ-FW1
show conn
show conn detail
show conn count
```

**Expected:**
- Active connections show: inside IP, outside IP, translated IP, flags
- Flags: UO = UDP open, UIOB = established TCP
- DMZ connections show server real IP and translated public IP
