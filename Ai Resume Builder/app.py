"""
Smart Resume Builder AI - Flask Application (v2 — Enhanced)
New in v2:
  • Improvement 1: Live HTML resume preview  (/api/preview)
  • Improvement 2: Real Groq AI via LangChain (/api/generate-summary, /api/role-suggestions, /api/rewrite-bullet)
  • Improvement 3: LinkedIn PDF import       (/api/import-linkedin)
"""
from flask import Flask, request, jsonify, render_template, send_file, abort
import json, os, uuid, tempfile
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from ats_engine import ATSAnalyzer, SuggestionEngine
from pdf_generator import ResumeGenerator, THEMES, THEME_LIST
from database_layer import (init_db, save_resume, update_resume, get_resume,
                             get_all_resumes, delete_resume, save_ats_report, get_ats_report)
from groq_ai_engine import (generate_ai_summary, get_ai_role_suggestions, rewrite_bullet,
                             generate_cover_letter, analyse_keyword_gap, generate_interview_questions)
from linkedin_importer import parse_linkedin_pdf

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

ats_analyzer     = ATSAnalyzer()
suggestion_engine = SuggestionEngine()


# ── Existing routes ────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/themes", methods=["GET"])
def get_themes():
    themes = []
    for k, v in THEMES.items():
        def hex_or(c, fallback="#000"):
            try:
                return "#{:02x}{:02x}{:02x}".format(
                    int(c.red*255), int(c.green*255), int(c.blue*255))
            except:
                return fallback
        themes.append({
            "id":      k,
            "name":    v["name"],
            "layout":  v.get("layout", "standard"),
            "primary": hex_or(v["primary"]),
            "accent":  hex_or(v["accent"]),
            "light":   hex_or(v["light"]),
        })
    return jsonify(themes)


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    resume_data     = data.get("resume", {})
    job_description = data.get("job_description", "")
    if not resume_data:
        return jsonify({"error": "No resume data provided"}), 400
    report = ats_analyzer.analyze(resume_data, job_description)
    role   = resume_data.get("personal", {}).get("desired_role", "")
    skills = resume_data.get("skills", [])
    report["role_suggestions"] = suggestion_engine.get_role_suggestions(role, skills) if role else {}
    if not resume_data.get("summary"):
        try:
            report["ai_summary"] = generate_ai_summary(resume_data)
        except Exception:
            report["ai_summary"] = suggestion_engine.generate_ai_summary(resume_data)
    return jsonify(report)


@app.route("/api/save", methods=["POST"])
def save():
    data        = request.get_json(force=True)
    resume_data = data.get("resume", {})
    ats_score   = data.get("ats_score", 0)
    template    = data.get("template", "modern_blue")
    resume_id   = data.get("resume_id")
    if not resume_data:
        return jsonify({"error": "No resume data"}), 400
    if resume_id:
        update_resume(resume_id, resume_data, ats_score, template)
        return jsonify({"success": True, "resume_id": resume_id, "message": "Resume updated"})
    rid = save_resume(resume_data, ats_score, template)
    return jsonify({"success": True, "resume_id": rid, "message": "Resume saved"})


@app.route("/api/export-pdf", methods=["POST"])
def export_pdf():
    data        = request.get_json(force=True)
    resume_data = data.get("resume", {})
    template    = data.get("template", "modern_blue")
    resume_id   = data.get("resume_id")
    if not resume_data:
        return jsonify({"error": "No resume data"}), 400

    filename    = f"resume_{uuid.uuid4().hex[:8]}.pdf"
    output_path = os.path.join(EXPORTS_DIR, filename)
    generator   = ResumeGenerator(theme=template)
    generator.generate(resume_data, output_path)

    if resume_id:
        report = ats_analyzer.analyze(resume_data)
        save_ats_report(resume_id, report)

    name = resume_data.get("personal", {}).get("name", "Resume").replace(" ", "_")
    return send_file(output_path, as_attachment=True,
                     download_name=f"{name}_Resume.pdf",
                     mimetype="application/pdf")


@app.route("/api/resumes", methods=["GET"])
def list_resumes():
    return jsonify(get_all_resumes())


@app.route("/api/resumes/<int:resume_id>", methods=["GET"])
def get_resume_api(resume_id):
    resume = get_resume(resume_id)
    if not resume: abort(404)
    return jsonify(resume)


@app.route("/api/resumes/<int:resume_id>", methods=["DELETE"])
def delete_resume_api(resume_id):
    delete_resume(resume_id)
    return jsonify({"success": True})


