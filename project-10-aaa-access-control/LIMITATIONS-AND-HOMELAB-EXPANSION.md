# Project 10 — Limitations and Homelab Expansion

## CML Lab Limitations

### L-01: 802.1X Unverifiable on IOL-L2

**Limitation:** IOL-L2 accepts 802.1X configuration commands but does not expose `show dot1x all` or `show authentication sessions`. Authentication state machine transitions cannot be observed.

**Homelab Fix:** Replace access switches with IOSvL2 nodes in CML, or use physical Catalyst hardware. IOSvL2 supports the full authentication manager framework including per-port session state, MAB fallback, and VLAN assignment via RADIUS.

### L-02: IOL Does Not Update TACACS Timeout Counters During Unreachable Test

**Limitation:** When the TACACS server address is changed to an unreachable IP, `show tacacs` retains the last-known `Server Status: Alive` and does not increment `Socket Timeouts` or `Failed Connect Attempts`. Counter evidence for the unreachable condition is not visible.

**Homelab Fix:** On real IOS or IOS XE, timeout counters increment correctly. The workaround used was to document the SSH fallback success as the primary evidence.

### L-03: `test aaa local auth default` Not Supported on IOL

**Limitation:** The command `test aaa local auth default <user> <password>` is rejected by IOL. Local credential verification before the failover test had to be done by explicitly resetting the local password.

**Homelab Fix:** Supported on IOS XE. On IOL, explicitly reset the local password before any failover test to guarantee the credential is known.

### L-04: HQ-TACACS TacPlus Node Does Not Expose Accounting Log

**Limitation:** The TacPlus node in CML does not provide interactive bash console access. `/var/log/tacplus-acct.log` could not be read to confirm accounting START/STOP records.

**Homelab Fix:** Deploy tac_plus on a real Linux VM with full SSH access. Run `tail -f /var/log/tacplus-acct.log` during live SSH sessions to observe real-time accounting records.

### L-05: `show aaa servers` Returns No Output on IOL

**Limitation:** `show aaa servers` is accepted by IOL but produces no output. `show tacacs` was used as the primary TACACS health indicator throughout.

**Homelab Fix:** `show aaa servers` works correctly on IOS XE and real hardware and provides richer per-server statistics.

### L-06: Per-Server `source-interface` Rejected by IOL

**Limitation:** `source-interface Loopback0` inside the `tacacs server` configuration block is rejected by IOL. The global `ip tacacs source-interface Loopback0` was used instead.

**Homelab Fix:** Not needed on real IOS XE — the per-server syntax works correctly on production hardware.

### L-07: HQ-FW1 (ASAv) Excluded from TACACS+ Rollout

**Limitation:** ASAv uses a completely different AAA syntax (`aaa-server`, `aaa authentication ssh console`, `aaa authorization exec`). It was excluded from Phase 1 to avoid mixing IOS and ASA procedures.

**Homelab Fix:** ASA TACACS+ configuration is a separate procedure. A dedicated phase would configure the `aaa-server` group and test SSH to the ASA management interface.

### L-08: No Real 802.1X Supplicant Available in CML

**Limitation:** CML IOL nodes cannot act as 802.1X supplicants. Even with `authentication open`, no EAP exchange occurs because the connected node does not initiate 802.1X. RADIUS logs would not show Access-Request events from a passive IOL endpoint.

**Homelab Fix:** Use a real Linux VM with `wpa_supplicant` configured as an EAP-MD5 or EAP-PEAP supplicant, connected to the access switch port. This enables observation of the full EAP exchange, RADIUS Access-Accept/Reject, and port state transitions.

---

## Homelab Expansion Path

| Capability | What to Add |
|-----------|-------------|
| Full 802.1X verification | IOSvL2 nodes in CML or physical Catalyst switches |
| Real supplicant | Linux VM with `wpa_supplicant` (EAP-MD5 or EAP-PEAP) |
| Accounting log access | tac_plus on a Linux VM with SSH access |
| ASA TACACS+ | Dedicated ASA AAA phase using `aaa-server` syntax |
| Command authorization | `aaa authorization commands 15 default group tacacs+` after accounting is proven |
| RADIUS dynamic VLAN assignment | FreeRADIUS `Tunnel-Type`, `Tunnel-Medium-Type`, `Tunnel-Private-Group-ID` attributes |
| TACACS+ per-command authorization | Authorize specific commands (e.g., permit `show`, deny `debug`, deny `reload`) |
