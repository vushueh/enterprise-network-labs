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


## [CLAUDE-REVIEW] Project 10 / Phase 1 / HQ-RTR1 TACACS+ Pilot Config

**Reviewed by:** Claude Code
**Date:** 2026-05-22
**Status:** OPEN — three required fixes before applying; close all items below before Phase B

---

### OPEN Item P10-05 — Split apply into Phase A (AAA config) and Phase B (vty lines). Test between them.

The proposed config bundles AAA + method lists + vty line changes in one block. If TACACS is not responding after Phase A, the vty lines are already committed to the failing method list. Split the apply.

**Phase A — apply first:**
```
aaa new-model

tacacs server HQ-TACACS
 address ipv4 10.1.99.52
 key tacacs123
 source-interface Loopback0
 exit

aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
aaa accounting commands 15 default start-stop group tacacs+
aaa accounting exec default start-stop group tacacs+

end
```

**Gate test — run before Phase B:**
```
test aaa group tacacs+ tacadmin admin123 new-code
test aaa group tacacs+ tacoper oper123 new-code
```

Both must return `User was successfully authenticated` before continuing.

**Phase B — only if both tests pass:**
```
configure terminal
line vty 0 4
 login authentication default
 authorization exec default
 transport input ssh
 exit
end
write memory
```

**Resolution:** Phase A applied, both test aaa commands pass, Phase B applied with a new SSH session confirmed.

---

### OPEN Item P10-06 — Verify ping 10.1.99.52 source Loopback0 before Phase A

Reachability was tested from `source 10.1.99.1` (VLAN 999 subinterface). With `source-interface Loopback0`, TACACS connections originate from 10.0.255.1. Must verify this path specifically:

```
ping 10.1.99.52 source Loopback0 repeat 5
```

If this fails while source 10.1.99.1 succeeds, check tac-plus.conf for per-client IP restrictions.

**Resolution:** ping 10.1.99.52 source Loopback0 returns 5/5.

---

### OPEN Item P10-07 — Verify SSH keys exist on HQ-RTR1 before Phase B applies transport input ssh

Phase B adds `transport input ssh` to vty 0-4, which blocks Telnet. If SSH keys are not configured, vty lines become unreachable.

```
show running-config | include ^hostname|^ip domain|^crypto key
ip ssh version 2
```

If crypto keys are absent:
```
configure terminal
ip domain-name lab.local
crypto key generate rsa modulus 2048
ip ssh version 2
end
```

**Resolution:** SSH keys confirmed present before Phase B.

---

### OPEN Item P10-08 — Verify HQ-RTR1 local fallback user and tac-plus.conf exec block

Two sub-items:

**A — Local user on HQ-RTR1:**
```
show running-config | include ^username
```
Must show at least one `username X privilege 15 secret Y`. WAN-RTR1 was confirmed (P10 session files). HQ-RTR1 is unconfirmed.

If missing: `username p10admin privilege 15 secret P10LocalFallback2026`

**B — tac-plus.conf exec authorization block:**
Confirm tac-plus.conf has `service = exec { priv-lvl = X }` inside each group. The `test aaa group tacacs+` output will reveal this — `User was not successfully authorized` (not authentication) means the exec service block is missing or returning FAIL.

If missing from tac-plus.conf, add `default service = permit` to the group and ensure:
```
group = netadmin {
    default service = permit
    service = exec {
        priv-lvl = 15
    }
}
```

**Resolution:** Both confirmed before Phase A.

---

### Architecture Decisions Recorded

**Source interface: Loopback0 is correct.** Matches P09 monitoring design. HQ-TACACS has gateway 10.1.99.1, which routes back to 10.0.255.1. tac-plus global key accepts any client IP with correct key.

**Command authorization: NOT in Phase 1.** Proposed config correctly uses `aaa accounting commands 15` (non-blocking logging) without `aaa authorization commands` (TACACS must permit each command). Command authorization is Phase 2+ after TACACS is proven stable.

**Accounting `start-stop` is correct.** Commands execute even if TACACS accounting START acknowledgment is delayed or missing. Non-blocking.

**Rollback improvement (use this version):**
```
configure terminal
no aaa new-model
line vty 0 4
 login local
 transport input all
 no authorization exec default
end
write memory
```
`transport input all` restores Telnet as emergency recovery path. Narrow back to SSH only after stable.

**Note:** Perform rollback from console if possible. Do not close the current VTY session until a new session confirms login works after Phase B.


