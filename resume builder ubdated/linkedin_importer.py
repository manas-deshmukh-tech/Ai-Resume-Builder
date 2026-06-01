"""
LinkedIn PDF Importer
Parses a LinkedIn-exported PDF and returns structured resume data
compatible with Smart Resume Builder Pro data schema.
"""
import re
import pdfplumber


# ── Section header patterns found in LinkedIn exports ─────────────────────
SECTION_HEADERS = [
    "Experience", "Education", "Skills", "Certifications",
    "Licenses & certifications", "Accomplishments", "Projects",
    "Volunteer Experience", "Languages", "Publications",
    "Honors & Awards", "Courses", "Organizations", "Summary",
    "About", "Contact", "Top Skills"
]

_HEADER_RE = re.compile(
    r"^(" + "|".join(re.escape(h) for h in SECTION_HEADERS) + r")\s*$",
    re.IGNORECASE
)

# Date patterns
_DATE_RANGE_RE = re.compile(
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|"
    r"April|June|July|August|September|October|November|December)[\s,]+\d{4}"
    r"(?:\s*[–\-]\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
    r"|January|February|March|April|June|July|August|September|October|November|December)"
    r"[\s,]+\d{4}))?",
    re.IGNORECASE
)
_EMAIL_RE    = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}")
_PHONE_RE    = re.compile(r"[\+\(]?[\d\s\-\(\)]{7,15}\d")
_LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-]+", re.IGNORECASE)
_GITHUB_RE   = re.compile(r"github\.com/[\w\-]+", re.IGNORECASE)
_URL_RE      = re.compile(r"https?://[^\s]+")


def parse_linkedin_pdf(file_path: str) -> dict:
    """
    Parse a LinkedIn exported PDF and return a resume data dict.
    Returns {} on any failure.
    """
    try:
        lines = _extract_lines(file_path)
        if not lines:
            return {}
        return _build_resume_data(lines)
    except Exception as e:
        print(f"[LinkedInParser] Error: {e}")
        return {}


# ── Extract raw text lines ─────────────────────────────────────────────────
def _extract_lines(file_path: str) -> list:
    lines = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=3, y_tolerance=3)
            if text:
                for line in text.split("\n"):
                    stripped = line.strip()
                    if stripped:
                        lines.append(stripped)
    return lines


# ── Section splitter ──────────────────────────────────────────────────────
def _split_sections(lines: list) -> dict:
    sections = {"header": []}
    current = "header"
    for line in lines:
        if _HEADER_RE.match(line):
            current = line.strip().lower()
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(line)
    return sections


# ── Build structured data ─────────────────────────────────────────────────
def _build_resume_data(lines: list) -> dict:
    sections = _split_sections(lines)
    full_text = " ".join(lines)

    personal = _parse_personal(sections.get("header", []), full_text)
    summary  = _parse_summary(sections)
    experiences = _parse_experience(sections)
    education   = _parse_education(sections)
    skills      = _parse_skills(sections)
    certs       = _parse_certs(sections)
    projects    = _parse_projects(sections)
    languages   = _parse_languages(sections)

    return {
        "personal":       personal,
        "summary":        summary,
        "experience":     experiences,
        "education":      education,
        "skills":         skills,
        "certifications": certs,
        "projects":       projects,
        "languages":      languages,
        "achievements":   [],
    }


def _parse_personal(header_lines: list, full_text: str) -> dict:
    personal = {
        "name": "", "email": "", "phone": "",
        "location": "", "desired_role": "",
        "linkedin": "", "github": "", "website": ""
    }

    # Name is usually the first non-empty line
    if header_lines:
        personal["name"] = header_lines[0].strip()
        # Second line is often the headline/desired role
        if len(header_lines) > 1 and not _HEADER_RE.match(header_lines[1]):
            personal["desired_role"] = header_lines[1].strip()

    email_m = _EMAIL_RE.search(full_text)
    if email_m:
        personal["email"] = email_m.group()

    phone_m = _PHONE_RE.search(full_text)
    if phone_m:
        personal["phone"] = phone_m.group().strip()

    linkedin_m = _LINKEDIN_RE.search(full_text)
    if linkedin_m:
        personal["linkedin"] = linkedin_m.group()

    github_m = _GITHUB_RE.search(full_text)
    if github_m:
        personal["github"] = github_m.group()

    return personal


