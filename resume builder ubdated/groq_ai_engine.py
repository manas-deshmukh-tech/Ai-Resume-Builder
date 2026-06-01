"""
Groq AI Engine - Direct Groq REST API (no LangChain required)
Real AI-powered summary generation, bullet rewriting, and role suggestions.
Uses: requests, groq API key from .env
"""
import os, re, json, requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API", "").strip()
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama3-70b-8192"


# ── Utility ──────────────────────────────────────────────────────────────
def _invoke(prompt: str, system: str = None, temperature: float = 0.7, max_tokens: int = 1024) -> str:
    """Call Groq API directly via requests and return the text response."""
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API key not found in .env file")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# ── 1. AI-Powered Professional Summary ────────────────────────────────────
def generate_ai_summary(resume_data: dict) -> str:
    """Generate a real, context-aware professional summary using Groq LLM."""
    personal   = resume_data.get("personal", {})
    name       = personal.get("name", "the candidate")
    role       = personal.get("desired_role", "Professional")
    skills     = resume_data.get("skills", [])[:8]
    experiences = resume_data.get("experience", [])
    education  = resume_data.get("education", [])

    # Build a compact context blob for the prompt
    exp_lines = []
    for e in experiences[:3]:
        if isinstance(e, dict) and (e.get("title") or e.get("company")):
            exp_lines.append(f"- {e.get('title','')} at {e.get('company','')} ({e.get('start_date','')}–{e.get('end_date','')}): {e.get('description','')[:200]}")

    edu_lines = []
    for ed in education[:2]:
        if isinstance(ed, dict):
            edu_lines.append(f"- {ed.get('degree','')} from {ed.get('institution','')} ({ed.get('year','')})")

    prompt = f"""You are an expert resume writer specialising in tailored professional summaries.
Write a compelling 3-sentence professional summary SPECIFICALLY for the role: "{role}".

Candidate details:
- Name: {name}
- Target Role: {role}
- Key Skills: {', '.join(skills) if skills else 'Not listed'}
- Work Experience:
{chr(10).join(exp_lines) if exp_lines else '  (Not provided)'}
- Education:
{chr(10).join(edu_lines) if edu_lines else '  (Not provided)'}

CRITICAL REQUIREMENTS — the summary MUST be unique to the "{role}" role:
1. Sentence 1: Name the exact target role "{role}" and highlight years of experience or the strongest domain expertise relevant to THIS role.
2. Sentence 2: Mention 2-3 role-specific technical skills or achievements from the experience that are directly relevant to "{role}" (e.g., for a Data Scientist mention ML models; for a DevOps Engineer mention CI/CD pipelines; for a Product Manager mention roadmaps/stakeholders).
3. Sentence 3: State what value the candidate brings to a team hiring for "{role}" specifically.
4. Use industry-appropriate terminology for the "{role}" field.
5. NO generic phrases like "passionate team player", "hardworking", "detail-oriented", or "results-driven" — be concrete.
6. Return ONLY the summary paragraph — no labels, no bullet points, no extra text.

Professional Summary for {role}:"""

    system = (
        "You are an elite resume writer. You write concise, role-specific professional summaries "
        "that are unique for EACH job title. Never use generic phrases. Always mention the exact role title."
    )
    try:
        result = _invoke(prompt, system=system, temperature=0.8)
        # Strip any labels the model might add
        for prefix in [f"Professional Summary for {role}:", "Professional Summary:", "Summary:"]:
            if result.startswith(prefix):
                result = result[len(prefix):].strip()
        return result
    except Exception:
        # Graceful fallback to template if API fails
        return _fallback_summary(name, role, skills, experiences)


