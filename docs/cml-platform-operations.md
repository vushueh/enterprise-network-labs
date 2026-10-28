# CML platform operations: Breakout, Wireshark, MCP and icons

Recorded 28 October 2026. This is the operating guide for Leonel's existing
CML installation. Start with the capture workflow below; use the
[platform history and evidence record](cml-platform-history-2026-10-28.md) for
what was actually verified and what still needs proof.

## Daily capture quick start

The installed tools are CML **2.10.1 build 21**, Breakout **2.10.1**, Wireshark
**4.6.9**, and PowerShell **7.6.9**. The controller is
`https://cml-controller` (`192.168.10.177`). The Breakout page runs locally at
`http://127.0.0.1:8080` while its launcher is running.

### 1. Start Breakout once for the session

Open a PowerShell terminal under the same Windows account that owns the
existing private credential, then run this exact command:

```powershell
& 'C:\Program Files\PowerShell\7\pwsh.exe' -NoLogo -NoProfile -File 'C:\Users\CHONGONG\Documents\Codex\2026-10-27\task-9\breakout\Start-CmlBreakout.ps1'
```

Keep that terminal open. The launcher waits for the foreground Breakout
process; closing or interrupting it ends this session. Open
`http://127.0.0.1:8080` in the browser. Start Breakout once per session,
then reuse it for subsequent captures. It does not need restarting for each
link. No unattended startup was configured during this work.

Use the explicit `pwsh.exe` command above even if the terminal says
"PowerShell." Windows PowerShell **5.1** failed with the launcher's guarded
generic error. PowerShell **7** was subsequently confirmed working by Leonel.
The launcher uses runtime APIs available in PowerShell 7; do not weaken its
checks to make the older shell work.

### 2. Start the link capture in CML

1. Open the intended lab and confirm the relevant nodes and link are running.
2. Select the link, then open **Packet Capture**.
3. For the short example used here, set **Max Packets: 50** and
   **Max Time: 90** (seconds).
4. Leave the capture filter empty for a broad capture, or deliberately enter
   a Berkeley Packet Filter (BPF), such as `ether dst 01:00:0c:cc:cc:cc` to
   select the CDP destination MAC.
5. Start the capture. Continue immediately to Breakout while it is active.

The limits stop the capture when either limit is reached. Starting a new
capture on the same link discards the previous capture. Download/save any
capture you need before replacing it. Choose a longer approved observation
window if a periodic protocol has not sent a packet yet.

### 3. Open the active stream from Breakout

1. In Breakout, select **CAPTURES**.
2. Click the circular refresh control, whose tooltip is
   **Refresh capture data from controller**.
3. Find the row for the intended lab and link endpoints.
4. Click that row's **Capture Key** icon. Its tooltip is
   **Stream packet capture to Wireshark**.
5. In Wireshark, confirm packets arrive on the intended link. Enter `cdp` in
   the display-filter bar to inspect CDP if that is the study objective.
6. Save the capture in Wireshark if you need durable evidence. Review packet
   contents before sharing; a packet file can contain credentials and payloads.

Only **active** captures appear in CAPTURES. An empty list after a capture
finishes does not establish a Breakout fault. The grey **LABS Status** toggle
is unrelated to opening a packet stream.

`cdp` is a **Wireshark display filter**. It changes which already received
packets are shown. The CML BPF field is a **capture filter** that determines
which packets are collected. Do not interchange the two syntaxes.

The installed UI and controls were inspected. Leonel's packet table proved
traffic was captured. The evidence retained for this write-up does **not**
independently prove the complete live-stream-to-Wireshark handoff or a saved
PCAP file. The numbered workflow describes the installed mechanism; treat
successful live reception and a reopened saved capture as the next acceptance
checks when using it.

### File workflow: no Breakout needed

For a completed capture, use **DOWNLOAD** in the CML Packet Capture pane,
then open the downloaded capture in Wireshark. This is the simpler route
when live streaming is unnecessary. Save it before starting a new capture
on the same link. Do not wait for a finished capture to reappear in Breakout's
active-capture list.

## What the installed launcher protects

The launcher is local support material, not a script shipped by this repo.
Its directory is
`C:\Users\CHONGONG\Documents\Codex\2026-10-27\task-9\breakout`.
The binary is `C:\Users\CHONGONG\Downloads\breakout-windows-amd64.exe`.
Before starting it, the launcher checks the pinned binary hash and requires
the expected controller, Windows username, loopback listen address and
`verify_tls: true` in its configuration.

It obtains the existing Windows-user-bound DPAPI credential through the
authorized private mechanism, passes authentication to the child process
through its environment, and withholds raw standard output/error. The
credential is not placed in command arguments or committed YAML. Runtime
environment delivery still makes the child process sensitive; do not dump
its environment or diagnostics into chat or a repository.

The controller HTTPS connection verifies the trusted identity
`cml-controller`. The browser's local Breakout connection uses HTTP on
**127.0.0.1 only**. Do not change the bind to `0.0.0.0`, publish port 8080,
disable certificate validation, or replace the private mechanism with a
password in YAML. This guide does not authorize such changes.

