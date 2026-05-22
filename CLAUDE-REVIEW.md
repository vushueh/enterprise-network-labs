# Claude Review File

This file is written by **Claude Code** and read by **Codex**.

- Claude writes critique items here after reviewing Codex session logs or proposed configs
- Codex reads this at the START of every session and resolves OPEN items before new work
- **Only Claude writes to this file** — Codex reads it, does not write to it

---

## Two ways Claude sends feedback to Codex

### 1. Real-time (within a session)

Switch to Claude Code and say:
`"Read Codex's latest session and review the Phase X config before I apply it to CML"`
Claude reads the Codex session file directly — no copy-paste needed.

Claude responds with a `[CLAUDE-REVIEW]` block. If corrections needed, paste it back to Codex.
If APPROVED, apply directly to CML — no paste needed.

```
[CLAUDE-REVIEW] Project X / Phase X / Device: NAME
STATUS: APPROVED | CORRECTIONS REQUIRED

Issues found:
- description and fix

Corrected config:
! corrected lines

Safe to apply to CML: YES | NO
```

### 2. Persistent (between sessions — Codex reads at session start)

Claude appends entries below. Status meanings:
- **OPEN** = not yet addressed — resolve before starting new work
- **RESOLVED** = already fixed — read for context only
- **INFO** = no action needed, background context only

---

<!-- Claude appends persistent review entries below this line -->

<!-- ============================================================ -->
<!-- PROJECT 08 ARCHIVED — all items RESOLVED, project pushed ✅  -->
<!-- ============================================================ -->

## [RESOLVED] Project 08 / Phase 2 / HQ-RTR1 + BR-RTR1 — IKEv2/IPsec

**Reviewed by:** Claude Code
**Date:** 2026-05-11
**Status:** RESOLVED — Phase 2 fully verified and complete

### Correction applied
`crypto ikev2 policy P08-IKEV2-POLICY` → `crypto ikev2 policy 10` on both routers.
Codex applied this from CLAUDE-REVIEW.md. IKEv2 SA formed correctly after fix.

### Phase 2 verified
- IKEv2 SA: READY, AES-CBC-256, SHA256, DH Grp 14, PSK both sides
- IPsec SA: transport mode, esp-256-aes esp-sha256-hmac, ACTIVE(ACTIVE)
- GRE protocol 47 protected between 10.0.0.1 ↔ 10.0.0.2
- encaps/decaps counters incrementing after traceroute
- OSPF stayed FULL over encrypted Tunnel0
- Traceroute first hop still 10.0.100.2 / 10.0.100.1

### Platform caveat — PFS on IOL (document in project notes)
`set pfs group14` is correctly present in the running IPsec profile on both routers.
However IOL's crypto engine accepts the command but does not perform the additional
Diffie-Hellman exchange during CREATE_CHILD_SA. `show crypto ipsec sa` reports
`PFS (Y/N): N` even after `clear crypto session`. This is an IOL platform limitation,
not a configuration error. On real hardware or IOS XE, this would negotiate correctly
and display `PFS (Y/N): Y, DH group: DH Group 14`. Config is correct — document the
caveat in decision-log.md when pushing the project.

---

## [INFO] Project 08 / Phase 1 / HQ-RTR1 + BR-RTR1 — GRE Tunnel Baseline

**Reviewed by:** Claude Code (independent review against committed configs)
**Date:** 2026-05-10
**Status:** INFO — APPROVED, safe to apply to CML

**Verified against:**
- `project-05-internet-nat/configs/HQ-RTR1.txt` — HQ-RTR1 baseline
- `project-07-asav-firewall/configs/HQ-RTR1-changes.md` — P07 changes (NAT removed, E0/3 repurposed)
- `project-03-ospf-dynamic-routing/configs/BR-RTR1.txt` — BR-RTR1 baseline
- `project-03-ospf-dynamic-routing/configs/HQ-RTR1.txt` — OSPF key and cost reference

**All config assumptions verified correct:**

| Assumption | Evidence | Result |
|-----------|----------|--------|
| `tunnel source Ethernet0/1` on HQ-RTR1 | P05: E0/1 = `10.0.0.1/30` (WAN link to BR-RTR1) | ✅ |
| `tunnel destination 10.0.0.2` | P03: BR-RTR1 E0/1 = `10.0.0.2/30` on same /30 | ✅ |
| `tunnel source Ethernet0/1` on BR-RTR1 | P03: E0/1 = `10.0.0.2/30` (WAN link to HQ-RTR1) | ✅ |
| `tunnel destination 10.0.0.1` on BR-RTR1 | P05: HQ-RTR1 E0/1 = `10.0.0.1` | ✅ |
| `10.0.100.0/30` tunnel subnet | No conflicts with 10.1.x, 10.2.x, 10.0.0.x address space | ✅ |
| `ip ospf message-digest-key 1 md5 OSPF-WAN-KEY` | P03/P05: same key used on E0/1 and E0/2 both routers | ✅ |
| `ip ospf cost 5` on Tunnel0 | E0/1=cost 100 (fallback), E0/2=cost 10 (via WAN-RTR1). Cost 5 wins. | ✅ |
| `ip mtu 1400` / `ip tcp adjust-mss 1360` | GRE overhead = 24 bytes. 1400 MTU is correct conservative value. | ✅ |
| No `ip nat inside` on Tunnel0 | P07 Phase 2: all NAT fully removed from HQ-RTR1 | ✅ |
| `no passive-interface Tunnel0` in OSPF | P03/P05: both routers use `passive-interface default` — explicit no-passive required | ✅ |