# ── 2. AI Role Suggestions ─────────────────────────────────────────────────
def get_ai_role_suggestions(role: str, current_skills: list, experience: list = None) -> dict:
    """Use Groq to give smart, role-specific suggestions tailored to the user's profile."""
    exp_titles = []
    if experience:
        for e in experience[:3]:
            if isinstance(e, dict) and e.get("title"):
                exp_titles.append(e["title"])

    prompt = f"""You are a career coach and hiring expert. A job seeker wants to become a "{role}".

Their current skills: {', '.join(current_skills[:15]) if current_skills else 'None listed'}
Their past job titles: {', '.join(exp_titles) if exp_titles else 'Not provided'}

Respond ONLY with a valid JSON object (no markdown, no extra text) in exactly this format:
{{
  "matched_role": "closest standard job title matching their target",
  "missing_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "recommended_skills": ["skill1", "skill2", "skill3", "skill4", "skill5", "skill6", "skill7", "skill8"],
  "tips": [
    "Specific actionable tip 1 for this exact role",
    "Specific actionable tip 2 for this exact role",
    "Specific actionable tip 3 for this exact role"
  ],
  "career_path": "Brief 1-sentence description of typical career progression for this role",
  "top_companies": ["Company1", "Company2", "Company3"]
}}

Rules:
- missing_skills = skills from recommended_skills NOT in their current skills list
- All tips must be specific to the "{role}" role, not generic advice
- recommended_skills should be the most in-demand skills for this role in 2024"""

    try:
        raw = _invoke(prompt)
        # Strip markdown fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
        data = json.loads(raw)
        # Ensure missing_skills is computed correctly
        current_lower = [s.lower() for s in current_skills]
        data["missing_skills"] = [
            s for s in data.get("recommended_skills", [])
            if s.lower() not in current_lower
        ][:8]
        return data
    except Exception:
        # Fallback to static engine on failure
        return _fallback_role_suggestions(role, current_skills)


# ── 3. Bullet Point Rewriter ───────────────────────────────────────────────
def rewrite_bullet(bullet: str, job_role: str = "") -> list:
    """Rewrite a weak experience bullet into 3 strong ATS-optimised versions."""
    role_context = f"for a {job_role} role" if job_role else ""

    prompt = f"""You are an expert resume writer. Rewrite this weak experience bullet point into 3 strong versions {role_context}.

Original bullet: "{bullet}"

Rules for each version:
- Start with a strong past-tense action verb (Developed, Engineered, Optimised, Delivered, etc.)
- Include a measurable impact or metric (%, $, users, time saved, team size, etc.) if possible
- Be concise: 1-2 lines max
- Use keywords relevant to ATS systems

Return ONLY a JSON array of 3 strings, no labels or extra text:
["improved version 1", "improved version 2", "improved version 3"]"""

    try:
        raw = _invoke(prompt)
        raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
        versions = json.loads(raw)
        if isinstance(versions, list) and len(versions) >= 1:
            return versions[:3]
    except Exception:
        pass
    return [bullet]  # Return original if all fails



# ── 4. Cover Letter Generator ─────────────────────────────────────────────
def generate_cover_letter(resume_data: dict, job_description: str = "") -> str:
    """Generate a personalised cover letter based on resume + job description."""
    personal    = resume_data.get("personal", {})
    name        = personal.get("name", "the candidate")
    role        = personal.get("desired_role", "the role")
    skills      = resume_data.get("skills", [])[:6]
    experiences = resume_data.get("experience", [])[:2]

    exp_lines = []
    for e in experiences:
        if isinstance(e, dict):
            exp_lines.append(f"- {e.get('title','')} at {e.get('company','')}: {e.get('description','')[:150]}")

    jd_context = f"\nJob Description:\n{job_description[:600]}" if job_description else ""

    prompt = f"""Write a professional, concise 3-paragraph cover letter for {name} applying for the role of {role}.

Candidate background:
- Skills: {', '.join(skills)}
- Experience:
{chr(10).join(exp_lines) if exp_lines else '  (Not provided)'}
{jd_context}

Requirements:
1. Paragraph 1: Strong opening — mention the exact role "{role}" and 1 standout qualification.
2. Paragraph 2: 2-3 specific achievements or skills most relevant to "{role}" with concrete examples.
3. Paragraph 3: Confident closing with call to action.
4. Professional tone. No filler phrases. No "I am writing to apply" opener.
5. Return ONLY the letter body — no subject line, no date, no address headers."""

    system = "You are an expert career coach who writes compelling, role-specific cover letters."
    try:
        return _invoke(prompt, system=system, temperature=0.75)
    except Exception:
        return (
            f"Dear Hiring Manager,\n\n"
            f"I am excited to apply for the {role} position. With experience in "
            f"{', '.join(skills[:3]) if skills else 'relevant technologies'}, "
            f"I am confident I can contribute effectively to your team.\n\n"
            f"My background includes hands-on work across key areas of {role}, and I am eager "
            f"to bring this expertise to your organisation.\n\n"
            f"I would welcome the opportunity to discuss how my experience aligns with your needs.\n\n"
            f"Sincerely,\n{name}"
        )


