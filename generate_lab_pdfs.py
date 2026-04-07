#!/usr/bin/env python3
"""
Generate Cisco-style PDF lab guides for Enterprise Network Labs Projects 01 and 02.
Embeds actual CML topology screenshots instead of ASCII text diagrams.
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Preformatted, Image, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from PIL import Image as PILImage

# ─── Cisco brand colors ───────────────────────────────────────────────────────
CISCO_BLUE   = colors.HexColor("#049fd9")
CISCO_DARK   = colors.HexColor("#1b2a4a")
CISCO_LIGHT  = colors.HexColor("#e8f4fb")
CISCO_GRAY   = colors.HexColor("#6b7280")
CISCO_GREEN  = colors.HexColor("#00bceb")
CISCO_WHITE  = colors.white
CODE_BG      = colors.HexColor("#1e1e2e")
CODE_FG      = colors.HexColor("#cdd6f4")

BASE = "/home/leonel/code/enterprise-network-labs"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def embed_image(path, max_width=470):
    """Return an Image flowable scaled to fit max_width (points), preserving aspect ratio."""
    if not os.path.exists(path):
        return Paragraph(f"<i>[Image not found: {path}]</i>", ParagraphStyle("miss", fontSize=8, textColor=colors.red))
    pil = PILImage.open(path)
    orig_w, orig_h = pil.size
    scale = min(max_width / orig_w, 1.0)
    return Image(path, width=orig_w * scale, height=orig_h * scale)


def make_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "title", fontSize=22, leading=28, textColor=CISCO_WHITE,
            fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontSize=13, leading=18, textColor=CISCO_LIGHT,
            fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4,
        ),
        "h1": ParagraphStyle(
            "h1", fontSize=14, leading=18, textColor=CISCO_WHITE,
            fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6,
            backColor=CISCO_DARK, leftIndent=-12, rightIndent=-12,
            borderPad=6,
        ),
        "h2": ParagraphStyle(
            "h2", fontSize=12, leading=16, textColor=CISCO_DARK,
            fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4,
            borderPad=4,
        ),
        "h3": ParagraphStyle(
            "h3", fontSize=10, leading=14, textColor=CISCO_BLUE,
            fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body", fontSize=9, leading=13, textColor=colors.black,
            fontName="Helvetica", spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontSize=9, leading=13, textColor=colors.black,
            fontName="Helvetica", leftIndent=16, spaceAfter=3,
            bulletIndent=6,
        ),
        "caption": ParagraphStyle(
            "caption", fontSize=8, leading=11, textColor=CISCO_GRAY,
            fontName="Helvetica-Oblique", alignment=TA_CENTER, spaceAfter=6,
        ),
        "code": ParagraphStyle(
            "code", fontSize=7.5, leading=11, textColor=CODE_FG,
            fontName="Courier", backColor=CODE_BG, spaceAfter=8,
            leftIndent=8, rightIndent=8, borderPad=6,
        ),
        "why": ParagraphStyle(
            "why", fontSize=8.5, leading=12, textColor=CISCO_DARK,
            fontName="Helvetica-Oblique", backColor=CISCO_LIGHT,
            leftIndent=12, rightIndent=12, spaceAfter=8, borderPad=5,
        ),
        "label": ParagraphStyle(
            "label", fontSize=8, leading=11, textColor=CISCO_GRAY,
            fontName="Helvetica-Bold", spaceAfter=2,
        ),
    }
    return styles


def table_style():
    return TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  CISCO_DARK),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  CISCO_WHITE),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CISCO_WHITE, CISCO_LIGHT]),
        ("GRID",        (0, 0), (-1, -1), 0.5, CISCO_GRAY),
        ("ALIGN",       (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ])


def section_header(text, styles):
    return [
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=2, color=CISCO_BLUE),
        Paragraph(f"  {text}", styles["h1"]),
        Spacer(1, 4),
    ]


def subsection(text, styles):
    return [Paragraph(text, styles["h2"])]


def code_block(text, styles):
    # Strip leading blank line if present
    lines = text.strip("\n").split("\n")
    return Preformatted("\n".join(lines), styles["code"])


def why_block(text, styles):
    return Paragraph(f"WHY: {text}", styles["why"])


def screenshot(path, caption, styles):
    items = []
    items.append(Spacer(1, 4))
    items.append(embed_image(path))
    items.append(Paragraph(caption, styles["caption"]))
    return items


# ─── Cover page ───────────────────────────────────────────────────────────────

def cover_page(story, title, subtitle, project_num, styles):
    # Dark header bar
    story.append(Spacer(1, 1.2 * inch))
    story.append(Table(
        [[Paragraph(title, styles["title"])],
         [Paragraph(subtitle, styles["subtitle"])]],
        colWidths=[6.5 * inch],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), CISCO_DARK),
            ("TOPPADDING", (0, 0), (-1, -1), 16),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
            ("LEFTPADDING", (0, 0), (-1, -1), 20),
            ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ])
    ))
    story.append(Spacer(1, 0.3 * inch))

    meta = [
        ["Series", "Enterprise Network Labs — CML 2.9"],
        ["Project", project_num],
        ["Platform", "Cisco Modeling Labs 2.9 (IOSv + IOL-L2)"],
        ["Author", "Leonel Chongong"],
        ["Purpose", "CCNA 200-301 hands-on lab documentation"],
    ]
    story.append(Table(
        meta,
        colWidths=[1.5 * inch, 5.0 * inch],
        style=TableStyle([
            ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE",  (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), CISCO_DARK),
            ("GRID",      (0, 0), (-1, -1), 0.5, CISCO_GRAY),
            ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ])
    ))
    story.append(PageBreak())


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT 01 — Campus Foundation
# ═══════════════════════════════════════════════════════════════════════════════

def build_project01(output_path):
    styles = make_styles()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    )
    story = []
    base = f"{BASE}/project-01-campus-foundation"
    ss   = f"{base}/verification/screenshots"

    # Cover
    cover_page(story,
               "Project 01 — Campus Foundation",
               "VLANs · Trunking · Inter-VLAN Routing · STP · SSH Hardening",
               "01 of 13", styles)

    # ── Overview ──────────────────────────────────────────────────────────────
    story += section_header("Overview", styles)
    story.append(Paragraph(
        "Build a fully segmented single-site campus network from a blank canvas. "
        "Multiple departments require isolation, a dedicated management plane, and "
        "controlled inter-department communication via router-on-a-stick. "
        "STP root placement and SSH access are deliberately hardened.",
        styles["body"]))
    story.append(Spacer(1, 6))

    story += subsection("STAR Summary", styles)
    star = [
        ["Situation", "Studying VLANs, trunking, and inter-VLAN routing as separate topics without a full end-to-end design."],
        ["Task", "Design and build a segmented campus network from a written requirement — VLAN scheme, IPs, trunks, STP, SSH."],
        ["Action", "Deployed VLANs 100/200/300/999/1000, router-on-a-stick, trunk pruning, deliberate STP root election, SSH ACL."],
        ["Result", "Can design a multi-VLAN campus from scratch, justify every design decision, and verify all features working together."],
    ]
    story.append(Table(star, colWidths=[1.1 * inch, 5.4 * inch], style=table_style()))
    story.append(Spacer(1, 8))

    # ── Topology ──────────────────────────────────────────────────────────────
    story += section_header("Lab Topology", styles)
    topology_path = f"{base}/diagrams/cml-topology.png"
    story.append(embed_image(topology_path, max_width=470))
    story.append(Paragraph(
        "Figure 1 — CML Lab Topology (Cisco Modeling Labs 2.9)",
        styles["caption"]))
    story.append(Spacer(1, 6))

    # ── Technologies ──────────────────────────────────────────────────────────
    story += section_header("Technologies Used", styles)
    techs = [
        "VLANs 100 (Engineering), 200 (Sales), 300 (Guest), 999 (Management), 1000 (Native/Unused)",
        "802.1Q Trunking with explicit VLAN allowed lists (VLAN pruning)",
        "Native VLAN hardening — VLAN 1000 carries no routable traffic",
        "Router-on-a-Stick inter-VLAN routing (HQ-RTR1 subinterfaces)",
        "Rapid-PVST+ with deliberate root bridge election (priority 4096/8192)",
        "PortFast + BPDU Guard on all access ports",
        "SSH v2 with VTY ACL restricting management to VLAN 999 only",
        "CDP neighbor verification for physical link confirmation",
        "Interface descriptions on every link",
    ]
    for t in techs:
        story.append(Paragraph(f"\u2022  {t}", styles["bullet"]))
    story.append(Spacer(1, 6))

    # ── IP Addressing ─────────────────────────────────────────────────────────
    story += section_header("IP Addressing", styles)
    ip_data = [
        ["Device", "Interface", "IP Address", "Purpose"],
        ["HQ-RTR1", "E0/0.100", "10.1.100.1/24", "Engineering gateway"],
        ["HQ-RTR1", "E0/0.200", "10.1.200.1/24", "Sales gateway"],
        ["HQ-RTR1", "E0/0.300", "10.1.44.1/24",  "Guest gateway"],
        ["HQ-RTR1", "E0/0.999", "10.1.99.1/24",  "Management gateway"],
        ["HQ-RTR1", "Loopback0", "10.0.255.1/32", "Router ID"],
        ["HQ-DSW1", "Vlan999",  "10.1.99.11/24", "Management SVI"],
        ["HQ-DSW2", "Vlan999",  "10.1.99.12/24", "Management SVI"],
        ["HQ-ASW1", "Vlan999",  "10.1.99.13/24", "Management SVI"],
        ["HQ-ASW2", "Vlan999",  "10.1.99.14/24", "Management SVI"],
        ["PC-ENG1",  "eth0",    "10.1.100.10/24", "Engineering endpoint"],
        ["PC-SALES1","eth0",    "10.1.200.10/24", "Sales endpoint"],
        ["PC-MGMT1", "eth0",    "10.1.99.100/24", "Management endpoint"],
    ]
    story.append(Table(ip_data, colWidths=[1.2*inch, 1.2*inch, 1.6*inch, 2.5*inch],
                       style=table_style()))
    story.append(Spacer(1, 6))

    # ── Phase 1: VLANs ────────────────────────────────────────────────────────
    story += section_header("Phase 1 — VLAN Configuration", styles)
    story += subsection("HQ-DSW1 / HQ-DSW2 — VLAN Database", styles)
    story.append(why_block(
        "VLANs must be created in the VLAN database on every switch that will carry them. "
        "VLAN 1000 is used as native VLAN to isolate untagged frames from all data VLANs.",
        styles))
    story.append(code_block("""vlan 100
 name ENGINEERING
