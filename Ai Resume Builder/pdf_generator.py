"""
Smart Resume Builder AI - Enhanced PDF Generator
15 Professional Templates with unique layouts and color schemes
"""
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, KeepTogether, Frame,
                                 PageTemplate, BaseDocTemplate)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus.flowables import Flowable
import io, os

# ══════════════════════════════════════════════════════════════════════════════
# 15 PROFESSIONAL THEMES
# ══════════════════════════════════════════════════════════════════════════════
THEMES = {
    # ── 1. Modern Blue (Corporate tech)
    "modern_blue": {
        "name": "Modern Blue",
        "primary":   HexColor("#1e3a5f"),
        "accent":    HexColor("#2563eb"),
        "accent2":   HexColor("#93c5fd"),
        "light":     HexColor("#eff6ff"),
        "text":      HexColor("#1e293b"),
        "muted":     HexColor("#64748b"),
        "border":    HexColor("#bfdbfe"),
        "header_bg": HexColor("#1e3a5f"),
        "header_fg": white,
        "layout":    "standard",
    },
    # ── 2. Executive Dark (Finance/Law)
    "executive_dark": {
        "name": "Executive Dark",
        "primary":   HexColor("#0f172a"),
        "accent":    HexColor("#7c3aed"),
        "accent2":   HexColor("#c4b5fd"),
        "light":     HexColor("#f5f3ff"),
        "text":      HexColor("#0f172a"),
        "muted":     HexColor("#6b7280"),
        "border":    HexColor("#ddd6fe"),
        "header_bg": HexColor("#0f172a"),
        "header_fg": white,
        "layout":    "standard",
    },
    # ── 3. Emerald (Healthcare/Life Sciences)
    "emerald_pro": {
        "name": "Emerald Pro",
        "primary":   HexColor("#064e3b"),
        "accent":    HexColor("#059669"),
        "accent2":   HexColor("#6ee7b7"),
        "light":     HexColor("#ecfdf5"),
        "text":      HexColor("#1a202c"),
        "muted":     HexColor("#6b7280"),
        "border":    HexColor("#a7f3d0"),
        "header_bg": HexColor("#064e3b"),
        "header_fg": white,
        "layout":    "standard",
    },
    # ── 4. Classic Slate (Traditional/Conservative)
    "classic_slate": {
        "name": "Classic Slate",
        "primary":   HexColor("#1e293b"),
        "accent":    HexColor("#475569"),
        "accent2":   HexColor("#94a3b8"),
        "light":     HexColor("#f8fafc"),
        "text":      HexColor("#1e293b"),
        "muted":     HexColor("#94a3b8"),
        "border":    HexColor("#cbd5e1"),
        "header_bg": HexColor("#1e293b"),
        "header_fg": white,
        "layout":    "standard",
    },
    # ── 5. Rose Gold (Creative/Marketing)
    "rose_gold": {
        "name": "Rose Gold",
        "primary":   HexColor("#881337"),
        "accent":    HexColor("#e11d48"),
        "accent2":   HexColor("#fda4af"),
        "light":     HexColor("#fff1f2"),
        "text":      HexColor("#1e293b"),
        "muted":     HexColor("#9f1239"),
        "border":    HexColor("#fecdd3"),
        "header_bg": HexColor("#881337"),
        "header_fg": white,
        "layout":    "standard",
    },
    # ── 6. Midnight Teal (Consulting/Strategy)
    "midnight_teal": {
        "name": "Midnight Teal",
        "primary":   HexColor("#134e4a"),
        "accent":    HexColor("#0d9488"),
        "accent2":   HexColor("#99f6e4"),
        "light":     HexColor("#f0fdfa"),
        "text":      HexColor("#134e4a"),
        "muted":     HexColor("#6b7280"),
        "border":    HexColor("#99f6e4"),
        "header_bg": HexColor("#134e4a"),
        "header_fg": white,
        "layout":    "standard",
    },
    # ── 7. Amber Warm (Sales/Business Dev)
    "amber_warm": {
        "name": "Amber Warm",
        "primary":   HexColor("#78350f"),
        "accent":    HexColor("#d97706"),
        "accent2":   HexColor("#fcd34d"),
        "light":     HexColor("#fffbeb"),
        "text":      HexColor("#1c1917"),
        "muted":     HexColor("#92400e"),
        "border":    HexColor("#fde68a"),
        "header_bg": HexColor("#78350f"),
        "header_fg": white,
        "layout":    "standard",
    },
    # ── 8. Indigo Split (Two-column sidebar)
    "indigo_split": {
        "name": "Indigo Split",
        "primary":   HexColor("#312e81"),
        "accent":    HexColor("#4f46e5"),
        "accent2":   HexColor("#a5b4fc"),
        "light":     HexColor("#eef2ff"),
        "text":      HexColor("#1e1b4b"),
        "muted":     HexColor("#6366f1"),
        "border":    HexColor("#c7d2fe"),
        "header_bg": HexColor("#312e81"),
        "header_fg": white,
        "sidebar_bg": HexColor("#312e81"),
        "sidebar_fg": white,
        "layout":    "two_column",
    },
    # ── 9. Carbon Dark (Tech/Engineering)
    "carbon_dark": {
        "name": "Carbon Dark",
        "primary":   HexColor("#18181b"),
        "accent":    HexColor("#22d3ee"),
        "accent2":   HexColor("#67e8f9"),
        "light":     HexColor("#f0f9ff"),
        "text":      HexColor("#27272a"),
        "muted":     HexColor("#71717a"),
        "border":    HexColor("#a1f0fa"),
        "header_bg": HexColor("#18181b"),
        "header_fg": HexColor("#22d3ee"),
        "layout":    "standard",
    },
    # ── 10. Forest Minimal (Sustainability/NGO)
    "forest_minimal": {
        "name": "Forest Minimal",
        "primary":   HexColor("#14532d"),
        "accent":    HexColor("#16a34a"),
        "accent2":   HexColor("#86efac"),
        "light":     HexColor("#f0fdf4"),
        "text":      HexColor("#14532d"),
        "muted":     HexColor("#4ade80"),
        "border":    HexColor("#bbf7d0"),
        "header_bg": HexColor("#f0fdf4"),
        "header_fg": HexColor("#14532d"),
        "layout":    "minimal",
    },
    # ── 11. Sky Clean (Entry-level/Academic)
    "sky_clean": {
        "name": "Sky Clean",
        "primary":   HexColor("#0c4a6e"),
        "accent":    HexColor("#0284c7"),
        "accent2":   HexColor("#7dd3fc"),
        "light":     HexColor("#f0f9ff"),
        "text":      HexColor("#0c4a6e"),
        "muted":     HexColor("#0369a1"),
        "border":    HexColor("#bae6fd"),
        "header_bg": HexColor("#0c4a6e"),
        "header_fg": white,
        "layout":    "standard",
    },
    # ── 12. Crimson Bold (Leadership/C-Suite)
    "crimson_bold": {
        "name": "Crimson Bold",
        "primary":   HexColor("#450a0a"),
        "accent":    HexColor("#b91c1c"),
        "accent2":   HexColor("#fca5a5"),
        "light":     HexColor("#fef2f2"),
        "text":      HexColor("#1c1917"),
        "muted":     HexColor("#7f1d1d"),
        "border":    HexColor("#fecaca"),
        "header_bg": HexColor("#450a0a"),
        "header_fg": white,
        "layout":    "standard",
    },
    # ── 13. Violet Sidebar (Design/UX/Creative)
    "violet_sidebar": {
        "name": "Violet Sidebar",
        "primary":   HexColor("#2e1065"),
        "accent":    HexColor("#7c3aed"),
        "accent2":   HexColor("#ddd6fe"),
        "light":     HexColor("#faf5ff"),
        "text":      HexColor("#1e1b4b"),
        "muted":     HexColor("#7c3aed"),
        "border":    HexColor("#e9d5ff"),
        "header_bg": HexColor("#2e1065"),
        "header_fg": white,
        "sidebar_bg": HexColor("#2e1065"),
        "sidebar_fg": white,
        "layout":    "two_column",
    },
    # ── 14. Monochrome Pro (Banking/Legal)
    "monochrome_pro": {
        "name": "Monochrome Pro",
        "primary":   HexColor("#000000"),
        "accent":    HexColor("#404040"),
        "accent2":   HexColor("#a0a0a0"),
        "light":     HexColor("#f5f5f5"),
        "text":      HexColor("#111111"),
        "muted":     HexColor("#606060"),
        "border":    HexColor("#d0d0d0"),
        "header_bg": HexColor("#000000"),
        "header_fg": white,
        "layout":    "classic",
    },
    # ── 15. Sunset Orange (Startup/Product)
    "sunset_orange": {
        "name": "Sunset Orange",
        "primary":   HexColor("#431407"),
        "accent":    HexColor("#ea580c"),
        "accent2":   HexColor("#fdba74"),
        "light":     HexColor("#fff7ed"),
        "text":      HexColor("#1c1917"),
        "muted":     HexColor("#9a3412"),
        "border":    HexColor("#fed7aa"),
        "header_bg": HexColor("#431407"),
        "header_fg": white,
        "layout":    "standard",
    },
}