# ── 5. ATS Keyword Gap Analyser ───────────────────────────────────────────
def analyse_keyword_gap(resume_data: dict, job_description: str) -> dict:
    """Compare resume content against a job description and return missing keywords."""
    if not job_description.strip():
        return {"error": "No job description provided"}

    skills  = resume_data.get("skills", [])
    role    = resume_data.get("personal", {}).get("desired_role", "")
    summary = resume_data.get("summary", "")
    exp_text = " ".join(
        e.get("description", "") for e in resume_data.get("experience", [])
        if isinstance(e, dict)
    )
    resume_text = f"{role} {summary} {' '.join(skills)} {exp_text}".lower()

    prompt = f"""You are an ATS (Applicant Tracking System) expert.

Job Description:
{job_description[:1500]}

Candidate's Resume Content:
{resume_text[:1000]}

Analyse the gap between the job description and resume. Respond ONLY with a valid JSON object:
{{
  "matched_keywords": ["keyword1", "keyword2"],
  "missing_keywords": ["keyword1", "keyword2", "keyword3"],
  "match_score": 72,
  "top_suggestions": [
    "Add 'keyword1' to your skills section",
    "Mention 'keyword2' in your experience bullets",
    "Include 'keyword3' in your professional summary"
  ]
}}

Rules:
- matched_keywords: important keywords from JD that appear in the resume
- missing_keywords: important keywords from JD missing from the resume (max 10)
- match_score: 0-100 percentage of important JD keywords covered
- top_suggestions: 3-5 specific, actionable tips to improve ATS match"""

    try:
        raw = _invoke(prompt, temperature=0.3)
        raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
        return json.loads(raw)
    except Exception:
        return {
            "matched_keywords": skills[:5],
            "missing_keywords": [],
            "match_score": 50,
            "top_suggestions": [
                "Mirror exact keywords from the job description in your resume",
                "Add measurable achievements to your experience bullets",
                "Ensure your skills section matches the required skills in the JD"
            ]
        }


# ── 6. Interview Question Generator ──────────────────────────────────────
def generate_interview_questions(resume_data: dict, job_description: str = "") -> list:
    """Generate likely interview questions based on the resume and role."""
    role   = resume_data.get("personal", {}).get("desired_role", "the role")
    skills = resume_data.get("skills", [])[:6]
    exp    = resume_data.get("experience", [])[:2]

    exp_lines = [f"- {e.get('title','')} at {e.get('company','')}" for e in exp if isinstance(e, dict)]
    jd_context = f"\nJob Description excerpt: {job_description[:400]}" if job_description else ""

    prompt = f"""Generate 8 targeted interview questions for a {role} candidate.

Candidate background:
- Skills: {', '.join(skills)}
- Experience: {chr(10).join(exp_lines) if exp_lines else 'Not provided'}
{jd_context}

Return ONLY a JSON array of 8 questions mixing:
- 2 technical/skill-based questions specific to {role}
- 2 behavioural questions (STAR format)
- 2 situational/scenario questions
- 1 culture/motivation question
- 1 role-specific deep-dive question

["Question 1?", "Question 2?", ...]"""

    try:
        raw = _invoke(prompt, temperature=0.7)
        raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
        questions = json.loads(raw)
        if isinstance(questions, list):
            return questions[:8]
    except Exception:
        pass
    return [
        f"What experience do you have that makes you a strong {role}?",
        "Describe a challenging project and how you handled it.",
        f"What tools and technologies do you use most as a {role}?",
        "Tell me about a time you disagreed with a teammate. How did you resolve it?",
        "Where do you see yourself in 3 years?",
    ]

# ── Fallbacks (used when API is unavailable) ──────────────────────────────