**Three things to know before applying (no config changes needed):**

1. **Two OSPF adjacencies on HQ-RTR1 after Phase 1** — `show ip ospf neighbor` will show
   BR-RTR1 twice: once over physical E0/1 (cost 100, fallback) and once over Tunnel0 (cost 5,
   primary). This is correct — do not remove the physical adjacency.

2. **Verify `show ip interface brief` on BR-RTR1 before running verification traceroutes** —
   Confirm E0/1 is up/up and has `10.0.0.2` before testing tunnel reachability.

3. **OSPF on the tunnel uses interface-level config** (`ip ospf 1 area 0` directly on Tunnel0)
   rather than a `network` statement. Both methods work fine together in IOS.
   The `10.0.100.0/30` subnet will appear in `show ip ospf database` as expected.

**One improvement to consider (not required for Phase 1):**
- Add `keepalive 10 3` to Tunnel0 on both routers in a later phase — this lets OSPF
  detect tunnel failure faster than the default dead interval. Not critical for Phase 1.

## [CLAUDE-REVIEW] Project 10 / Phase 1 Pre-Check / TACACS+ and RADIUS Reachability

**Reviewed by:** Claude Code
**Date:** 2026-05-22
**Status:** OPEN — resolve all items below before typing `aaa new-model` on any device

---

### Diagnosis

The incomplete ARP on HQ-RTR1 is the key symptom. Routing is correct (10.1.99.0/24 is connected via Ethernet0/0.999). The problem is Layer 2: no ARP reply is coming back for 10.1.99.52.

The zero MACs in VLAN 1 on both distribution switches is a node-not-running signal — a running Linux node sends broadcast traffic and would appear in the MAC table. HQ-TACACS and/or HQ-RADIUS may not be started in CML yet.

---

### OPEN Item P10-01 — Confirm CML node state before touching any IOS config

Codex identified the right approach (find port, move to VLAN 999). But the empty MAC table suggests the server nodes may not be running. The CML canvas shows which switch interface connects to each node. Confirm HQ-TACACS and HQ-RADIUS are in STARTED state before proceeding.

**Resolution:** In CML, confirm both nodes are running. If stopped, start them. Then check `show mac address-table vlan 1` again to see if MACs appear.

---

### OPEN Item P10-02 — Move server switchports to VLAN 999 (confirmed correct approach)

Codex recommendation approved. After confirming node state, move the identified VLAN 1 switchports to VLAN 999. Do not move unrelated ports.

```text
! Example — confirm actual ports from CML canvas first:
configure terminal
interface EthernetX/X     ! HQ-TACACS port
 description HQ-TACACS-10.1.99.52
 switchport mode access
 switchport access vlan 999
 no shutdown
end

interface EthernetX/X     ! HQ-RADIUS port
 description HQ-RADIUS-10.1.99.53
 switchport mode access
 switchport access vlan 999
 no shutdown
end
write memory
```

Verify: `show vlan brief | include 999` and `show mac address-table vlan 999`.

**Resolution:** Ports moved to VLAN 999, server IPs confirmed from console, `ping 10.1.99.52` and `ping 10.1.99.53` both return 5/5 from HQ-RTR1 Loopback0. ARP entries resolve (no longer incomplete).

---

### OPEN Item P10-03 — Verify TACACS and RADIUS daemons are listening

Reachable IP is not the same as working AAA. Confirm the services are up before any IOS AAA config:

```bash
# On HQ-TACACS — tac_plus must be on TCP/49:
ss -tlnp | grep ':49'
systemctl status tac_plus

# On HQ-RADIUS — FreeRADIUS must be on UDP/1812 and 1813:
ss -ulnp | grep ':1812'
systemctl status freeradius
```

**Resolution:** Both daemons confirmed running and listening on correct ports.

---

### OPEN Item P10-04 — Local fallback user must exist on ALL devices before aaa new-model

Once `aaa new-model` is enabled, IOS routes all authentication through the configured method list. If TACACS is unreachable and no local user exists, the device becomes inaccessible. This must be verified BEFORE any device receives AAA configuration.

```text
! On every in-scope device — check first:
show running-config | include ^username

! If no local user exists, add one:
configure terminal
username p10admin privilege 15 secret P10LocalFallback2026
end
write memory
```

The AAA method list must include `local` as the final fallback:
```text
aaa authentication login default group tacacs+ local
```

Without a local user, the `local` fallback is useless.

**Resolution:** Local user confirmed on all in-scope devices before any AAA configuration is applied.

---

### Go / No-Go Gate for Phase 1 AAA Config

Do NOT proceed until all items below are resolved:

| Check | Pass Criteria |
|-------|--------------|
| HQ-TACACS node running in CML | Node in STARTED state |
| HQ-TACACS switchport in VLAN 999 | `show vlan brief` confirms |
| ping 10.1.99.52 from HQ-RTR1 Loopback0 | 5/5 |
| ARP 10.1.99.52 resolved | Full MAC, not Incomplete |
| tac_plus listening on TCP/49 | `ss -tlnp` returns result |
| HQ-RADIUS node running in CML | Node in STARTED state |
| HQ-RADIUS switchport in VLAN 999 | `show vlan brief` confirms |
| ping 10.1.99.53 from HQ-RTR1 Loopback0 | 5/5 |
| FreeRADIUS listening on UDP/1812 | `ss -ulnp` returns result |
| Local fallback user on all in-scope devices | `show run \| include ^username` not empty |