vlan 200
 name SALES
vlan 300
 name GUEST
vlan 999
 name MANAGEMENT
vlan 1000
 name NATIVE-UNUSED""", styles))

    story += subsection("HQ-ASW1 — Access Port Configuration", styles)
    story.append(why_block(
        "Access ports carry a single VLAN. switchport nonegotiate disables DTP negotiation. "
        "PortFast skips STP listening/learning for endpoint ports. BPDU Guard err-disables "
        "the port if a switch is accidentally connected.",
        styles))
    story.append(code_block("""interface Ethernet0/0
 description ACCESS-PC-ENG1-VLAN100
 switchport mode access
 switchport access vlan 100
 switchport nonegotiate
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown""", styles))

    story += subsection("Verification Screenshots", styles)
    story += screenshot(f"{ss}/p01-ph1-show-vlan-brief-ASW1.png",
                        "show vlan brief — HQ-ASW1: VLANs 100, 200, 300, 999, 1000 active", styles)
    story += screenshot(f"{ss}/p01-ph1-show-vlan-brief-ASW2.png",
                        "show vlan brief — HQ-ASW2: matching VLAN database", styles)

    # ── Phase 2: Trunking ─────────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Phase 2 — Trunking", styles)
    story += subsection("HQ-DSW1 — Trunk Port Configuration", styles)
    story.append(why_block(
        "encapsulation dot1q must be set before switchport mode trunk on IOL-L2 images. "
        "Explicit allowed VLAN lists prevent accidental leakage of VLANs to uplinks. "
        "Native VLAN 1000 is set on both ends to prevent native VLAN mismatch.",
        styles))
    story.append(code_block("""interface Ethernet0/0
 description TRUNK-TO-HQ-RTR1-E0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 1000
 switchport trunk allowed vlan 100,200,300,999,1000
 no shutdown

interface Ethernet0/1
 description TRUNK-TO-HQ-DSW2-E0/1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 1000
 switchport trunk allowed vlan 100,200,300,999,1000
 no shutdown