# Role-specific sentence templates for fallback summaries
_ROLE_TEMPLATES = {
    "data scientist": {
        "intro": "Data Scientist with {years}+ years of experience building and deploying machine learning models and statistical analyses.",
        "skills_fmt": "Proficient in {skills}, with a track record of transforming raw datasets into predictive models that drive business decisions.",
        "goal": "Eager to apply advanced analytics and ML expertise to solve complex data challenges at scale.",
    },
    "software engineer": {
        "intro": "Software Engineer with {years}+ years of experience designing, building, and shipping production-grade applications.",
        "skills_fmt": "Skilled in {skills}, with a strong foundation in system design, clean code practices, and agile delivery.",
        "goal": "Committed to building scalable, maintainable software that creates measurable impact for users and businesses.",
    },
    "frontend developer": {
        "intro": "Frontend Developer with {years}+ years of experience crafting responsive, accessible, and high-performance web interfaces.",
        "skills_fmt": "Expert in {skills}, focused on pixel-perfect UIs, smooth user experiences, and cross-browser compatibility.",
        "goal": "Passionate about turning complex product requirements into elegant, user-centred interfaces.",
    },
    "backend developer": {
        "intro": "Backend Developer with {years}+ years of experience architecting robust APIs, microservices, and data pipelines.",
        "skills_fmt": "Experienced in {skills}, with a focus on scalability, security, and reliable service delivery.",
        "goal": "Driven to build the invisible infrastructure that powers seamless user experiences.",
    },
    "devops engineer": {
        "intro": "DevOps Engineer with {years}+ years of experience automating infrastructure, CI/CD pipelines, and cloud deployments.",
        "skills_fmt": "Hands-on with {skills}, consistently reducing deployment friction and improving system reliability.",
        "goal": "Dedicated to bridging the gap between development and operations through automation and observability.",
    },
    "data analyst": {
        "intro": "Data Analyst with {years}+ years of experience translating raw data into actionable business insights.",
        "skills_fmt": "Proficient in {skills}, with expertise in building dashboards, running A/B tests, and presenting findings to stakeholders.",
        "goal": "Focused on empowering data-driven decisions that improve efficiency and accelerate growth.",
    },
    "product manager": {
        "intro": "Product Manager with {years}+ years of experience owning end-to-end product roadmaps from discovery to launch.",
        "skills_fmt": "Skilled in {skills}, with a proven ability to align cross-functional teams around a clear product vision.",
        "goal": "Driven to ship products that delight users and deliver measurable business outcomes.",
    },
    "machine learning engineer": {
        "intro": "Machine Learning Engineer with {years}+ years of experience building, training, and deploying ML systems in production.",
        "skills_fmt": "Expert in {skills}, with experience taking models from prototype to scalable, monitored production services.",
        "goal": "Passionate about closing the gap between research and real-world ML impact.",
    },
    "web developer": {
        "intro": "Web Developer with {years}+ years of experience building full-stack web applications from concept to deployment.",
        "skills_fmt": "Versatile in {skills}, delivering clean, maintainable code for both customer-facing interfaces and server-side logic.",
        "goal": "Committed to developing fast, reliable web products that meet user needs and business goals.",
    },
    "ux designer": {
        "intro": "UX Designer with {years}+ years of experience researching, prototyping, and delivering user-centred digital experiences.",
        "skills_fmt": "Skilled in {skills}, translating user research and business requirements into intuitive, visually compelling interfaces.",
        "goal": "Dedicated to creating designs that reduce friction, increase engagement, and delight users.",
    },
    "cybersecurity analyst": {
        "intro": "Cybersecurity Analyst with {years}+ years of experience identifying vulnerabilities and defending critical systems.",
        "skills_fmt": "Proficient in {skills}, with hands-on experience in threat detection, incident response, and security audits.",
        "goal": "Committed to hardening infrastructure and protecting organisations from evolving cyber threats.",
    },
    "cloud engineer": {
        "intro": "Cloud Engineer with {years}+ years of experience designing and managing scalable cloud infrastructure.",
        "skills_fmt": "Experienced in {skills}, specialising in cost optimisation, high availability, and infrastructure-as-code.",
        "goal": "Focused on building resilient, secure cloud environments that accelerate team delivery.",
    },
}

def _match_role_template(role: str) -> dict:
    """Find the best matching role template for the given role string."""
    role_lower = role.lower()
    # Sort by specificity: longer/more-specific keys checked first
    sorted_templates = sorted(_ROLE_TEMPLATES.items(), key=lambda x: -len(x[0]))
    for key, template in sorted_templates:
        key_words = key.split()
        # All words in the key must appear in the role for a match
        if all(word in role_lower for word in key_words):
            return template
    # Partial match fallback — at least one word matches
    for key, template in sorted_templates:
        if any(word in role_lower for word in key.split()):
            return template
    # Generic fallback template
    return {
        "intro": f"{role} with {{years}}+ years of professional experience in the field.",
        "skills_fmt": "Skilled in {skills}, with a strong ability to deliver quality outcomes in fast-paced environments.",
        "goal": f"Seeking to leverage domain expertise in {role} to contribute to high-impact teams and projects.",
    }