THEME_LIST = [
    {"id": k, "name": v["name"], "layout": v.get("layout","standard"),
     "primary": v["primary"].hexval() if hasattr(v["primary"],"hexval") else "#000",
     "accent":  v["accent"].hexval()  if hasattr(v["accent"],"hexval")  else "#000",
    }
    for k, v in THEMES.items()
]


# ══════════════════════════════════════════════════════════════════════════════
# BASE GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
class ResumeGenerator:
    def __init__(self, theme="modern_blue"):
        self.theme_key = theme
        self.T = THEMES.get(theme, THEMES["modern_blue"])
        self.page_width, self.page_height = A4
        self.margin = 18 * mm
        self.layout = self.T.get("layout", "standard")

    # ── Public entry point ──────────────────────────────────────────────────
    def generate(self, resume_data, output_path):
        if self.layout == "two_column":
            return self._generate_two_column(resume_data, output_path)
        elif self.layout == "classic":
            return self._generate_classic(resume_data, output_path)
        elif self.layout == "minimal":
            return self._generate_minimal(resume_data, output_path)
        else:
            return self._generate_standard(resume_data, output_path)

    # ══════════════════════════════════════════════════════════════════════════
    # LAYOUT 1 – STANDARD  (header band + full-width sections)
    # ══════════════════════════════════════════════════════════════════════════
    def _generate_standard(self, data, output_path):
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=self.margin, leftMargin=self.margin,
            topMargin=0, bottomMargin=self.margin,
        )
        styles = self._styles()
        story = []

        story.extend(self._build_header_band(data, styles))
        story.extend(self._build_summary_section(data, styles))
        story.extend(self._build_experience_section(data, styles))
        story.extend(self._build_skills_section(data, styles))
        story.extend(self._build_projects_section(data, styles))
        story.extend(self._build_education_section(data, styles))
        story.extend(self._build_certs_section(data, styles))
        story.extend(self._build_achievements_section(data, styles))
        story.extend(self._build_languages_section(data, styles))

        doc.build(story, onFirstPage=self._page_frame, onLaterPages=self._page_frame)
        return output_path

    # ══════════════════════════════════════════════════════════════════════════
    # LAYOUT 2 – TWO COLUMN  (left sidebar + right main)
    # ══════════════════════════════════════════════════════════════════════════
    def _generate_two_column(self, data, output_path):
        T = self.T
        pw, ph = A4
        m = self.margin
        sidebar_w = 68 * mm
        main_w = pw - 2*m - sidebar_w - 6*mm

        styles = self._styles()
        sidebar_styles = self._sidebar_styles()

        # Build sidebar content
        sidebar = []
        personal = data.get("personal", {})
        # Photo placeholder + name
        sidebar.append(Paragraph(personal.get("name","Your Name"), sidebar_styles["name"]))
        if personal.get("desired_role"):
            sidebar.append(Paragraph(personal["desired_role"], sidebar_styles["role"]))
        sidebar.append(Spacer(1, 8))

        # Contact in sidebar
        sidebar.append(Paragraph("CONTACT", sidebar_styles["section"]))
        for icon, key in [("✉", "email"), ("✆","phone"), ("⌖","location"),
                          ("in","linkedin"), ("⌥","github")]:
            val = personal.get(key,"")
            if val:
                sidebar.append(Paragraph(f"{icon}  {val}", sidebar_styles["contact"]))
        sidebar.append(Spacer(1, 8))

        # Skills in sidebar
        skills = data.get("skills", [])
        if skills:
            sidebar.append(Paragraph("SKILLS", sidebar_styles["section"]))
            for sk in skills:
                sidebar.append(Paragraph(f"▸ {sk}", sidebar_styles["skill"]))
            sidebar.append(Spacer(1, 8))

        # Languages in sidebar
        langs = data.get("languages", [])
        if langs:
            sidebar.append(Paragraph("LANGUAGES", sidebar_styles["section"]))
            for lg in langs:
                sidebar.append(Paragraph(f"• {lg}", sidebar_styles["skill"]))
            sidebar.append(Spacer(1, 8))

        # Certs in sidebar
        certs = data.get("certifications", [])
        if certs:
            sidebar.append(Paragraph("CERTIFICATIONS", sidebar_styles["section"]))
            for cert in certs:
                if isinstance(cert, dict):
                    sidebar.append(Paragraph(cert.get("name",""), sidebar_styles["skill"]))
                else:
                    sidebar.append(Paragraph(str(cert), sidebar_styles["skill"]))

        # Build main content
        main = []
        main.extend(self._build_summary_section(data, styles, no_title=False))
        main.extend(self._build_experience_section(data, styles))
        main.extend(self._build_projects_section(data, styles))
        main.extend(self._build_education_section(data, styles))
        main.extend(self._build_achievements_section(data, styles))

        # Combine as table
        content_table = Table(
            [[sidebar, main]],
            colWidths=[sidebar_w, main_w],
        )
        content_table.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("BACKGROUND", (0,0), (0,-1), T["sidebar_bg"]),
            ("LEFTPADDING", (0,0), (0,-1), 10),
            ("RIGHTPADDING", (0,0), (0,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING", (1,0), (1,-1), 10),
            ("RIGHTPADDING", (1,0), (1,-1), 6),
        ]))

        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=m, leftMargin=m,
            topMargin=0, bottomMargin=m,
        )
        story = [content_table]
        doc.build(story, onFirstPage=self._page_frame_two_col,
                  onLaterPages=self._page_frame_two_col)
        return output_path

    # ══════════════════════════════════════════════════════════════════════════
    # LAYOUT 3 – CLASSIC  (centered header, ruled sections)
    # ══════════════════════════════════════════════════════════════════════════
    def _generate_classic(self, data, output_path):
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=self.margin, leftMargin=self.margin,
            topMargin=self.margin, bottomMargin=self.margin,
        )
        styles = self._styles_classic()
        story = []

        personal = data.get("personal", {})
        # Centered name
        story.append(Paragraph(personal.get("name","Your Name"), styles["name_center"]))
        if personal.get("desired_role"):
            story.append(Paragraph(personal["desired_role"], styles["role_center"]))

        # Contact line
        parts = []
        for k in ["email","phone","location","linkedin"]:
            v = personal.get(k,"")
            if v: parts.append(v)
        if parts:
            story.append(Paragraph("  |  ".join(parts), styles["contact_center"]))
        story.append(HRFlowable(width="100%", thickness=1.5, color=self.T["primary"], spaceAfter=8))

        # Sections
        for title, builder in [
            ("Professional Summary", lambda: self._build_summary_section(data, styles)),
            ("Work Experience", lambda: self._build_experience_classic(data, styles)),
            ("Education", lambda: self._build_education_section(data, styles)),
            ("Skills", lambda: self._build_skills_section(data, styles)),
            ("Projects", lambda: self._build_projects_section(data, styles)),
            ("Certifications", lambda: self._build_certs_section(data, styles)),
            ("Achievements", lambda: self._build_achievements_section(data, styles)),
        ]:
            items = builder()
            if len(items) > 1:
                story.extend(items)

        doc.build(story, onFirstPage=self._page_frame_simple,
                  onLaterPages=self._page_frame_simple)
        return output_path

    # ══════════════════════════════════════════════════════════════════════════
    # LAYOUT 4 – MINIMAL  (clean, light, understated)
    # ══════════════════════════════════════════════════════════════════════════
    def _generate_minimal(self, data, output_path):
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            rightMargin=22*mm, leftMargin=22*mm,
            topMargin=20*mm, bottomMargin=20*mm,
        )
        styles = self._styles_minimal()
        story = []

        personal = data.get("personal", {})
        story.append(Paragraph(personal.get("name","Your Name"), styles["name"]))
        if personal.get("desired_role"):
            story.append(Paragraph(personal["desired_role"], styles["role"]))
        parts = []
        for k in ["email","phone","location","linkedin","github"]:
            v = personal.get(k,"")
            if v: parts.append(v)
        if parts:
            story.append(Paragraph("  ·  ".join(parts), styles["contact"]))
        story.append(Spacer(1, 12))

        story.extend(self._build_summary_section(data, styles))
        story.extend(self._build_experience_section(data, styles))
        story.extend(self._build_education_section(data, styles))
        story.extend(self._build_skills_section(data, styles))
        story.extend(self._build_projects_section(data, styles))
        story.extend(self._build_certs_section(data, styles))

        doc.build(story, onFirstPage=self._page_frame_simple,
                  onLaterPages=self._page_frame_simple)
        return output_path

    # ══════════════════════════════════════════════════════════════════════════
    # STYLES
    # ══════════════════════════════════════════════════════════════════════════
    def _styles(self):
        T = self.T
        return {
            "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=26,
                textColor=T["header_fg"], spaceAfter=2, leading=30),
            "tagline": ParagraphStyle("tagline", fontName="Helvetica", fontSize=10,
                textColor=HexColor("#e2e8f0"), spaceAfter=4, leading=13),
            "contact_bar": ParagraphStyle("contact_bar", fontName="Helvetica", fontSize=8.5,
                textColor=HexColor("#cbd5e1"), leading=12),
            "section_title": ParagraphStyle("section_title", fontName="Helvetica-Bold",
                fontSize=10, textColor=T["primary"], spaceBefore=10, spaceAfter=3,
                leading=14),
            "job_title": ParagraphStyle("job_title", fontName="Helvetica-Bold",
                fontSize=10.5, textColor=T["text"], spaceAfter=1, leading=13),
            "company": ParagraphStyle("company", fontName="Helvetica-Oblique",
                fontSize=9.5, textColor=T["accent"], spaceAfter=2, leading=12),
            "date": ParagraphStyle("date", fontName="Helvetica", fontSize=9,
                textColor=T["muted"], leading=11, alignment=TA_RIGHT),
            "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9.5,
                textColor=T["text"], leftIndent=12, spaceAfter=2, leading=13),
            "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.5,
                textColor=T["text"], spaceAfter=2, leading=13),
            "summary": ParagraphStyle("summary", fontName="Helvetica", fontSize=10,
                textColor=T["text"], spaceAfter=4, leading=14, alignment=TA_JUSTIFY),
            "skill_tag": ParagraphStyle("skill_tag", fontName="Helvetica", fontSize=9,
                textColor=T["primary"], leading=11),
            "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8.5,
                textColor=T["muted"], leading=11),
            # aliases for classic/minimal compatibility
            "name_center": ParagraphStyle("name_center", fontName="Helvetica-Bold",
                fontSize=24, textColor=T["primary"], alignment=TA_CENTER, spaceAfter=3),
            "role_center": ParagraphStyle("role_center", fontName="Helvetica",
                fontSize=11, textColor=T["accent"], alignment=TA_CENTER, spaceAfter=4),
            "contact_center": ParagraphStyle("contact_center", fontName="Helvetica",
                fontSize=9, textColor=T["muted"], alignment=TA_CENTER, spaceAfter=6),
        }

    def _styles_classic(self):
        T = self.T
        base = self._styles()
        base["section_title"] = ParagraphStyle("section_title", fontName="Helvetica-Bold",
            fontSize=11, textColor=T["primary"], spaceBefore=10, spaceAfter=2,
            leading=14, borderPad=0)
        return base

    def _styles_minimal(self):
        T = self.T
        return {
            "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=28,
                textColor=T["primary"], spaceAfter=3, leading=32),
            "role": ParagraphStyle("role", fontName="Helvetica", fontSize=12,
                textColor=T["accent"], spaceAfter=4, leading=15),
            "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=9,
                textColor=T["muted"], spaceAfter=6, leading=12),
            "section_title": ParagraphStyle("section_title", fontName="Helvetica-Bold",
                fontSize=9, textColor=T["accent"], spaceBefore=12, spaceAfter=4,
                leading=11),
            "job_title": ParagraphStyle("job_title", fontName="Helvetica-Bold",
                fontSize=10.5, textColor=T["text"], spaceAfter=1, leading=13),
            "company": ParagraphStyle("company", fontName="Helvetica-Oblique",
                fontSize=9.5, textColor=T["muted"], spaceAfter=2, leading=12),
            "date": ParagraphStyle("date", fontName="Helvetica", fontSize=9,
                textColor=T["muted"], leading=11, alignment=TA_RIGHT),
            "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9.5,
                textColor=T["text"], leftIndent=12, spaceAfter=2, leading=13),
            "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.5,
                textColor=T["text"], spaceAfter=2, leading=13),
            "summary": ParagraphStyle("summary", fontName="Helvetica", fontSize=10,
                textColor=T["text"], spaceAfter=4, leading=14, alignment=TA_JUSTIFY),
            "skill_tag": ParagraphStyle("skill_tag", fontName="Helvetica", fontSize=9,
                textColor=T["primary"], leading=11),
            "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8.5,
                textColor=T["muted"], leading=11),
        }

    def _sidebar_styles(self):
        T = self.T
        sf = T.get("sidebar_fg", white)
        return {
            "name": ParagraphStyle("sb_name", fontName="Helvetica-Bold", fontSize=15,
                textColor=sf, spaceAfter=4, leading=18),
            "role": ParagraphStyle("sb_role", fontName="Helvetica", fontSize=9,
                textColor=T["accent2"], spaceAfter=3, leading=12),
            "section": ParagraphStyle("sb_section", fontName="Helvetica-Bold",
                fontSize=8, textColor=T["accent2"], spaceBefore=8, spaceAfter=4,
                leading=10),
            "contact": ParagraphStyle("sb_contact", fontName="Helvetica", fontSize=8,
                textColor=sf, spaceAfter=3, leading=11, wordWrap="CJK"),
            "skill": ParagraphStyle("sb_skill", fontName="Helvetica", fontSize=8.5,
                textColor=sf, spaceAfter=3, leading=11),
        }

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION BUILDERS (shared across layouts)
    # ══════════════════════════════════════════════════════════════════════════
    def _section_header(self, title, styles):
        T = self.T
        layout = self.layout

        if layout == "minimal":
            items = [
                HRFlowable(width="100%", thickness=0.5, color=T["border"], spaceAfter=2),
                Paragraph(title.upper(), styles["section_title"]),
            ]
        elif layout == "classic":
            items = [
                Paragraph(title.upper(), styles["section_title"]),
                HRFlowable(width="100%", thickness=1, color=T["accent"], spaceAfter=4),
            ]
        else:
            border = Table([[Paragraph(f"  {title.upper()}", styles["section_title"])]],
                           colWidths=[self.page_width - 2*self.margin])
            border.setStyle(TableStyle([
                ("LEFTPADDING",  (0,0), (-1,-1), 6),
                ("RIGHTPADDING", (0,0), (-1,-1), 6),
                ("TOPPADDING",   (0,0), (-1,-1), 2),
                ("BOTTOMPADDING",(0,0), (-1,-1), 2),
                ("LINEBEFORE",   (0,0), (0,-1), 4, T["accent"]),
                ("BACKGROUND",   (0,0), (-1,-1), T["light"]),
            ]))
            items = [border, Spacer(1, 3)]
        return items

    def _build_summary_section(self, data, styles, no_title=False):
        summary = data.get("summary","")
        if not summary:
            return []
        items = []
        if not no_title:
            items.extend(self._section_header("Professional Summary", styles))
        items.append(Paragraph(summary, styles.get("summary", styles.get("body"))))
        items.append(Spacer(1, 4))
        return items

    def _build_experience_section(self, data, styles):
        experiences = data.get("experience",[])
        if not experiences:
            return []
        items = self._section_header("Work Experience", styles)
        for exp in experiences:
            items.extend(self._build_exp_entry(exp, styles))
        return items

    def _build_experience_classic(self, data, styles):
        return self._build_experience_section(data, styles)

    def _build_exp_entry(self, exp, styles):
        items = []
        if not isinstance(exp, dict):
            return items
        title   = exp.get("title","")
        company = exp.get("company","")
        start   = exp.get("start_date","")
        end     = exp.get("end_date","Present")
        desc    = exp.get("description","")
        date_str = f"{start} – {end}" if start else end

        avail_w = self.page_width - 2*self.margin
        if self.layout == "two_column":
            avail_w = avail_w - 68*mm - 6*mm

        row = Table([[Paragraph(title, styles["job_title"]),
                      Paragraph(date_str, styles["date"])]],
                    colWidths=[avail_w - 60, 60])
        row.setStyle(TableStyle([
            ("VALIGN",         (0,0),(-1,-1),"TOP"),
            ("LEFTPADDING",    (0,0),(-1,-1),0),
            ("RIGHTPADDING",   (0,0),(-1,-1),0),
            ("TOPPADDING",     (0,0),(-1,-1),0),
            ("BOTTOMPADDING",  (0,0),(-1,-1),0),
        ]))
        items.append(row)
        if company:
            items.append(Paragraph(company, styles["company"]))
        if desc:
            for line in [l.strip() for l in desc.split("\n") if l.strip()]:
                items.append(Paragraph(f"• {line.lstrip('•-* ')}", styles["bullet"]))
        items.append(Spacer(1, 6))
        return items

    def _build_skills_section(self, data, styles):
        skills = data.get("skills",[])
        if not skills:
            return []
        T = self.T
        items = self._section_header("Technical Skills", styles)

        avail_w = self.page_width - 2*self.margin
        cols = 4
        col_w = avail_w / cols
        rows = []
        row = []
        for sk in skills:
            row.append(Paragraph(f"▸ {sk}", styles["skill_tag"]))
            if len(row) == cols:
                rows.append(row); row = []
        if row:
            while len(row) < cols:
                row.append(Paragraph("", styles["skill_tag"]))
            rows.append(row)

        if rows:
            tbl = Table(rows, colWidths=[col_w]*cols)
            tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), T["light"]),
                ("TEXTCOLOR",     (0,0),(-1,-1), T["primary"]),
                ("FONTNAME",      (0,0),(-1,-1),"Helvetica"),
                ("FONTSIZE",      (0,0),(-1,-1), 9),
                ("TOPPADDING",    (0,0),(-1,-1), 4),
                ("BOTTOMPADDING", (0,0),(-1,-1), 4),
                ("LEFTPADDING",   (0,0),(-1,-1), 6),
                ("GRID",          (0,0),(-1,-1), 0.5, T["border"]),
            ]))
            items.append(tbl)
        items.append(Spacer(1, 4))
        return items

    def _build_projects_section(self, data, styles):
        projects = data.get("projects",[])
        if not projects:
            return []
        items = self._section_header("Projects", styles)
        for proj in projects:
            if not isinstance(proj, dict):
                continue
            name = proj.get("name","")
            tech = proj.get("technologies","")
            desc = proj.get("description","")
            link = proj.get("link","")
            title_str = name + (f"  [{tech}]" if tech else "")
            items.append(Paragraph(title_str, styles["job_title"]))
            if desc:
                for line in [l.strip() for l in desc.split("\n") if l.strip()]:
                    items.append(Paragraph(f"• {line.lstrip('•-* ')}", styles["bullet"]))
            if link:
                items.append(Paragraph(f"🔗 {link}", styles["small"]))
            items.append(Spacer(1, 5))
        return items

    def _build_education_section(self, data, styles):
        education = data.get("education",[])
        if not education:
            return []
        items = self._section_header("Education", styles)
        avail_w = self.page_width - 2*self.margin
        for edu in education:
            if not isinstance(edu, dict):
                continue
            degree  = edu.get("degree","")
            inst    = edu.get("institution","")
            year    = edu.get("year","")
            gpa     = edu.get("gpa","")
            left    = f"{degree}" + (f" — {inst}" if inst else "")
            row = Table([[Paragraph(left, styles["job_title"]),
                          Paragraph(year, styles["date"])]],
                        colWidths=[avail_w - 60, 60])
            row.setStyle(TableStyle([
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("LEFTPADDING",(0,0),(-1,-1),0),
                ("RIGHTPADDING",(0,0),(-1,-1),0),
                ("TOPPADDING",(0,0),(-1,-1),0),
                ("BOTTOMPADDING",(0,0),(-1,-1),0),
            ]))
            items.append(row)
            if gpa:
                items.append(Paragraph(f"GPA: {gpa}", styles["small"]))
            items.append(Spacer(1, 5))
        return items

    def _build_certs_section(self, data, styles):
        certs = data.get("certifications",[])
        if not certs:
            return []
        items = self._section_header("Certifications", styles)
        for cert in certs:
            if isinstance(cert, dict):
                name   = cert.get("name","")
                issuer = cert.get("issuer","")
                year   = cert.get("year","")
                line   = name + (f" — {issuer}" if issuer else "") + (f" ({year})" if year else "")
                items.append(Paragraph(f"• {line}", styles["bullet"]))
            else:
                items.append(Paragraph(f"• {cert}", styles["bullet"]))
        items.append(Spacer(1, 4))
        return items

    def _build_achievements_section(self, data, styles):
        ach = data.get("achievements",[])
        if not ach:
            return []
        items = self._section_header("Achievements & Awards", styles)
        for a in ach:
            items.append(Paragraph(f"• {a}", styles["bullet"]))
        items.append(Spacer(1, 4))
        return items

    def _build_languages_section(self, data, styles):
        langs = data.get("languages",[])
        if not langs:
            return []
        items = self._section_header("Languages", styles)
        items.append(Paragraph("  •  ".join(langs), styles["body"]))
        items.append(Spacer(1, 4))
        return items

    # ══════════════════════════════════════════════════════════════════════════
    # HEADER BUILDERS
    # ══════════════════════════════════════════════════════════════════════════
    def _build_header_band(self, data, styles):
        T = self.T
        personal = data.get("personal",{})
        name         = personal.get("name","Your Name")
        desired_role = personal.get("desired_role","")
        contact_parts = []
        for icon, key in [("✉","email"),("✆","phone"),("⌖","location"),
                          ("in","linkedin"),("⌥","github")]:
            v = personal.get(key,"")
            if v: contact_parts.append(f"{icon} {v}")
        contact_str = "   |   ".join(contact_parts)

        rows = [[Paragraph(name, styles["name"])]]
        if desired_role:
            rows.append([Paragraph(desired_role, styles["tagline"])])
        if contact_str:
            rows.append([Paragraph(contact_str, styles["contact_bar"])])

        w = self.page_width - 2*self.margin
        tbl = Table(rows, colWidths=[w])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), T["header_bg"]),
            ("TOPPADDING",    (0,0),(-1,-1), 12),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ("LEFTPADDING",   (0,0),(-1,-1), 14),
            ("RIGHTPADDING",  (0,0),(-1,-1), 14),
        ]))
        return [tbl, Spacer(1, 6),
                HRFlowable(width="100%", thickness=2, color=T["accent"], spaceAfter=6)]

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE DECORATORS
    # ══════════════════════════════════════════════════════════════════════════
    def _page_frame(self, canv, doc):
        T = self.T
        canv.setStrokeColor(T["accent"])
        canv.setLineWidth(2)
        canv.line(self.margin, 12*mm, self.page_width - self.margin, 12*mm)
        canv.setFont("Helvetica", 7)
        canv.setFillColor(T["muted"])
        canv.drawCentredString(self.page_width/2, 8*mm, "Generated by Smart Resume Builder AI")

    def _page_frame_two_col(self, canv, doc):
        T = self.T
        pw, ph = A4
        canv.setFillColor(T.get("sidebar_bg", T["primary"]))
        canv.rect(0, 0, 68*mm + self.margin, ph, fill=1, stroke=0)
        canv.setFont("Helvetica", 7)
        canv.setFillColor(T.get("sidebar_fg", white))
        canv.drawString(10, 8*mm, "Smart Resume Builder AI")

    def _page_frame_simple(self, canv, doc):
        T = self.T
        canv.setFont("Helvetica", 7)
        canv.setFillColor(T["muted"])
        canv.drawCentredString(self.page_width/2, 8*mm, "Generated by Smart Resume Builder AI")