interface Ethernet1/0
 description TRUNK-TO-HQ-ASW1-E0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 1000
 switchport trunk allowed vlan 100,200,300,999,1000
 no shutdown""", styles))

    story += subsection("Verification Screenshots", styles)
    story += screenshot(f"{ss}/p01-ph2-show-cdp-neighbors-DSW1.png",
                        "show cdp neighbors — HQ-DSW1: RTR1, DSW2, ASW1, ASW2 confirmed", styles)
    story += screenshot(f"{ss}/p01-ph2-show-interfaces-trunk-DSW1.png",
                        "show interfaces trunk — HQ-DSW1: all uplinks trunking, native VLAN 1000", styles)
    story += screenshot(f"{ss}/p01-ph2-show-interfaces-trunk-DSW2.png",
                        "show interfaces trunk — HQ-DSW2: uplinks trunking correctly", styles)

    # ── Phase 3: Inter-VLAN Routing ───────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Phase 3 — Inter-VLAN Routing (Router-on-a-Stick)", styles)
    story += subsection("HQ-RTR1 — Subinterface Configuration", styles)
    story.append(why_block(
        "Router-on-a-stick uses subinterfaces — one per VLAN — on a single physical trunk link. "
        "encapsulation dot1Q tells IOS which VLAN tag to match. The parent interface has no IP. "
        "Each subinterface IP becomes the default gateway for that VLAN's hosts.",
        styles))
    story.append(code_block("""interface Ethernet0/0
 description TRUNK-TO-HQ-DSW1-E0/0
 no ip address
 no shutdown

interface Ethernet0/0.100
 description GATEWAY-VLAN100-ENGINEERING
 encapsulation dot1Q 100
 ip address 10.1.100.1 255.255.255.0
 no shutdown

interface Ethernet0/0.200
 description GATEWAY-VLAN200-SALES
 encapsulation dot1Q 200
 ip address 10.1.200.1 255.255.255.0
 no shutdown

interface Ethernet0/0.300
 description GATEWAY-VLAN300-GUEST
 encapsulation dot1Q 300
 ip address 10.1.44.1 255.255.255.0
 no shutdown

interface Ethernet0/0.999
 description GATEWAY-VLAN999-MANAGEMENT
 encapsulation dot1Q 999
 ip address 10.1.99.1 255.255.255.0
 no shutdown

interface Ethernet0/0.1000
 description NATIVE-VLAN1000-UNUSED
 encapsulation dot1Q 1000 native
 no shutdown""", styles))

    story += subsection("Verification Screenshots", styles)
    story += screenshot(f"{ss}/p01-ph3-show-ip-interface-brief-RTR1.png",
                        "show ip interface brief — HQ-RTR1: all subinterfaces up/up", styles)
    story += screenshot(f"{ss}/p01-ph3-show-ip-route-RTR1.png",
                        "show ip route — HQ-RTR1: connected routes for all 4 VLANs", styles)
    story += screenshot(f"{ss}/p01-ph3-ping-cross-vlan-ENG1-to-SALES1.png",
                        "Cross-VLAN ping — PC-ENG1 (10.1.100.10) to PC-SALES1 (10.1.200.10): SUCCESS", styles)
    story += screenshot(f"{ss}/p01-ph3-ping-MGMT1-to-gateways.png",
                        "PC-MGMT1 pinging all 4 VLAN gateways: all reachable", styles)

    # ── Phase 4: STP ──────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Phase 4 — STP Hardening", styles)
    story += subsection("Root Bridge Election Strategy", styles)
    story.append(why_block(
        "Root bridge placement is deliberate: HQ-DSW1 is root for VLANs 100 and 999, "
        "HQ-DSW2 is root for VLANs 200 and 300. This distributes traffic and provides "
        "redundancy. Priority 4096 = 1/8 of default 32768, guaranteeing the election win.",
        styles))
    story.append(code_block("""! HQ-DSW1 — Root for VLAN 100, 999 | Secondary for VLAN 200, 300
spanning-tree mode rapid-pvst
spanning-tree vlan 100,999 priority 4096
spanning-tree vlan 200,300 priority 8192

! HQ-DSW2 — Root for VLAN 200, 300 | Secondary for VLAN 100, 999
spanning-tree mode rapid-pvst
spanning-tree vlan 200,300 priority 4096
spanning-tree vlan 100,999 priority 8192""", styles))

    story += subsection("Verification Screenshots", styles)
    story += screenshot(f"{ss}/p01-ph4-show-spanning-tree-vlan100-DSW1.png",
                        "show spanning-tree vlan 100 — HQ-DSW1: 'This bridge is the root', priority 4096", styles)
    story += screenshot(f"{ss}/p01-ph4-show-spanning-tree-root-ASW1.png",
                        "show spanning-tree root — HQ-ASW1: DSW1=root VLANs 100/999, DSW2=root VLANs 200/300", styles)

    # ── Phase 5: SSH ──────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Phase 5 — SSH Hardening", styles)
    story += subsection("SSH + VTY ACL Configuration", styles)
    story.append(why_block(
        "SSH v2 requires a domain name and RSA key of at least 1024 bits. "
        "transport input ssh disables Telnet. The VTY ACL (access-class) restricts "
        "SSH access to the management VLAN 999 subnet only — devices in data VLANs "
        "cannot SSH to any switch or router even if routed connectivity exists.",
        styles))
    story.append(code_block("""! Applied on every managed device (RTR1, DSW1, DSW2, ASW1, ASW2)
ip domain-name lab.local
crypto key generate rsa modulus 2048
ip ssh version 2

username admin privilege 15 secret <password>

ip access-list standard MGMT-ONLY
 permit 10.1.99.0 0.0.0.255
 deny   any

