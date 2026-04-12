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
BLACK       = colors.black
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
                    leading=16, textColor=colors.black, alignment=TA_CENTER, spaceAfter=4),
    "body": S("body", fontName="Helvetica", fontSize=10, leading=14,
              textColor=colors.black, spaceAfter=4),
    "body_bold": S("body_bold", fontName="Helvetica-Bold", fontSize=10, leading=14,
                   textColor=colors.black, spaceAfter=4),
    "step": S("step", fontName="Helvetica-Bold", fontSize=10, leading=14,
              textColor=colors.black, spaceAfter=3, spaceBefore=8),
    "subsec": S("subsec", fontName="Helvetica-Bold", fontSize=12, leading=16,
                textColor=SUBSEC_TEXT, spaceAfter=4, spaceBefore=10),
    "caption": S("caption", fontName="Helvetica-Oblique", fontSize=8, leading=11,
                 textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=8),
    "bullet": S("bullet", fontName="Helvetica", fontSize=10, leading=14,
                textColor=colors.black, leftIndent=16, bulletIndent=6, spaceAfter=3),
    "tbl_hdr": S("tbl_hdr", fontName="Helvetica-Bold", fontSize=9, leading=12,
                 textColor=WHITE, alignment=TA_CENTER),
    "tbl_body": S("tbl_body", fontName="Helvetica", fontSize=9, leading=12,
                  textColor=colors.black),
    "tbl_body_c": S("tbl_body_c", fontName="Helvetica", fontSize=9, leading=12,
                    textColor=colors.black, alignment=TA_CENTER),
    "why": S("why", fontName="Helvetica-Oblique", fontSize=9, leading=13,
             textColor=colors.black, spaceAfter=8, spaceBefore=4),
    "note": S("note", fontName="Helvetica", fontSize=9, leading=13,
              textColor=colors.black, spaceAfter=8, spaceBefore=4),
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
                                textColor=colors.black, leftIndent=10)
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
                                       leading=13, textColor=colors.black))
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
                                       leading=13, textColor=colors.black))
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
# Project 03 — OSPF Dynamic Routing
# ═══════════════════════════════════════════════════════════════════════════════

