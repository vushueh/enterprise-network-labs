# Enterprise Lab Credential Exposure Remediation

**Date:** 2026-07-14
**Scope:** `enterprise-network-labs` current branch, Git history, and the related
Cisco CML lab
**Current state:** Current-tip redaction prepared; live rotation and any approved
history cleanup remain open

## Why This Matters

I found lab credentials in tracked configuration and evidence files. Replacing
them in the newest commit prevents new readers from seeing them at the current
tip, but it does not make the old credentials safe. They may remain in earlier
Git commits and may still work in the CML lab until I rotate them.

## What I Changed In The Repository

I replaced credential values with typed placeholders such as
`<TACACS-SHARED-SECRET>`, `<LOCAL-USER-PASSWORD>`, and
`<IPSEC-PRESHARED-KEY>`. The remediation covers these credential classes:

- TACACS+ shared keys and user passwords
- Local IOS usernames and passwords
- Enable, line, and parser-view secrets
- SNMP communities and authentication/privacy secrets
- NTP and OSPF authentication keys
- IPsec pre-shared keys
- VTP domain passwords
- Automation passwords and authentication key strings

I kept usernames, device names, IP addressing, commands, and verification
context when they were not secrets. I also rechecked command syntax after the
redaction so that protocol words such as `tacacs+` were not mistaken for values.

## What I Verified

| Check | Result |
|---|---|
| Structured credential-value scan | No unredacted candidates at the current tip |
| Network credential-context scan | No remaining value-bearing matches outside typed placeholders |
| Placeholder-boundary scan | No credential placeholder joined to a word or token |
| Protocol repair scan | No remaining repair candidates |
| Gitleaks scan | Not run — Gitleaks is not installed in this environment |

These checks reduce publication risk, but they do not prove that every possible
secret format is absent. A supported secret scanner remains a required check
before any history rewrite or final security closure.

## What Leonel Needs To Do

Leonel owns the live CML changes. He should use console access and rotate one
dependency at a time without pasting new values into chat, terminal transcripts,
screenshots, or repository files.

1. Confirm console access and a tested local fallback account on every device.
2. Generate new values in a password manager or another private channel.
3. Rotate local, enable, line, and parser-view credentials one device at a time.
4. Rotate paired protocol secrets in controlled windows: OSPF, NTP, IPsec, VTP,
   and SNMP must be changed on both ends, across the VTP domain, or on the
   manager and device together.
5. Rotate TACACS+ user credentials and shared keys only after local fallback is
   proven. Change the server and one network device at a time.
6. Update private automation environment variables after device credentials are
   changed. Do not commit `.env` files or plaintext inventories.
7. Verify each service before proceeding to the next device or dependency.

## Verification After Rotation

Record only pass/fail evidence and redacted command output.

| Area | Minimum proof |
|---|---|
| Local access | Console login and privilege escalation succeed with the new private values |
| TACACS+ | Central login, expected privilege, accounting, and local fallback all work |
| OSPF | All expected neighbors return to `FULL` and routes remain stable |
| NTP | Peers are reachable and authentication is accepted |
| IPsec | IKE/IPsec security associations rebuild and protected traffic passes |
| VTP | The intended domain, mode, revision behavior, and VLAN state remain correct |
| SNMP | The monitoring system polls successfully; unauthorized values fail |
| Automation | Read-only collection succeeds without placing credentials in output |

Stop immediately if console fallback fails, an adjacency does not recover, the
VPN stays down, monitoring loses required visibility, or a device cannot be
reached through the approved management path. Restore the previous private value
from the password manager for that one dependency, then investigate before
continuing.

## Git History Decision

The current remediation does not rewrite old commits. After live rotation, I
should run a supported scanner against the full history and decide whether to:

- keep history intact because every exposed value is retired; or
- perform a separately approved coordinated history rewrite.

A history rewrite affects every clone and requires owner coordination, a clean
backup, collaborator instructions, remote verification, and an explicitly
approved force-push. It is not part of this change.

## Safe Evidence Rules

- Never store the new values in Git, chat, screenshots, or transcripts.
- Replace values with typed placeholders before saving evidence.
- Keep the password manager entry and rotation record outside this repository.
- Record the device, credential class, date, verification result, and operator—not
  the value itself.
- Treat all values found in old commits as compromised until rotation is proven.

## Closure Criteria

I can close the credential incident only when:

- the sanitized current tip is published and independently reviewed;
- every live credential class is rotated and verified;
- private automation inputs use the new values;
- a full-history supported scanner reports its findings; and
- the repository owner records the decision to retain or rewrite history.

Until then, the documentation migration may be published, but security status
must remain **live rotation pending**.