line vty 0 4
 login local
 transport input ssh
 access-class MGMT-ONLY in""", styles))

    story += subsection("Verification Screenshots", styles)
    story += screenshot(f"{ss}/p01-ph5-ssh-login-success-MGMT1.png",
                        "SSH login SUCCESS — PC-MGMT1 (10.1.99.100) in VLAN 999: permitted by ACL", styles)
    story += screenshot(f"{ss}/p01-ph5-ssh-denied-ENG1.png",
                        "SSH DENIED — PC-ENG1 (10.1.100.10) in VLAN 100: blocked by ACL", styles)

    # ── Break/Fix ─────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Break/Fix Challenge — VLAN 100 Removed from Trunk", styles)
    story.append(Paragraph(
        "A fault is introduced by removing VLAN 100 from the allowed list on the "
        "DSW1-to-RTR1 trunk. PC-ENG1 loses all connectivity. The task is to identify "
        "and restore the fault using only show commands and trunk configuration.",
        styles["body"]))
    story.append(Spacer(1, 6))

    story += subsection("Break Command", styles)
    story.append(code_block("""! On HQ-DSW1 — remove VLAN 100 from trunk to RTR1
interface Ethernet0/0
 switchport trunk allowed vlan remove 100""", styles))

    story += subsection("Diagnosis and Fix", styles)
    story.append(code_block("""! 1. PC-ENG1 ping fails — ARP cannot reach gateway
! 2. show interfaces trunk on DSW1 — VLAN 100 missing from "VLANs allowed and active"
! 3. show vlan brief on DSW1 — VLAN 100 exists in VLAN DB but not on trunk
! 4. Root cause: trunk allowed list is missing VLAN 100

! Fix:
interface Ethernet0/0
 switchport trunk allowed vlan add 100""", styles))

    story += subsection("Break/Fix Screenshots", styles)
    story += screenshot(f"{ss}/p01-breakfix-ping-working-ENG1-before.png",
                        "Before break — PC-ENG1 ping to gateway 10.1.100.1: SUCCESS", styles)
    story += screenshot(f"{ss}/p01-breakfix-trunk-broken-vlan100-missing.png",
                        "Trunk broken — VLAN 100 missing from allowed/active list on DSW1-to-RTR1 trunk", styles)
    story += screenshot(f"{ss}/p01-breakfix-ping-failing-ENG1.png",
                        "After break — PC-ENG1 ping failing: no path to router", styles)
    story += screenshot(f"{ss}/p01-breakfix-trunk-fixed-vlan100-restored.png",
                        "Trunk fixed — VLAN 100 restored to allowed list", styles)
    story += screenshot(f"{ss}/p01-breakfix-ping-restored-ENG1.png",
                        "Connectivity restored — PC-ENG1 ping to 10.1.100.1: SUCCESS", styles)

    # ── Key Verification Table ─────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Key Verification Checklist", styles)
    verify = [
        ["Check", "Command", "Expected Result"],
        ["VLANs exist", "show vlan brief", "VLANs 100, 200, 300, 999, 1000 active on all switches"],
        ["Trunks up", "show interfaces trunk", "All uplinks trunking, native VLAN 1000, pruned VLAN list"],
        ["Inter-VLAN routing", "ping 10.1.200.10 from PC-ENG1", "SUCCESS — traffic routed via HQ-RTR1"],
        ["STP root DSW1", "show spanning-tree root on ASW1", "DSW1 = root for VLANs 100, 999"],
        ["STP root DSW2", "show spanning-tree root on ASW1", "DSW2 = root for VLANs 200, 300"],
        ["SSH from MGMT", "ssh admin@10.1.99.11 from PC-MGMT1", "Login prompt — permitted by ACL"],
        ["SSH blocked", "ssh admin@10.1.99.11 from PC-ENG1", "Connection refused — blocked by ACL"],
        ["CDP neighbors", "show cdp neighbors on DSW1", "RTR1, DSW2, ASW1, ASW2 all visible"],
    ]
    story.append(Table(verify, colWidths=[1.5*inch, 2.0*inch, 3.0*inch], style=table_style()))

    doc.build(story)
    print(f"[OK] Project 01 PDF: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT 02 — Multi-Site DHCP
# ═══════════════════════════════════════════════════════════════════════════════

def build_project02(output_path):
    styles = make_styles()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    )
    story = []
    base = f"{BASE}/project-02-multi-site-dhcp"
    ss   = f"{base}/verification/screenshots"

    # Cover
    cover_page(story,
               "Project 02 — Multi-Site Expansion + DHCP",
               "Branch Switching · WAN · Centralized DHCP · IPv6 Dual-Stack · DNS",
               "02 of 13", styles)

    # ── Overview ──────────────────────────────────────────────────────────────
    story += section_header("Overview", styles)
    story.append(Paragraph(
        "HQ exists as an isolated campus. A second site (branch) opens. "
        "Build the branch from scratch, connect over a point-to-point WAN, deploy "
        "centralized DHCP serving both sites via relay agent, add IPv6 dual-stack "
        "with SLAAC, and verify DNS end-to-end across the WAN.",
        styles["body"]))
    story.append(Spacer(1, 6))

    story += subsection("STAR Summary", styles)
    star = [
        ["Situation", "Single-site campus with no branch, no DHCP, no DNS. All endpoints using static IPs."],
        ["Task", "Build branch site, WAN link, centralized DHCP with relay, IPv6 dual-stack, DNS resolution."],
        ["Action", "Deployed BR-RTR1/DSW1/ASW1, /30 WAN, static routes, Dnsmasq with relay pools, IPv6, Dnsmasq DNS."],
        ["Result", "Multi-site network with centralized DHCP serving 8 VLANs across 2 sites, IPv6 SLAAC, cross-site DNS."],
    ]
    story.append(Table(star, colWidths=[1.1 * inch, 5.4 * inch], style=table_style()))
    story.append(Spacer(1, 8))

    # ── Topology ──────────────────────────────────────────────────────────────
    story += section_header("Lab Topology", styles)
    topology_path = f"{base}/diagrams/cml-topology.png"
    story.append(embed_image(topology_path, max_width=470))
    story.append(Paragraph(
        "Figure 1 — CML Lab Topology (Cisco Modeling Labs 2.9)",
        styles["caption"]))
    story.append(Spacer(1, 6))

    # ── Technologies ──────────────────────────────────────────────────────────
    story += section_header("Technologies Used", styles)
    techs = [
        "Router-on-a-Stick inter-VLAN routing at branch site (BR-RTR1)",
        "802.1Q trunking with VLAN pruning — VLANs 100, 200, 300, 500, 999, 1000",
        "Point-to-point WAN /30 link (10.0.0.0/30) between HQ-RTR1 and BR-RTR1",
        "Static routing — explicit per-subnet routes in both directions",
        "Centralized DHCP (Dnsmasq on HQ-DHCP-DNS at 10.1.99.50)",
        "ip helper-address DHCP relay on all router subinterfaces at both sites",
        "DHCP pools for 8 VLANs across 2 sites with static MAC reservations",
        "IPv6 dual-stack — /126 WAN, /64 VLAN 100 at both sites",
        "SLAAC (Stateless Address Autoconfiguration) via Router Advertisements",
        "DNS with static A records (Dnsmasq address= directives)",
        "Rapid-PVST+ with BR-DSW1 as root for all branch VLANs",
        "PortFast + BPDU Guard on all branch access ports",
        "SSH v2 with VTY ACL restricted to management VLAN 999",
        "ip routing on BR-ASW1 for remote-subnet ICMP reply routing",
        "bandwidth/delay tuned on WAN interfaces for Project 03 OSPF cost accuracy",
    ]
    for t in techs:
        story.append(Paragraph(f"\u2022  {t}", styles["bullet"]))
    story.append(Spacer(1, 6))

    # ── IP Addressing ─────────────────────────────────────────────────────────
    story += section_header("IP Addressing", styles)
    story += subsection("Branch Site (10.2.x.x)", styles)
    ip_branch = [
        ["Device", "Interface", "IP Address", "Purpose"],
        ["BR-RTR1", "E0/0.100", "10.2.100.1/24", "Engineering gateway"],
        ["BR-RTR1", "E0/0.200", "10.2.200.1/24", "Sales gateway"],
        ["BR-RTR1", "E0/0.300", "10.2.44.1/24",  "Guest gateway"],
        ["BR-RTR1", "E0/0.500", "10.2.50.1/24",  "Voice gateway"],
        ["BR-RTR1", "E0/0.999", "10.2.99.1/24",  "Management gateway"],
        ["BR-DSW1", "Vlan999",  "10.2.99.2/24",  "Management SVI"],
        ["BR-ASW1", "Vlan999",  "10.2.99.3/24",  "Management SVI"],
        ["PC-BR1",  "eth0",     "10.2.100.197/24","DHCP reserved (Engineering)"],
        ["PC-BR2",  "eth0",     "10.2.200.108/24","DHCP reserved (Sales)"],
    ]
    story.append(Table(ip_branch, colWidths=[1.2*inch, 1.2*inch, 1.6*inch, 2.5*inch],
                       style=table_style()))
    story.append(Spacer(1, 6))

    story += subsection("WAN Link + HQ Additions", styles)
    ip_wan = [
        ["Device", "Interface", "IP Address", "Purpose"],
        ["HQ-RTR1", "E0/1", "10.0.0.1/30", "WAN hub-side"],
        ["BR-RTR1", "E0/1", "10.0.0.2/30", "WAN spoke-side"],
        ["HQ-RTR1", "E0/0.500", "10.1.50.1/24", "HQ Voice gateway (new)"],
        ["HQ-DHCP-DNS", "eth0", "10.1.99.50/24", "Centralized DHCP + DNS server"],
    ]
    story.append(Table(ip_wan, colWidths=[1.2*inch, 1.2*inch, 1.6*inch, 2.5*inch],
                       style=table_style()))
    story.append(Spacer(1, 6))

    story += subsection("IPv6 Addressing", styles)
    ip_v6 = [
        ["Interface", "IPv6 Address", "Purpose"],
        ["HQ-RTR1 E0/1",    "2001:db8:0:1::1/126",               "WAN HQ-side"],
        ["BR-RTR1 E0/1",    "2001:db8:0:1::2/126",               "WAN Branch-side"],
        ["HQ-RTR1 E0/0.100","2001:db8:1:100::1/64",              "HQ Engineering IPv6 GW"],
        ["BR-RTR1 E0/0.100","2001:db8:2:100::1/64",              "Branch Engineering IPv6 GW"],
        ["PC-BR1 eth0",     "2001:db8:2:100:5054:ff:fe22:a69c/64","SLAAC (EUI-64 from MAC)"],
    ]
    story.append(Table(ip_v6, colWidths=[1.8*inch, 2.8*inch, 1.9*inch], style=table_style()))
    story.append(Spacer(1, 6))

    # ── Phase 1: Branch Site ───────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Phase 1 — Branch Site Base", styles)
    story += subsection("BR-RTR1 — Router-on-a-Stick", styles)
    story.append(why_block(
        "Parent interface carries all VLAN traffic — no IP assigned. "
        "encapsulation dot1Q selects which VLAN tag this subinterface processes. "
        "VLAN 500 Voice built now to avoid rework in Project 11 QoS phase.",
        styles))
    story.append(code_block("""interface Ethernet0/0
 description TRUNK-TO-BR-DSW1-E0/0
 no ip address
 no shutdown