def build_project_03():
    SS   = f"{BASE}/project-03-ospf-dynamic-routing/verification/screenshots"
    TOPO = f"{BASE}/project-03-ospf-dynamic-routing/diagrams/cml-topology.png"
    story = []

    # ── Cover ──
    story += cover_page(
        "Project 03 — OSPF Dynamic Routing",
        "Multi-Area OSPF with BFD, MD5 Auth, IP SLA, and OSPFv3",
        [
            "Author: Leonel Chongong",
            "Date: April 2026",
            "Platform: Cisco CML 2.9 | IOL Routers",
            "Methodology: Build → Verify → Break → Fix",
        ]
    )

    # ── Setup and Scenario ──
    story.append(section_header("Setup and Scenario"))
    story.append(sp(8))
    story.append(p("<b>Business Context</b>", "subsec"))
    story.append(p(
        "After completing Projects 01 and 02, the two-site HQ and Branch network "
        "relied entirely on manually configured static routes. Every subnet had to be "
        "explicitly listed on every router. There was no automatic failover — if a WAN "
        "link failed, traffic stopped. There was no authentication on routing updates, "
        "and convergence after a failure depended on the OSPF dead timer (40 seconds "
        "by default). This lab replaces the static routing foundation with a production-grade "
        "dynamic routing architecture."
    ))
    story.append(sp(6))
    story.append(p("<b>What You Will Build</b>", "subsec"))
    story.append(p(
        "A three-router WAN with multi-area OSPF, adding a transit router (WAN-RTR1) "
        "as a second WAN path between HQ and Branch. The design includes:"
    ))
    for item in [
        "Single-area OSPF migration removing all static routes with zero downtime",
        "Multi-area design: Area 0 (WAN backbone), Area 1 (HQ campus), Area 2 (Branch)",
        "ABR route summarization: 10.1.0.0/16 at HQ-RTR1 and 10.2.0.0/16 at BR-RTR1",
        "MD5 authentication on all WAN-facing OSPF interfaces (key-id 1)",
        "OSPF cost manipulation: WAN-RTR1 path preferred (cost 20), direct link backup (cost 100)",
        "BFD at 300ms / multiplier 3 for sub-second link failure detection",
        "IP SLA ICMP probes with object tracking and floating static routes (AD 250)",
        "OSPFv3 replacing IPv6 static routes from Project 02",
        "Full link failure, convergence, and restoration testing",
    ]:
        story.append(p(f"• {item}", "bullet"))
    story.append(sp(6))

    # ── STAR Summary ──
    story.append(section_header("STAR Summary"))
    story.append(sp(8))
    for label, text in [
        ("Situation",
         "Two-site network with static routing only — no failover, no authentication, "
         "40-second convergence on link failure, manual route maintenance for every subnet."),
        ("Task",
         "Migrate to multi-area OSPF with redundancy, authentication, sub-second BFD "
         "failover, and a tracked floating static last-resort backup layer."),
        ("Action",
         "Deployed WAN-RTR1 as transit router. Migrated to single-area OSPF then "
         "restructured into 3-area design with ABR summarization. Configured MD5 auth, "
         "cost-based path selection, BFD, IP SLA tracking, floating statics (AD 250), "
         "and OSPFv3. Diagnosed and resolved 5 real troubleshooting scenarios."),
        ("Result",
         "Network fails over in under 1 second (BFD). Three redundancy layers: "
         "preferred OSPF path via WAN-RTR1, backup OSPF via direct link, and tracked "
         "floating static last resort. Full IPv6 dynamic routing via OSPFv3."),
    ]:
        story.append(p(f"<b>{label}:</b>", "subsec"))
        story.append(p(text))
        story.append(sp(4))

    # ── Technologies Used ──
    story.append(section_header("Technologies Used"))
    story.append(sp(8))
    for item in [
        "OSPFv2 — multi-area (Areas 0, 1, 2) with loopback router IDs",
        "OSPFv3 — IPv6 dynamic routing replacing static routes from Project 02",
        "OSPF MD5 authentication on WAN interfaces (key-id 1, key: OSPF-WAN-KEY)",
        "OSPF cost manipulation — explicit ip ospf cost per interface",
        "OSPF passive-interface default with selective no passive on WAN links",
        "BFD — Bidirectional Forwarding Detection (300ms interval / multiplier 3)",
        "IP SLA — ICMP echo probes to directly connected /30 neighbor IPs",
        "Object Tracking — track ip sla reachability",
        "Floating static routes — AD 250 with track condition",
        "ABR route summarization — area range command",
        "ip ospf network point-to-point on all /30 WAN interfaces",
        "CDP verification before IP assignment on new devices",
    ]:
        story.append(p(f"• {item}", "bullet"))
    story.append(sp(6))

    # ── Network Topology ──
    story.append(section_header("Network Topology"))
    story.append(sp(6))
    story.append(embed_image(TOPO))
    story.append(caption("Figure T.1 — CML Topology — Project 03 OSPF Dynamic Routing (15 Nodes)"))
    story.append(sp(6))
    story.append(p("<b>OSPF Area Design</b>", "subsec"))
    story.append(p(
        "Area 0 (Backbone): All three WAN /30 links and loopbacks. "
        "Area 1 (HQ Campus): HQ VLAN subinterfaces — summarized to 10.1.0.0/16 at ABR. "
        "Area 2 (Branch Campus): Branch VLAN subinterfaces — summarized to 10.2.0.0/16 at ABR. "
        "HQ-RTR1 and BR-RTR1 are ABRs. WAN-RTR1 is an internal Area 0 router only."
    ))
    story.append(sp(4))
    story.append(p("<b>New Connections Added in Project 03</b>", "subsec"))
    story.append(ip_table(
        ["Side A", "Interface", "Side B", "Interface", "Subnet"],
        [
            ["HQ-RTR1",  "Ethernet0/2", "WAN-RTR1", "Ethernet0/1", "10.0.0.4/30"],
            ["WAN-RTR1", "Ethernet0/0", "BR-RTR1",  "Ethernet0/2", "10.0.0.8/30"],
        ]
    ))
    story.append(sp(10))

    # ── IP Addressing ──
    story.append(section_header("IP Addressing"))
    story.append(sp(6))
    story.append(p("<b>WAN Links (Point-to-Point /30)</b>", "subsec"))
    story.append(ip_table(
        ["Link", "Router A", "IP", "Router B", "IP"],
        [
            ["Primary WAN",   "HQ-RTR1 E0/1",  "10.0.0.1/30",  "BR-RTR1 E0/1",  "10.0.0.2/30"],
            ["HQ to WAN-RTR1","HQ-RTR1 E0/2",  "10.0.0.5/30",  "WAN-RTR1 E0/1", "10.0.0.6/30"],
            ["BR to WAN-RTR1","BR-RTR1 E0/2",  "10.0.0.10/30", "WAN-RTR1 E0/0", "10.0.0.9/30"],
        ]
    ))
    story.append(sp(8))
    story.append(p("<b>Loopbacks (Router IDs)</b>", "subsec"))
    story.append(ip_table(
        ["Router", "Loopback0", "OSPF Role"],
        [
            ["HQ-RTR1",  "10.0.255.1/32", "ABR — Area 0 and Area 1"],
            ["BR-RTR1",  "10.0.255.2/32", "ABR — Area 0 and Area 2"],
            ["WAN-RTR1", "10.0.255.3/32", "Internal — Area 0 only"],
        ]
    ))
    story.append(sp(8))
    story.append(p("<b>HQ Campus VLANs (Area 1 — summarized to 10.1.0.0/16)</b>", "subsec"))
    story.append(ip_table(
        ["VLAN", "Name", "Subnet", "Gateway"],
        [
            ["100", "Engineering", "10.1.100.0/24", "10.1.100.1 (HQ-RTR1)"],
            ["200", "Sales",       "10.1.200.0/24", "10.1.200.1"],
            ["300", "Guest",       "10.1.44.0/24",  "10.1.44.1"],
            ["400", "Server",      "10.1.40.0/24",  "10.1.40.1"],
            ["999", "Management",  "10.1.99.0/24",  "10.1.99.1"],
        ]
    ))
    story.append(sp(8))
    story.append(p("<b>Branch Campus VLANs (Area 2 — summarized to 10.2.0.0/16)</b>", "subsec"))
    story.append(ip_table(
        ["VLAN", "Name", "Subnet", "Gateway"],
        [
            ["100", "Engineering", "10.2.100.0/24", "10.2.100.1 (BR-RTR1)"],
            ["200", "Sales",       "10.2.200.0/24", "10.2.200.1"],
            ["300", "Guest",       "10.2.44.0/24",  "10.2.44.1"],
            ["500", "Wireless",    "10.2.50.0/24",  "10.2.50.1"],
            ["999", "Management",  "10.2.99.0/24",  "10.2.99.1"],
        ]
    ))
    story.append(sp(10))

    # ── Pre-Work ──
    story.append(section_header("Pre-Work — Verify Physical Layer Before Any Config"))
    story.append(sp(8))
    story.append(p(
        "Before touching OSPF, add WAN-RTR1 to the CML topology, cable it, and verify "
        "actual interface connections using CDP. Do NOT assign IPs until CDP confirms "
        "which physical interface connects to which neighbor."
    ))
    story.append(sp(4))
    story.append(p("<b>Step 1: Add WAN-RTR1 to CML and run CDP</b>", "step"))
    story.append(code_block(
        "show cdp neighbors\n"
        "show ip interface brief"
    ))
    story.append(why_box(
        "In this build, the CML cables for WAN-RTR1 were connected to opposite interfaces "
        "from the design document. CDP revealed the actual connections before any IPs were "
        "assigned, preventing silent misconfiguration. Always trust CDP over the diagram."
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/P03-Ph1-cdp-neighbors-wan-rtr1.png"))
    story.append(caption("Figure P.0 — show cdp neighbors on WAN-RTR1 confirming actual cable layout"))
    story.append(sp(4))
    story.append(p("<b>Step 2: Configure WAN-RTR1 base config (match IPs to actual cables)</b>", "step"))
    story.append(code_block(
        "hostname WAN-RTR1\n"
        "!\n"
        "interface Loopback0\n"
        " description ROUTER-ID-LOOPBACK\n"
        " ip address 10.0.255.3 255.255.255.255\n"
        "!\n"
        "interface Ethernet0/1\n"
        " description WAN-TO-HQ-RTR1-E0/2\n"
        " ip address 10.0.0.6 255.255.255.252\n"
        " no shutdown\n"
        "!\n"
        "interface Ethernet0/0\n"
        " description WAN-TO-BR-RTR1-E0/2\n"
        " ip address 10.0.0.9 255.255.255.252\n"
        " no shutdown\n"
        "!\n"
        "lldp run"
    ))
    story.append(sp(8))

    # ── Phase 1 ──
    story.append(PageBreak())
    story.append(section_header("Phase 1 — Single-Area OSPF Migration"))
    story.append(sp(8))
    story.append(p(
        "Remove all static routes and replace with OSPF Area 0 on all three routers. "
        "Use passive-interface default to prevent OSPF hellos from reaching endpoints. "
        "Set all WAN interfaces to point-to-point to eliminate DR/BDR elections."
    ))
    story.append(sp(4))
    story.append(note_box(
        "Critical sequence: configure OSPF on a router FIRST, wait for neighbors to reach "
        "FULL state, THEN remove static routes. This ensures zero downtime during cutover. "
        "Never remove statics before OSPF is established."
    ))
    story.append(sp(6))
    story.append(p("<b>Step 1: OSPF on WAN-RTR1 (no statics to remove — start here)</b>", "step"))
    story.append(code_block(
        "router ospf 1\n"
        " router-id 10.0.255.3\n"
        " log-adjacency-changes detail\n"
        " passive-interface default\n"
        " no passive-interface Ethernet0/0\n"
        " no passive-interface Ethernet0/1\n"
        " network 10.0.255.3 0.0.0.0 area 0\n"
        " network 10.0.0.4 0.0.0.3 area 0\n"
        " network 10.0.0.8 0.0.0.3 area 0"
    ))
    story.append(sp(4))
    story.append(p("<b>Step 2: OSPF on HQ-RTR1 (configure first, remove statics after FULL)</b>", "step"))
    story.append(code_block(
        "router ospf 1\n"
        " router-id 10.0.255.1\n"
        " log-adjacency-changes detail\n"
        " passive-interface default\n"
        " no passive-interface Ethernet0/1\n"
        " no passive-interface Ethernet0/2\n"
        " network 10.0.255.1 0.0.0.0 area 0\n"
        " network 10.0.0.0 0.0.0.3 area 0\n"
        " network 10.0.0.4 0.0.0.3 area 0\n"
        " network 10.1.100.0 0.0.0.255 area 0\n"
        " network 10.1.200.0 0.0.0.255 area 0\n"
        " network 10.1.44.0 0.0.0.255 area 0\n"
        " network 10.1.40.0 0.0.0.255 area 0\n"
        " network 10.1.99.0 0.0.0.255 area 0\n"
        "!\n"
        "! After OSPF neighbors reach FULL:\n"
        "no ip route 10.2.44.0 255.255.255.0 10.0.0.2\n"
        "no ip route 10.2.99.0 255.255.255.0 10.0.0.2\n"
        "no ip route 10.2.100.0 255.255.255.0 10.0.0.2\n"
        "no ip route 10.2.200.0 255.255.255.0 10.0.0.2"
    ))
    story.append(sp(4))
    story.append(p("<b>Step 3: Fix DR/BDR election — apply to all WAN interfaces on all 3 routers</b>", "step"))
    story.append(code_block(
        "! HQ-RTR1 and BR-RTR1: Ethernet0/1 and Ethernet0/2\n"
        "! WAN-RTR1: Ethernet0/0 and Ethernet0/1\n"
        "interface Ethernet0/1\n"
        " ip ospf network point-to-point\n"
        "interface Ethernet0/2\n"
        " ip ospf network point-to-point"
    ))
    story.append(why_box(
        "IOL Ethernet interfaces default to OSPF BROADCAST network type, triggering DR/BDR "
        "election on every /30 WAN link. With only 2 routers on a /30, the election is "
        "pure overhead and slows convergence. point-to-point eliminates it. Neighbors will "
        "briefly drop and reform — expected behavior during the change."
    ))
    story.append(sp(4))
    story.append(p("<b>Phase 1 Verification</b>", "verify_label"))
    story.append(code_block(
        "show ip ospf neighbor        ! FULL/ - with Pri=0 on all routers\n"
        "show ip route ospf           ! O routes present, no S routes remaining\n"
        "show running-config | include ip route  ! Should return nothing\n"
        "ping 10.2.100.1 source 10.1.100.1"
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/P03-Ph1-ospf-neighbors-full.png"))
    story.append(caption("Figure P.1 — show ip ospf neighbor on HQ-RTR1 — FULL/ - with Pri=0 on both neighbors"))
    story.append(sp(8))

    # ── Phase 2 ──
    story.append(PageBreak())
    story.append(section_header("Phase 2 — Multi-Area OSPF Design"))
    story.append(sp(8))
    story.append(p(
        "Split the single Area 0 into three areas. Move HQ campus VLANs to Area 1 "
        "and Branch campus VLANs to Area 2. Configure ABR summarization so WAN-RTR1 "
        "sees one summary per site instead of 5 individual /24 routes."
    ))
    story.append(sp(4))
    story.append(p("<b>Step 1: HQ-RTR1 — move campus VLANs from Area 0 to Area 1</b>", "step"))
    story.append(code_block(
        "router ospf 1\n"
        " no network 10.1.100.0 0.0.0.255 area 0\n"
        " no network 10.1.200.0 0.0.0.255 area 0\n"
        " no network 10.1.44.0  0.0.0.255 area 0\n"
        " no network 10.1.40.0  0.0.0.255 area 0\n"
        " no network 10.1.99.0  0.0.0.255 area 0\n"
        " network 10.1.100.0 0.0.0.255 area 1\n"
        " network 10.1.200.0 0.0.0.255 area 1\n"
        " network 10.1.44.0  0.0.0.255 area 1\n"
        " network 10.1.40.0  0.0.0.255 area 1\n"
        " network 10.1.99.0  0.0.0.255 area 1\n"
        " area 1 range 10.1.0.0 255.255.0.0"
    ))
    story.append(sp(4))
    story.append(p("<b>Step 2: BR-RTR1 — move campus VLANs from Area 0 to Area 2</b>", "step"))
    story.append(code_block(
        "router ospf 1\n"
        " no network 10.2.100.0 0.0.0.255 area 0\n"
        " no network 10.2.200.0 0.0.0.255 area 0\n"
        " no network 10.2.44.0  0.0.0.255 area 0\n"
        " no network 10.2.50.0  0.0.0.255 area 0\n"
        " no network 10.2.99.0  0.0.0.255 area 0\n"
        " network 10.2.100.0 0.0.0.255 area 2\n"
        " network 10.2.200.0 0.0.0.255 area 2\n"
        " network 10.2.44.0  0.0.0.255 area 2\n"
        " network 10.2.50.0  0.0.0.255 area 2\n"
        " network 10.2.99.0  0.0.0.255 area 2\n"
        " area 2 range 10.2.0.0 255.255.0.0"
    ))
    story.append(why_box(
        "The area range command at each ABR generates a single Type 3 Summary LSA into Area 0. "
        "WAN-RTR1 sees O IA 10.1.0.0/16 and O IA 10.2.0.0/16 instead of 5 individual /24 "
        "routes per site. New subnets added within the range are automatically included with "
        "no changes required on WAN-RTR1 or the remote site."
    ))
    story.append(sp(4))
    story.append(note_box(
        "HQ-RTR1 and BR-RTR1 will show 'O 10.x.0.0/16 is a summary, Null0' in the route "
        "table. This is correct behavior — IOS installs a discard route to Null0 at the ABR "
        "to prevent routing loops within the summary range. It is not an error."
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/P03-Ph2-wan-rtr1-ospf-routes.png"))
    story.append(caption("Figure P.2 — show ip route ospf on WAN-RTR1 — O IA 10.1.0.0/16 and O IA 10.2.0.0/16"))
    story.append(sp(8))

    # ── Phase 3 ──
    story.append(section_header("Phase 3 — OSPF MD5 Authentication"))
    story.append(sp(8))
    story.append(p(
        "Authenticate all OSPF routing updates on WAN interfaces. Without authentication, "
        "any device on a WAN link can inject false routes. MD5 means packets without the "
        "correct key are silently dropped. Both sides of every WAN link must use the same "
        "key ID (1) and password (OSPF-WAN-KEY)."
    ))
    story.append(sp(4))
    story.append(p("<b>Apply on all WAN interfaces on all 3 routers:</b>", "step"))
    story.append(code_block(
        "! HQ-RTR1 — Ethernet0/1 and Ethernet0/2\n"
        "interface Ethernet0/1\n"
        " ip ospf message-digest-key 1 md5 OSPF-WAN-KEY\n"
        " ip ospf authentication message-digest\n"
        "interface Ethernet0/2\n"
        " ip ospf message-digest-key 1 md5 OSPF-WAN-KEY\n"
        " ip ospf authentication message-digest\n"
        "!\n"
        "! Repeat identical config on BR-RTR1 E0/1 and E0/2\n"
        "! and on WAN-RTR1 E0/0 and E0/1"
    ))
    story.append(why_box(
        "Passive interfaces do not send OSPF hellos so authentication on LAN interfaces is "
        "meaningless — there are no neighbors to authenticate. WAN links are the attack surface "
        "where a rogue device could be inserted. Interface-level MD5 is explicit and auditable "
        "per-interface. A mismatch in key ID or password drops the adjacency immediately."
    ))
    story.append(sp(4))
    story.append(p("<b>Verification</b>", "verify_label"))
    story.append(code_block(
        "show running-config interface Ethernet0/1\n"
        "! Look for: ip ospf authentication message-digest\n"
        "!           ip ospf message-digest-key 1 md5 7 [encrypted-key]\n"
        "!\n"
        "show ip ospf neighbor   ! All neighbors still FULL/ -"
    ))
    story.append(sp(8))

    # ── Phase 4 ──
    story.append(section_header("Phase 4 — OSPF Cost Manipulation"))
    story.append(sp(8))
    story.append(p(
        "Make path selection deterministic. Preferred path via WAN-RTR1 (total cost 20). "
        "Backup path via direct HQ-RTR1 to BR-RTR1 link (cost 100)."
    ))
    story.append(sp(4))
    story.append(ip_table(
        ["Path", "Interfaces", "Cost", "Total", "Role"],
        [
            ["Via WAN-RTR1",  "HQ-RTR1 E0/2 + WAN-RTR1 transit", "10 + 10", "20",  "PREFERRED"],
            ["Direct HQ-BR",  "HQ-RTR1 E0/1",                     "100",     "100", "BACKUP"],
        ]
    ))
    story.append(sp(6))
    story.append(p("<b>Apply on all 3 routers:</b>", "step"))
    story.append(code_block(
        "! HQ-RTR1\n"
        "interface Ethernet0/1\n"
        " ip ospf cost 100   ! direct backup link\n"
        "interface Ethernet0/2\n"
        " ip ospf cost 10    ! preferred WAN-RTR1 path\n"
        "!\n"
        "! BR-RTR1 (mirror of HQ-RTR1)\n"
        "interface Ethernet0/1\n"
        " ip ospf cost 100\n"
        "interface Ethernet0/2\n"
        " ip ospf cost 10\n"
        "!\n"
        "! WAN-RTR1 (transit router — both links preferred)\n"
        "interface Ethernet0/0\n"
        " ip ospf cost 10\n"
        "interface Ethernet0/1\n"
        " ip ospf cost 10"
    ))
    story.append(why_box(
        "Explicit cost values are deterministic and portable. When you read the config you "
        "immediately know the cost — no math required. With bandwidth-calculated costs you "
        "must know the reference bandwidth and calculate. Explicit costs survive interface "
        "type changes without unexpected side effects."
    ))
    story.append(sp(4))
    story.append(p("<b>Phase 4 Verification</b>", "verify_label"))
    story.append(code_block(
        "show ip route 10.2.100.1   ! Next hop: 10.0.0.6 (WAN-RTR1), metric 30\n"
        "traceroute 10.2.100.1 source 10.1.100.1\n"
        "! Expected: Hop 1: 10.0.0.6 (WAN-RTR1), Hop 2: 10.0.0.10 (BR-RTR1)"
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/P03-Ph4-traceroute-preferred-path.png"))
    story.append(caption("Figure P.4 — traceroute HQ to Branch confirming path goes through WAN-RTR1"))
    story.append(sp(8))

    # ── Phase 5 ──
    story.append(PageBreak())
    story.append(section_header("Phase 5 — Link Failure and Convergence Testing"))
    story.append(sp(8))
    story.append(p(
        "Prove the backup path activates automatically. Shut the preferred WAN-RTR1 link, "
        "confirm OSPF reconverges to the direct backup, restore the link, and confirm "
        "traffic returns to the preferred path."
    ))
    story.append(sp(4))
    story.append(p("<b>Step 1: Baseline — confirm preferred path active on HQ-RTR1</b>", "step"))
    story.append(code_block(
        "show ip ospf neighbor           ! Both neighbors: FULL/ -\n"
        "show ip route 10.2.100.1        ! Via 10.0.0.6 on E0/2, metric 30\n"
        "traceroute 10.2.100.1 source 10.1.100.1"
    ))
    story.append(sp(4))
    story.append(p("<b>Step 2: Simulate failure — shut HQ-RTR1 Ethernet0/2</b>", "step"))
    story.append(code_block(
        "configure terminal\n"
        " interface Ethernet0/2\n"
        "  shutdown\n"
        "end"
    ))
    story.append(sp(4))
    story.append(p("<b>Step 3: Verify failover — backup path active</b>", "step"))
    story.append(code_block(
        "show ip ospf neighbor\n"
        "! WAN-RTR1 (10.0.255.3) should be gone\n"
        "show ip route 10.2.100.1\n"
        "! Expected: via 10.0.0.2 on Ethernet0/1, metric 110"
    ))
    story.append(embed_image(f"{SS}/P03-Ph5-failover-route-change.png"))
    story.append(caption("Figure P.5a — Route switches to backup path (metric 110) after E0/2 shutdown"))
    story.append(sp(4))
    story.append(p("<b>Step 4: Restore E0/2 and verify preferred path returns</b>", "step"))
    story.append(code_block(
        "configure terminal\n"
        " interface Ethernet0/2\n"
        "  no shutdown\n"
        "end\n"
        "!\n"
        "show ip route 10.2.100.1\n"
        "! Expected: back to 10.0.0.6 on Ethernet0/2, metric 30"
    ))
    story.append(embed_image(f"{SS}/P03-Ph5-route-restored.png"))
    story.append(caption("Figure P.5b — Route restored to preferred WAN-RTR1 path after E0/2 no shutdown"))
    story.append(sp(4))
    story.append(ip_table(
        ["State", "Next Hop", "Metric", "Interface"],
        [
            ["Normal",        "10.0.0.6", "30",  "Ethernet0/2 (via WAN-RTR1)"],
            ["E0/2 shutdown", "10.0.0.2", "110", "Ethernet0/1 (direct backup)"],
            ["Restored",      "10.0.0.6", "30",  "Ethernet0/2 (preferred returns)"],
        ]
    ))
    story.append(sp(8))

    # ── Phase 6 ──
    story.append(section_header("Phase 6 — BFD for Sub-Second Failover"))
    story.append(sp(8))
    story.append(p(
        "OSPF's default dead timer is 40 seconds — a link failure can take up to 40 seconds "
        "to trigger reconvergence. BFD runs independently of OSPF and detects link failures "
        "in milliseconds. When BFD detects failure it immediately notifies OSPF."
    ))
    story.append(sp(4))
    story.append(ip_table(
        ["Parameter", "Value", "Result"],
        [
            ["BFD interval",    "300ms",  "Probe sent every 300ms"],
            ["min_rx",          "300ms",  "Accept probes every 300ms"],
            ["Multiplier",      "3",      "Failure declared after 3 missed probes"],
            ["Detection time",  "900ms",  "Sub-second — 44x faster than OSPF dead timer"],
        ]
    ))
    story.append(sp(6))
    story.append(p("<b>Apply on all WAN interfaces on all 3 routers:</b>", "step"))
    story.append(code_block(
        "! HQ-RTR1 E0/1 and E0/2 (repeat for BR-RTR1 and WAN-RTR1)\n"
        "interface Ethernet0/1\n"
        " bfd interval 300 min_rx 300 multiplier 3\n"
        " ip ospf bfd\n"
        "interface Ethernet0/2\n"
        " bfd interval 300 min_rx 300 multiplier 3\n"
        " ip ospf bfd"
    ))
    story.append(sp(4))
    story.append(p("<b>Phase 6 Verification</b>", "verify_label"))
    story.append(code_block(
        "show bfd neighbors\n"
        "! Expected:\n"
        "! NeighAddr   LD/RD   RH/RS  State  Int\n"
        "! 10.0.0.2    1/1     Up     Up     Et0/1\n"
        "! 10.0.0.6    2/2     Up     Up     Et0/2\n"
        "!\n"
        "show ip ospf neighbor   ! All still FULL/ -"
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/P03-Ph6-bfd-neighbors-up.png"))
    story.append(caption("Figure P.6 — show bfd neighbors on HQ-RTR1 — all sessions Up/Up"))
    story.append(sp(8))

    # ── Phase 7 ──
    story.append(PageBreak())
    story.append(section_header("Phase 7 — IP SLA + Tracked Floating Static Route"))
    story.append(sp(8))
    story.append(p(
        "Add a third redundancy layer. If OSPF itself fails (not just a link), a tracked "
        "floating static route (AD 250) activates automatically. The IP SLA probe target "
        "must be reachable independently of OSPF."
    ))
    story.append(sp(4))
    story.append(note_box(
        "Critical design lesson learned during this build: the initial probe targeted "
        "WAN-RTR1's loopback (10.0.255.3), reachable only via OSPF routes. When OSPF "
        "was shut down to test the backup, the probe lost its route, the track went Down, "
        "and the floating static never installed — defeating the entire backup mechanism. "
        "Fix: always probe the directly connected /30 neighbor IP. No routing needed — just ARP."
    ))
    story.append(sp(6))
    story.append(p("<b>Step 1: Configure IP SLA, tracking, and floating static on HQ-RTR1</b>", "step"))
    story.append(code_block(
        "ip sla 10\n"
        " icmp-echo 10.0.0.2 source-ip 10.0.0.1\n"
        " timeout 1000\n"
        " threshold 1000      ! threshold must be <= timeout\n"
        " frequency 5\n"
        "exit\n"
        "!\n"
        "ip sla schedule 10 life forever start-time now\n"
        "!\n"
        "track 10 ip sla 10 reachability\n"
        "!\n"
        "ip route 10.2.0.0 255.255.0.0 10.0.0.2 250 track 10"
    ))
    story.append(sp(4))
    story.append(p("<b>Step 2: Mirror on BR-RTR1</b>", "step"))
    story.append(code_block(
        "ip sla 10\n"
        " icmp-echo 10.0.0.1 source-ip 10.0.0.2\n"
        " timeout 1000\n"
        " threshold 1000\n"
        " frequency 5\n"
        "exit\n"
        "ip sla schedule 10 life forever start-time now\n"
        "track 10 ip sla 10 reachability\n"
        "ip route 10.1.0.0 255.255.0.0 10.0.0.1 250 track 10"
    ))
    story.append(why_box(
        "A directly connected /30 IP requires only ARP — no routing protocol. The probe "
        "survives an OSPF failure because the physical E0/1 link is still up. AD 250 sits "
        "below OSPF (AD 110), so the floating static is invisible during normal operation "
        "and only installs when OSPF routes disappear from the table."
    ))
    story.append(sp(4))
    story.append(p("<b>Phase 7 Verification</b>", "verify_label"))
    story.append(code_block(
        "show ip sla statistics     ! Successes incrementing, return code: OK\n"
        "show track                 ! Reachability is Up\n"
        "show ip route static       ! Empty — OSPF preferred (AD 110 < 250)\n"
        "!\n"
        "! Test with OSPF shut down on BR-RTR1:\n"
        "! router ospf 1 -> shutdown\n"
        "! show track            -> Reachability is Up (probe still works)\n"
        "! show ip route static  -> S 10.1.0.0/16 [250/0] via 10.0.0.1\n"
        "! ping 10.1.100.1 source 10.2.100.1 -> !!!!! 100%"
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/P03-Ph7-track-up-sla-running.png"))
    story.append(caption("Figure P.7a — show track and show ip sla statistics — Reachability Up, return code OK"))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/P03-Ph7-floating-static-active.png"))
    story.append(caption("Figure P.7b — show ip route static on BR-RTR1 with OSPF shut — S 10.1.0.0/16 [250/0] installed"))
    story.append(sp(8))

    # ── Phase 8 ──
    story.append(PageBreak())
    story.append(section_header("Phase 8 — OSPFv3 for IPv6"))
    story.append(sp(8))
    story.append(p(
        "Replace IPv6 static routes from Project 02 with OSPFv3 multi-area dynamic routing. "
        "IPv6 exists only on the direct HQ-BR WAN link (E0/1) and VLAN 100 subinterfaces. "
        "WAN-RTR1 backup path has no IPv6 in this design."
    ))
    story.append(sp(4))
    story.append(p("<b>Step 1: Configure OSPFv3 on HQ-RTR1</b>", "step"))
    story.append(code_block(
        "no ipv6 route 2001:DB8:2:100::/64 2001:DB8:0:1::2\n"
        "!\n"
        "ipv6 unicast-routing\n"
        "!\n"
        "ipv6 router ospf 10\n"
        " router-id 10.0.255.1\n"
        "!\n"
        "interface Ethernet0/1\n"
        " ipv6 ospf 10 area 0\n"
        " ipv6 ospf network point-to-point\n"
        "!\n"
        "interface Ethernet0/0.100\n"
        " ipv6 ospf 10 area 1"
    ))
    story.append(sp(4))
    story.append(p("<b>Step 2: Configure OSPFv3 on BR-RTR1</b>", "step"))
    story.append(code_block(
        "no ipv6 route 2001:DB8:1:100::/64 2001:DB8:0:1::1\n"
        "!\n"
        "ipv6 unicast-routing\n"
        "!\n"
        "ipv6 router ospf 10\n"
        " router-id 10.0.255.2\n"
        "!\n"
        "interface Ethernet0/1\n"
        " ipv6 ospf 10 area 0\n"
        " ipv6 ospf network point-to-point\n"
        "!\n"
        "interface Ethernet0/0.100\n"
        " ipv6 ospf 10 area 2"
    ))
    story.append(why_box(
        "OSPFv3 needs the same point-to-point treatment as OSPFv2. Apply "
        "ipv6 ospf network point-to-point on both sides before checking adjacency. "
        "A one-sided change produces a transient NET_TYPE_MISMATCH log message that "
        "resolves automatically once both routers are updated."
    ))
    story.append(sp(4))
    story.append(p("<b>Phase 8 Verification</b>", "verify_label"))
    story.append(code_block(
        "show ospfv3 neighbor\n"
        "! Expected: Neighbor ID 10.0.255.2, Pri 0, State FULL/ -\n"
        "!\n"
        "show ipv6 route ospf\n"
        "! Expected: OI 2001:DB8:2:100::/64 [110/110] via FE80::..., Ethernet0/1\n"
        "!\n"
        "ping 2001:DB8:2:100::1 source 2001:DB8:1:100::1\n"
        "ping 2001:DB8:1:100::1 source 2001:DB8:2:100::1"
    ))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/P03-Ph8-ospfv3-neighbor-full.png"))
    story.append(caption("Figure P.8a — show ospfv3 neighbor on HQ-RTR1 — FULL/ - with Pri=0"))
    story.append(sp(4))
    story.append(embed_image(f"{SS}/P03-Ph8-ipv6-ping-success.png"))
    story.append(caption("Figure P.8b — IPv6 ping from HQ VLAN 100 to Branch VLAN 100: !!!!! 100%"))
    story.append(sp(8))

    # ── Final Checklist ──
    story.append(PageBreak())
    story.append(section_header("Final Verification Checklist"))
    story.append(sp(8))
    story.append(checklist_table(
        ["#", "Test", "Command", "Device", "Expected"],
        [
            ["1",  "OSPF neighbors FULL",        "show ip ospf neighbor",             "All routers", "FULL/ - Pri=0"],
            ["2",  "No statics remain",          "show run | include ip route",        "HQ/BR-RTR1",  "Empty"],
            ["3",  "O IA summaries on WAN-RTR1", "show ip route ospf",                 "WAN-RTR1",    "O IA 10.1.0.0/16 and 10.2.0.0/16"],
            ["4",  "E0/2 cost = 10",             "show ip ospf int E0/2",              "HQ/BR-RTR1",  "Cost: 10, POINT_TO_POINT"],
            ["5",  "E0/1 cost = 100",            "show ip ospf int E0/1",              "HQ/BR-RTR1",  "Cost: 100"],
            ["6",  "MD5 auth on WAN ints",       "show run int E0/1 | include ospf",   "All routers", "authentication message-digest"],
            ["7",  "BFD sessions Up",            "show bfd neighbors",                 "All routers", "Up/Up on all sessions"],
            ["8",  "IP SLA running",             "show ip sla statistics",             "HQ/BR-RTR1",  "Successes incrementing, OK"],
            ["9",  "Track object Up",            "show track",                         "HQ/BR-RTR1",  "Reachability Up"],
            ["10", "Traceroute via WAN-RTR1",    "traceroute 10.2.100.1 src 10.1.100.1","HQ-RTR1",   "Hop 1: 10.0.0.6"],
            ["11", "OSPFv3 neighbor FULL",       "show ospfv3 neighbor",               "HQ/BR-RTR1",  "FULL/ - Pri=0"],
            ["12", "IPv4 end-to-end",            "ping 10.2.100.1 src 10.1.100.1",    "HQ-RTR1",     "!!!!!"],
            ["13", "IPv6 end-to-end",            "ping 2001:DB8:2:100::1",            "HQ-RTR1",     "!!!!!"],
        ]
    ))
    story.append(sp(10))

    # ── Troubleshooting ──
    story.append(section_header("Troubleshooting Log — Project 03"))
    story.append(sp(8))
    entries = [
        (
            "Entry 1 — WAN-RTR1 Interface IP Mismatch",
            "Pings from WAN-RTR1 to HQ and Branch failing 0% immediately after config. Same-subnet /30 pings require only ARP — they should never fail.",
            "CML cables were connected to opposite interfaces from the design. IPs assigned from the design had the wrong side on each interface. Additionally, 'no ip address' without the full mask left E0/0 unassigned.",
            "Ran 'show cdp neighbors' to discover actual cable layout. Reassigned IPs to match physical connections confirmed by CDP. Pings returned 100% after fix.",
            "Always run 'show cdp neighbors' BEFORE assigning IPs to any new device. Never assume CML cable connections match the design diagram.",
        ),
        (
            "Entry 2 — DR/BDR Election on /30 WAN Links",
            "'show ip ospf neighbor' showed FULL/DR and FULL/BDR instead of FULL/ - with Pri=0 on point-to-point /30 WAN links.",
            "IOL Ethernet interfaces default to OSPF network type BROADCAST regardless of subnet mask. This triggers DR/BDR election on every link, including /30s with only 2 endpoints.",
            "Applied 'ip ospf network point-to-point' to all WAN interfaces on all 3 routers. Adjacencies briefly dropped and reformed — expected during network type change.",
            "Always apply 'ip ospf network point-to-point' on /30 WAN links in IOL. The same applies to OSPFv3 — use 'ipv6 ospf network point-to-point'.",
        ),
        (
            "Entry 3 — Intentional Failover Test (Phase 5)",
            "Intentional outage: shut HQ-RTR1 E0/2 to verify OSPF reconverges to backup path without waiting 40 seconds.",
            "Intentional test. No actual fault.",
            "Interface-down triggered immediate adjacency loss. Route metric changed from 30 (preferred via WAN-RTR1) to 110 (backup direct link). On restoration, traffic returned to preferred path automatically.",
            "Interface-down events trigger immediate OSPF adjacency removal — no dead timer wait. Cost engineering produces deterministic failover.",
        ),
        (
            "Entry 4 — IP SLA Probe Would Not Start",
            "IP SLA not running. Track showed Reachability Down, return code Unknown. 'show ip sla statistics' returned Unknown counters. Operation time to live: 0.",
            "IOS rejects 'ip sla schedule' when threshold > timeout. Default threshold is 5000ms; timeout was 1000ms. The schedule command was silently rejected, leaving the probe in notInService state.",
            "Removed and recreated SLA with threshold 1000 and timeout 1000. After fix: track showed Reachability Up with RTT 1ms, success counters incrementing.",
            "When IP SLA will not start, check 'show ip sla configuration' for 'Pending trigger' and 'notInService'. Always set threshold equal to or less than timeout.",
        ),
        (
            "Entry 5 — IP SLA Probe Failed During OSPF Outage",
            "When OSPF was shut down to test the floating static backup, the track went Down. Floating static never installed. Network lost all inter-site reachability.",
            "The probe target was WAN-RTR1 loopback 10.0.255.3 — reachable only via OSPF routes. When OSPF died, the route to the probe target disappeared, the probe failed, track went Down, and the floating static never installed.",
            "Changed probe target to the directly connected /30 IP on the backup link (10.0.0.2 from HQ-RTR1, 10.0.0.1 from BR-RTR1). A /30 directly connected IP requires only ARP — it works regardless of OSPF state.",
            "IP SLA probe target must be reachable independently of the routing protocol it backs up. Always probe a directly connected interface IP on the backup path, never a loopback or remote address.",
        ),
    ]
    for title, symptom, root_cause, fix, lesson in entries:
        story.append(p(f"<b>{title}</b>", "subsec"))
        for label, content in [("Symptom", symptom), ("Root Cause", root_cause),
                                ("Fix", fix), ("Lesson", lesson)]:
            story.append(p(f"<b>{label}:</b> {content}"))
            story.append(sp(3))
        story.append(HRFlowable(width=USABLE_W, thickness=0.5,
                                color=colors.HexColor("#CCCCCC"), spaceAfter=8))

    # ── Break / Fix Challenge ──
    story.append(section_header("Break / Fix Challenge"))
    story.append(sp(8))
    story.append(p(
        "Each challenge introduces a deliberate misconfiguration. Diagnose using only "
        "show commands — do not look at the running-config until you have a hypothesis."
    ))
    story.append(sp(6))
    challenges = [
        (
            "Challenge 1 — OSPF adjacency drops after applying MD5",
            "After adding MD5 authentication, one WAN adjacency drops and never recovers. "
            "'show ip ospf neighbor' shows EXSTART or DOWN oscillation on one interface.",
            "Check 'show ip ospf interface E0/x' on both sides. Compare the authentication type. "
            "Run 'debug ip ospf adj' briefly to see the mismatch message.",
        ),
        (
            "Challenge 2 — Traffic taking the backup path instead of WAN-RTR1",
            "Traceroute from HQ to Branch shows only 1 hop (direct to BR-RTR1). "
            "The preferred WAN-RTR1 path should produce 2 hops. Both OSPF neighbors are FULL.",
            "Check 'show ip ospf interface E0/1' and 'show ip ospf interface E0/2' on HQ-RTR1. "
            "Compare the Cost values. What was not applied?",
        ),
        (
            "Challenge 3 — IP SLA showing Unknown return code after scheduling",
            "After configuring and scheduling IP SLA, 'show ip sla statistics' shows "
            "Return code: Unknown and Number of successes: 0. Track object shows Down.",
            "Run 'show ip sla configuration 10'. Look at the Threshold and Timeout values. "
            "Which one is larger, and why does that matter?",
        ),
        (
            "Challenge 4 — OSPFv3 neighbor stuck at EXSTART",
            "After configuring OSPFv3, 'show ospfv3 neighbor' shows EXSTART and never "
            "reaches FULL. IPv4 OSPF is working correctly on the same interfaces.",
            "Run 'show ospfv3 interface E0/1' on both routers. Compare the network type. "
            "Is it the same on both sides?",
        ),
    ]
    for scenario, symptoms, hint in challenges:
        story.append(p(f"<b>{scenario}</b>", "subsec"))
        story.append(p(f"<b>Symptoms:</b> {symptoms}"))
        story.append(sp(3))
        story.append(p(f"<b>Hint:</b> {hint}"))
        story.append(sp(3))
        story.append(HRFlowable(width=USABLE_W, thickness=0.5,
                                color=colors.HexColor("#CCCCCC"), spaceAfter=6))

    story.append(sp(10))
    story.append(p(
        "<b>Build date:</b> 2026-04-12 &nbsp;&nbsp; "
        "<b>Platform:</b> Cisco IOL in CML 2.9 &nbsp;&nbsp; "
        "<b>Nodes:</b> 15 (adds WAN-RTR1 to Project 02 topology)"
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
        "p03": [
            f"{BASE}/project-03-ospf-dynamic-routing/docs/ospf-dynamic-routing-lab-guide.pdf",
            f"{BASE}/docs/project-03-ospf-dynamic-routing-lab-guide.pdf",
        ],
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

    print("\nBuilding Project 03 story...")
    story03 = build_project_03()
    print(f"  Story elements: {len(story03)}")

    primary03 = outputs["p03"][0]
    generate_pdf(story03, primary03, "Project 03 — OSPF Dynamic Routing")

    for dest in outputs["p03"][1:]:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(primary03, dest)
        print(f"  Copied: {dest}")

    print("\nAll PDFs generated successfully.")


if __name__ == "__main__":
    main()
