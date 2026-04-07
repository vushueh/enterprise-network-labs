#!/usr/bin/env python3
"""
Generate Cisco-style PDF lab guides for Enterprise Network Labs Projects 01 and 02.
Matches reference PDF structure: cover, setup, STAR, technologies, topology, IP tables,
numbered phases with steps/commands/WHY, verification, final checklist, troubleshooting,
break/fix challenge.
"""

import os
import shutil
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from PIL import Image as PILImage

# ─── Colors ───────────────────────────────────────────────────────────────────
NAVY        = colors.HexColor("#005073")   # primary brand blue
WHITE       = colors.white
BLACK       = colors.HexColor("#000000")
CODE_BG     = colors.HexColor("#F0F0F0")
WHY_BG      = colors.HexColor("#EBF5FB")
WHY_BORDER  = colors.HexColor("#0070AD")
NOTE_BG     = colors.HexColor("#FFF8E1")
NOTE_BORDER = colors.HexColor("#F9A825")
TBL_ALT     = colors.HexColor("#EBF5FB")
TBL_BORDER  = colors.HexColor("#CCCCCC")
GRAY_FOOT   = colors.HexColor("#888888")
SUBSEC_TEXT = NAVY

PAGE_W, PAGE_H = letter   # 612 x 792 pt
L_MARGIN = R_MARGIN = T_MARGIN = B_MARGIN = 54
USABLE_W = PAGE_W - L_MARGIN - R_MARGIN   # 504 pt

BASE = "/home/leonel/code/enterprise-network-labs"

# ─── Style factory ────────────────────────────────────────────────────────────

def S(name, **kw):
    return ParagraphStyle(name, **kw)

STYLES = {
    "cover_title": S("cover_title", fontName="Helvetica-Bold", fontSize=26,
                     leading=32, textColor=WHITE, alignment=TA_CENTER, spaceAfter=8),
    "cover_subtitle": S("cover_subtitle", fontName="Helvetica", fontSize=14,
                        leading=20, textColor=WHITE, alignment=TA_CENTER, spaceAfter=6),
    "cover_meta": S("cover_meta", fontName="Helvetica", fontSize=11,
                    leading=16, textColor=BLACK, alignment=TA_CENTER, spaceAfter=4),
    "body": S("body", fontName="Helvetica", fontSize=10, leading=14,
              textColor=BLACK, spaceAfter=4),
    "body_bold": S("body_bold", fontName="Helvetica-Bold", fontSize=10, leading=14,
                   textColor=BLACK, spaceAfter=4),
    "step": S("step", fontName="Helvetica-Bold", fontSize=10, leading=14,
              textColor=BLACK, spaceAfter=3, spaceBefore=8),
    "subsec": S("subsec", fontName="Helvetica-Bold", fontSize=12, leading=16,
                textColor=SUBSEC_TEXT, spaceAfter=4, spaceBefore=10),
    "caption": S("caption", fontName="Helvetica-Oblique", fontSize=8, leading=11,
                 textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=8),
    "bullet": S("bullet", fontName="Helvetica", fontSize=10, leading=14,
                textColor=BLACK, leftIndent=16, bulletIndent=6, spaceAfter=3),
    "tbl_hdr": S("tbl_hdr", fontName="Helvetica-Bold", fontSize=9, leading=12,
                 textColor=WHITE, alignment=TA_CENTER),
    "tbl_body": S("tbl_body", fontName="Helvetica", fontSize=9, leading=12,
                  textColor=BLACK),
    "tbl_body_c": S("tbl_body_c", fontName="Helvetica", fontSize=9, leading=12,
                    textColor=BLACK, alignment=TA_CENTER),
    "why": S("why", fontName="Helvetica-Oblique", fontSize=9, leading=13,
             textColor=BLACK, spaceAfter=8, spaceBefore=4),
    "note": S("note", fontName="Helvetica", fontSize=9, leading=13,
              textColor=BLACK, spaceAfter=8, spaceBefore=4),
    "verify_label": S("verify_label", fontName="Helvetica-Bold", fontSize=10,
                      leading=14, textColor=NAVY, spaceAfter=3, spaceBefore=8),
}

# ─── Page header / footer callbacks ───────────────────────────────────────────

def make_page_callbacks(project_title):
    def on_first_page(canvas, doc):
        pass  # cover page — no header/footer

    def on_later_pages(canvas, doc):
        canvas.saveState()
        # Header bar
        canvas.setFillColor(NAVY)
        canvas.rect(0, PAGE_H - 36, PAGE_W, 36, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(L_MARGIN, PAGE_H - 24, project_title)
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(PAGE_W - R_MARGIN, PAGE_H - 24, "Enterprise Network Labs")
        # Footer
        canvas.setFillColor(GRAY_FOOT)
        canvas.setFont("Helvetica", 8)
        page_str = f"Page {doc.page} of {doc._pageCount if hasattr(doc, '_pageCount') else '?'}"
        canvas.drawRightString(PAGE_W - R_MARGIN, B_MARGIN - 16, page_str)
        canvas.restoreState()

    return on_first_page, on_later_pages

# We need page count for footer — use a two-pass approach with a custom template
class PageCountDocTemplate(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pageCount = 0

    def handle_pageEnd(self):
        self._pageCount = self.page
        super().handle_pageEnd()

    def multiBuild(self, story, onFirstPage=None, onLaterPages=None, **kwargs):
        # First pass to count pages
        self._firstPassDoc = True
        super().multiBuild(story, onFirstPage=onFirstPage, onLaterPages=onLaterPages, **kwargs)

# ─── Element helpers ──────────────────────────────────────────────────────────

def section_header(title):
    """Full-width navy bar with white bold title text."""
    data = [[Paragraph(title, ParagraphStyle("sh", fontName="Helvetica-Bold", fontSize=14,
                                              leading=18, textColor=WHITE))]]
    t = Table(data, colWidths=[USABLE_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    return t


def code_block(text):
    """Gray background, black Courier-Bold text, navy left border.
    Uses one table row per line so the block can split across pages.
    Returns a LIST of flowables (no outer wrapper) to allow page splitting."""
    line_style = ParagraphStyle("cb", fontName="Courier-Bold", fontSize=8.5, leading=12,
                                textColor=BLACK, leftIndent=10)
    lines = text.strip("\n").split("\n")
    data = []
    for line in lines:
        safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe = safe.replace(" ", "&nbsp;")
        data.append([Paragraph(safe, line_style)])

    n = len(data)
    # Use full usable width; left border is via LINEBEFORE
    t = Table(data, colWidths=[USABLE_W], splitByRow=1)
    style_cmds = [
        ("BACKGROUND",   (0, 0), (-1, -1), CODE_BG),
        ("LEFTPADDING",  (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
        ("LINEBEFORE",   (0, 0), (0, -1), 3, NAVY),
        ("TOPPADDING",   (0, 0), (-1,  0), 6),
        ("BOTTOMPADDING",(0, n-1), (-1, n-1), 6),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def why_box(text):
    """Light blue callout box with WHY: prefix."""
    bold_prefix = '<font name="Helvetica-Bold">WHY: </font>'
    content = Paragraph(bold_prefix + text,
                        ParagraphStyle("wh", fontName="Helvetica-Oblique", fontSize=9,
                                       leading=13, textColor=BLACK))
    data = [[content]]
    t = Table(data, colWidths=[USABLE_W - 20])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), WHY_BG),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LINEBEFORE",   (0, 0), (0, -1), 3, WHY_BORDER),
    ]))
    outer = Table([[t]], colWidths=[USABLE_W])
    outer.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    return outer


def note_box(text):
    """Yellow NOTE callout box."""
    bold_prefix = '<font name="Helvetica-Bold">NOTE: </font>'
    content = Paragraph(bold_prefix + text,
                        ParagraphStyle("nb", fontName="Helvetica", fontSize=9,
                                       leading=13, textColor=BLACK))
    data = [[content]]
    t = Table(data, colWidths=[USABLE_W - 20])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), NOTE_BG),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LINEBEFORE",   (0, 0), (0, -1), 3, NOTE_BORDER),
    ]))
    outer = Table([[t]], colWidths=[USABLE_W])
    outer.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    return outer


def embed_image(path, max_width=460):
    if not os.path.exists(path):
        return Paragraph(f"<i>[Image not found: {path}]</i>",
                         ParagraphStyle("miss", fontSize=8, textColor=colors.red))
    pil = PILImage.open(path)
    orig_w, orig_h = pil.size
    scale = min(max_width / orig_w, 1.0)
    img = Image(path, width=orig_w * scale, height=orig_h * scale)
    # Center via single-cell table
    t = Table([[img]], colWidths=[USABLE_W])
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("LEFTPADDING", (0,0),(-1,-1), 0),
                            ("RIGHTPADDING",(0,0),(-1,-1), 0),
                            ("TOPPADDING",  (0,0),(-1,-1), 4),
                            ("BOTTOMPADDING",(0,0),(-1,-1), 2)]))
    return t


def caption(text):
    return Paragraph(text, STYLES["caption"])


def p(text, style="body"):
    return Paragraph(text, STYLES[style])


def sp(h=6):
    return Spacer(1, h)


def ip_table(headers, rows):
    """Styled IP/VLAN table with navy header, alternating rows."""
    hdr_style = STYLES["tbl_hdr"]
    body_style = STYLES["tbl_body"]

    data = [[Paragraph(h, hdr_style) for h in headers]]
    for i, row in enumerate(rows):
        data.append([Paragraph(str(c), body_style) for c in row])

    col_w = USABLE_W / len(headers)
    t = Table(data, colWidths=[col_w] * len(headers), repeatRows=1)
    style_cmds = [
        ("BACKGROUND",   (0, 0), (-1,  0), NAVY),
        ("TEXTCOLOR",    (0, 0), (-1,  0), WHITE),
        ("FONTNAME",     (0, 0), (-1,  0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("GRID",         (0, 0), (-1, -1), 0.5, TBL_BORDER),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), TBL_ALT))
    t.setStyle(TableStyle(style_cmds))
    return t


