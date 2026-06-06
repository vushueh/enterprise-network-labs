---
name: cml-evidence-documentation
description: >
  CML Enterprise Network Labs evidence and portfolio documentation workflow.
  Trigger when Leonel says: "document phase", "save configs", "project complete",
  "update README", "log break fix", "save show outputs", or after completing any
  CML Enterprise Lab project (P01-P13).
  This skill handles PROVING the work was done.
  The technical skill (cml-enterprise-labs) handles HOW to do the work.
---

# CML Enterprise Network Labs — Evidence and Portfolio Documentation

## Purpose

This skill guides you through capturing and organizing proof that each CML lab
project was completed. The portfolio shows:
- Real IOS/IOS-XE configs from CML nodes
- Real show command outputs proving each technology works
- Topology screenshots from CML GUI
- Break/fix logs proving troubleshooting depth
- CCNA/CCNP exam topic connections per project

---

## Folder Structure Per Project

```
projects/project-NN-name/
├── README.md                    ← planning + STAR summary
├── configs/                     ← startup configs per device
│   ├── R1-startup.cfg
│   ├── R2-startup.cfg
│   ├── SW1-startup.cfg
│   └── ASAv-startup.cfg
├── verification-outputs/        ← show command outputs
│   ├── project-NN-R1-show-ip-route.txt
│   ├── project-NN-R1-show-ip-ospf-neighbor.txt
│   └── ...
├── decision-log.md              ← why certain design choices were made
└── troubleshooting/
    └── break-fix-log.md
```

---

## Screenshot Naming Convention

```
<project>-<what-it-shows>.png

Examples:
  p01-cml-topology-overview.png           ← CML GUI showing full topology
  p03-r1-ospf-neighbor-full.png           ← terminal: FULL adjacency
  p07-asav-security-levels.png            ← ASAv interface security levels
  p10-r1-tacacs-aaa-working.png           ← AAA login success in terminal
  p12-r1-qos-policy-map-applied.png       ← MQC policy applied
```

---

## Verification Output Naming Convention

```
project-<NN>-<device>-<command>.txt

Examples:
  project-03-R1-show-ip-ospf-neighbor.txt
  project-03-R2-show-ip-route-ospf.txt
  project-07-ASAv-show-conn.txt
  project-10-R1-show-aaa-sessions.txt
```

---

## Per-Phase Documentation Loop

### Step 1 — Before (export current startup configs)

```cisco
! Before starting a project — export startup configs
show startup-config
! Copy output to configs/<device>-startup-BEFORE-pNN.cfg
! CML also allows config export via lab menu → Export → download configs
```

### Step 2 — Do the Work

Follow the technical skill (cml-enterprise-labs) for configuration.
Screenshot CML topology view after each major change.

### Step 3 — Save Configs After Project

```cisco
! After all configs applied and verified
copy running-config startup-config
! Export via CML GUI: lab menu → Export configs
! Save each device config to configs/<device>-startup.cfg
```

### Step 4 — Run and Save Verification Commands

```cisco
! Run ALL verification commands from the project README
! Key commands by project:

! P01 Campus Foundation:
show vlan brief | show interfaces trunk | show spanning-tree

! P03 OSPF:
show ip ospf neighbor | show ip route ospf | show ip ospf database

! P07 ASAv Firewall:
show interface ip brief | show conn | show access-list | show route

! P08 VPN:
show crypto isakmp sa | show crypto ipsec sa | show ip route

! P09 Monitoring:
show logging | show snmp | show ntp status | show ip flow export

! P10 AAA:
show aaa sessions | show tacacs | show privilege

! P11 QoS:
show policy-map interface | show queue | show class-map
```

Save all outputs: `verification-outputs/project-NN-<device>-<command>.txt`

### Step 5 — Topology Screenshot from CML

```
CML GUI → open lab → take full topology screenshot
Save as: verification-outputs/screenshots/pNN-cml-topology-final.png

Also capture:
- Individual node terminal windows showing key show outputs
- Lab health panel (all nodes green)
```

### Step 6 — Break/Fix Log

```markdown
## Break/Fix — [Title] — YYYY-MM-DD

**Project/Phase:** P0X Phase Y
**What I did:** [Config change that caused the issue]

**Symptom:**
[show command output showing the problem]

**Root cause:**
[One sentence]

**Fix:**
```
[IOS commands that resolved it]
```

**Verification:**
[show command confirming fixed]

**Exam lesson:**
[One sentence connecting to CCNA/CCNP exam topic]
```

### Step 7 — Decision Log Entry

Add to `decision-log.md`:
```markdown
## Design Decision — YYYY-MM-DD

**Topic:** [e.g. OSPF timer tuning]
**Decision:** [What I chose]
**Why:** [Reason — exam requirement, lab constraint, design principle]
**Trade-off:** [What I gave up or accepted]
```

---

## Completed Project README Template

```markdown
---

## ✅ Project Complete — YYYY-MM-DD

### Topology

![CML Topology](verification-outputs/screenshots/pNN-cml-topology-final.png)

### What I Built
- [Bullet 1 — specific technology configured]
- [Bullet 2]
- [Bullet 3]

### Verification Summary
```
[Key show command output — 5-10 lines max]
[e.g. show ip ospf neighbor showing all FULL adjacencies]
```

### Problems Encountered and Fixed
| Problem | Root Cause | Fix |
|---------|-----------|-----|
| [e.g. OSPF not forming] | Area mismatch on R2 | Corrected area 0 on R2 Fa0/1 |

### CCNA/CCNP Topics Covered
| Topic | Where |
|-------|-------|
| [e.g. OSPFv2 neighbour states] | R1 ↔ R2 adjacency formation |
| [e.g. Default-information originate] | R1 injecting default route |

### STAR Result
**Result:** [2-3 sentences]

### Links
[Configs](configs/) | [Verification outputs](verification-outputs/) | [Decision log](decision-log.md) | [Break/Fix](troubleshooting/break-fix-log.md)
```

---

## Main README Update

```markdown
| [P03](projects/project-03-ospf-dynamic-routing/) | OSPF Dynamic Routing | ✅ Complete |

## ✅ Project 03 — OSPF Dynamic Routing

**Built:** YYYY-MM-DD | [Full detail →](projects/project-03-ospf-dynamic-routing/)

Implemented single-area OSPFv2 across 4 routers. All adjacencies FULL.
R1 injects default route via default-information originate. OSPFv3 added for IPv6.
BFD and IP SLA configured for fast convergence.

[→ Configs](projects/project-03-ospf-dynamic-routing/configs/) |
[→ Verification](projects/project-03-ospf-dynamic-routing/verification-outputs/) |
[→ Break/Fix](projects/project-03-ospf-dynamic-routing/troubleshooting/break-fix-log.md)
```

---

## Trigger Phrases

Load this skill when Leonel says:
- "document this CML project" / "CML phase complete"
- "save CML configs" / "export lab configs"
- "project complete" / "update CML README"
- "log the break fix" (for CML lab)
- After completing any CML Enterprise Lab project