interface Ethernet0/0.100
 description GATEWAY-VLAN100-ENGINEERING
 encapsulation dot1Q 100
 ip address 10.2.100.1 255.255.255.0
 no shutdown

interface Ethernet0/0.200
 description GATEWAY-VLAN200-SALES
 encapsulation dot1Q 200
 ip address 10.2.200.1 255.255.255.0
 no shutdown

interface Ethernet0/0.300
 description GATEWAY-VLAN300-GUEST
 encapsulation dot1Q 300
 ip address 10.2.44.1 255.255.255.0
 no shutdown

interface Ethernet0/0.500
 description GATEWAY-VLAN500-VOICE
 encapsulation dot1Q 500
 ip address 10.2.50.1 255.255.255.0
 no shutdown

interface Ethernet0/0.999
 description GATEWAY-VLAN999-MANAGEMENT
 encapsulation dot1Q 999
 ip address 10.2.99.1 255.255.255.0
 no shutdown

interface Ethernet0/0.1000
 description NATIVE-VLAN1000-UNUSED
 encapsulation dot1Q 1000 native
 no shutdown""", styles))

    story += subsection("BR-DSW1 — STP Root + Trunking", styles)
    story.append(why_block(
        "ip routing enabled now — Project 03 needs DSW1 as an OSPF area router. "
        "encapsulation dot1q must precede switchport mode trunk on IOL-L2. "
        "Explicit VLAN allowed lists prevent accidental VLAN leakage.",
        styles))
    story.append(code_block("""ip routing
spanning-tree mode rapid-pvst
spanning-tree vlan 100,200,300,500,999,1000 priority 4096

