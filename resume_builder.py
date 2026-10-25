import io
import json
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from ai_feedback import ask_llm


# ---------- 1. Ask the AI to rewrite the resume as structured JSON ----------

def build_rewrite_prompt(resume_text, jd_text, confirmed_skills):
    confirmed = ", ".join(confirmed_skills) or "none"
    return f"""You are an expert resume writer. Rewrite the resume below so it fits the job description better.

STRICT RULES:
1. Use ONLY facts that appear in the original resume. Do NOT invent jobs, projects, tools, degrees, dates or numbers.
2. Keep every number exactly as written in the original.
3. You may reword, reorder, and make bullet points stronger (start with an action verb, show impact).
4. Write a short professional summary (2-3 sentences) tailored to the job, using only real facts.
5. Skills the candidate CONFIRMED they have (add these to the skills section): {confirmed}
6. Do not add any other skill that is not in the original resume or the confirmed list.
7. Use standard section content only: summary, skills, experience, projects, education, certifications.

Return ONLY valid JSON (no markdown, no explanation) in exactly this shape:
{{
  "name": "string",
  "contact": ["email, phone, location, links as separate short strings"],
  "summary": "string",
  "skills": {{"Category name": ["skill", "skill"]}},
  "experience": [{{"title": "Role - Company (dates)", "bullets": ["..."]}}],
  "projects": [{{"title": "Project name", "bullets": ["..."]}}],
  "education": [{{"title": "Degree, years", "detail": "Institute | CGPA"}}],
  "certifications": ["..."]
}}

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}
"""

def parse_resume_json(text):
    text = text.strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("The AI did not return JSON. Please try again.")
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        raise ValueError("The AI returned invalid JSON. Please try again.")

    return {
        "name": str(data.get("name") or "Your Name"),
        "contact": [str(c) for c in (data.get("contact") or [])],
        "summary": str(data.get("summary") or ""),
        "skills": data.get("skills") or {},
        "experience": data.get("experience") or [],
        "projects": data.get("projects") or [],
        "education": data.get("education") or [],
        "certifications": [str(c) for c in (data.get("certifications") or [])],
    }

def rewrite_resume(resume_text, jd_text, confirmed_skills):
    prompt = build_rewrite_prompt(resume_text, jd_text, confirmed_skills)
    return parse_resume_json(ask_llm(prompt))


# ---------- 2. Turn the structured data into an ATS-friendly PDF ----------

def build_pdf(data):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm, title=data["name"])

    name_s = ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=20, leading=26, spaceAfter=2)
    contact_s = ParagraphStyle("contact", fontName="Helvetica", fontSize=9.5,
                               textColor=colors.HexColor("#444444"), spaceAfter=6)
    head_s = ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=11.5, spaceBefore=8,
                            spaceAfter=2, textColor=colors.HexColor("#1F3A5F"))
    body_s = ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=13.5)
    bullet_s = ParagraphStyle("bullet", parent=body_s, leftIndent=12, bulletIndent=2)
    role_s = ParagraphStyle("role", parent=body_s, fontName="Helvetica-Bold", spaceBefore=4)

    def esc(x):
        return escape(str(x))

    story = []

    def section(title):
        story.append(Paragraph(title.upper(), head_s))
        story.append(HRFlowable(width="100%", thickness=0.6,
                                color=colors.HexColor("#1F3A5F"), spaceAfter=3))

    def bullets(items):
        for b in items:
            story.append(Paragraph(esc(b), bullet_s, bulletText="-"))

    story.append(Paragraph(esc(data["name"]), name_s))
    if data["contact"]:
        story.append(Paragraph(esc(" | ".join(data["contact"])), contact_s))

    if data["summary"]:
        section("Professional Summary")
        story.append(Paragraph(esc(data["summary"]), body_s))

    if data["skills"]:
        section("Technical Skills")
        for category, items in data["skills"].items():
            if isinstance(items, str):
                items = [items]
            story.append(Paragraph(f"<b>{esc(category)}:</b> {esc(', '.join(map(str, items)))}", body_s))

    if data["experience"]:
        section("Experience")
        for job in data["experience"]:
            story.append(Paragraph(esc(job.get("title", "")), role_s))
            bullets(job.get("bullets", []))

    if data["projects"]:
        section("Projects")
        for pr in data["projects"]:
            story.append(Paragraph(esc(pr.get("title", "")), role_s))
            bullets(pr.get("bullets", []))

    if data["education"]:
        section("Education")
        for ed in data["education"]:
            story.append(Paragraph(esc(ed.get("title", "")), role_s))
            if ed.get("detail"):
                story.append(Paragraph(esc(ed["detail"]), body_s))

    if data["certifications"]:
        section("Certifications")
        bullets(data["certifications"])

    doc.build(story)
    return buf.getvalue()