def _fallback_summary(name, role, skills, experiences):
    years = max(len(experiences), 1)
    top_skills = ", ".join(skills[:4]) if skills else "core domain tools and methodologies"
    template = _match_role_template(role)
    sentence1 = template["intro"].format(years=years)
    sentence2 = template["skills_fmt"].format(skills=top_skills)
    sentence3 = template["goal"]
    return f"{sentence1} {sentence2} {sentence3}"


def _fallback_role_suggestions(role, current_skills):
    ROLE_SKILLS = {
        "software engineer":     ["algorithms","data structures","system design","REST API","git","ci/cd","testing","agile","docker","aws"],
        "data scientist":        ["python","machine learning","sql","statistics","tensorflow","pandas","numpy","data visualisation","a/b testing","feature engineering"],
        "web developer":         ["html","css","javascript","react","node.js","REST API","responsive design","git","webpack","testing"],
        "devops engineer":       ["docker","kubernetes","ci/cd","aws","terraform","linux","bash","monitoring","ansible","jenkins"],
        "data analyst":          ["sql","python","excel","tableau","power bi","data cleaning","statistics","reporting","etl","data visualisation"],
        "frontend developer":    ["react","typescript","css","html","figma","responsive design","webpack","testing","performance optimisation","accessibility"],
        "backend developer":     ["python","java","node.js","sql","REST API","microservices","docker","caching","message queues","system design"],
        "machine learning engineer": ["python","tensorflow","pytorch","mlops","scikit-learn","feature engineering","model deployment","docker","sql","statistics"],
    }
    role_lower = role.lower()
    best = "software engineer"
    for r in ROLE_SKILLS:
        if any(w in role_lower for w in r.split()):
            best = r
            break
    recommended = ROLE_SKILLS[best]
    current_lower = [s.lower() for s in current_skills]
    return {
        "matched_role": best,
        "recommended_skills": recommended,
        "missing_skills": [s for s in recommended if s not in current_lower][:8],
        "tips": ["Tailor your resume keywords to each job description",
                 "Quantify your achievements with numbers and percentages",
                 "Use a clean, ATS-friendly format without tables or graphics"],
        "career_path": f"Standard progression for {best} roles.",
        "top_companies": []
    }


# ── 7. Bullet Point Suggestions (by job title) ────────────────────────────
def get_bullet_suggestions(job_title: str, role: str = "") -> list:
    """Return 4 strong achievement-oriented bullet suggestions for a given job title."""
    prompt = f"""Generate 4 strong resume bullet points for someone who worked as a "{job_title}".
These should be achievement-oriented, start with a past-tense action verb, and be ATS-friendly.
Include realistic metrics where possible (%, time saved, team size, scale).
Return ONLY a JSON array of 4 strings:
["bullet 1", "bullet 2", "bullet 3", "bullet 4"]"""
    try:
        raw = _invoke(prompt, temperature=0.7, max_tokens=512)
        raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`")
        bullets = json.loads(raw)
        if isinstance(bullets, list):
            return [b.lstrip("•- ") for b in bullets[:4]]
    except Exception:
        pass
    # Fallback static bullets per role keyword
    title_lower = job_title.lower()
    if "data" in title_lower:
        return [
            "Analysed datasets of 1M+ records to uncover actionable business insights",
            "Built dashboards in Tableau/Power BI reducing reporting time by 40%",
            "Automated data pipelines using Python, saving 8 hrs/week of manual work",
            "Collaborated with product teams to define KPIs and tracking frameworks",
        ]
    if "devops" in title_lower or "cloud" in title_lower:
        return [
            "Reduced deployment time by 60% by implementing CI/CD pipelines using Jenkins",
            "Managed Kubernetes clusters serving 500K+ daily active users",
            "Decreased infrastructure costs by 35% through AWS resource optimisation",
            "Automated server provisioning with Terraform cutting setup time from days to hours",
        ]
    if "frontend" in title_lower or "ui" in title_lower:
        return [
            "Delivered pixel-perfect React components used by 200K+ monthly users",
            "Improved page load speed by 45% through code splitting and lazy loading",
            "Built a reusable component library adopted across 5 product teams",
            "Reduced bug reports by 30% by implementing comprehensive unit and E2E tests",
        ]
    return [
        f"Led key initiatives as {job_title}, delivering results ahead of schedule",
        f"Collaborated with cross-functional teams to ship high-impact features",
        f"Optimised existing workflows reducing turnaround time by 25%",
        f"Mentored junior team members and contributed to team knowledge sharing",
    ]