def _parse_summary(sections: dict) -> str:
    for key in ["summary", "about"]:
        lines = sections.get(key, [])
        if lines:
            return " ".join(lines).strip()
    return ""


def _parse_experience(sections: dict) -> list:
    lines = sections.get("experience", [])
    if not lines:
        return []

    experiences = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Skip date-only lines at top
        if _DATE_RANGE_RE.match(line):
            i += 1
            continue

        # Look for job title — usually a non-date, non-company line
        title = line
        company = ""
        date_str = ""
        desc_lines = []

        i += 1
        # Next line often company name
        if i < len(lines) and not _DATE_RANGE_RE.match(lines[i]):
            company = lines[i]
            i += 1

        # Collect date + description until next title-like line
        while i < len(lines):
            l = lines[i]
            if _DATE_RANGE_RE.search(l):
                date_str = l
                i += 1
            elif _HEADER_RE.match(l):
                break
            elif len(l) > 3 and not _DATE_RANGE_RE.match(l):
                # Stop if looks like new job title (short, title-case, no dot)
                if len(l) < 60 and l[0].isupper() and not l.endswith(".") and not desc_lines:
                    break
                desc_lines.append(l)
                i += 1
            else:
                i += 1

        if title and len(title) > 2:
            # Parse dates
            start_date, end_date = _parse_date_range(date_str)
            experiences.append({
                "title":       title,
                "company":     company,
                "start_date":  start_date,
                "end_date":    end_date,
                "description": "\n".join(f"• {d}" for d in desc_lines if d),
            })

    return experiences[:10]  # Cap at 10


def _parse_date_range(date_str: str):
    if not date_str:
        return "", "Present"
    parts = re.split(r"\s*[–\-]\s*", date_str, maxsplit=1)
    start = parts[0].strip() if parts else ""
    end   = parts[1].strip() if len(parts) > 1 else "Present"
    return start, end


def _parse_education(sections: dict) -> list:
    lines = sections.get("education", [])
    result = []
    i = 0
    while i < len(lines):
        institution = lines[i]; i += 1
        degree = lines[i].strip() if i < len(lines) else ""; i += 1
        year_line = lines[i] if i < len(lines) else ""; i += 1
        year_m = re.search(r"\d{4}", year_line)
        year = year_m.group() if year_m else ""
        if institution:
            result.append({
                "institution": institution,
                "degree":      degree,
                "year":        year,
                "gpa":         ""
            })
    return result[:5]


def _parse_skills(sections: dict) -> list:
    lines = sections.get("skills", []) + sections.get("top skills", [])
    skills = []
    for line in lines:
        # Skills may be comma separated or one per line
        for s in re.split(r"[,•·]", line):
            s = s.strip()
            if 1 < len(s) < 50 and not _DATE_RANGE_RE.match(s):
                skills.append(s)
    return list(dict.fromkeys(skills))[:25]  # Deduplicated, max 25


def _parse_certs(sections: dict) -> list:
    lines = sections.get("certifications", []) + \
            sections.get("licenses & certifications", [])
    certs = []
    for i, line in enumerate(lines):
        if line and not _DATE_RANGE_RE.match(line) and len(line) > 3:
            issuer = lines[i+1] if i+1 < len(lines) else ""
            certs.append({"name": line, "issuer": issuer, "year": ""})
    return certs[:10]


def _parse_projects(sections: dict) -> list:
    lines = sections.get("projects", [])
    projects = []
    i = 0
    while i < len(lines):
        name = lines[i]; i += 1
        desc_lines = []
        while i < len(lines) and not (lines[i][0].isupper() and len(lines[i]) < 80 and not lines[i].endswith(".")):
            desc_lines.append(lines[i]); i += 1
        if name:
            projects.append({
                "name":        name,
                "description": " ".join(desc_lines),
                "tech":        "",
                "url":         ""
            })
    return projects[:8]


def _parse_languages(sections: dict) -> list:
    lines = sections.get("languages", [])
    langs = []
    for line in lines:
        for l in re.split(r"[,•·]", line):
            l = l.strip()
            if 1 < len(l) < 40:
                langs.append(l)
    return langs[:8]