## Troubleshooting by symptom

| Symptom | First checks and supported response |
|---|---|
| Generic guarded startup error | Run the exact PowerShell 7 command above under the credential-owning Windows account. Check the binary and configuration paths exist. The message deliberately hides private diagnostics; it does not identify a bad password by itself. |
| Local page does not open | Confirm the launcher terminal is still running and the URL is exactly `http://127.0.0.1:8080`. Inspect any listener conflict before starting another instance. Do not kill unrelated processes. |
| CAPTURES is empty | Start the desired capture in CML, switch to CAPTURES and refresh while it remains active. Check the lab and link identity. A 50-packet or 90-second limit may already have ended it. |
| Packets in CML but no stream | Verify the active row and Capture Key tooltip. Preserve the CML capture with DOWNLOAD and use the file workflow while diagnosing the local Wireshark handoff. |
| No CDP visible | Confirm the correct link, allow time for periodic advertisements and check whether a restrictive capture/display filter is hiding traffic. A display filter cannot recover packets excluded by a capture filter. |
| TLS or hostname error | Preserve verification. Check controller identity, the trusted public certificate and hostname resolution. Do not accept a changed certificate without independently validating it. |
| Binary hash check fails | Establish whether a deliberate Breakout upgrade changed the binary. Verify its source/version/hash before considering a launcher update; do not delete the check. |
| Authentication fails | Have Leonel use the existing private credential-entry helper for an explicitly authorized replacement. Do not print/decrypt the stored credential or paste an authorization header. |
| CML node says STOPPED but start reports container already running | See the separate [stale-container recovery record](cml-stale-container-recovery.md). Its check-only path and exact state-match guard matter; repair is a live action requiring its own approval. Do not wipe the lab. |

For read-only local diagnosis, a terminal can inspect listener ownership with
`Get-NetTCPConnection -LocalPort 8080 -State Listen` and check
`$PSVersionTable.PSVersion`. Avoid full process command/environment dumps.

## MCP integration and its security boundary

