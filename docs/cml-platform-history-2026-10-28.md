# CML VM history and 2.10.1 upgrade evidence

**Owner:** Leonel · **Record date:** 28 October 2026 · **Scope:** existing CML
platform, upgrade, image catalog, client integration and capture workflow.
This dated record documents prior work; it does not reopen Projects 01–13
or authorize another infrastructure change.

## Why This Matters

I wanted a reliable lab platform that kept my existing study work while adding
new images, AI integration and packet analysis. A successful upgrade screen
alone would not prove that my labs, recovery path or client security survived.
I kept the operational guide separate so I can quickly find
[the exact Breakout/Wireshark steps](cml-platform-operations.md#daily-capture-quick-start).

## Portfolio Summary

| Part | My record |
|---|---|
| Situation | My enterprise series was built on CML 2.9. I had an existing Proxmox CML VM and wanted the 2.10.1 features without losing the lab collection. |
| Task | Establish a usable recovery copy, verify upgrade media, upgrade the existing controller, preserve old image bindings, and set up secure Windows tooling. |
| Action | I performed the approved manual operations and supplied console/UI evidence. Codex checked package signatures, retained backup/upgrade/import observations, prepared guarded client launchers, and documented the verified UI paths. |
| Result | CML 2.10.1 build 21, a completed PBS backup record, 33 added image definitions, healthy controller observations, working user-confirmed PowerShell 7 Breakout launch and captured traffic. Full restore, every-node regression and live-stream/save acceptance remain unproved. |

## How To Read This Record

- For everyday use, open [CML platform operations](cml-platform-operations.md).
- For the sequence and recovery boundary, read the dated phases below.
- For evidence strength, read [What I Proved](#what-i-proved) and
  [Technical Evidence](#technical-evidence).
- For icons and license choices, see
  [custom icons](cml-platform-operations.md#custom-icons).

## My Test Boundary

This publication is documentation only. It made no CML, Proxmox, PBS,
network, account, credential or client-policy changes. It did not start a
lab, a packet capture or an MCP tool call. Icon files were saved locally
at my request, without importing them into CML. No credential store,
encrypted blob, private key, raw configuration or screenshot was copied
into this repository.

This is a retrospective **DOC-only** evidence package. Sanitized text and
explicit evidence limits replace new screenshots; no new credentialed UI
actions were performed to obtain proof. Local source files remain local.

## Phase Status

These are dispositions of the documentation scope, not new queue projects.

| Phase | Documentation status |
|---|---|
| 1 — Existing VM and recovery baseline | Complete — known facts and unproved restore boundary recorded |
| 2 — Controller upgrade | Complete — historical outcome and smoke-test limits recorded |
| 3 — Reference image imports | Complete — catalog checks and runtime gaps recorded |
| 4 — MCP integration | Complete — recorded policy, client differences and approval limits recorded |
| 5 — Packet capture and icons | Complete — workflow, user observations and missing acceptance proof recorded |

## Phase 1 — Existing VM and recovery baseline

I began with an existing **Proxmox host `pve`, VM 114, named `CML2.9`**.
The original installation date, original ISO/OVA and first-install procedure
are not established by this record. At **27 October 2026 19:30:37 UTC**, SSH
inspection reported `cml2 2.9.0-3` and `virl2_client 2.9.0+build.3`.
The preflight counted **222 nodes, all STOPPED or CREATED**. That count is
stored lab inventory; it does not imply 222 running licensed nodes.

The earlier NFS backup had been deleted by me, and an aborted PBS copy was
not a usable recovery point. After explicit approval and verification that
no backup task was active, the backup lock was cleared. A replacement
**stop-mode PBS backup completed TASK OK / exit OK on 28 October 2026 at
01:44:44 UTC**, checked at 01:45:55. This established a recorded completed
backup before the upgrade; an actual restore was not tested.

### Recorded VM shape and recovery copy

| Item | Recorded value and evidence boundary |
|---|---|
| CPU | User-supplied UI values: 8 cores, 2 sockets, CPU type host, NUMA off; do not infer a resize or a separately measured total vCPU count. |
| Memory | User-supplied 50,048 MB. |
| Firmware/controller | OVMF, `virtio-scsi-single`. |
| Storage | 230 GiB ZFS main disk plus EFI disk. No disk resize or bridge change performed in this work. |
| PBS target | `ugreen-pbs`, datastore `ugreen-store`. |
| Backup identity | `vm/114/2026-10-28T01:27:48Z`. |
| Backup inventory | Main disk + EFI logical inventory: 246,961,161,061 bytes. This is logical content inventory, not physical backup storage consumed. |
| End of backup | VM stopped and unlocked; I later restarted it for the upgrade. |
| Recovery limit | No PBS integrity verification or restore rehearsal retained. A successful task is not proof of a bootable restored VM. |

## Phase 2 — Controller upgrade

I used the verified `cml2_p_2.10.1-21_amd64-23-pkg.zip` archive and the
extracted `cml2_2.10.1-21_amd64-23.pkg`. Archive integrity passed. Cisco's
verifier passed the certificate chain, certificate expiration checks and
SHA-512 package signature with exit code 0. The filename suffix **`-23`**
is packaging information; the installed version was **2.10.1 build 21**.
The local verification record predates the actual upgrade and explicitly
says it had not yet performed one; later installer/reboot evidence supplies
the outcome.

I restarted the VM, uploaded the package and used maintenance mode. The
documented CML 2.9 Cockpit output-timeout workaround changed
`LOG_MAX_RESTARTS` from 8 to 240, with a grep readback. The installer reported
**Global upgrade completed, code 0, at 02:24:31 UTC**, and package
`2.10.1-21` was confirmed at 02:25:20. The actual reboot occurred at
02:28:10. By 02:29:07 the kernel was `6.8.0-147-generic`, previously
`6.8.0-60-generic`; core services were active and no failed units were seen.

Labs remained visible, and the UI showed **CML_Personal Registered/Authorized,
20 nodes**. R1 and SW1 console prompts at 02:42 supplied a limited smoke
test. This did not establish complete configuration equality, end-to-end
connectivity or every-node health. Maintenance mode being switched off was
not separately read back. Later READY health observations strengthen the
controller-health evidence but do not substitute for that missing readback.

### Upgrade media identity

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| ZIP archive | 160,898,940 | `a646e0510614baad685b39b0bd35e5070954be5234236cee621b3791dfae7c58` |
| Extracted package | 161,095,680 | `da347f3bab4a2020796cdc781e676017181e328737afaf431aeb37c317ef81de` |

These hashes identify historical local files. They do not replace Cisco's
signature verification for any later download.

## Phase 3 — Reference image imports

I manually ran Cisco's **standard importer**, which returned exit 0.
The imports added **11 supplemental + 1 Splunk + 21 FCS = 33** image
definitions, increasing the catalog from **22 to 55**. Catalog size is
independent of the license's running-node allowance. The import inspections
checked metadata, disk payload associations and service/core counters; they
did not boot each new image.

I accepted the possibility that **Automatic** image selection could choose
newer images on future initialization or after a wipe. Existing files and
observed instantiated bindings were preserved. In the final FCS comparison,
all **47 pre-existing active node-definition hashes** were unchanged, four
sampled legacy disk hashes matched, and observed QEMU/IOL bindings remained
unchanged. Those observations do not prove every lab's configured
Automatic/explicit flag: protected configuration was unreadable to that
inspection account. No lab selection was pinned or changed by the agent.

| Media | Size | Retained verification |
|---|---:|---|
| `refplat-20260611-supplemental.iso` | 15,620,308,992 bytes | Cisco signature valid; 11 additions. |
| `refplat-20260701-splunk.iso` | 1,806,141,440 bytes | SHA-256 `98aac1cda7d1c48e63ac90f152169c228239b982e37ad1d2e2d8d7ee168dd207`; 1 addition. |
| `refplat-20260409-fcs.iso` | 15,638,921,216 bytes | SHA-256 `075369b39fac0053a69aab44611dd5c4695f2cbff6c07a14f4eee75e8a671abf`; 21 additions. |

Local and remote ISO sizes/hashes matched in the retained history. The
nonfatal CSR quote-format patch rejection did not replace the active
definition; rejection artifacts were preserved. A proposed custom wrapper
was disabled and not executed. There was no custom cross-ID hard-link
preparation. The standard importer cleaned its staging ISO as expected;
original verified media remained on the PC.

At **04:25:44 UTC**, the post-import check recorded healthy services and
zero failed units, with about **154 GiB free in `/var`**. An earlier
02:52 observation had about 184.83 GiB free in `/var` and 5.09 GiB in root.
Those are different times, not a capacity contradiction. ZFS was healthy
with 13% physical use but 91.18% reserved allocation and 158.56 GiB of
allocation headroom in the earlier observation. No storage resize was made.

New-image runtime qualification and an authenticated UI/API catalog audit
were not performed in that postflight. Splunk was not booted and its EULA
was not accepted. ISE download/import remains unresolved. New image presence
is not evidence that it runs correctly or that its terms were accepted.

## Phase 4 — MCP integration

I progressed from an initially inactive MCP service to seven read tools and
then the **51 known registered tools** I requested. The fixed ACL and local
proxy deny unknown tools and unlisted users. The encrypted user-bound
credential and verified TLS hostname kept authentication material out of
plaintext client configuration. The
[MCP operations section](cml-platform-operations.md#mcp-integration-and-its-security-boundary)
records the launcher paths and client-specific limits.

Initialization and tool discovery used protocol `2025-03-26`. Separately
approved status calls returned healthy licensed READY results; the retained
05:31 call completed at **05:31:51.115 UTC**. Earlier transient 502 errors
stopped reproducing without a known routing or permission fix; their cause
remains unknown. Only the Codex `mcp_servers.cml` configuration scope was
added in that setup, and unrelated settings such as `node_repl` were
preserved with a protected backup. This does not establish native approval
popup enforcement.

The latest conversation policy permits read-only inspection and requires
approval for each mutating CML call. Recorded client prompt settings may be
stricter; this documentation did not change them. Claude Desktop discovery
showed 51 tools and Manual mode, with a local tool-call-blocking guard still
pending its per-tool approval verification. A later **user-supplied Claude
Code report** said user-scope CML/`permissions.ask` was configured, a popup
was seen, the Code-only guard was removed with approval, and two status calls
succeeded. That report was not independently verified and does not prove
Claude Desktop was completed. Desktop, Code and Codex remain separate clients.

## Phase 5 — Packet capture and icons

On 28 October 2026 I manually started the lab named
**2026-10-25 Standard IPv4 ACL Order STARTER**. Its inspected topology had
five booted nodes, **R1, SW1, PC20, PC21 and SERVER**, four links and no
external connectors. The observed link was **SW1 Ethernet0/0 ↔ R1
Ethernet0/0**. My supplied table contained **44 packet rows across about
66 seconds**, including R1 CDP at rows 6/40 and SW1 CDP at row 19, plus
STP, LOOP and ICMPv6. This was captured traffic, not a CDP-only BPF result.
It did not prove an ACL test, ACL mastery or a saved capture file.

Breakout 2.10.1 and Wireshark 4.6.9 were prepared with a guarded local
launcher. Windows PowerShell 5.1 failed; I confirmed the PowerShell 7 path
worked. The installed CML/Breakout assets established the capture controls
and active-stream selection workflow. I also said the custom-icon demo
worked, but its final save/global scope was not established. The
[operations guide](cml-platform-operations.md) retains the exact steps and
the limits rather than treating either observation as broader acceptance.

## What I Proved

| Area | Supported conclusion | Remaining gap |
|---|---|---|
| Existing VM | CML 2.9 package baseline and VM identity recorded | Original installation provenance/date/process unknown |
| Recovery | Replacement PBS stop backup finished successfully | No PBS integrity verify or actual restore/boot test |
| Upgrade | Installer exit 0, installed 2.10.1-21, reboot/new kernel/services | No full config diff, every-node regression or maintenance-off readback |
| Images | 33 additions, 55 total; preserved sampled disks/bindings and 47 definition hashes | No new-image runtime acceptance or authenticated catalog audit; ISE unresolved |
| MCP | Discovery and approved health calls succeeded; fail-closed controls documented | Native approval enforcement/client persistence not independently proved |
| Capture | Packets including CDP observed on the intended R1/SW1 link | Live Wireshark stream, saved/reopened PCAP and ACL behavior not independently proved |
| Icons | Verified editor controls and user-confirmed demonstration; safe local download | Exact saved state/global effect and per-node override not verified |

## Technical Evidence

The following local references identify retained source material. They are
**not portable repository links** and should be inspected only for the
specific nonsecret evidence needed. Do not bulk-copy the directories.

| Local reference under `%USERPROFILE%` | What it contributes |
|---|---|
| `Documents\Codex\2026-10-27\task-7\cml-upgrade-2.10.1-23\verification.txt` | Directly re-read for this publication: archive/package size, hashes, verifier command and exit 0. This early record predates upgrade execution. |
| `Documents\Codex\2026-10-27\task-7\cml-fcs-20260409\postimport.txt` | Directly re-read: standard-importer exit 0, 55 image counter, 47 unchanged definitions, sampled disk/binding preservation, service/capacity checks and runtime limits. |
| `Documents\Codex\2026-10-27\task-10\cml-mcp-setup\approved-status-once-20261028T0530.json` | Directly re-read: exactly one approved request, timestamps, licensed/READY healthy result. |
| `.codex\cml-mcp-readonly\CML-MCP-HANDOFF-FOR-CLAUDE.md` | Directly re-read: transport, TLS, private credential method, paths, pinned policy and historical client setup limits. Historical approval wording is superseded by later user policy; it was not copied as current authority. |
| `Documents\Codex\2026-10-27\task-9\breakout\Start-CmlBreakout.ps1` | Directly re-read: binary/config checks, loopback, private runtime authentication and foreground lifecycle. Credential files were not opened. |
| Sanitized recovered session observations and user reports | Backup/installer/reboot chronology, VM UI values, smoke-test/capture observations and Code-specific report; these have the evidence limits described above. |

Upstream context: [Cisco 2.10 release notes](https://developer.cisco.com/docs/modeling-labs/cml-release-notes/),
[in-place upgrade procedure](https://developer.cisco.com/docs/modeling-labs/in-place-upgrade/),
[MCP usage](https://developer.cisco.com/docs/modeling-labs/mcp-server-usage/),
and [node definition editor](https://developer.cisco.com/docs/modeling-labs/creating-a-new-node-definition/).
Vendor procedures explain the supported mechanisms; they do not prove this
VM followed every step or supply authorization to repeat it.

## How We Worked Together

### My Input And How I Helped

I requested the upgrade/tooling work, approved the scoped live actions,
performed manual upload/import and lab operations, supplied UI/console and
packet observations, confirmed the PowerShell 7 launch, and requested this
documentation publication and Downloads icon folder.

### What Codex Did And How

Codex inspected the retained evidence, checked package/media integrity,
prepared guarded local integration and capture support, distinguished direct
verification from reports, researched icon sources, and wrote/published this
scoped retrospective. The publication itself used no live CML changes.

### What Claude Did And How

Claude Desktop was a separately configured discovery client. The later Claude
Code connection outcome came from my report; this documentation did not
independently run Claude Code or claim a Claude review of the final package.

### How We Communicated And Completed The Project

I supplied the manual observations and confirmations; the documentation ties
them to dated checks and leaves unverified acceptance items visible. The
existing 13-project series and its queue status remain unchanged.

### Pushback And How We Resolved It

The failed PowerShell 5.1 launch was resolved by using the installed
PowerShell 7 runtime while preserving the launcher's guards. The unusable
earlier backup attempts were replaced by the recorded completed PBS job.
Automatic image-selection changes were explicitly accepted before the FCS
import; existing observed files/bindings were checked afterward. Other
unproved results remain limitations rather than invented passes.

## Reproduce Or Re-Verify

Use the [daily operations guide](cml-platform-operations.md) for captures and
icons. Future controller upgrades need a separately authorized change window
with a checked recovery copy, verified signed media, current vendor guidance,
stopped labs, maintenance-state checks and an explicit postflight. The prior
timeout workaround is history, not a blanket instruction for another version.

For a fuller preservation test, export/compare sanitized lab definitions and
configs, qualify representative existing and new images, and check actual
traffic. For recovery proof, schedule an isolated restore test; do not restore
VM 114 over the running controller as a documentation check.

## Rollback and recovery facts

The PBS snapshot above is the recorded pre-upgrade recovery artifact, not a
tested automatic rollback. No downgrade or restore was performed. Do not
attempt a package downgrade or assume uninstalling 2.10.1 restores lab state.
A recovery decision needs the actual backup's current availability, an
approved outage/restore plan and isolation to prevent a duplicate controller
IP or license conflict. Record data created since the snapshot before any
authorized restore because it would not be in that backup.

Client configuration backups and prior root-only controller-policy backups
were retained in the setup history. Their existence does not authorize
blind restoration or prove current validity. Do not commit the backups or
credential stores. For the separate older stale-container issue, use the
[existing guarded recovery record](cml-stale-container-recovery.md), with
fresh state checks and approval before repair.

## What Happens Next

This platform documentation closes the requested retrospective only. The next
operational acceptance opportunity is an explicitly authorized capture in
Wireshark that is saved and reopened, with sanitized evidence. It is not a new
master-queue project or permission to change CML. Original installation
provenance and the other gaps above remain visible until evidence is retained.