interface Ethernet0/0
 description TRUNK-TO-BR-RTR1-E0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 1000
 switchport trunk allowed vlan 100,200,300,500,999,1000
 no shutdown

interface Ethernet0/1
 description TRUNK-TO-BR-ASW1-E0/0
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 1000
 switchport trunk allowed vlan 100,200,300,500,999,1000
 no shutdown""", styles))

    story += subsection("BR-ASW1 — Access Ports + ip routing", styles)
    story.append(why_block(
        "ip routing enabled on BR-ASW1 — ip default-gateway alone cannot route "
        "replies to remote-subnet sources (e.g. HQ-RTR1 pinging from 10.0.0.1). "
        "Static default route ensures all unknown destinations reach BR-RTR1.",
        styles))
    story.append(code_block("""ip routing
ip route 0.0.0.0 0.0.0.0 10.2.99.1

interface Ethernet1/0
 description ACCESS-PC-BR1-VLAN100
 switchport mode access
 switchport access vlan 100
 switchport nonegotiate
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown

interface Ethernet1/1
 description ACCESS-PC-BR2-VLAN200
 switchport mode access
 switchport access vlan 200
 switchport nonegotiate
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown""", styles))

    story += subsection("Phase 1 Verification Screenshots", styles)
    story += screenshot(f"{ss}/p02-p1-02-RTR1-ip-brief.png",
                        "BR-RTR1 show ip interface brief — all subinterfaces E0/0.100–.999 up/up", styles)
    story += screenshot(f"{ss}/p02-p1-03-RTR1-cdp.png",
                        "BR-RTR1 show cdp neighbors — BR-DSW1 confirmed on E0/0", styles)
    story += screenshot(f"{ss}/p02-p1-04-DSW1-trunks.png",
                        "BR-DSW1 show interfaces trunk — E0/0 and E0/1 trunking, native 1000", styles)
    story += screenshot(f"{ss}/p02-p1-05-DSW1-stp-root.png",
                        "BR-DSW1 show spanning-tree vlan 100 — 'This bridge is the root', priority 4096", styles)
    story += screenshot(f"{ss}/p02-p1-06-ASW1-vlan.png",
                        "BR-ASW1 show vlan brief — PC-BR1 in VLAN 100, PC-BR2 in VLAN 200", styles)
    story += screenshot(f"{ss}/p02-p1-08-ping-cross-device.png",
                        "Cross-device ping — management plane reachable across all branch devices", styles)

    # ── Phase 2: WAN ──────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Phase 2 — WAN Connectivity", styles)
    story += subsection("HQ-RTR1 — WAN Interface + Static Routes to Branch", styles)
    story.append(why_block(
        "/30 gives exactly 2 usable IPs — correct for point-to-point links. "
        "bandwidth 1000 and delay 1000 set now for OSPF cost accuracy in Project 03 "
        "(IOL defaults to 10 Mbps which will produce wrong OSPF costs). "
        "Explicit per-subnet routes give better visibility than a summary during troubleshooting.",
        styles))
    story.append(code_block("""interface Ethernet0/1
 description WAN-TO-BR-RTR1-E0/1
 ip address 10.0.0.1 255.255.255.252
 bandwidth 1000
 delay 1000
 no shutdown

ip route 10.2.100.0 255.255.255.0 10.0.0.2
ip route 10.2.200.0 255.255.255.0 10.0.0.2
ip route 10.2.44.0  255.255.255.0 10.0.0.2
ip route 10.2.50.0  255.255.255.0 10.0.0.2
ip route 10.2.99.0  255.255.255.0 10.0.0.2""", styles))

    story += subsection("BR-RTR1 — WAN Interface + Static Routes to HQ", styles)
    story.append(code_block("""interface Ethernet0/1
 description WAN-TO-HQ-RTR1-E0/1
 ip address 10.0.0.2 255.255.255.252
 bandwidth 1000
 delay 1000
 no shutdown

ip route 10.1.100.0 255.255.255.0 10.0.0.1
ip route 10.1.200.0 255.255.255.0 10.0.0.1
ip route 10.1.44.0  255.255.255.0 10.0.0.1
ip route 10.1.50.0  255.255.255.0 10.0.0.1
ip route 10.1.99.0  255.255.255.0 10.0.0.1
ip route 10.0.255.1 255.255.255.255 10.0.0.1""", styles))

    story += subsection("Phase 2 Verification Screenshots", styles)
    story += screenshot(f"{ss}/p02-p2-01-HQ-RTR1-ip-route.png",
                        "HQ-RTR1 show ip route — 5 static routes to 10.2.x.x branch subnets", styles)
    story += screenshot(f"{ss}/p02-p2-01-cross-site-ping.png",
                        "Cross-site ping — PC-MGMT1 (10.1.99.100) reaching BR-ASW1 (10.2.99.3): SUCCESS", styles)
    story += screenshot(f"{ss}/p02-p2-02-BR-RTR1-ip-route.png",
                        "BR-RTR1 show ip route — 6 static routes to 10.1.x.x HQ subnets", styles)

    # ── Phase 3: DHCP ─────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Phase 3 — Centralized DHCP", styles)
    story += subsection("HQ-RTR1 + BR-RTR1 — DHCP Relay (ip helper-address)", styles)
    story.append(why_block(
        "helper-address goes on the SUBINTERFACE — not the physical parent interface. "
        "The relay agent uses the subinterface IP as the giaddr field in the DHCP packet. "
        "Dnsmasq reads giaddr to match the correct DHCP pool. "
        "ALL data VLAN subinterfaces need helper-address — missing one = that VLAN never gets DHCP.",
        styles))
    story.append(code_block("""! On HQ-RTR1 — add helper-address to all data subinterfaces
interface Ethernet0/0.100
 ip helper-address 10.1.99.50
interface Ethernet0/0.200
 ip helper-address 10.1.99.50
interface Ethernet0/0.300
 ip helper-address 10.1.99.50
interface Ethernet0/0.500
 ip helper-address 10.1.99.50

! On BR-RTR1 — same pattern for branch subinterfaces
interface Ethernet0/0.100
 ip helper-address 10.1.99.50
interface Ethernet0/0.200
 ip helper-address 10.1.99.50
interface Ethernet0/0.300
 ip helper-address 10.1.99.50