def checklist_table(headers, rows):
    """Final verification checklist table — same styling as ip_table but wider command cols."""
    hdr_style = STYLES["tbl_hdr"]
    body_style = STYLES["tbl_body"]
    center_style = STYLES["tbl_body_c"]

    data = [[Paragraph(h, hdr_style) for h in headers]]
    for i, row in enumerate(rows):
        data.append([Paragraph(str(c), body_style) for c in row])

    # Col widths: #(20), Test(90), Command(130), Device(80), Expected(184)
    col_widths = [20, 90, 130, 80, 184]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND",   (0, 0), (-1,  0), NAVY),
        ("TEXTCOLOR",    (0, 0), (-1,  0), WHITE),
        ("FONTNAME",     (0, 0), (-1,  0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("GRID",         (0, 0), (-1, -1), 0.5, TBL_BORDER),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), TBL_ALT))
    t.setStyle(TableStyle(style_cmds))
    return t


def cover_page(title, subtitle, meta_lines):
    """Build cover page story elements."""
    elems = []

    # Navy banner spanning full usable width, height 180pt
    banner_data = [[
        Paragraph(title,    STYLES["cover_title"]),
    ]]
    banner = Table(banner_data, colWidths=[USABLE_W])
    banner.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING",   (0, 0), (-1, -1), 50),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
    ]))
    elems.append(banner)

    # Subtitle inside a second navy row
    sub_data = [[Paragraph(subtitle, STYLES["cover_subtitle"])]]
    sub_tbl = Table(sub_data, colWidths=[USABLE_W])
    sub_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 40),
    ]))
    elems.append(sub_tbl)
    elems.append(sp(24))

    for line in meta_lines:
        elems.append(p(line, "cover_meta"))
        elems.append(sp(2))

    elems.append(PageBreak())
    return elems


def issue_block(title, symptom, root_cause, fix):
    """Format a troubleshooting issue."""
    elems = []
    elems.append(p(f"<b>{title}</b>", "subsec"))
    elems.append(p(f"<b>Symptom:</b> {symptom}"))
    elems.append(p(f"<b>Root Cause:</b> {root_cause}"))
    elems.append(p(f"<b>Fix:</b> {fix}"))
    elems.append(sp(6))
    return elems


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT 01 — CAMPUS FOUNDATION
# ═══════════════════════════════════════════════════════════════════════════════

