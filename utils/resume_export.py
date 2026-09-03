from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


BLUE = RGBColor(31, 78, 121)
DARK = RGBColor(35, 35, 35)
GRAY = RGBColor(90, 90, 90)


def set_run(run, size=10.5, bold=False, color=DARK, name="Calibri"):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.font.color.rgb = color


def add_bottom_line(paragraph, color="1F4E79"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "10")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def section_heading(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text.upper())
    set_run(run, 11, True, BLUE)
    add_bottom_line(p, "1F4E79")
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    return p


def body_para(doc, text, size=10.5, bold=False, color=DARK, space_after=2):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run(run, size, bold, color)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    return p


def bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(text)
    set_run(run, 10.5, False, DARK)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.left_indent = Inches(0.15)
    return p


def title_date_line(doc, left_main, left_sub, right_date):
    """Job/project title on left, date on right."""
    p = doc.add_paragraph()
    # left bold title
    r1 = p.add_run(left_main)
    set_run(r1, 10.5, True, DARK)
    if left_sub:
        r2 = p.add_run(f"  ·  {left_sub}")
        set_run(r2, 10.5, False, GRAY)
    # right date using tab
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)
    r3 = p.add_run(f"\t{right_date}" if right_date else "")
    set_run(r3, 10, False, GRAY)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.space_before = Pt(4)
    return p


def parse_block_lines(text):
    """
    Format per line:
    Title | Company/Type | Dates | bullet1; bullet2; bullet3
    """
    items = []
    for line in (text or "").split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        while len(parts) < 4:
            parts.append("")
        title, org, dates, bullets = parts[0], parts[1], parts[2], parts[3]
        bullet_list = [b.strip() for b in bullets.split(";") if b.strip()]
        items.append({"title": title, "org": org, "dates": dates, "bullets": bullet_list})
    return items


def export_docx(data) -> bytes:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    # ===== HEADER =====
    name_p = doc.add_paragraph()
    name_run = name_p.add_run((data.get("name") or "YOUR NAME").upper())
    set_run(name_run, 22, True, BLUE)
    name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name_p.paragraph_format.space_after = Pt(2)

    role_p = doc.add_paragraph()
    role_run = role_p.add_run(data.get("headline") or data.get("role") or "")
    set_run(role_run, 10.5, False, DARK)
    role_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    role_p.paragraph_format.space_after = Pt(2)

    contact_bits = []
    for key in ["location", "phone", "email", "linkedin", "github", "portfolio"]:
        val = (data.get(key) or "").strip()
        if val:
            contact_bits.append(val)
    contact_p = doc.add_paragraph()
    contact_run = contact_p.add_run("  ·  ".join(contact_bits))
    set_run(contact_run, 9.5, False, GRAY)
    contact_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact_p.paragraph_format.space_after = Pt(8)

    # ===== OBJECTIVE =====
    objective = (data.get("summary") or "").strip()
    if not objective:
        objective = (
            f"Motivated student targeting {data.get('role') or 'software'} roles, "
            f"with hands-on project experience and strong communication skills."
        )
    section_heading(doc, "Objective")
    body_para(doc, objective, 10.5)

    # ===== SKILLS =====
    section_heading(doc, "Skills")
    skills_map = [
        ("Technical", data.get("skills", "")),
        ("Tools", data.get("tools", "")),
        ("Soft Skills", data.get("soft_skills", "")),
        ("Languages", data.get("languages", "")),
    ]
    for label, value in skills_map:
        value = (value or "").strip()
        if not value:
            continue
        p = doc.add_paragraph()
        r1 = p.add_run(f"{label}: ")
        set_run(r1, 10.5, True, BLUE)
        r2 = p.add_run(value)
        set_run(r2, 10.5, False, DARK)
        p.paragraph_format.space_after = Pt(2)

    # ===== EXPERIENCE =====
    exp_items = parse_block_lines(data.get("experience", ""))
    section_heading(doc, "Experience")
    if exp_items:
        for item in exp_items:
            title_date_line(doc, item["title"], item["org"], item["dates"])
            for b in item["bullets"]:
                bullet(doc, b)
    else:
        body_para(doc, "Fresher | Academic and personal projects", 10.5, color=GRAY)

    # ===== PROJECTS =====
    project_items = parse_block_lines(data.get("projects", ""))
    if project_items:
        section_heading(doc, "Projects")
        for item in project_items:
            title_date_line(doc, item["title"], item["org"], item["dates"])
            for b in item["bullets"]:
                bullet(doc, b)

    # ===== EDUCATION =====
    edu_items = parse_block_lines(data.get("education", ""))
    if edu_items:
        section_heading(doc, "Education")
        for item in edu_items:
            title_date_line(doc, item["title"], item["org"], item["dates"])
            for b in item["bullets"]:
                # italic-like secondary detail
                p = doc.add_paragraph()
                run = p.add_run(b)
                set_run(run, 10, False, GRAY)
                p.paragraph_format.space_after = Pt(1)

    # ===== ACHIEVEMENTS =====
    achievements = [a.strip() for a in (data.get("achievements") or "").split("\n") if a.strip()]
    if achievements:
        section_heading(doc, "Achievements & Certifications")
        body_para(doc, "  ·  ".join(achievements), 10.5)

    # ===== ADDITIONAL =====
    additional_parts = []
    if data.get("availability"):
        additional_parts.append(f"Availability: {data.get('availability')}")
    if data.get("interests"):
        additional_parts.append(f"Interests: {data.get('interests')}")
    if data.get("references"):
        additional_parts.append(f"References: {data.get('references')}")
    if additional_parts:
        section_heading(doc, "Additional")
        body_para(doc, "  ".join(additional_parts), 10.5)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.read()