interface Ethernet0/0.500
 ip helper-address 10.1.99.50""", styles))

    story += subsection("HQ-DHCP-DNS — Dnsmasq Pool Configuration", styles)
    story.append(why_block(
        "Dnsmasq reads the giaddr field to select the matching DHCP pool. "
        "dhcp-range with set:<tag> assigns the pool to the matching subnet. "
        "Static reservations lock endpoints to permanent IPs via MAC — required "
        "so that address= DNS records remain accurate across reboots.",
        styles))
    story.append(code_block("""domain=lab.local
local=/lab.local/
log-dhcp

# HQ pools — giaddr matches HQ subinterface IPs
dhcp-range=set:hq-eng,10.1.100.100,10.1.100.200,255.255.255.0,24h
dhcp-option=tag:hq-eng,option:router,10.1.100.1
dhcp-option=tag:hq-eng,option:dns-server,10.1.99.50

dhcp-range=set:hq-sales,10.1.200.100,10.1.200.200,255.255.255.0,24h
dhcp-option=tag:hq-sales,option:router,10.1.200.1
dhcp-option=tag:hq-sales,option:dns-server,10.1.99.50

# Branch pools — giaddr matches BR-RTR1 subinterface IPs
dhcp-range=set:br-eng,10.2.100.100,10.2.100.200,255.255.255.0,24h
dhcp-option=tag:br-eng,option:router,10.2.100.1
dhcp-option=tag:br-eng,option:dns-server,10.1.99.50

dhcp-range=set:br-sales,10.2.200.100,10.2.200.200,255.255.255.0,24h
dhcp-option=tag:br-sales,option:router,10.2.200.1
dhcp-option=tag:br-sales,option:dns-server,10.1.99.50

# Static DHCP reservations by MAC
dhcp-host=52:54:00:22:a6:9c,pc-br1,10.2.100.197
dhcp-host=52:54:00:53:da:69,pc-br2,10.2.200.108

# DNS A records
address=/hq-rtr1.lab.local/10.1.99.1
address=/br-rtr1.lab.local/10.2.99.1
address=/hq-dhcp-dns.lab.local/10.1.99.50
address=/pc-br1.lab.local/10.2.100.197
address=/pc-br2.lab.local/10.2.200.108""", styles))

    story += subsection("Phase 3 Verification Screenshots", styles)
    story += screenshot(f"{ss}/p02-p3-01-dnsmasq-log.png",
                        "dnsmasq log — live DHCP lease assignments from both HQ and Branch", styles)
    story += screenshot(f"{ss}/p02-p3-02-BR-RTR1-arp.png",
                        "BR-RTR1 show ip arp — PC-BR1 (10.2.100.197) and PC-BR2 (10.2.200.108) leased", styles)
    story += screenshot(f"{ss}/p02-p3-03-HQ-RTR1-arp.png",
                        "HQ-RTR1 show ip arp — HQ endpoints with DHCP leases visible", styles)
    story += screenshot(f"{ss}/p02-p3-04-PC-BR2-ip.png",
                        "PC-BR2 ip addr show eth0 — 10.2.200.108 leased from 10.1.99.50", styles)
    story += screenshot(f"{ss}/p02-p3-05-HQ-DSW2-vlan.png",
                        "HQ-DSW2 show vlan brief — DHCP server port Et0/0 confirmed in VLAN 999", styles)

    # ── Phase 4: IPv6 ─────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Phase 4 — IPv6 Dual-Stack", styles)
    story += subsection("HQ-RTR1 + BR-RTR1 — IPv6 Configuration", styles)
    story.append(why_block(
        "ipv6 unicast-routing must be enabled globally — without it the router drops all IPv6 packets. "
        "/64 prefix is mandatory for SLAAC (hosts build their full address from the /64 prefix + EUI-64). "
        "PC-BR1 EUI-64 from MAC 52:54:00:22:a6:9c → insert ff:fe → flip 7th bit → 5054:ff:fe22:a69c.",
        styles))
    story.append(code_block("""! HQ-RTR1
ipv6 unicast-routing

interface Ethernet0/1
 ipv6 address 2001:db8:0:1::1/126
 ipv6 enable

interface Ethernet0/0.100
 ipv6 address 2001:db8:1:100::1/64
 ipv6 enable

ipv6 route 2001:db8:2:100::/64 2001:db8:0:1::2

! BR-RTR1
ipv6 unicast-routing

interface Ethernet0/1
 ipv6 address 2001:db8:0:1::2/126
 ipv6 enable

interface Ethernet0/0.100
 ipv6 address 2001:db8:2:100::1/64
 ipv6 enable

ipv6 route 2001:db8:1:100::/64 2001:db8:0:1::1""", styles))

    story += subsection("Phase 4 Verification Screenshots", styles)
    story += screenshot(f"{ss}/p02-p4-01-HQ-RTR1-ipv6-route.png",
                        "HQ-RTR1 show ipv6 route — static route S 2001:db8:2:100::/64 via 2001:db8:0:1::2", styles)
    story += screenshot(f"{ss}/p02-p4-02-BR-RTR1-ipv6-route.png",
                        "BR-RTR1 show ipv6 route — static route S 2001:db8:1:100::/64 via 2001:db8:0:1::1", styles)
    story += screenshot(f"{ss}/p02-p4-03-cross-site-ipv6-ping.png",
                        "Cross-site IPv6 ping — HQ-RTR1 to BR-RTR1 VLAN 100 (2001:db8:2:100::1): SUCCESS", styles)
    story += screenshot(f"{ss}/p02-p4-04-PC-BR1-slaac.png",
                        "PC-BR1 ip -6 addr show eth0 — SLAAC address 2001:db8:2:100:5054:ff:fe22:a69c/64", styles)

    # ── Phase 5: DNS ──────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Phase 5 — DNS End-to-End", styles)
    story += subsection("Router DNS Client Configuration", styles)
    story.append(why_block(
        "no ip domain lookup was set during hardening to prevent IOS from DNS-resolving "
        "mistyped commands (causes a 30-second timeout). Re-enable it now that we have a "
        "valid name-server. ip domain lookup + ip name-server lets routers resolve FQDNs.",
        styles))
    story.append(code_block("""! On HQ-RTR1 and BR-RTR1