@app.route("/api/ats-report/<int:resume_id>", methods=["GET"])
def get_ats_report_api(resume_id):
    report = get_ats_report(resume_id)
    if not report: abort(404)
    return jsonify(report)


# ── IMPROVEMENT 2: Real AI endpoints (Groq + LangChain) ───────────────────

@app.route("/api/generate-summary", methods=["POST"])
def generate_summary():
    """Generate professional summary using Groq LLM with role-specific fallback."""
    data        = request.get_json(force=True)
    resume_data = data.get("resume", {})
    role        = resume_data.get("personal", {}).get("desired_role", "")
    if not role:
        return jsonify({"error": "Please fill in the Desired Job Role field first."}), 400
    summary = generate_ai_summary(resume_data)
    source  = "groq_ai" if os.getenv("GROQ_API") else "template"
    return jsonify({"summary": summary, "source": source, "role": role})


@app.route("/api/role-suggestions", methods=["POST"])
def role_suggestions():
    """Get AI-powered role-specific skill and career suggestions."""
    data       = request.get_json(force=True)
    role       = data.get("role", "")
    skills     = data.get("skills", [])
    experience = data.get("experience", [])
    if not role:
        return jsonify({"error": "Role is required"}), 400
    try:
        suggestions = get_ai_role_suggestions(role, skills, experience)
        return jsonify({"success": True, "suggestions": suggestions, "source": "groq_ai"})
    except Exception as e:
        fallback = suggestion_engine.get_role_suggestions(role, skills)
        return jsonify({"success": True, "suggestions": fallback, "source": "template", "error": str(e)})


@app.route("/api/rewrite-bullet", methods=["POST"])
def rewrite_bullet_api():
    """Rewrite a weak bullet point into 3 strong ATS-optimised versions."""
    data   = request.get_json(force=True)
    bullet = data.get("bullet", "").strip()
    role   = data.get("role", "")
    if not bullet:
        return jsonify({"error": "Bullet text is required"}), 400
    try:
        versions = rewrite_bullet(bullet, role)
        return jsonify({"success": True, "versions": versions})
    except Exception as e:
        return jsonify({"success": False, "versions": [bullet], "error": str(e)})


# ── IMPROVEMENT 1: Live HTML Preview ──────────────────────────────────────

