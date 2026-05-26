# Project 10 — Decision Log

## DL-01: Phase A / Phase B Split Apply

**Decision:** Split TACACS+ rollout into Phase A (AAA method lists only) and Phase B (vty line changes only). Run `test aaa group tacacs+` between them.

**Why:** Combining both in one block means vty lines are attached to an untested method list. If TACACS is unreachable or misconfigured at commit time, vty becomes inaccessible immediately and the only recovery is the console. Splitting the apply creates a safe checkpoint.

## DL-02: Console Safeguard Applied Before Phase B on Every Device

**Decision:** Apply `aaa authentication login CONSOLE local` + `line con 0 / login authentication CONSOLE` on every device before changing vty lines.

**Why:** After `aaa new-model`, the console uses the `default` method list by default. If `default` includes `group tacacs+`, a TACACS outage locks the console. The safeguard decouples console and VTY authentication permanently.

## DL-03: Global `ip tacacs source-interface Loopback0` Instead of Per-Server

**Decision:** Use the global `ip tacacs source-interface Loopback0` command instead of `source-interface` inside the `tacacs server` block.

**Why:** IOL rejects the per-server syntax. The global command achieves the same result. Loopback0 is used because it is stable — physical interfaces can go down, Loopback0 does not.

## DL-04: admin User Added to TACACS+ Rather Than Relying on Local Fallback

**Decision:** Added the `admin` username to tac-plus.conf as a member of `netadmin` (priv 15).

**Why:** With `aaa authentication login default group tacacs+ local`, IOS tries TACACS first. If TACACS is reachable and the username does not exist in TACACS, the server rejects the login — IOS does not fall through to local. The `admin` user must exist in TACACS for normal admin logins to work while TACACS is healthy.

## DL-05: NOC-VIEW Proven Locally Before TACACS Integration

**Decision:** Phase 3 configured and tested the parser view without assigning `tacoper` to it via TACACS+.

**Why:** TACACS-to-view mapping adds another layer of complexity. Proving the view works locally first isolates the parser view feature from TACACS assignment. Integration (assigning the view via TACACS `service = exec { priv-lvl = 15 / set priv-view = NOC-VIEW }`) is the next controlled step in a future phase.

## DL-06: Phase 4 Not Applied — Platform Limitation Documented Honestly

**Decision:** No 802.1X configuration was applied to HQ-ASW1. Phase 4 is recorded as not completed.

**Why:** IOL-L2 accepts 802.1X configuration syntax but does not support `show dot1x all` or `show authentication sessions`. Without operational verification, applying the config and claiming completion would be dishonest. IOSvL2, which supports full 802.1X verification, is not available in this CML installation.

## DL-07: Unreachable Target Used for Local Fallback Test, Not Server Shutdown

**Decision:** Phase 6 Part A tested local fallback by pointing HQ-RTR1 at an unused IP (`10.1.99.250`) rather than shutting down HQ-TACACS.

**Why:** Shutting down HQ-TACACS globally would break all 7 enrolled devices simultaneously, making the lab unmanageable. Changing the server address on one device scopes the failure safely to HQ-RTR1 only.