def build_project_01():
    SS = f"{BASE}/project-01-campus-foundation/verification/screenshots"
    TOPO = f"{BASE}/project-01-campus-foundation/diagrams/cml-topology.png"
    story = []

    # ── Cover ──
    story += cover_page(
        "Project 01 — Campus Foundation",
        "Building a Fully Segmented Enterprise Campus Network",
        [
            "Author: Leonel Chongong",
            "Date: April 2026",
            "Platform: Cisco CML 2.9 | IOL + IOL-L2",
            "Methodology: Build → Verify → Break → Fix",
        ]
    )

    # ── Setup and Scenario ──
    story.append(section_header("Setup and Scenario"))
    story.append(sp(8))
    story.append(p("<b>Business Context</b>", "subsec"))
    story.append(p(
        "A growing technology company needs to segment its headquarters network into "
        "separate security zones for Engineering, Sales, Guest users, and Network "
        "Management. The current flat network allows all devices to communicate freely — "
        "a Guest laptop can reach Engineering servers, and management interfaces are "
        "reachable from any workstation. This lab designs and builds the complete "
        "segmentation from a written requirement."
    ))
    story.append(sp(6))
    story.append(p("<b>What You Will Build</b>", "subsec"))
    story.append(p(
        "A multi-VLAN campus using two distribution switches (HQ-DSW1, HQ-DSW2), "
        "two access switches (HQ-ASW1, HQ-ASW2), and one router (HQ-RTR1) performing "
        "router-on-a-stick inter-VLAN routing. The design includes:"
    ))
    for bullet in [
        "Four production VLANs (100 Engineering, 200 Sales, 300 Guest, 999 Management) plus VLAN 1000 as a hardened native VLAN",
        "802.1Q trunks with explicit allowed VLAN lists on all switch-to-switch links",
        "Router-on-a-stick subinterfaces as the default gateway for each VLAN",
        "Rapid-PVST+ with deliberate root bridge election across both distribution switches",
        "PortFast + BPDU Guard on all access ports",
        "SSH v2 management restricted to VLAN 999 only via ACL",
    ]:
        story.append(p(f"• {bullet}", "bullet"))
    story.append(sp(8))

    # ── STAR Summary ──
    story.append(section_header("STAR Summary"))
    story.append(sp(8))
    for label, text in [
        ("Situation", "Studying VLANs, trunking, and inter-VLAN routing as separate topics without a real design exercise."),
        ("Task", "Design and build a fully segmented campus network from a written requirement."),
        ("Action", "Built multi-VLAN campus (100/200/300/999) with trunks, router-on-a-stick inter-VLAN routing, deliberate STP root election, and SSH-only management restricted to VLAN 999."),
        ("Result", "Can design a multi-VLAN campus from scratch, explain every decision, and verify all technologies working together."),
    ]:
        story.append(p(f"<b>{label}:</b> {text}"))
        story.append(sp(3))
    story.append(sp(8))

    # ── Technologies Used ──
    story.append(section_header("Technologies Used"))
    story.append(sp(8))
    for tech in [
        "VLANs (100, 200, 300, 999, 1000)",
        "802.1Q Trunking",
        "Native VLAN hardening (VLAN 1000)",
        "Router-on-a-Stick inter-VLAN routing",
        "Rapid-PVST+ Spanning Tree",
        "PortFast + BPDU Guard",
        "SSH v2 with VTY ACL (management VLAN only)",
        "CDP for neighbor discovery",
        "Interface descriptions",
    ]:
        story.append(p(f"• {tech}", "bullet"))
    story.append(sp(8))

    # ── Network Topology ──
    story.append(section_header("Network Topology"))
    story.append(sp(8))
    story.append(embed_image(TOPO))
    story.append(caption("Figure T.1 — CML Topology — Project 01 Campus Foundation"))
    story.append(sp(8))

    # ── IP Addressing Table ──
    story.append(section_header("IP Addressing"))
    story.append(sp(8))
    story.append(ip_table(
        ["Device", "Interface", "IP Address", "Subnet", "Purpose"],
        [
            ["HQ-RTR1",   "E0/0.100",  "10.1.100.1",  "/24", "Engineering gateway"],
            ["HQ-RTR1",   "E0/0.200",  "10.1.200.1",  "/24", "Sales gateway"],
            ["HQ-RTR1",   "E0/0.300",  "10.1.44.1",   "/24", "Guest gateway"],
            ["HQ-RTR1",   "E0/0.999",  "10.1.99.1",   "/24", "Management gateway"],
            ["HQ-RTR1",   "Loopback0", "10.0.255.1",  "/32", "Router ID"],
            ["HQ-DSW1",   "VLAN 999",  "10.1.99.11",  "/24", "Management SVI"],
            ["HQ-DSW2",   "VLAN 999",  "10.1.99.12",  "/24", "Management SVI"],
            ["HQ-ASW1",   "VLAN 999",  "10.1.99.13",  "/24", "Management SVI"],
            ["HQ-ASW2",   "VLAN 999",  "10.1.99.14",  "/24", "Management SVI"],
            ["PC-ENG1",   "eth0",      "10.1.100.10", "/24", "Engineering endpoint"],
            ["PC-SALES1", "eth0",      "10.1.200.10", "/24", "Sales endpoint"],
            ["PC-MGMT1",  "eth0",      "10.1.99.100", "/24", "Management endpoint"],
        ]
    ))
    story.append(sp(12))
    story.append(ip_table(
        ["VLAN", "Name", "Subnet", "Purpose"],
        [
            ["100",  "Engineering",  "10.1.100.0/24", "Developer workstations"],
            ["200",  "Sales",        "10.1.200.0/24", "Sales team"],
            ["300",  "Guest",        "10.1.44.0/24",  "Guest isolation"],
            ["999",  "Management",   "10.1.99.0/24",  "Network device management"],
            ["1000", "NATIVE-UNUSED","none",           "Native VLAN (no traffic)"],
        ]
    ))
    story.append(sp(8))

    # ════════════════════════════════════════════════════════
    # PHASE 1: VLAN Configuration
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Phase 1: VLAN Configuration"))
    story.append(sp(8))
    story.append(p("<b>Goal:</b> Create the VLAN database on all switches and configure access ports for end devices."))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p("Open the console for HQ-DSW1. Enter configuration mode and create the VLAN database:"))
    story.append(code_block(
        "enable\nconfigure terminal\nhostname HQ-DSW1\nlldp run\n\n"
        "vlan 100\n name Engineering\nvlan 200\n name Sales\nvlan 300\n name Guest\n"
        "vlan 999\n name Management\nvlan 1000\n name NATIVE-UNUSED"
    ))
    story.append(why_box(
        "VLANs must exist in the VLAN database before they can be assigned to ports. "
        "VLAN 1000 is created as an unused native VLAN — a security hardening step to "
        "ensure untagged frames on trunks go nowhere."
    ))

    story.append(p("Step 2", "step"))
    story.append(p("Configure the Management SVI and default gateway on HQ-DSW1:"))
    story.append(code_block(
        "interface vlan 999\n ip address 10.1.99.11 255.255.255.0\n no shutdown\n\n"
        "ip default-gateway 10.1.99.1"
    ))
    story.append(why_box(
        "Without a Layer 3 SVI, the switch cannot be reached via SSH for management. "
        "The default gateway tells the switch where to forward packets destined beyond "
        "its directly connected subnets."
    ))

    story.append(p("Step 3", "step"))
    story.append(p(
        "Repeat the VLAN database and SVI configuration on HQ-DSW2 (ip: 10.1.99.12), "
        "HQ-ASW1 (ip: 10.1.99.13), and HQ-ASW2 (ip: 10.1.99.14). Use the same VLAN "
        "names and the same management gateway 10.1.99.1."
    ))

    story.append(p("Step 4", "step"))
    story.append(p("On HQ-ASW1, configure access ports for endpoints:"))
    story.append(code_block(
        "interface Ethernet0/2\n description ACCESS-PC-ENG1-VLAN100\n"
        " switchport mode access\n switchport access vlan 100\n no shutdown\n\n"
        "interface Ethernet0/3\n description ACCESS-PC-MGMT1-VLAN999\n"
        " switchport mode access\n switchport access vlan 999\n no shutdown"
    ))
    story.append(why_box(
        "switchport mode access restricts the port to a single VLAN and disables trunk "
        "negotiation. End devices do not understand 802.1Q tags — they need an untagged "
        "access port."
    ))

    story.append(p("Step 5", "step"))
    story.append(p(
        "On HQ-ASW2, configure the access port for PC-SALES1 on interface Ethernet0/2, "
        "VLAN 200."
    ))

    story.append(sp(8))
    story.append(p("Verification", "verify_label"))
    story.append(code_block("show vlan brief"))
    story.append(p(
        "Expected result: VLANs 100, 200, 300, 999, 1000 all show as \"active\". "
        "Ethernet0/2 listed under VLAN 100 on ASW1, Ethernet0/3 under VLAN 999."
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/p01-ph1-show-vlan-brief-ASW1.png"))
    story.append(caption("Figure 1.1 — show vlan brief — HQ-ASW1"))

    # ════════════════════════════════════════════════════════
    # PHASE 2: 802.1Q Trunking
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Phase 2: 802.1Q Trunking"))
    story.append(sp(8))
    story.append(p("<b>Goal:</b> Configure 802.1Q trunk links between all switches so tagged VLAN traffic can cross switch-to-switch links."))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p("On HQ-DSW1, configure trunk links to all connected devices:"))
    story.append(code_block(
        "interface Ethernet0/0\n description TRUNK-TO-HQ-RTR1-E0/0\n"
        " switchport trunk encapsulation dot1q\n switchport mode trunk\n"
        " switchport trunk native vlan 1000\n switchport trunk allowed vlan 100,200,300,999\n"
        " switchport nonegotiate\n no shutdown\n\n"
        "interface Ethernet0/1\n description TRUNK-TO-HQ-ASW1-E0/0\n"
        " switchport trunk encapsulation dot1q\n switchport mode trunk\n"
        " switchport trunk native vlan 1000\n switchport trunk allowed vlan 100,200,300,999\n"
        " switchport nonegotiate\n no shutdown\n\n"
        "interface Ethernet0/2\n description TRUNK-TO-HQ-ASW2-E0/0\n"
        " switchport trunk encapsulation dot1q\n switchport mode trunk\n"
        " switchport trunk native vlan 1000\n switchport trunk allowed vlan 100,200,300,999\n"
        " switchport nonegotiate\n no shutdown\n\n"
        "interface Ethernet0/3\n description TRUNK-TO-HQ-DSW2-E0/3\n"
        " switchport trunk encapsulation dot1q\n switchport mode trunk\n"
        " switchport trunk native vlan 1000\n switchport trunk allowed vlan 100,200,300,999\n"
        " switchport nonegotiate\n no shutdown"
    ))
    story.append(why_box(
        "switchport trunk encapsulation dot1q must be set BEFORE mode trunk on IOL-L2 — "
        "skipping this causes IOS to reject the trunk command. The explicit allowed VLAN "
        "list prevents unnecessary VLANs from traversing trunks. VLAN 1000 as native "
        "means untagged frames are discarded."
    ))

    story.append(p("Step 2", "step"))
    story.append(p(
        "On HQ-DSW2, configure trunks on E0/1 (to ASW1), E0/2 (to ASW2), E0/3 (to DSW1) "
        "using the same trunk template above with correct descriptions."
    ))

    story.append(p("Step 3", "step"))
    story.append(p(
        "On HQ-ASW1, configure trunks on E0/0 (primary uplink to DSW1) and E0/1 "
        "(redundant uplink to DSW2)."
    ))

    story.append(p("Step 4", "step"))
    story.append(p("On HQ-ASW2, configure trunks on E0/0 (to DSW1) and E0/1 (to DSW2)."))

    story.append(sp(8))
    story.append(p("Verification", "verify_label"))
    story.append(code_block("show interfaces trunk\nshow cdp neighbors"))
    story.append(p(
        "Expected: All trunk ports listed with Mode=on, Encapsulation=802.1q, Native VLAN=1000. "
        "Note: \"Vlans in spanning tree forwarding state = none\" on a redundant port is CORRECT — "
        "STP is blocking the loop path. This is not a failure."
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/p01-ph2-show-interfaces-trunk-DSW1.png"))
    story.append(caption("Figure 2.1 — show interfaces trunk — HQ-DSW1"))

    # ════════════════════════════════════════════════════════
    # PHASE 3: Inter-VLAN Routing
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Phase 3: Inter-VLAN Routing (Router-on-a-Stick)"))
    story.append(sp(8))
    story.append(p("<b>Goal:</b> Configure HQ-RTR1 subinterfaces so it can route traffic between all VLANs."))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p(
        "On HQ-RTR1, bring up the physical trunk interface (no IP — the subinterfaces "
        "handle routing):"
    ))
    story.append(code_block(
        "enable\nconfigure terminal\nhostname HQ-RTR1\nlldp run\n\n"
        "interface Ethernet0/0\n description TRUNK-TO-HQ-DSW1-E0/0\n"
        " no ip address\n no shutdown"
    ))
    story.append(why_box(
        "The parent interface is a \"pipe\" only — it carries 802.1Q-tagged frames from "
        "the switch. No IP is assigned here because routing happens on the subinterfaces."
    ))

    story.append(p("Step 2", "step"))
    story.append(p("Create subinterfaces for each VLAN:"))
    story.append(code_block(
        "interface Ethernet0/0.100\n description GATEWAY-VLAN100-ENGINEERING\n"
        " encapsulation dot1Q 100\n ip address 10.1.100.1 255.255.255.0\n\n"
        "interface Ethernet0/0.200\n description GATEWAY-VLAN200-SALES\n"
        " encapsulation dot1Q 200\n ip address 10.1.200.1 255.255.255.0\n\n"
        "interface Ethernet0/0.300\n description GATEWAY-VLAN300-GUEST\n"
        " encapsulation dot1Q 300\n ip address 10.1.44.1 255.255.255.0\n\n"
        "interface Ethernet0/0.999\n description GATEWAY-VLAN999-MANAGEMENT\n"
        " encapsulation dot1Q 999\n ip address 10.1.99.1 255.255.255.0\n\n"
        "interface Loopback0\n description ROUTER-ID-AND-MGMT\n"
        " ip address 10.0.255.1 255.255.255.255\n\nend\nwrite memory"
    ))
    story.append(why_box(
        "encapsulation dot1Q tells IOS which VLAN to strip/add tags for on this "
        "subinterface. Each subinterface becomes the default gateway for all hosts in "
        "that VLAN. The Loopback provides a stable router ID for OSPF in Project 03."
    ))

    story.append(p("Step 3", "step"))
    story.append(p("Set the domain name and generate RSA keys for SSH (also required for Phase 5):"))
    story.append(code_block(
        "configure terminal\nip domain-name lab.local\n"
        "crypto key generate rsa general-keys modulus 2048"
    ))

    story.append(p("Step 4", "step"))
    story.append(p("Assign static IPs to endpoints. On PC-ENG1:"))
    story.append(code_block(
        "ip addr add 10.1.100.10/24 dev eth0\n"
        "ip link set eth0 up\n"
        "ip route add default via 10.1.100.1"
    ))
    story.append(p(
        "On PC-SALES1 (10.1.200.10, gw 10.1.200.1) and PC-MGMT1 (10.1.99.100, "
        "gw 10.1.99.1) — same pattern."
    ))

    story.append(sp(8))
    story.append(p("Verification", "verify_label"))
    story.append(code_block(
        "show ip interface brief     ! on HQ-RTR1\n"
        "show ip route               ! on HQ-RTR1\n"
        "ping 10.1.200.10            ! from PC-ENG1 — cross-VLAN ping"
    ))
    story.append(p(
        "Expected: All subinterfaces up/up with correct IPs. Routing table shows "
        "directly connected routes for all 4 VLANs. Cross-VLAN ping succeeds."
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/p01-ph3-ping-cross-vlan-ENG1-to-SALES1.png"))
    story.append(caption("Figure 3.1 — Cross-VLAN ping — PC-ENG1 to PC-SALES1"))

    # ════════════════════════════════════════════════════════
    # PHASE 4: STP Hardening
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Phase 4: STP Hardening"))
    story.append(sp(8))
    story.append(p("<b>Goal:</b> Force a deliberate Spanning Tree root bridge election and enable PortFast + BPDU Guard on all access ports."))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p("On HQ-DSW1, set STP priorities to make it root for VLANs 100 and 999:"))
    story.append(code_block(
        "spanning-tree mode rapid-pvst\n"
        "spanning-tree vlan 100 priority 4096\n"
        "spanning-tree vlan 999 priority 4096\n"
        "spanning-tree vlan 200 priority 8192\n"
        "spanning-tree vlan 300 priority 8192"
    ))
    story.append(why_box(
        "Default STP root election uses the lowest MAC address — unpredictable. "
        "Priority 4096 (1/8 of default 32768) guarantees DSW1 wins for VLANs 100 and "
        "999. Rapid-PVST+ converges in 1–3 seconds vs 30–50 seconds for 802.1D."
    ))

    story.append(p("Step 2", "step"))
    story.append(p("On HQ-DSW2, set opposite priorities (root for VLANs 200/300, backup for 100/999):"))
    story.append(code_block(
        "spanning-tree mode rapid-pvst\n"
        "spanning-tree vlan 200 priority 4096\n"
        "spanning-tree vlan 300 priority 4096\n"
        "spanning-tree vlan 100 priority 8192\n"
        "spanning-tree vlan 999 priority 8192"
    ))
    story.append(why_box(
        "Splitting root assignment across two distribution switches load-balances STP "
        "traffic. Each switch handles half the VLANs as primary root."
    ))

    story.append(p("Step 3", "step"))
    story.append(p("On HQ-ASW1 and HQ-ASW2, enable PortFast and BPDU Guard on access ports:"))
    story.append(code_block(
        "spanning-tree mode rapid-pvst\n\n"
        "interface range Ethernet0/2 - 3\n"
        " spanning-tree portfast\n"
        " spanning-tree bpduguard enable"
    ))
    story.append(why_box(
        "PortFast skips STP Listening and Learning states — PCs get connectivity "
        "immediately. BPDU Guard err-disables the port if a switch is plugged in, "
        "protecting the STP topology."
    ))

    story.append(sp(8))
    story.append(p("Verification", "verify_label"))
    story.append(code_block(
        "show spanning-tree vlan 100     ! on HQ-DSW1 — look for \"This bridge is the root\"\n"
        "show spanning-tree root         ! on HQ-ASW1 — verify correct root for each VLAN"
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/p01-ph4-show-spanning-tree-vlan100-DSW1.png"))
    story.append(caption("Figure 4.1 — STP Root confirmed — HQ-DSW1 VLAN 100"))

    # ════════════════════════════════════════════════════════
    # PHASE 5: SSH Hardening
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Phase 5: SSH Hardening"))
    story.append(sp(8))
    story.append(p("<b>Goal:</b> Restrict all device management to SSH v2, limited to the management VLAN only."))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p(
        "Apply the following configuration to ALL five devices "
        "(HQ-RTR1, HQ-DSW1, HQ-DSW2, HQ-ASW1, HQ-ASW2):"
    ))
    story.append(code_block(
        "ip domain-name lab.local\n"
        "username admin privilege 15 secret CMLlab2025!\n"
        "ip ssh version 2\n"
        "ip ssh time-out 60\n"
        "ip ssh authentication-retries 3\n\n"
        "line vty 0 4\n transport input ssh\n login local\n exec-timeout 10 0\n"
        " logging synchronous\n access-class 10 in\n\n"
        "line con 0\n login local\n exec-timeout 10 0\n logging synchronous\n\n"
        "access-list 10 permit 10.1.99.0 0.0.0.255\n"
        "access-list 10 deny any log\n\n"
        "no ip http server\n"
        "no ip http secure-server\n\n"
        "banner motd ^\n"
        "============================================\n"
        "AUTHORIZED ACCESS ONLY\n"
        "All access is logged and monitored\n"
        "============================================\n"
        "^\n\n"
        "service password-encryption\n"
        "enable secret CMLenableP@ss!\n\n"
        "end\nwrite memory"
    ))
    story.append(why_box(
        "transport input ssh: Telnet sends credentials in cleartext — never acceptable "
        "in production. access-class 10: Restricts SSH to 10.1.99.0/24 (management VLAN "
        "only). service password-encryption: Encrypts all cleartext passwords in running config."
    ))

    story.append(p("Step 2", "step"))
    story.append(p("Generate RSA keys on each device after the config above:"))
    story.append(code_block(
        "configure terminal\n"
        "ip domain-name lab.local\n"
        "crypto key generate rsa general-keys modulus 2048"
    ))
    story.append(note_box(
        "ip domain-name MUST be set before generating keys. Without keys, SSH port 22 "
        "never opens — show ip ssh will show \"SSH Disabled\"."
    ))

    story.append(sp(8))
    story.append(p("Verification", "verify_label"))
    story.append(code_block(
        "show ip ssh                     ! should show: SSH Enabled - version 2.0\n"
        "ssh admin@10.1.99.11            ! from PC-MGMT1 — should succeed\n"
        "ssh admin@10.1.99.11            ! from PC-ENG1  — should be refused by ACL"
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/p01-ph5-ssh-login-success-MGMT1.png"))
    story.append(caption("Figure 5.1 — SSH login success from PC-MGMT1"))

    # ════════════════════════════════════════════════════════
    # FINAL VERIFICATION CHECKLIST
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Final Verification Checklist"))
    story.append(sp(8))
    story.append(checklist_table(
        ["#", "Test", "Command", "Device", "Expected"],
        [
            ["1", "VLANs exist",     "show vlan brief",                "All switches", "100,200,300,999,1000 active"],
            ["2", "Trunks up",       "show interfaces trunk",          "DSW1",         "All uplinks trunking, native 1000"],
            ["3", "Subinterfaces",   "show ip interface brief",        "HQ-RTR1",      "E0/0.100–.999 all up/up"],
            ["4", "Cross-VLAN ping", "ping 10.1.200.10",               "PC-ENG1",      "5/5 success"],
            ["5", "STP root DSW1",   "show spanning-tree vlan 100",    "HQ-DSW1",      "This bridge is the root"],
            ["6", "STP root DSW2",   "show spanning-tree vlan 200",    "HQ-DSW2",      "This bridge is the root"],
            ["7", "SSH from Mgmt",   "ssh admin@10.1.99.11",           "PC-MGMT1",     "Login succeeds"],
            ["8", "SSH blocked",     "ssh admin@10.1.99.11",           "PC-ENG1",      "Connection refused"],
        ]
    ))
    story.append(sp(8))

    # ════════════════════════════════════════════════════════
    # TROUBLESHOOTING
    # ════════════════════════════════════════════════════════
    story.append(section_header("Troubleshooting — Top 5 Issues"))
    story.append(sp(8))

    story += issue_block(
        "Issue 1 — Interface Naming Mismatch",
        "Commands targeting GigabitEthernet0/0 returned \"Invalid interface\" errors on every device.",
        "CML IOL images use Ethernet0/x naming, not GigabitEthernet. IOL-L2 switches have one 4-port slot (E0/0–E0/3), not dual slots.",
        "Ran show ip interface brief on every node after boot and adapted all configs to the actual interface names shown."
    )

    story += issue_block(
        "Issue 2 — Native VLAN Mismatch CDP Warning",
        "CDP warnings \"NATIVE_VLAN_MISMATCH on Ethernet0/3 (1000) with HQ-DSW2 (1)\" appeared on DSW1 console during build.",
        "DSW1 was configured with native VLAN 1000 first; the far-end switches still had default native VLAN 1 while being configured.",
        "Completed trunk configuration on all remaining switches. Warnings cleared automatically once both ends matched."
    )

    story += issue_block(
        "Issue 3 — STP Redundant Trunk Showing \"none\" for Forwarding VLANs",
        "show interfaces trunk on HQ-DSW2 showed \"Vlans in spanning tree forwarding state = none\" on redundant uplink ports.",
        "Not a failure — Rapid-PVST+ was blocking the redundant path to prevent a Layer 2 loop. This is correct behavior in a dual-distribution design.",
        "No fix required. Confirmed correct STP root layout and verified traffic was flowing via the primary path."
    )

    story += issue_block(
        "Issue 4 — SSH Connection Refused Despite VTY Config Applied",
        "SSH from PC-MGMT1 to HQ-DSW1 failed with \"connection refused\" even though ping succeeded.",
        "crypto key generate rsa was not run after ip domain-name was set. Without RSA host keys, SSH port 22 never opens.",
        "Re-ran ip domain-name lab.local followed by crypto key generate rsa general-keys modulus 2048 on all devices. IOS logged: %SSH-5-ENABLED: SSH 2.0 has been enabled."
    )

    story += issue_block(
        "Issue 5 — Break/Fix: VLAN 100 Removed from Trunk Allowed List",
        "PC-ENG1 lost all connectivity. Trunks remained up with no physical errors — no interface down messages.",
        "Both ASW1 uplinks had VLAN 100 removed from the allowed VLAN list. The trunk stayed UP — the only evidence was in show interfaces trunk.",
        "Added VLAN 100 back to the allowed list on both ASW1 uplinks with switchport trunk allowed vlan 100,200,300,999."
    )

    # ════════════════════════════════════════════════════════
    # BREAK/FIX CHALLENGE
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Break/Fix Challenge"))
    story.append(sp(8))
    story.append(p(
        "<b>Scenario:</b> PC-ENG1 has lost all network connectivity. Trunks are up, "
        "no interfaces are down. Diagnose and fix using show commands only."
    ))
    story.append(sp(6))

    story.append(embed_image(f"{SS}/p01-breakfix-ping-failing-ENG1.png"))
    story.append(caption("Figure B.1 — PC-ENG1 ping failing — VLAN 100 blocked"))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p("Verify the problem from PC-ENG1:"))
    story.append(code_block("ping 10.1.100.1     ! gateway — fails\nping 10.1.99.11     ! management switch — fails"))

    story.append(p("Step 2", "step"))
    story.append(p("Check Layer 1/2 at HQ-ASW1:"))
    story.append(code_block("show vlan brief\nshow interfaces trunk"))
    story.append(p(
        "Look for VLAN 100 missing from \"Vlans allowed on trunk\" column on E0/0 and E0/1."
    ))

    story.append(p("Step 3", "step"))
    story.append(p("Apply fix on HQ-ASW1:"))
    story.append(code_block(
        "configure terminal\ninterface Ethernet0/0\n"
        " switchport trunk allowed vlan 100,200,300,999\n"
        "interface Ethernet0/1\n"
        " switchport trunk allowed vlan 100,200,300,999\n"
        "end\nwrite memory"
    ))

    story.append(p("Step 4", "step"))
    story.append(p("Re-verify from PC-ENG1:"))
    story.append(code_block("ping 10.1.200.10    ! cross-VLAN — should now succeed"))
    story.append(embed_image(f"{SS}/p01-breakfix-ping-restored-ENG1.png"))
    story.append(caption("Figure B.2 — PC-ENG1 connectivity restored"))
    story.append(sp(6))
    story.append(note_box(
        "Key Lesson: A wrong allowed VLAN list is one of the most common trunking "
        "failures. The trunk stays UP with no physical errors. The only diagnostic tool "
        "is show interfaces trunk — check the Vlans allowed column carefully."
    ))

    return story


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT 02 — MULTI-SITE EXPANSION + DHCP
# ═══════════════════════════════════════════════════════════════════════════════

def build_project_02():
    SS = f"{BASE}/project-01-campus-foundation/verification/screenshots"  # shared screenshots dir
    TOPO = f"{BASE}/project-02-multi-site-dhcp/diagrams/cml-topology.png"
    story = []

    # ── Cover ──
    story += cover_page(
        "Project 02 — Multi-Site Expansion + DHCP",
        "Branch Site, WAN Link, Centralized DHCP, IPv6 Dual-Stack, DNS",
        [
            "Author: Leonel Chongong",
            "Date: April 2026",
            "Platform: Cisco CML 2.9 | IOL + IOL-L2",
            "Prerequisite: Project 01 — Campus Foundation",
            "Methodology: Build → Verify → Break → Fix",
        ]
    )

    # ── Setup and Scenario ──
    story.append(section_header("Setup and Scenario"))
    story.append(sp(8))
    story.append(p("<b>Business Context</b>", "subsec"))
    story.append(p(
        "The HQ campus from Project 01 exists as an isolated single site: static IPs "
        "on all endpoints, no DHCP or DNS services, and no branch connectivity. A new "
        "branch office needs to be connected, all endpoints should get IPs automatically, "
        "and IPv6 dual-stack should be enabled for forward compatibility."
    ))
    story.append(sp(6))
    story.append(p("<b>What You Will Build</b>", "subsec"))
    for bullet in [
        "Branch site switching infrastructure (BR-RTR1, BR-DSW1, BR-ASW1) matching HQ's VLAN scheme",
        "Point-to-point /30 WAN link between HQ-RTR1 and BR-RTR1",
        "Static routing so both sites reach all remote subnets including management",
        "Centralized Dnsmasq DHCP server at HQ (10.1.99.50) serving 8 VLAN pools via ip helper-address relay",
        "Static DHCP reservations by MAC for branch endpoints",
        "IPv6 dual-stack: /126 WAN, /64 VLAN 100 at both sites, SLAAC for endpoints",
        "DNS A records for all devices in lab.local domain",
    ]:
        story.append(p(f"• {bullet}", "bullet"))
    story.append(sp(8))

    # ── STAR Summary ──
    story.append(section_header("STAR Summary"))
    story.append(sp(8))
    for label, text in [
        ("Situation", "HQ campus existed as an isolated single site with static IPs on all endpoints and no DHCP or DNS service."),
        ("Task", "Add a branch site, connect both sites over WAN, deploy centralized DHCP serving all 8 VLANs via relay, add IPv6 dual-stack, and verify DNS end-to-end."),
        ("Action", "Deployed BR-RTR1/DSW1/ASW1 matching HQ's VLAN scheme, built /30 WAN, deployed Dnsmasq DHCP server at HQ serving 8 pools via ip helper-address, configured IPv6 SLAAC, added DNS A records for all devices."),
        ("Result", "Can design a multi-site enterprise network, configure centralized DHCP serving remote sites over WAN, and verify dual-stack connectivity from endpoints at both sites."),
    ]:
        story.append(p(f"<b>{label}:</b> {text}"))
        story.append(sp(3))
    story.append(sp(8))

    # ── Technologies Used ──
    story.append(section_header("Technologies Used"))
    story.append(sp(8))
    for tech in [
        "Router-on-a-Stick (branch site)",
        "802.1Q Trunking",
        "Point-to-Point WAN /30 link",
        "Static Routing (IPv4)",
        "Centralized DHCP (Dnsmasq) with ip helper-address relay",
        "DHCP pools for 8 VLANs across both sites",
        "Static DHCP reservations by MAC address",
        "IPv6 dual-stack (/126 WAN / /64 VLAN 100)",
        "SLAAC via Router Advertisements",
        "DNS with address= directives (Dnsmasq)",
        "Rapid-PVST+ STP, PortFast + BPDU Guard",
        "SSH v2 hardening (all devices)",
        "ip routing on access switch (BR-ASW1)",
    ]:
        story.append(p(f"• {tech}", "bullet"))
    story.append(sp(8))

    # ── Network Topology ──
    story.append(section_header("Network Topology"))
    story.append(sp(8))
    story.append(embed_image(TOPO))
    story.append(caption("Figure T.1 — CML Topology — Project 02 Multi-Site Expansion"))
    story.append(sp(8))

    # ── IP Addressing Tables ──
    story.append(section_header("IP Addressing"))
    story.append(sp(8))
    story.append(p("<b>Branch Site (10.2.x.x)</b>", "subsec"))
    story.append(ip_table(
        ["Device", "Interface", "IP Address", "Subnet", "Purpose"],
        [
            ["BR-RTR1",  "E0/0.100",  "10.2.100.1",   "/24", "Engineering gateway"],
            ["BR-RTR1",  "E0/0.200",  "10.2.200.1",   "/24", "Sales gateway"],
            ["BR-RTR1",  "E0/0.300",  "10.2.44.1",    "/24", "Guest gateway"],
            ["BR-RTR1",  "E0/0.500",  "10.2.50.1",    "/24", "Voice gateway"],
            ["BR-RTR1",  "E0/0.999",  "10.2.99.1",    "/24", "Management gateway"],
            ["BR-DSW1",  "VLAN 999",  "10.2.99.2",    "/24", "Management SVI"],
            ["BR-ASW1",  "VLAN 999",  "10.2.99.3",    "/24", "Management SVI"],
            ["PC-BR1",   "eth0",      "10.2.100.197", "/24", "Branch Engineering (DHCP reserved)"],
            ["PC-BR2",   "eth0",      "10.2.200.108", "/24", "Branch Sales (DHCP reserved)"],
        ]
    ))
    story.append(sp(10))
    story.append(p("<b>WAN Link</b>", "subsec"))
    story.append(ip_table(
        ["Device", "Interface", "IP Address", "Subnet", "Purpose"],
        [
            ["HQ-RTR1", "E0/1", "10.0.0.1", "/30", "WAN HQ-side"],
            ["BR-RTR1", "E0/1", "10.0.0.2", "/30", "WAN Branch-side"],
        ]
    ))
    story.append(sp(10))
    story.append(p("<b>HQ Additions</b>", "subsec"))
    story.append(ip_table(
        ["Device", "Interface", "IP Address", "Subnet", "Purpose"],
        [
            ["HQ-RTR1",      "E0/0.500", "10.1.50.1",  "/24", "Voice VLAN gateway (new)"],
            ["HQ-DHCP-DNS",  "eth0",     "10.1.99.50", "/24", "Centralized DHCP+DNS"],
        ]
    ))
    story.append(sp(10))
    story.append(p("<b>IPv6 Addressing</b>", "subsec"))
    story.append(ip_table(
        ["Interface", "IPv6 Address", "Purpose"],
        [
            ["HQ-RTR1 E0/1",      "2001:db8:0:1::1/126", "WAN HQ-side"],
            ["BR-RTR1 E0/1",      "2001:db8:0:1::2/126", "WAN Branch-side"],
            ["HQ-RTR1 E0/0.100",  "2001:db8:1:100::1/64","HQ Eng IPv6 gateway"],
            ["BR-RTR1 E0/0.100",  "2001:db8:2:100::1/64","Branch Eng IPv6 gateway"],
        ]
    ))
    story.append(sp(10))
    story.append(p("<b>DHCP Pools</b>", "subsec"))
    story.append(ip_table(
        ["Tag", "Subnet", "Range", "Gateway", "DNS"],
        [
            ["hq-eng",   "10.1.100.0/24", ".100–.200", "10.1.100.1", "10.1.99.50"],
            ["hq-sales", "10.1.200.0/24", ".100–.200", "10.1.200.1", "10.1.99.50"],
            ["hq-guest", "10.1.44.0/24",  ".100–.200", "10.1.44.1",  "10.1.99.50"],
            ["hq-voice", "10.1.50.0/24",  ".100–.200", "10.1.50.1",  "10.1.99.50"],
            ["br-eng",   "10.2.100.0/24", ".100–.200", "10.2.100.1", "10.1.99.50"],
            ["br-sales", "10.2.200.0/24", ".100–.200", "10.2.200.1", "10.1.99.50"],
            ["br-guest", "10.2.44.0/24",  ".100–.200", "10.2.44.1",  "10.1.99.50"],
            ["br-voice", "10.2.50.0/24",  ".100–.200", "10.2.50.1",  "10.1.99.50"],
        ]
    ))
    story.append(sp(8))

    # ════════════════════════════════════════════════════════
    # PHASE 1: Branch Site Base
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Phase 1: Branch Site Base"))
    story.append(sp(8))
    story.append(p("<b>Goal:</b> Build the complete branch switching and routing infrastructure from scratch."))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p("On BR-RTR1, configure router-on-a-stick for all branch VLANs:"))
    story.append(code_block(
        "enable\nconfigure terminal\nhostname BR-RTR1\nlldp run\n\n"
        "interface Ethernet0/0\n description TRUNK-TO-BR-DSW1-E0/0\n"
        " no ip address\n no shutdown\n\n"
        "interface Ethernet0/0.100\n description GATEWAY-VLAN100-ENGINEERING\n"
        " encapsulation dot1Q 100\n ip address 10.2.100.1 255.255.255.0\n no shutdown\n\n"
        "interface Ethernet0/0.200\n description GATEWAY-VLAN200-SALES\n"
        " encapsulation dot1Q 200\n ip address 10.2.200.1 255.255.255.0\n no shutdown\n\n"
        "interface Ethernet0/0.300\n description GATEWAY-VLAN300-GUEST\n"
        " encapsulation dot1Q 300\n ip address 10.2.44.1 255.255.255.0\n no shutdown\n\n"
        "interface Ethernet0/0.500\n description GATEWAY-VLAN500-VOICE\n"
        " encapsulation dot1Q 500\n ip address 10.2.50.1 255.255.255.0\n no shutdown\n\n"
        "interface Ethernet0/0.999\n description GATEWAY-VLAN999-MGMT\n"
        " encapsulation dot1Q 999\n ip address 10.2.99.1 255.255.255.0\n no shutdown\n\n"
        "interface Ethernet0/0.1000\n description NATIVE-VLAN1000-UNUSED\n"
        " encapsulation dot1Q 1000 native\n no shutdown\n\nend\nwrite memory"
    ))
    story.append(why_box(
        "Voice VLAN 500 is built now even without phones — avoids rework when Project 11 "
        "(QoS) is configured. The native VLAN 1000 subinterface explicitly tags untagged "
        "frames, preventing VLAN hopping attacks."
    ))

    story.append(p("Step 2", "step"))
    story.append(p("On BR-DSW1, configure as distribution switch and STP root:"))
    story.append(code_block(
        "enable\nconfigure terminal\nhostname BR-DSW1\nlldp run\nip routing\n\n"
        "vlan 100\n name Engineering\nvlan 200\n name Sales\nvlan 300\n name Guest\n"
        "vlan 500\n name Voice\nvlan 999\n name Management\nvlan 1000\n name NATIVE-UNUSED\n\n"
        "interface vlan 999\n ip address 10.2.99.2 255.255.255.0\n no shutdown\n\n"
        "ip default-gateway 10.2.99.1\n\n"
        "spanning-tree mode rapid-pvst\n"
        "spanning-tree vlan 100,200,300,500,999,1000 priority 4096\n\n"
        "interface Ethernet0/0\n description TRUNK-TO-BR-RTR1-E0/0\n"
        " switchport trunk encapsulation dot1q\n switchport mode trunk\n"
        " switchport trunk native vlan 1000\n"
        " switchport trunk allowed vlan 100,200,300,500,999,1000\n no shutdown\n\n"
        "interface Ethernet0/1\n description TRUNK-TO-BR-ASW1-E0/0\n"
        " switchport trunk encapsulation dot1q\n switchport mode trunk\n"
        " switchport trunk native vlan 1000\n"
        " switchport trunk allowed vlan 100,200,300,500,999,1000\n no shutdown\n\nend\nwrite memory"
    ))
    story.append(why_box(
        "ip routing enabled: Project 03 OSPF needs BR-DSW1 as an area router — enabling "
        "it now avoids reconfiguration. Single switch as root for all VLANs: Only one "
        "distribution switch at branch — auto-election could make BR-ASW1 root, causing "
        "a forwarding black-hole."
    ))

    story.append(p("Step 3", "step"))
    story.append(p("On BR-ASW1, configure access switch with ip routing:"))
    story.append(code_block(
        "enable\nconfigure terminal\nhostname BR-ASW1\nlldp run\nip routing\n"
        "ip route 0.0.0.0 0.0.0.0 10.2.99.1\n\n"
        "vlan 100\n name Engineering\nvlan 200\n name Sales\nvlan 300\n name Guest\n"
        "vlan 500\n name Voice\nvlan 999\n name Management\nvlan 1000\n name NATIVE-UNUSED\n\n"
        "interface vlan 999\n ip address 10.2.99.3 255.255.255.0\n no shutdown\n\n"
        "spanning-tree mode rapid-pvst\n\n"
        "interface Ethernet0/0\n description TRUNK-TO-BR-DSW1-E0/1\n"
        " switchport trunk encapsulation dot1q\n switchport mode trunk\n"
        " switchport trunk native vlan 1000\n"
        " switchport trunk allowed vlan 100,200,300,500,999,1000\n no shutdown\n\n"
        "interface Ethernet1/0\n description ACCESS-PC-BR1-VLAN100\n"
        " switchport mode access\n switchport access vlan 100\n switchport nonegotiate\n"
        " spanning-tree portfast\n spanning-tree bpduguard enable\n no shutdown\n\n"
        "interface Ethernet1/1\n description ACCESS-PC-BR2-VLAN200\n"
        " switchport mode access\n switchport access vlan 200\n switchport nonegotiate\n"
        " spanning-tree portfast\n spanning-tree bpduguard enable\n no shutdown\n\nend\nwrite memory"
    ))
    story.append(why_box(
        "ip routing instead of ip default-gateway: ip default-gateway cannot route replies "
        "destined to remote subnets. When HQ-RTR1 (10.0.0.1) pings BR-ASW1, the ICMP "
        "reply must return to a remote subnet — this requires the routing engine, not the "
        "management-plane handler."
    ))
    story.append(note_box(
        "BR-ASW1 uses BOTH Ethernet0/x (trunks) AND Ethernet1/x (access ports). "
        "Always verify with show cdp neighbors after cabling."
    ))

    story.append(sp(8))
    story.append(p("Verification", "verify_label"))
    story.append(code_block(
        "show ip interface brief          ! BR-RTR1 — E0/0.100 through .999 all up/up\n"
        "show interfaces trunk            ! BR-DSW1 — both trunks up, native 1000\n"
        "show spanning-tree vlan 100      ! BR-DSW1 — \"This bridge is the root\""
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/p02-p1-02-RTR1-ip-brief.png"))
    story.append(caption("Figure 1.1 — BR-RTR1 show ip interface brief"))

    # ════════════════════════════════════════════════════════
    # PHASE 2: WAN Connectivity
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Phase 2: WAN Connectivity"))
    story.append(sp(8))
    story.append(p("<b>Goal:</b> Connect HQ and Branch over a point-to-point /30 link and add static routes so both sites reach all remote subnets."))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p("On HQ-RTR1, configure the WAN interface and add VLAN 500 (Voice) subinterface:"))
    story.append(code_block(
        "configure terminal\n\n"
        "interface Ethernet0/1\n description WAN-TO-BR-RTR1-E0/1\n"
        " ip address 10.0.0.1 255.255.255.252\n bandwidth 1000\n delay 1000\n no shutdown\n\n"
        "interface Ethernet0/0.500\n description GATEWAY-VLAN500-VOICE\n"
        " encapsulation dot1Q 500\n ip address 10.1.50.1 255.255.255.0\n\n"
        "ip route 10.2.100.0 255.255.255.0 10.0.0.2\n"
        "ip route 10.2.200.0 255.255.255.0 10.0.0.2\n"
        "ip route 10.2.44.0  255.255.255.0 10.0.0.2\n"
        "ip route 10.2.50.0  255.255.255.0 10.0.0.2\n"
        "ip route 10.2.99.0  255.255.255.0 10.0.0.2\n\nend\nwrite memory"
    ))
    story.append(why_box(
        "/30 gives exactly 2 usable IPs for a point-to-point link — using /24 wastes 252 "
        "addresses. bandwidth 1000 and delay 1000: OSPF in Project 03 calculates cost from "
        "bandwidth — IOL defaults to 10 Mbps making WAN look identical to LAN. Setting "
        "1 Mbps now ensures correct OSPF cost without rework. 10.2.99.0 route included: "
        "Without it, SSH to branch switches fails."
    ))

    story.append(p("Step 2", "step"))
    story.append(p("On BR-RTR1, configure the WAN interface and static routes back to HQ:"))
    story.append(code_block(
        "configure terminal\n\n"
        "interface Ethernet0/1\n description WAN-TO-HQ-RTR1-E0/1\n"
        " ip address 10.0.0.2 255.255.255.252\n bandwidth 1000\n delay 1000\n no shutdown\n\n"
        "ip route 10.1.100.0 255.255.255.0 10.0.0.1\n"
        "ip route 10.1.200.0 255.255.255.0 10.0.0.1\n"
        "ip route 10.1.44.0  255.255.255.0 10.0.0.1\n"
        "ip route 10.1.50.0  255.255.255.0 10.0.0.1\n"
        "ip route 10.1.99.0  255.255.255.0 10.0.0.1\n\nend\nwrite memory"
    ))

    story.append(sp(8))
    story.append(p("Verification", "verify_label"))
    story.append(code_block(
        "show ip route            ! HQ-RTR1 — 5 static routes to 10.2.x.x via 10.0.0.2\n"
        "ping 10.2.99.3           ! HQ-RTR1 — cross-site ping to BR-ASW1 management"
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/p02-p2-01-cross-site-ping.png"))
    story.append(caption("Figure 2.1 — Cross-site ping confirmed"))

    # ════════════════════════════════════════════════════════
    # PHASE 3: Centralized DHCP
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Phase 3: Centralized DHCP"))
    story.append(sp(8))
    story.append(p("<b>Goal:</b> Deploy HQ-DHCP-DNS (Dnsmasq) at 10.1.99.50 and configure ip helper-address relay on both routers to serve all 8 VLANs across both sites."))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p(
        "In CML, cable HQ-DHCP-DNS eth0 to HQ-DSW2 Ethernet0/0. "
        "Then on HQ-DSW2, configure the port as an access port in VLAN 999:"
    ))
    story.append(code_block(
        "configure terminal\ninterface Ethernet0/0\n description TO_HQ-DHCP-DNS\n"
        " switchport mode access\n switchport access vlan 999\n"
        " spanning-tree portfast\n spanning-tree bpduguard enable\n no shutdown\nend\nwrite memory"
    ))
    story.append(why_box(
        "The DHCP server has IP 10.1.99.50 on the management subnet — it must be in "
        "VLAN 999 to have Layer 2 connectivity."
    ))

    story.append(p("Step 2", "step"))
    story.append(p(
        "In CML, click HQ-DHCP-DNS → CONFIG tab. "
        "Paste the following as the Startup Script:"
    ))
    story.append(code_block(
        "#!/bin/sh\nhostname hq-dhcp-dns\n"
        "ip addr add 10.1.99.50/24 dev eth0\nip link set eth0 up\n"
        "ip route add default via 10.1.99.1\n"
        "kill -9 $(cat /var/run/dnsmasq.pid) 2>/dev/null\n"
        "dnsmasq --conf-file=/etc/dnsmasq.conf\n"
        'echo "=== HQ-DHCP-DNS READY ==="\nip addr show eth0\nip route show'
    ))

    story.append(p("Step 3", "step"))
    story.append(p("In the CML CONFIG tab, paste the following as dnsmasq.conf:"))
    story.append(code_block(
        "domain=lab.local\nlocal=/lab.local/\nlog-dhcp\n\n"
        "dhcp-range=set:hq-eng,10.1.100.100,10.1.100.200,255.255.255.0,24h\n"
        "dhcp-option=tag:hq-eng,option:router,10.1.100.1\n"
        "dhcp-option=tag:hq-eng,option:dns-server,10.1.99.50\n\n"
        "dhcp-range=set:hq-sales,10.1.200.100,10.1.200.200,255.255.255.0,24h\n"
        "dhcp-option=tag:hq-sales,option:router,10.1.200.1\n"
        "dhcp-option=tag:hq-sales,option:dns-server,10.1.99.50\n\n"
        "dhcp-range=set:hq-guest,10.1.44.100,10.1.44.200,255.255.255.0,24h\n"
        "dhcp-option=tag:hq-guest,option:router,10.1.44.1\n"
        "dhcp-option=tag:hq-guest,option:dns-server,10.1.99.50\n\n"
        "dhcp-range=set:hq-voice,10.1.50.100,10.1.50.200,255.255.255.0,24h\n"
        "dhcp-option=tag:hq-voice,option:router,10.1.50.1\n"
        "dhcp-option=tag:hq-voice,option:dns-server,10.1.99.50\n\n"
        "dhcp-range=set:br-eng,10.2.100.100,10.2.100.200,255.255.255.0,24h\n"
        "dhcp-option=tag:br-eng,option:router,10.2.100.1\n"
        "dhcp-option=tag:br-eng,option:dns-server,10.1.99.50\n\n"
        "dhcp-range=set:br-sales,10.2.200.100,10.2.200.200,255.255.255.0,24h\n"
        "dhcp-option=tag:br-sales,option:router,10.2.200.1\n"
        "dhcp-option=tag:br-sales,option:dns-server,10.1.99.50\n\n"
        "dhcp-range=set:br-guest,10.2.44.100,10.2.44.200,255.255.255.0,24h\n"
        "dhcp-option=tag:br-guest,option:router,10.2.44.1\n"
        "dhcp-option=tag:br-guest,option:dns-server,10.1.99.50\n\n"
        "dhcp-range=set:br-voice,10.2.50.100,10.2.50.200,255.255.255.0,24h\n"
        "dhcp-option=tag:br-voice,option:router,10.2.50.1\n"
        "dhcp-option=tag:br-voice,option:dns-server,10.1.99.50\n\n"
        "dhcp-host=52:54:00:22:a6:9c,pc-br1,10.2.100.197\n"
        "dhcp-host=52:54:00:53:da:69,pc-br2,10.2.200.108\n\n"
        "address=/hq-rtr1.lab.local/10.1.99.1\n"
        "address=/hq-dsw1.lab.local/10.1.99.11\n"
        "address=/hq-dsw2.lab.local/10.1.99.12\n"
        "address=/hq-asw1.lab.local/10.1.99.13\n"
        "address=/hq-asw2.lab.local/10.1.99.14\n"
        "address=/br-rtr1.lab.local/10.2.99.1\n"
        "address=/br-dsw1.lab.local/10.2.99.2\n"
        "address=/br-asw1.lab.local/10.2.99.3\n"
        "address=/hq-dhcp-dns.lab.local/10.1.99.50\n"
        "address=/pc-br1.lab.local/10.2.100.197\n"
        "address=/pc-br2.lab.local/10.2.200.108"
    ))
    story.append(note_box(
        "CRITICAL: Do NOT include bind-interfaces — it causes a container crash (exit "
        "code 30). Do NOT include interface=eth0 — it silently blocks relayed DHCP packets."
    ))

    story.append(p("Step 4", "step"))
    story.append(p(
        "On both HQ-RTR1 and BR-RTR1, configure ip helper-address on all data VLAN subinterfaces:"
    ))
    story.append(code_block(
        "configure terminal\n"
        "interface Ethernet0/0.100\n ip helper-address 10.1.99.50\n"
        "interface Ethernet0/0.200\n ip helper-address 10.1.99.50\n"
        "interface Ethernet0/0.300\n ip helper-address 10.1.99.50\n"
        "interface Ethernet0/0.500\n ip helper-address 10.1.99.50\nend\nwrite memory"
    ))
    story.append(why_box(
        "The relay inserts the subinterface IP as giaddr (gateway address field). "
        "Dnsmasq reads giaddr to select the correct DHCP pool. If configured on parent "
        "E0/0, giaddr = 0.0.0.0 and pool selection fails."
    ))

    story.append(sp(8))
    story.append(p("Verification", "verify_label"))
    story.append(p(
        "Wait 20 seconds after HQ-DHCP-DNS shows BOOTED (startup script needs time). "
        "Then on PC-BR1:"
    ))
    story.append(code_block("udhcpc -i eth0 -f"))
    story.append(p("Expected: IP in range 10.2.100.100–200 from server 10.1.99.50."))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/p02-p3-01-dnsmasq-log.png"))
    story.append(caption("Figure 3.1 — Dnsmasq DHCP leases across both sites"))

    # ════════════════════════════════════════════════════════
    # PHASE 4: IPv6 Dual-Stack
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Phase 4: IPv6 Dual-Stack"))
    story.append(sp(8))
    story.append(p("<b>Goal:</b> Add IPv6 to the WAN link and VLAN 100 at both sites. Enable SLAAC so endpoints self-configure IPv6 addresses."))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p("On HQ-RTR1, enable IPv6 routing and configure interfaces:"))
    story.append(code_block(
        "configure terminal\nipv6 unicast-routing\n\n"
        "interface Ethernet0/1\n ipv6 address 2001:db8:0:1::1/126\n ipv6 enable\n\n"
        "interface Ethernet0/0.100\n ipv6 address 2001:db8:1:100::1/64\n ipv6 enable\n\n"
        "ipv6 route 2001:db8:2:100::/64 2001:db8:0:1::2\n\nend\nwrite memory"
    ))
    story.append(why_box(
        "ipv6 unicast-routing: Without this global command, the router drops all IPv6 "
        "packets even if interfaces have addresses. /126 on WAN: IPv6 equivalent of /30 — "
        "exactly 2 usable addresses. /64 on VLAN 100: SLAAC requires /64 — hosts use "
        "EUI-64 (derived from MAC) combined with the /64 prefix to build a global IPv6 "
        "address automatically."
    ))

    story.append(p("Step 2", "step"))
    story.append(p("On BR-RTR1, mirror the IPv6 configuration:"))
    story.append(code_block(
        "configure terminal\nipv6 unicast-routing\n\n"
        "interface Ethernet0/1\n ipv6 address 2001:db8:0:1::2/126\n ipv6 enable\n\n"
        "interface Ethernet0/0.100\n ipv6 address 2001:db8:2:100::1/64\n ipv6 enable\n\n"
        "ipv6 route 2001:db8:1:100::/64 2001:db8:0:1::1\n\nend\nwrite memory"
    ))

    story.append(sp(8))
    story.append(p("Verification", "verify_label"))
    story.append(code_block(
        "show ipv6 route                     ! HQ-RTR1 — static route to 2001:db8:2:100::/64\n"
        "ping ipv6 2001:db8:0:1::2           ! HQ-RTR1 to BR-RTR1 WAN\n"
        "ip -6 addr show eth0                ! PC-BR1 — SLAAC address in 2001:db8:2:100::/64"
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/p02-p4-03-cross-site-ipv6-ping.png"))
    story.append(caption("Figure 4.1 — Cross-site IPv6 ping"))

    # ════════════════════════════════════════════════════════
    # PHASE 5: DNS End-to-End
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Phase 5: DNS End-to-End"))
    story.append(sp(8))
    story.append(p("<b>Goal:</b> Enable DNS resolution for all devices using the Dnsmasq server."))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p(
        "Phase 1 applied no ip domain lookup to stop IOS from hanging on mistyped "
        "commands. Re-enable DNS now that a valid server exists. On HQ-RTR1 and BR-RTR1:"
    ))
    story.append(code_block(
        "configure terminal\nip domain lookup\nip name-server 10.1.99.50\nend\nwrite memory"
    ))
    story.append(why_box(
        "no ip domain lookup blocks ALL DNS queries from the router — including legitimate "
        "ones like ping hq-rtr1.lab.local. With a real name-server configured, this "
        "restriction no longer applies."
    ))

    story.append(sp(8))
    story.append(p("Verification", "verify_label"))
    story.append(code_block(
        "nslookup hq-rtr1.lab.local 10.1.99.50    ! PC-BR1 — should return 10.1.99.1\n"
        "nslookup br-rtr1.lab.local 10.1.99.50    ! PC-BR1 — should return 10.2.99.1\n"
        "ping hq-rtr1.lab.local                   ! BR-RTR1 — should resolve and ping"
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/p02-p5-01-PC-BR1-nslookup-hqrtr1.png"))
    story.append(caption("Figure 5.1 — DNS resolution from PC-BR1"))

    # ════════════════════════════════════════════════════════
    # FINAL VERIFICATION CHECKLIST
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Final Verification Checklist"))
    story.append(sp(8))
    story.append(checklist_table(
        ["#", "Test", "Command", "Device", "Expected"],
        [
            ["1",  "Branch subinterfaces",    "show ip interface brief",       "BR-RTR1",  "E0/0.100–.999 all up/up"],
            ["2",  "Branch trunks",           "show interfaces trunk",         "BR-DSW1",  "E0/0 and E0/1 trunking, native 1000"],
            ["3",  "Branch STP root",         "show spanning-tree vlan 100",   "BR-DSW1",  "This bridge is the root"],
            ["4",  "WAN routing",             "show ip route",                 "HQ-RTR1",  "5 static routes to 10.2.x.x"],
            ["5",  "Cross-site ping",         "ping 10.2.99.3",                "HQ-RTR1",  "5/5 success"],
            ["6",  "DHCP relay",              "udhcpc -i eth0",                "PC-BR1",   "IP from 10.1.99.50 in 10.2.100.x"],
            ["7",  "Helper-address audit",    "show run | section helper",     "Both RTRs","10.1.99.50 on all data subifs"],
            ["8",  "IPv6 WAN",                "ping ipv6 2001:db8:0:1::2",     "HQ-RTR1",  "5/5 success"],
            ["9",  "SLAAC address",           "ip -6 addr show eth0",          "PC-BR1",   "2001:db8:2:100::/64 present"],
            ["10", "DNS resolution",          "nslookup hq-rtr1.lab.local",    "PC-BR1",   "Returns 10.1.99.1"],
        ]
    ))
    story.append(sp(8))

    # ════════════════════════════════════════════════════════
    # TROUBLESHOOTING
    # ════════════════════════════════════════════════════════
    story.append(section_header("Troubleshooting — Top 5 Issues"))
    story.append(sp(8))

    story += issue_block(
        "Issue 1 — Dnsmasq Container Crash (bind-interfaces)",
        "CML reported \"container failed to start\" with exit code 30 when starting HQ-DHCP-DNS.",
        "The bind-interfaces directive causes dnsmasq to crash because it tries to bind to eth0 before the interface is fully available — a race condition on CML Dnsmasq nodes.",
        "Removed bind-interfaces from dnsmasq.conf and used the RESTORE button in the CML CONFIG tab to apply the corrected configuration."
    )

    story += issue_block(
        "Issue 2 — ip default-gateway Insufficient for Remote-Subnet ICMP",
        "Pings from HQ-RTR1 (10.0.0.1) to BR-ASW1 (10.2.99.3) failed with 0% success while pings to BR-RTR1 and BR-DSW1 succeeded.",
        "ip default-gateway on IOL-L2 cannot route ICMP replies back to remote subnets. It only handles management-plane packets destined to the same subnet.",
        "Replaced ip default-gateway with ip routing and added ip route 0.0.0.0 0.0.0.0 10.2.99.1."
    )

    story += issue_block(
        "Issue 3 — interface=eth0 Blocking DHCP Relay Packets",
        "After configuring helper-address, dnsmasq logs continued showing \"no address range available via eth0\" instead of \"via 10.x.x.x\" — indicating relay was not recognized.",
        "interface=eth0 restricts dnsmasq to only process broadcast DHCP requests on eth0. Relayed packets arrive as unicast UDP — this directive silently dropped them.",
        "Removed interface=eth0 from dnsmasq.conf."
    )

    story += issue_block(
        "Issue 4 — HQ-DHCP-DNS NO-CARRIER — Missing VLAN Config on HQ-DSW2",
        "ip link show eth0 on HQ-DHCP-DNS showed NO-CARRIER, state DOWN despite a cable existing in CML.",
        "HQ-DSW2 E0/0 (connected to HQ-DHCP-DNS) was never configured as an access port. The port was in default VLAN 1 with no active VLAN assignment.",
        "Configured HQ-DSW2 E0/0 as access port VLAN 999 with PortFast and BPDU Guard."
    )

    story += issue_block(
        "Issue 5 — Null0 Black-Hole Masking DHCP Failure",
        "Two simultaneous DHCP failures (Branch VLAN 100, HQ VLAN 200). Ping to DHCP server appeared to work intermittently — false positive.",
        "Three faults — wrong helper-address (10.1.99.99) on two subinterfaces, PLUS a Null0 static route competing with the correct route to 10.1.99.0/24. IOS load-balanced across both routes; relay packets consistently hit the Null0 path.",
        "Removed Null0 route FIRST (dependency order matters), then corrected helper-address to 10.1.99.50 on both subinterfaces."
    )

    # ════════════════════════════════════════════════════════
    # BREAK/FIX CHALLENGE
    # ════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_header("Break/Fix Challenge"))
    story.append(sp(8))
    story.append(p(
        "<b>Scenario:</b> Two helpdesk tickets — Branch VLAN 100 no DHCP, HQ VLAN 200 "
        "no DHCP. DNS and management unaffected."
    ))
    story.append(sp(6))

    story.append(p("Step 1", "step"))
    story.append(p("Verify endpoints cannot get DHCP:"))
    story.append(code_block("udhcpc -i eth0 -f    ! PC-BR1 — should time out"))

    story.append(p("Step 2", "step"))
    story.append(p("Check Layer 1/2 (start at the bottom of OSI):"))
    story.append(code_block(
        "show vlan brief          ! both sites — VLANs active?\n"
        "show interfaces trunk    ! trunks up, correct VLANs?"
    ))
    story.append(p("Result: Clean. No L1/L2 issues."))

    story.append(p("Step 3", "step"))
    story.append(p("Check routing table for DHCP server subnet:"))
    story.append(code_block("show ip route 10.1.99.0    ! BR-RTR1"))
    story.append(p(
        "Look for two competing entries — one via 10.0.0.1 (correct) and one via Null0 "
        "(black-hole). Intermittent ping success is a FALSE POSITIVE."
    ))

    story.append(p("Step 4", "step"))
    story.append(p("Check helper-address config:"))
    story.append(code_block("show running-config | section helper    ! both routers"))
    story.append(p("Look for 10.1.99.99 instead of 10.1.99.50 on affected subinterfaces."))

    story.append(p("Step 5", "step"))
    story.append(p("Apply fixes in dependency order:"))
    story.append(code_block(
        "! Fix 1: Remove Null0 route FIRST\n"
        "no ip route 10.1.99.0 255.255.255.0 Null0\n\n"
        "! Fix 2: Correct helper on BR-RTR1\n"
        "interface Ethernet0/0.100\n ip helper-address 10.1.99.50\n\n"
        "! Fix 3: Correct helper on HQ-RTR1\n"
        "interface Ethernet0/0.200\n ip helper-address 10.1.99.50"
    ))
    story.append(embed_image(f"{SS}/p02-bf-05-PC-BR1-dhcp-restored.png"))
    story.append(caption("Figure B.1 — DHCP restored after all three faults fixed"))
    story.append(sp(6))
    story.append(note_box(
        "Key Lesson: Fix lowest-layer faults first. Fixing helper-address while the "
        "Null0 route exists still fails — the routing fault blocks the fix from taking effect."
    ))

    return story


# ═══════════════════════════════════════════════════════════════════════════════
# PDF generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_pdf(story, output_path, project_title):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    on_first, on_later = make_page_callbacks(project_title)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=L_MARGIN,
        rightMargin=R_MARGIN,
        topMargin=T_MARGIN + 20,   # extra for running header bar
        bottomMargin=B_MARGIN + 10,
    )
    doc.multiBuild(story, onFirstPage=on_first, onLaterPages=on_later)
    size = os.path.getsize(output_path)
    print(f"  Written: {output_path}  ({size:,} bytes)")
    return output_path


def main():
    outputs = {
        "p01": [
            f"{BASE}/project-01-campus-foundation/docs/campus-foundation-lab-guide.pdf",
            f"{BASE}/docs/project-01-campus-foundation-lab-guide.pdf",
        ],
        "p02": [
            f"{BASE}/project-02-multi-site-dhcp/docs/multi-site-dhcp-lab-guide.pdf",
            f"{BASE}/docs/project-02-multi-site-dhcp-lab-guide.pdf",
        ],
    }

    print("Building Project 01 story...")
    story01 = build_project_01()
    print(f"  Story elements: {len(story01)}")

    primary01 = outputs["p01"][0]
    generate_pdf(story01, primary01, "Project 01 — Campus Foundation")

    for dest in outputs["p01"][1:]:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(primary01, dest)
        print(f"  Copied: {dest}")

    print("\nBuilding Project 02 story...")
    story02 = build_project_02()
    print(f"  Story elements: {len(story02)}")

    primary02 = outputs["p02"][0]
    generate_pdf(story02, primary02, "Project 02 — Multi-Site Expansion + DHCP")

    for dest in outputs["p02"][1:]:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(primary02, dest)
        print(f"  Copied: {dest}")

    print("\nAll PDFs generated successfully.")


if __name__ == "__main__":
    main()