ip domain lookup
ip name-server 10.1.99.50""", styles))

    story += subsection("Phase 5 Verification Screenshots", styles)
    story += screenshot(f"{ss}/p02-p5-01-PC-BR1-nslookup-hqrtr1.png",
                        "PC-BR1 nslookup hq-rtr1.lab.local — resolves to 10.1.99.1 via 10.1.99.50", styles)
    story += screenshot(f"{ss}/p02-p5-02-PC-BR1-nslookup-brrtr1.png",
                        "PC-BR1 nslookup br-rtr1.lab.local — resolves to 10.2.99.1", styles)
    story += screenshot(f"{ss}/p02-p5-03-BR-RTR1-ping-name.png",
                        "BR-RTR1 ping hq-rtr1.lab.local — name resolves cross-site, ping succeeds", styles)
    story += screenshot(f"{ss}/p02-p5-04-HQ-RTR1-ping-name.png",
                        "HQ-RTR1 ping br-rtr1.lab.local — name resolves, cross-site ping succeeds", styles)
    story += screenshot(f"{ss}/p02-p5-05-HQ-DSW2-vlan-verify.png",
                        "HQ-DSW2 show vlan brief — Et0/0 confirmed in VLAN 999 for DHCP-DNS server", styles)

    # ── Break/Fix ─────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Break/Fix Challenge — Three Simultaneous DHCP Faults", styles)
    story.append(Paragraph(
        "Three simultaneous DHCP faults are introduced: (1) wrong helper-address on BR-RTR1 "
        "subinterfaces pointing to a non-existent IP, (2) helper-address removed from "
        "HQ-RTR1 VLAN 100 subinterface, (3) DHCP server process stopped on HQ-DHCP-DNS. "
        "All three must be found and fixed simultaneously.",
        styles["body"]))
    story.append(Spacer(1, 6))

    story += subsection("Diagnosis Approach", styles)
    story.append(code_block("""! 1. Check if PC-BR1 gets DHCP — udhcpc -i eth0 (times out = relay or server fault)
! 2. show run | section helper on BR-RTR1 — verify helper-address is 10.1.99.50
! 3. show run | section helper on HQ-RTR1 — verify all subinterfaces have helper
! 4. SSH to HQ-DHCP-DNS — check: systemctl status dnsmasq or ps aux | grep dnsmasq
! 5. Fix all three, then re-run udhcpc on PC-BR1 and PC-BR2""", styles))

    story += subsection("Break/Fix Screenshots", styles)
    story += screenshot(f"{ss}/p02-bf-07-BR-RTR1-fixed-helper.png",
                        "BR-RTR1 fixed — all 4 subinterfaces show ip helper-address 10.1.99.50", styles)
    story += screenshot(f"{ss}/p02-bf-08-HQ-RTR1-fixed-helper.png",
                        "HQ-RTR1 fixed — helper-address restored on VLAN 100 subinterface", styles)
    story += screenshot(f"{ss}/p02-bf-05-PC-BR1-dhcp-restored.png",
                        "PC-BR1 DHCP restored — 10.2.100.197 leased from 10.1.99.50 after all three fixes", styles)
    story += screenshot(f"{ss}/p02-bf-06-PC-BR2-dhcp-restored.png",
                        "PC-BR2 DHCP restored — 10.2.200.108 leased from 10.1.99.50", styles)

    # ── Key Verification ──────────────────────────────────────────────────────
    story.append(PageBreak())
    story += section_header("Key Verification Checklist", styles)
    verify = [
        ["Command", "Device", "Expected Result"],
        ["show ip interface brief", "BR-RTR1", "E0/0.100–.999 all up/up with 10.2.x.x IPs"],
        ["show interfaces trunk", "BR-DSW1", "E0/0 and E0/1 trunking, native 1000, VLANs 100/200/300/500/999"],
        ["show vlan brief", "BR-ASW1", "Et1/0 in VLAN 100, Et1/1 in VLAN 200"],
        ["show spanning-tree vlan 100", "BR-DSW1", "'This bridge is the root' priority 4196"],
        ["show ip route", "HQ-RTR1", "5 static routes to 10.2.x.x via 10.0.0.2"],
        ["show ip route", "BR-RTR1", "6 static routes to 10.1.x.x via 10.0.0.1"],
        ["show run | section helper", "Both routers", "ip helper-address 10.1.99.50 on all data subinterfaces"],
        ["udhcpc -i eth0", "PC-BR1", "Lease 10.2.100.197 from 10.1.99.50"],
        ["show ipv6 route", "HQ-RTR1", "S 2001:db8:2:100::/64 via 2001:db8:0:1::2"],
        ["ip -6 addr show eth0", "PC-BR1", "SLAAC 2001:db8:2:100:5054:ff:fe22:a69c/64"],
        ["nslookup hq-rtr1.lab.local 10.1.99.50", "PC-BR1", "A record: 10.1.99.1"],
        ["ping br-rtr1.lab.local", "HQ-RTR1", "Name resolves, cross-site ping succeeds"],
    ]
    story.append(Table(verify, colWidths=[2.2*inch, 1.5*inch, 2.8*inch], style=table_style()))

    doc.build(story)
    print(f"[OK] Project 02 PDF: {output_path}")
    return output_path


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import time

    outputs = {
        "p01_project": f"{BASE}/project-01-campus-foundation/docs/campus-foundation-lab-guide.pdf",
        "p01_docs":    f"{BASE}/docs/project-01-campus-foundation-lab-guide.pdf",
        "p02_project": f"{BASE}/project-02-multi-site-dhcp/docs/multi-site-dhcp-lab-guide.pdf",
        "p02_docs":    f"{BASE}/docs/project-02-multi-site-dhcp-lab-guide.pdf",
    }

    # Project 01 — generate once, copy to docs/
    t0 = time.time()
    build_project01(outputs["p01_project"])
    import shutil
    shutil.copy2(outputs["p01_project"], outputs["p01_docs"])
    print(f"[OK] Copied to docs/ ({time.time()-t0:.1f}s)")

    # Project 02
    t0 = time.time()
    build_project02(outputs["p02_project"])
    shutil.copy2(outputs["p02_project"], outputs["p02_docs"])
    print(f"[OK] Copied to docs/ ({time.time()-t0:.1f}s)")

    print("\nAll 4 PDF files generated successfully.")
    for k, v in outputs.items():
        size = os.path.getsize(v) // 1024
        print(f"  {v}  ({size} KB)")
