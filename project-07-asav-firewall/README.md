# Project 07 — Perimeter Firewall with ASAv

## Problem Statement

The network relied on stateless router ACLs for internet security. HQ-RTR1 was simultaneously
the campus router, the NAT boundary, and the internet gateway — with no dedicated security
enforcement point. HQ-SRV1 lived on the same internal VLAN as engineering workstations.
Any compromised internal host could reach the server directly.

This project inserts an ASAv firewall between HQ-RTR1 and ISP-RTR1, moves HQ-SRV1 into an
isolated DMZ, migrates NAT ownership to the firewall, enforces zone-based ACL policy, and
enables stateful inspection with syslog visibility.

---

## Topology Changes

| Change | Before | After |
|--------|--------|-------|
| Internet boundary | HQ-RTR1 E0/3 → ISP-RTR1 | HQ-FW1 Gi0/1 → ISP-RTR1 |
| NAT | HQ-RTR1 PAT + static | HQ-FW1 PAT + static |
| HQ-SRV1 | VLAN 400 (internal) | DMZ (isolated) |
| Security enforcement | Stateless ACLs | Stateful ASA inspection |

### Node Added

| Node | Image | Hostname | Role |
|------|-------|----------|------|
| ASAv | ASAv | HQ-FW1 | Perimeter firewall |

### Connections

| Side A | Side B | Purpose |
|--------|--------|---------|
| HQ-RTR1 Ethernet0/3 | HQ-FW1 GigabitEthernet0/0 | Inside link (10.0.0.12/30) |
| HQ-FW1 GigabitEthernet0/1 | ISP-RTR1 Ethernet0/0 | Outside link (203.0.113.0/30) |
| HQ-FW1 GigabitEthernet0/2 | HQ-SRV1 eth0 | DMZ (10.1.40.0/24) |

---

## IP Address Plan

| Interface | Device | IP | Zone |
|-----------|--------|----|------|
| GigabitEthernet0/0 | HQ-FW1 | 10.0.0.14/30 | Inside |
| Ethernet0/3 | HQ-RTR1 | 10.0.0.13/30 | Inside |
| GigabitEthernet0/1 | HQ-FW1 | 203.0.113.1/30 | Outside |
| Ethernet0/0 | ISP-RTR1 | 203.0.113.2/30 | Outside |
| GigabitEthernet0/2 | HQ-FW1 | 10.1.40.1/24 | DMZ |
| eth0 | HQ-SRV1 | 10.1.40.10/24 | DMZ |

---

## Phases

| Phase | Focus |
|-------|-------|
| 1 | ASAv basic setup — interfaces, security levels, static routes, HQ-RTR1 cutover |
| 2 | NAT migration — remove from HQ-RTR1, rebuild PAT + static NAT on HQ-FW1 |
| 3 | ACL policy — outside→inside deny, outside→DMZ HTTP permit, application inspection |
| 4 | packet-tracer — trace allowed and denied flows, verify NAT translations |
| 5 | Firewall logging — syslog to HQ-SYSLOG, ACL hit logging, threat-detection |
| 6 | show conn — stateful connection table analysis |

---

## Break/Fix Challenge

**The Fault:** Inside interface security level set to 0 instead of 100.

**Symptom:** All traffic from inside to outside denied — security levels reversed.

**Diagnosis:** `packet-tracer input inside ...` shows implicit deny. `show nameif` reveals wrong security level.

**Fix:** `security-level 100` on GigabitEthernet0/0.

---

## STAR Summary

**Situation:** Internet security relied on stateless router ACLs. No DMZ, no stateful inspection, no application-layer visibility.

**Task:** Deploy ASAv as dedicated perimeter firewall with stateful inspection, DMZ isolation, and complete NAT migration.

**Action:** Inserted ASAv between HQ-RTR1 and ISP, migrated NAT from router to firewall, built zone-based ACL policies with HTTP/DNS/ICMP inspection, mastered packet-tracer troubleshooting, enabled syslog visibility, analyzed stateful connection table, and diagnosed a security level misconfiguration.

**Result:** Can deploy and configure ASA firewall, design DMZ architecture, migrate NAT between platforms, enforce zone-based policy, and troubleshoot with packet-tracer.

---

## Screenshots

| File | Phase | Description |
|------|-------|-------------|
| P07-Ph1-topology-firewall-inserted.png | 1 | CML topology with HQ-FW1 added |
| P07-Ph1-hq-fw1-status.png | 1 | ASA interface status and security levels |
| P07-Ph1-hq-fw1-connectivity-policy.png | 1 | ASA connectivity and nameif verification |
| P07-Ph1-hq-rtr1-interface-ip route-brief.png | 1 | HQ-RTR1 post-cutover interface and route table |
| P07-Ph1-isp-rtr1-outside-ping.png | 1 | ISP-RTR1 ping to ASA outside interface |
| P07-Ph2-hq-fw1-nat-status.png | 2 | NAT objects and translation table on ASA |
| P07-Ph2-hq-fw1-packet-tracer-nat.png | 2 | packet-tracer verifying NAT path |
| P07-Ph3-hq-fw1-policy-config.png | 3 | ACL policy and inspection config |
| P07-Ph3-hq-fw1-packet-tracer-policy-Allowed.png | 3 | packet-tracer allowed flow |
| P07-Ph3-hq-fw1-packet-tracer-policy-Drop.png | 3 | packet-tracer denied flow |
| P07-Ph3-hq-rtr1-icmp-inspection-test.png | 3 | ICMP inspection test result |
| P07-Ph5-hq-fw1-logging-config.png | 5 | Syslog and logging configuration |
| P07-Ph5-hq-fw1-log-proof.png | 5 | Live log entries on syslog server |
| P07-Ph5-isp-rtr1-log-tests.png | 5 | ISP-side tests triggering log entries |
| P07-Ph6-hq-fw1-conn-outside-dmz.png | 6 | show conn — outside to DMZ stateful table |