@app.route("/api/preview", methods=["POST"])
def preview_resume():
    """Return an HTML preview of the resume (no PDF needed)."""
    data        = request.get_json(force=True)
    resume_data = data.get("resume", {})
    template    = data.get("template", "modern_blue")
    if not resume_data:
        return jsonify({"error": "No resume data"}), 400

    theme = THEMES.get(template, THEMES["modern_blue"])

    def hex_color(c, fallback="#000000"):
        try:
            return "#{:02x}{:02x}{:02x}".format(
                int(c.red*255), int(c.green*255), int(c.blue*255))
        except:
            return fallback

    primary = hex_color(theme["primary"])
    accent  = hex_color(theme["accent"])
    light   = hex_color(theme["light"])
    muted   = hex_color(theme.get("muted", theme["accent"]))

    personal    = resume_data.get("personal", {})
    summary     = resume_data.get("summary", "")
    skills      = resume_data.get("skills", [])
    languages   = resume_data.get("languages", [])
    experiences = resume_data.get("experience", [])
    education   = resume_data.get("education", [])
    projects    = resume_data.get("projects", [])
    certs       = resume_data.get("certifications", [])
    achievements = resume_data.get("achievements", [])

    def esc(s):
        return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;") if s else ""

    # Build experience HTML
    exp_html = ""
    for e in experiences:
        if not isinstance(e, dict): continue
        bullets = ""
        desc = e.get("description","")
        if desc:
            for line in desc.split("\n"):
                line = line.strip().lstrip("•-").strip()
                if line:
                    bullets += f"<li>{esc(line)}</li>"
        exp_html += f"""
        <div class="section-item">
          <div class="item-header">
            <div>
              <div class="item-title">{esc(e.get('title',''))}</div>
              <div class="item-sub">{esc(e.get('company',''))}</div>
            </div>
            <div class="item-date">{esc(e.get('start_date',''))} – {esc(e.get('end_date','Present'))}</div>
          </div>
          {f'<ul class="item-bullets">{bullets}</ul>' if bullets else ''}
        </div>"""

    # Build education HTML
    edu_html = ""
    for ed in education:
        if not isinstance(ed, dict): continue
        edu_html += f"""
        <div class="section-item">
          <div class="item-header">
            <div>
              <div class="item-title">{esc(ed.get('degree',''))}</div>
              <div class="item-sub">{esc(ed.get('institution',''))}</div>
            </div>
            <div class="item-date">{esc(ed.get('year',''))}{(' · GPA: ' + esc(ed.get('gpa',''))) if ed.get('gpa') else ''}</div>
          </div>
        </div>"""

    # Projects
    proj_html = ""
    for p in projects:
        if not isinstance(p, dict): continue
        proj_html += f"""
        <div class="section-item">
          <div class="item-header">
            <div class="item-title">{esc(p.get('name',''))}{(' — <span style="font-weight:400">' + esc(p.get('tech','')) + '</span>') if p.get('tech') else ''}</div>
            {('<div class="item-date"><a href="'+esc(p.get('url',''))+'">🔗 Link</a></div>') if p.get('url') else ''}
          </div>
          {('<p class="item-desc">' + esc(p.get('description','')) + '</p>') if p.get('description') else ''}
        </div>"""

    # Skills chips
    skill_html = " ".join(f'<span class="chip">{esc(s)}</span>' for s in skills)
    lang_html  = " ".join(f'<span class="chip chip-lang">{esc(l)}</span>' for l in languages)

    # Certs
    cert_html = ""
    for c in certs:
        if not isinstance(c, dict): continue
        cert_html += f'<div class="section-item"><div class="item-title">{esc(c.get("name",""))}</div><div class="item-sub">{esc(c.get("issuer",""))} {esc(c.get("year",""))}</div></div>'

    # Achievements
    ach_html = ""
    for a in achievements:
        if a:
            ach_html += f"<li>{esc(str(a))}</li>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; color: #1a202c; background: #fff; line-height: 1.5; }}
  .resume {{ max-width: 780px; margin: 0 auto; }}
  .header {{ background: {primary}; color: #fff; padding: 28px 32px 22px; }}
  .header-name {{ font-size: 26px; font-weight: 700; letter-spacing: 0.3px; }}
  .header-role {{ font-size: 14px; color: rgba(255,255,255,0.85); margin-top: 4px; }}
  .header-contacts {{ display: flex; flex-wrap: wrap; gap: 14px; margin-top: 12px; font-size: 12px; color: rgba(255,255,255,0.9); }}
  .header-contacts span {{ display: flex; align-items: center; gap: 4px; }}
  .summary {{ background: {light}; padding: 16px 32px; font-size: 13px; color: #2d3748; border-left: 4px solid {accent}; }}
  .body {{ padding: 0 32px 32px; }}
  .section {{ margin-top: 22px; }}
  .section-title {{ font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: {accent}; border-bottom: 1.5px solid {accent}; padding-bottom: 4px; margin-bottom: 12px; }}
  .section-item {{ margin-bottom: 12px; }}
  .item-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }}
  .item-title {{ font-weight: 600; font-size: 13px; color: #1a202c; }}
  .item-sub {{ color: {muted}; font-size: 12px; margin-top: 1px; }}
  .item-date {{ font-size: 11px; color: {muted}; white-space: nowrap; flex-shrink: 0; }}
  .item-bullets {{ margin: 6px 0 0 16px; color: #2d3748; }}
  .item-bullets li {{ margin-bottom: 2px; font-size: 12px; }}
  .item-desc {{ font-size: 12px; color: #4a5568; margin-top: 4px; }}
  .chip {{ display: inline-block; background: {light}; color: {primary}; border: 1px solid {accent}33; border-radius: 12px; padding: 3px 10px; font-size: 11px; margin: 2px 3px 2px 0; }}
  .chip-lang {{ background: #f0f4ff; color: #3730a3; border-color: #c7d2fe; }}
  a {{ color: {accent}; text-decoration: none; }}
  @media print {{ body {{ -webkit-print-color-adjust: exact; }} }}
</style>
</head>
<body>
<div class="resume">
  <div class="header">
    <div class="header-name">{esc(personal.get('name','Your Name'))}</div>
    <div class="header-role">{esc(personal.get('desired_role',''))}</div>
    <div class="header-contacts">
      {('<span>✉ ' + esc(personal.get('email','')) + '</span>') if personal.get('email') else ''}
      {('<span>📞 ' + esc(personal.get('phone','')) + '</span>') if personal.get('phone') else ''}
      {('<span>📍 ' + esc(personal.get('location','')) + '</span>') if personal.get('location') else ''}
      {('<span>🔗 ' + esc(personal.get('linkedin','')) + '</span>') if personal.get('linkedin') else ''}
      {('<span>💻 ' + esc(personal.get('github','')) + '</span>') if personal.get('github') else ''}
    </div>
  </div>

  {('<div class="summary">' + esc(summary) + '</div>') if summary else ''}

  <div class="body">
    {('<div class="section"><div class="section-title">Experience</div>' + exp_html + '</div>') if exp_html else ''}
    {('<div class="section"><div class="section-title">Education</div>' + edu_html + '</div>') if edu_html else ''}
    {('<div class="section"><div class="section-title">Skills</div><div>' + skill_html + '</div>' + ('<div style="margin-top:8px">' + lang_html + '</div>' if lang_html else '') + '</div>') if skill_html else ''}
    {('<div class="section"><div class="section-title">Projects</div>' + proj_html + '</div>') if proj_html else ''}
    {('<div class="section"><div class="section-title">Certifications</div>' + cert_html + '</div>') if cert_html else ''}
    {('<div class="section"><div class="section-title">Achievements</div><ul style="padding-left:18px">' + ach_html + '</ul></div>') if ach_html else ''}
  </div>
</div>
</body>
</html>"""

    return jsonify({"html": html})


# ── IMPROVEMENT 3: LinkedIn PDF Import ────────────────────────────────────

@app.route("/api/import-linkedin", methods=["POST"])
def import_linkedin():
    """Parse an uploaded LinkedIn PDF and return structured resume data."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["file"]
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF file"}), 400

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    try:
        f.save(tmp.name)
        tmp.close()
        resume_data = parse_linkedin_pdf(tmp.name)
        if not resume_data:
            return jsonify({"error": "Could not parse PDF. Please ensure it is a LinkedIn export."}), 422
        return jsonify({"success": True, "resume": resume_data})
    except Exception as e:
        return jsonify({"error": f"Import failed: {str(e)}"}), 500
    finally:
        try:
            os.unlink(tmp.name)
        except:
            pass


# ── NEW: Cover Letter Generator ────────────────────────────────────────────

@app.route("/api/cover-letter", methods=["POST"])
def cover_letter():
    """Generate a personalised cover letter."""
    data            = request.get_json(force=True)
    resume_data     = data.get("resume", {})
    job_description = data.get("job_description", "")
    role = resume_data.get("personal", {}).get("desired_role", "")
    if not role:
        return jsonify({"error": "Please fill in the Desired Job Role field first."}), 400
    letter = generate_cover_letter(resume_data, job_description)
    return jsonify({"success": True, "cover_letter": letter})


# ── NEW: ATS Keyword Gap Analyser ─────────────────────────────────────────

@app.route("/api/keyword-gap", methods=["POST"])
def keyword_gap():
    """Analyse keyword gap between resume and job description."""
    data            = request.get_json(force=True)
    resume_data     = data.get("resume", {})
    job_description = data.get("job_description", "")
    if not job_description.strip():
        return jsonify({"error": "Please provide a job description to analyse."}), 400
    result = analyse_keyword_gap(resume_data, job_description)
    return jsonify({"success": True, "analysis": result})


# ── NEW: Interview Question Generator ─────────────────────────────────────

@app.route("/api/interview-questions", methods=["POST"])
def interview_questions():
    """Generate interview questions based on resume and role."""
    data            = request.get_json(force=True)
    resume_data     = data.get("resume", {})
    job_description = data.get("job_description", "")
    questions = generate_interview_questions(resume_data, job_description)
    return jsonify({"success": True, "questions": questions})


# ── Feature 4: AI Bullet Suggestions ──────────────────────────────────────
@app.route("/api/bullet-suggestions", methods=["POST"])
def bullet_suggestions():
    data      = request.get_json(force=True)
    job_title = data.get("job_title", "").strip()
    role      = data.get("role", job_title).strip()
    if not job_title:
        return jsonify({"error": "job_title required"}), 400
    from groq_ai_engine import get_bullet_suggestions
    bullets = get_bullet_suggestions(job_title, role)
    return jsonify({"success": True, "bullets": bullets})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Smart Resume Builder AI v2 starting on http://localhost:{port}")
    print(f"   ✅ Groq AI: {'configured' if os.getenv('GROQ_API') else 'NOT configured — check .env'}")
    app.run(debug=True, host="0.0.0.0", port=port)

# ── Feature 3: Duplicate Resume ────────────────────────────────────────────
@app.route("/api/resumes/<int:resume_id>/duplicate", methods=["POST"])
def duplicate_resume(resume_id):
    resume = get_resume(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    data = resume.get("data", {})
    # Append "(Copy)" to name
    personal = data.get("personal", {})
    personal["name"] = personal.get("name", "Resume") + " (Copy)"
    data["personal"] = personal
    new_id = save_resume(data, resume.get("ats_score", 0), resume.get("template", "modern_blue"))
    return jsonify({"success": True, "resume_id": new_id, "message": "Resume duplicated"})