MCP exposes CML capabilities to an AI client. Cisco documents the controller
HTTP endpoint and `mcp-remote` bridge in its
[MCP usage guide](https://developer.cisco.com/docs/modeling-labs/mcp-server-usage/).
This installation uses `https://cml-controller/mcp`, backed by the existing
nginx HTTPS path and `virl2-mcp-server` service. The service's Unix socket is
`/run/virl2/mcp_server.sock`; the retained setup record reports no new public
TCP listener.

Local support lives in `C:\Users\CHONGONG\.codex\cml-mcp-readonly`.
The directory's historical `readonly` name is **not an access guarantee**:
the later pinned set contains 51 registered tools, including mutating tools.
Tool availability, account rights, client approval and a current user instruction
are separate requirements.

| Layer | Recorded arrangement and limit |
|---|---|
| Transport | PowerShell 7 launches Node and pinned `mcp-remote` 0.15.2 through `restricted-proxy.mjs`; normal TLS validation remains enabled. |
| Identity | Process-scoped public controller certificate and matching `cml-controller` name; the MCP hostname helper resolves locally without needing an OS-wide hosts edit for this connection. |
| Credential | Windows-user-bound DPAPI file, used only inside the launcher. The encrypted blob, decrypted value and authorization header stay out of Git, chat and process arguments. Base64 alone provides no secrecy. |
| Local capability guard | Exact pinned registered names; future/unknown tool names are denied. The proxy also refuses server-initiated client actions. |
| Controller policy | Explicit user/tool ACL, default deny, unauthenticated fallback disabled, startup preflight. Paths are `/etc/cml-mcp-readonly/acl.yaml`, `/etc/cml-mcp-readonly/preflight.py` and `/etc/systemd/system/virl2-mcp-server.service.d/90-codex-claude-readonly.conf`. Historical names do not imply read-only policy. |
| Codex | `Start-CmlMcp.ps1` and prompt approval settings recorded in `C:\Users\CHONGONG\.codex\config.toml`. Configuration inspection and a launcher test do not prove native approval dialogs were exercised. |
| Claude Desktop | Last inspected launcher is `Start-CmlDiscoveryOnly.ps1`; it permits discovery but rejects every tool call locally. Per-tool approval persistence was not proved in that retained record. Claude Desktop configuration does not configure Claude Code. |
| Device CLI | PyATS/device credentials were not configured in the retained setup. Seeing a CLI tool in the tool list does not prove device-login readiness. |

Do not remove the discovery-only guard or alter approval settings using this
guide. The latest conversation policy allows read-only inspection and requires
approval for each mutating CML call. Client settings may remain stricter.
Reconcile any older handoff wording with the user's **current**
authorization before an invocation. This documentation task authorized no
CML tool invocation, lab change, capture start, account edit or credential
change; none was needed to write it.

The last retained approved health call on 28 October 2026 returned valid
controller/compute health, admission state READY, licensed true, Enterprise
false, and no CPU/memory/disk overload. This is a dated observation, not
continuous monitoring or a guarantee that all 51 tools work.

## Custom icons

The verified CML route is **Tools → Node and Image Definitions → Node
Definitions → edit the intended definition → User Interface → Icon: custom
→ Upload Custom Icon**. The editor also offers **Image as Base64 URI**.
The installed UI accepts **PNG, JPEG or SVG below 100 KB**; SVG is preferred
for scaling. Keep well below the limit.

Changing a shared node definition, such as Alpine, can affect nodes using
that definition. Record the original definition/icon and choose the intended
scope before saving. A per-node Workbench override was not verified in this
session. Leonel said the demonstration worked; the exact final save and its
global scope were not established. No icon was imported by the documentation
agent.

### Recommended packs and saved selection

My primary choice is **[Affinity](https://github.com/ecceman/affinity)**:
network-specific router, switch, multilayer switch, firewall, load balancer,
wireless controller, server, storage, endpoint and cloud symbols in a coherent
style. Its [Unlicense](https://github.com/ecceman/affinity/blob/master/LICENSE)
permits adaptation and redistribution. Prefer **naked** for a clean topology
or **circle-blue** for more visual separation. Use one style throughout and
place descriptive node labels outside the artwork. The upstream collection's
556 SVG variants are not 556 distinct concepts; some variants exceed CML's
limit, so selecting a pack blindly is insufficient.

At my request, **65 SVGs** were saved in
`C:\Users\CHONGONG\Downloads\CML-Network-Icons`:
**43 naked + 22 selected circle-blue**. Source commit:
`48d4a4fa87957cb542678ed5952227028b8657f5`.
The files are 627–78,929 bytes, comfortably below 100,000 bytes.
The download includes `LICENSE-Affinity.txt`, `README.txt`, `inventory.csv`
with original URLs and upstream/local SHA-256 hashes, and a local
`preview.html` contact sheet. These are local paths, not repository assets.

Only the standard external SVG DTD declarations were removed; the artwork
was preserved. The saved files passed XML/root/viewBox, size, DTD/entity,
active-element, event-handler and external-content checks. Downloaded code
was not executed. These static checks do not establish CML import/rendering
acceptance. No third-party icon files are redistributed in this repository.

| Rank/use | Source | Why choose it / license boundary |
|---|---|---|
| 1 — CML network topology | [Affinity](https://github.com/ecceman/affinity) | Best overall fit for this lab: purpose-built network roles and editable SVG; Unlicense. Saved subset above. |
| 2 — Familiar Cisco diagrams | [Cisco topology icons](https://www.cisco.com/c/en/us/about/brand-center/network-topology-icons.html) | Vendor-authentic traditional symbols. Available packs include EPS/JPG, Visio and PowerPoint; not a ready SVG replacement. Cisco permits use without alteration; do not recolor/remix. See [copyright/use terms](https://www.cisco.com/c/en/us/about/brand-center/copyright-use.html). |
| 3 — Modern endpoint/UI roles | [Tabler](https://tabler.io/icons) | Broad 24×24 SVG set with consistent strokes; [MIT](https://tabler.io/license), retain required notices. More general-purpose than Affinity. |
| 4 — Alternative line style | [Lucide](https://lucide.dev/) | Clean general-purpose symbols; [ISC and applicable Feather notices](https://lucide.dev/license). Choose as an alternative style, not a random mixture. |

For cloud architectures, link to the official packs:
[AWS](https://aws.amazon.com/architecture/icons/),
[Azure](https://learn.microsoft.com/en-us/azure/architecture/icons/) and
[Google Cloud](https://cloud.google.com/icons/). Their product/brand terms
are separate from open-source icon licenses. AWS permits architecture-diagram
usage; Azure prohibits cropping, rotating, flipping or distorting its icons;
the Google landing page does not establish unrestricted redistribution.
They were not downloaded as part of this folder.

For physical rack/product drawings, use manufacturer stencils:
[Cisco](https://www.cisco.com/c/en/us/products/visio-stencil-listing.html),
[Juniper](https://www.juniper.net/us/en/products/icons-and-stencils.html) and
[Palo Alto Networks](https://www.paloaltonetworks.com/company/press-kit).
Check the source terms and logo rules before reuse. Changing an icon is a
visual choice; it does not change the simulated node's capabilities.

## Re-verify without broadening the task

Inspect local launcher versions, file presence, public certificate identity
and loopback listener ownership first. When the user authorizes an actual
capture, confirm packets in Wireshark, save the file, reopen it and record
the link/time/filter and packet count. Retain sanitized text if a screenshot
would expose credentials, private payload or unrelated windows.

For MCP, discovery is different from a tool invocation. Use current
authorization and client controls for any functional test; do not invoke a
read tool simply to prove this documentation remains accurate. Unknown or
uncertain outcomes require inspection before retries.
