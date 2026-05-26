# Project 10 - Claude Review Phase 1 Pre-Check

Date: 2026-05-22

## Verdict

Codex direction approved.

The correct sequence is:

1. Identify CML node state.
2. Identify exact server switchports from the CML canvas.
3. Move only those ports to VLAN 999.
4. Console-verify server IP and daemon state.
5. Retest reachability and ARP.
6. Only then start IOS AAA configuration.

## Required Additions Before AAA

### P10-01 - Check CML Node State First

The empty VLAN 1 MAC table is significant. A running Linux node usually generates some broadcast traffic. Zero MACs suggests `HQ-TACACS` and/or `HQ-RADIUS` may not be started in CML.

Check the CML canvas before touching switch config.

### P10-02 - Move Exact Ports To VLAN 999

Once nodes are confirmed running, identify exact switchports from the CML canvas. Do not guess from MAC tables.

Move the TACACS/RADIUS server ports to VLAN 999 with:

- interface description
- `switchport access vlan 999`
- `no shutdown`

Retest:

- Ping from `HQ-RTR1` source `Loopback0` or VLAN 999 source should succeed 5/5.
- ARP should change from incomplete to resolved MAC.

### P10-03 - Daemon Verification

Reachable IP does not prove AAA is working.

On `HQ-TACACS`:

```text
ss -tlnp | grep ':49'
```

On `HQ-RADIUS`:

```text
ss -ulnp | grep ':1812'
```

If either command returns empty, start/fix the server daemon before IOS AAA configuration.

### P10-04 - Local Fallback User Required

Before `aaa new-model`, confirm every device has a local privilege 15 fallback user:

```text
show running-config | include ^username
```

If a device has no local user, add one before applying AAA.

The planned method list is:

```text
aaa authentication login default group tacacs+ local
```

The `local` fallback only works if a local user actually exists.

## Status

Do not configure AAA until the full go/no-go checklist is green.