---

## Project 10 — Phase 3 Review (Parser Views)

### ~~RESOLVED~~ Item P10-09 — `ping` in parser views may need `include all ping` on IOL

`commands exec include ping` may not expose the full ping command tree on IOL images. If `ping` is unavailable or incomplete inside `NOC-VIEW`, change the line to:

```ios
commands exec include all ping
```

Stop and document the error output if ping behaves unexpectedly inside the view.

### ~~RESOLVED~~ Item P10-10 — Run `show parser view all` immediately after configuring NOC-VIEW

Before testing `enable view NOC-VIEW`, run:

```ios
show parser view all
```

This confirms the view was accepted and lists every permitted command. If the view is missing or empty, stop before testing.

### ~~RESOLVED~~ Item P10-11 — Confirm `enable secret` exists on HQ-RTR1 before applying Phase 3

Parser views require `enable secret` (not just `enable password`). Run this pre-check first:

```ios
show running-config | include ^enable secret
```

If no `enable secret` is shown, configure one before proceeding:

```ios
configure terminal
enable secret P10Enable2026
end
write memory
```

Do not proceed to `enable view` without confirming this.

---

## Project 10 — Phase 4 Review (802.1X)

### OPEN Item P10-12 — IOL-L2 may not support 802.1X — check before applying anything

`dot1x system-auth-control` and `authentication port-control auto` may be rejected on the IOL-L2 image. The `show dot1x all` pre-check in Step 2 exists to catch this. If either command returns an error or `Invalid input`, stop completely and document the output. Do not proceed to Steps 4 or 5 if the platform does not support dot1x.

### OPEN Item P10-13 — No 802.1X supplicant in CML — add `authentication open` before `port-control auto`

The endpoint on `Ethernet0/2` is a CML IOL device and cannot act as an 802.1X supplicant. With `authentication port-control auto` alone, the port goes unauthorized and blocks all traffic permanently.

Add `authentication open` to the pilot port config before applying `port-control auto`:

```ios
configure terminal
interface Ethernet0/2
 authentication open
 authentication port-control auto
 dot1x pae authenticator
end
write memory
```

`authentication open` allows traffic through even when authentication is incomplete. The port stays up while 802.1X runs in the background — which is the only way to observe dot1x behavior without a real supplicant.

### OPEN Item P10-14 — Check `clients.conf` before restarting HQ-RADIUS

If `clients.conf` already has a wildcard entry covering `10.0.0.0/8`, HQ-ASW1 (`10.1.99.13`) is already permitted and no file change is needed. Only restart HQ-RADIUS if the file was actually changed. Unnecessary restarts cause ARP stale entry issues (same problem seen in Phase 2 — required `clear arp 10.1.99.52` to recover).

---

## Project 10 — Phase 4 Closed (Platform Limitation)

Phase 4 802.1X is documented as not completed. IOSvL2 is not available in this CML installation. All alternative show commands were tested and rejected on IOL-L2. No configuration was applied. This is the correct and honest outcome.

**Future completion path:** Repeat Phase 4 when a CML image supporting `show dot1x all` and `show authentication sessions` is available.

---

## Project 10 — Phase 5 Review (AAA Accounting)

### OPEN Item P10-15 — `show tacacs` packet counter increase is weak evidence for accounting

TACACS counters increase for authentication, authorization, and accounting combined. Counter increase proves TACACS is communicating — not that accounting specifically is working. The accounting log file on HQ-TACACS is the only valid primary evidence for Phase 5.

### OPEN Item P10-16 — Close the SSH session fully before checking the accounting log

`start-stop` accounting sends START on session open and STOP on session close. Check the log only after the SSH session has fully exited and disconnected. A log with START but no STOP means the session is still open or the STOP record failed.

### OPEN Item P10-17 — Read the accounting log directly from HQ-TACACS console

On the HQ-TACACS CML node console:

```bash
cat /var/log/tacplus-acct.log
```

If the file is empty or not found:

```bash
ls -la /var/log/tacplus*
```

Some tac_plus builds use a different path or filename. Identify the actual file before concluding the log is missing.

### OPEN Item P10-18 — Per-command accounting may not appear on IOL — exec records are sufficient to pass

`aaa accounting commands 15` may not produce individual command records on IOL. Exec START/STOP records for the admin session are sufficient evidence for Phase 5 to pass. Document which record types are present — do not fail the phase if exec records appear but command records do not.
