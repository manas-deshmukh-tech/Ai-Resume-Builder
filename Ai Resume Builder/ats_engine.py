"""
ATS Engine - Custom NLP-based resume analysis
No external NLP libraries required - pure Python implementation
"""
import re
import math
import collections
import json

# ──────────────────────────────────────────────
# INDUSTRY KEYWORD TAXONOMY
# ──────────────────────────────────────────────
TECH_SKILLS = {
    "programming": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
                    "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "dart"],
    "web": ["html", "css", "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
            "spring", "express", "next.js", "nuxt", "tailwind", "bootstrap", "graphql", "rest", "api"],
    "data": ["machine learning", "deep learning", "data analysis", "tensorflow", "pytorch", "keras",
             "scikit-learn", "pandas", "numpy", "sql", "nosql", "mongodb", "postgresql", "mysql",
             "data visualization", "tableau", "power bi", "spark", "hadoop", "etl"],
    "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "devops", "terraform",
              "jenkins", "github actions", "linux", "bash", "microservices", "serverless"],
    "tools": ["git", "github", "gitlab", "jira", "agile", "scrum", "figma", "postman",
              "vs code", "intellij", "excel", "powerpoint"],
}

SOFT_SKILLS = ["communication", "leadership", "teamwork", "problem solving", "analytical",
               "critical thinking", "time management", "project management", "collaboration",
               "adaptability", "creativity", "attention to detail", "organized", "motivated"]

ACTION_VERBS = ["developed", "designed", "implemented", "built", "created", "managed", "led",
                "optimized", "improved", "increased", "reduced", "delivered", "deployed",
                "architected", "automated", "analyzed", "collaborated", "mentored", "launched",
                "scaled", "integrated", "maintained", "researched", "coordinated", "executed"]

WEAK_PHRASES = ["responsible for", "worked on", "helped with", "assisted in", "participated in",
                "involved in", "tried to", "attempted to", "was part of", "duties included"]

QUANTIFIER_PATTERNS = [
    r'\d+%', r'\d+x', r'\$\d+', r'\d+ (users|clients|projects|team|members|hours|days|months|years)',
    r'(increased|decreased|reduced|improved|grew|boosted) by \d+',
    r'\d+ (million|billion|thousand|hundred)',
]

# ──────────────────────────────────────────────
# TEXT UTILITIES
# ──────────────────────────────────────────────
STOPWORDS = {"a","an","the","and","or","but","in","on","at","to","for","of","with",
             "by","from","up","about","into","through","during","including","until",
             "against","among","throughout","despite","towards","upon","concerning",
             "is","are","was","were","be","been","being","have","has","had","do","does",
             "did","will","would","could","should","may","might","shall","can","need",
             "dare","ought","used","i","me","my","myself","we","our","ours","you","your",
             "he","him","his","she","her","it","its","they","them","their","what","which",
             "who","this","that","these","those","am","if","as","so","not","no","nor",
             "very","just","than","then","when","while","where","how","all","each","every",
             "both","few","more","most","other","some","such","only","own","same","too",
             "also","again","further","once","here","there","any"}

def tokenize(text):
    """Simple word tokenizer"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\.\+\#]', ' ', text)
    words = text.split()
    return [w for w in words if len(w) > 1]

def remove_stopwords(tokens):
    return [t for t in tokens if t not in STOPWORDS]

def get_bigrams(tokens):
    return [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)]

def extract_keywords(text):
    tokens = tokenize(text)
    unigrams = remove_stopwords(tokens)
    bigrams = get_bigrams(tokens)
    return unigrams + bigrams

def tfidf_score(term, doc_tokens, corpus_size=1000):
    """Simplified TF-IDF scoring"""
    tf = doc_tokens.count(term) / (len(doc_tokens) + 1)
    idf = math.log(corpus_size / (1 + 1))  # simplified
    return tf * idf

def text_similarity(text1, text2):
    """Cosine similarity between two texts using TF vectors"""
    tokens1 = set(extract_keywords(text1))
    tokens2 = set(extract_keywords(text2))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1 & tokens2
    return len(intersection) / math.sqrt(len(tokens1) * len(tokens2))


# ──────────────────────────────────────────────
# ATS ANALYZER
# ──────────────────────────────────────────────
class ATSAnalyzer:
    def analyze(self, resume_data, job_description=""):
        """Full ATS analysis returning score + detailed feedback"""
        full_text = self._flatten_resume(resume_data)
        tokens = extract_keywords(full_text)
        token_set = set(tokens)

        scores = {}
        feedback = {"strengths": [], "improvements": [], "missing_keywords": [],
                    "weak_phrases": [], "suggestions": []}

        # 1. Contact completeness (10 pts)
        scores["contact"] = self._score_contact(resume_data, feedback)

        # 2. Skills coverage (25 pts)
        scores["skills"] = self._score_skills(token_set, resume_data, feedback)

        # 3. Experience quality (25 pts)
        scores["experience"] = self._score_experience(resume_data, full_text, feedback)

        # 4. Education (10 pts)
        scores["education"] = self._score_education(resume_data, feedback)

        # 5. Formatting & structure (15 pts)
        scores["formatting"] = self._score_formatting(resume_data, feedback)

        # 6. Keyword density & action verbs (15 pts)
        scores["keywords"] = self._score_keywords(full_text, token_set, feedback)

        # 7. Job description match (bonus if provided)
        jd_score = 0
        if job_description.strip():
            jd_score = self._score_jd_match(full_text, job_description, feedback)
            scores["jd_match"] = jd_score

        total = sum(scores.values())
        # cap at 100
        total = min(100, round(total))

        breakdown = {k: round(v, 1) for k, v in scores.items()}
        rating, color = self._get_rating(total)

        return {
            "total_score": total,
            "breakdown": breakdown,
            "rating": rating,
            "color": color,
            "feedback": feedback,
            "keyword_cloud": self._keyword_cloud(token_set),
        }

    def _flatten_resume(self, data):
        parts = []
        for key, val in data.items():
            if isinstance(val, str):
                parts.append(val)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        parts.extend(str(v) for v in item.values())
                    else:
                        parts.append(str(item))
        return " ".join(parts)

    def _score_contact(self, data, feedback):
        score = 0
        personal = data.get("personal", {})
        if personal.get("name"): score += 2
        if personal.get("email") and re.match(r'[^@]+@[^@]+\.[^@]+', personal.get("email","")): score += 2
        if personal.get("phone"): score += 2
        if personal.get("linkedin"): score += 2; feedback["strengths"].append("LinkedIn profile included")
        if personal.get("github"): score += 1; feedback["strengths"].append("GitHub portfolio linked")
        if personal.get("location"): score += 1
        if score < 7:
            feedback["improvements"].append("Complete all contact details (email, phone, LinkedIn, location)")
        return min(score, 10)

    def _score_skills(self, token_set, data, feedback):
        score = 0
        found_cats = []
        missing_cats = []
        all_skills = data.get("skills", [])
        skill_text = " ".join(all_skills).lower() if all_skills else ""
        skill_tokens = set(extract_keywords(skill_text))

        for category, skills in TECH_SKILLS.items():
            matches = [s for s in skills if s in skill_tokens or s in token_set]
            if matches:
                found_cats.append(category)
                score += min(len(matches) * 1.5, 5)
            else:
                missing_cats.append(category)

        if found_cats:
            feedback["strengths"].append(f"Skills found in: {', '.join(found_cats)}")

        soft_found = [s for s in SOFT_SKILLS if s in token_set]
        if len(soft_found) >= 3:
            score += 3
            feedback["strengths"].append(f"{len(soft_found)} soft skills mentioned")
        else:
            feedback["improvements"].append("Add soft skills: leadership, communication, problem-solving, etc.")

        if len(all_skills) < 5:
            feedback["improvements"].append("List at least 8-10 relevant technical skills")
        elif len(all_skills) >= 10:
            feedback["strengths"].append(f"Strong skills section with {len(all_skills)} skills")

        missing_important = []
        for cat in missing_cats[:2]:
            missing_important.extend(TECH_SKILLS[cat][:3])
        if missing_important:
            feedback["missing_keywords"].extend(missing_important[:6])

        return min(score, 25)

    def _score_experience(self, data, full_text, feedback):
        score = 0
        experiences = data.get("experience", [])
        if not experiences:
            feedback["improvements"].append("Add work experience — it's the most critical ATS section")
            return 0

        score += min(len(experiences) * 4, 12)

        # Check action verbs
        found_verbs = [v for v in ACTION_VERBS if v in full_text.lower()]
        if len(found_verbs) >= 5:
            score += 5
            feedback["strengths"].append(f"Strong action verbs used: {', '.join(found_verbs[:5])}")
        elif len(found_verbs) >= 2:
            score += 2
            feedback["improvements"].append("Use more action verbs: developed, implemented, optimized, led...")
        else:
            feedback["improvements"].append("Bullet points need strong action verbs (built, created, deployed...)")

        # Check quantifiers
        quant_found = []
        for pat in QUANTIFIER_PATTERNS:
            matches = re.findall(pat, full_text, re.IGNORECASE)
            quant_found.extend(matches)
        if len(quant_found) >= 3:
            score += 5
            feedback["strengths"].append(f"Quantified achievements found ({len(quant_found)} metrics)")
        elif len(quant_found) >= 1:
            score += 2
            feedback["improvements"].append("Add more quantified results (e.g., 'Improved performance by 40%')")
        else:
            feedback["improvements"].append("Quantify your impact: use numbers, percentages, dollar values")

        # Weak phrases
        weak_found = [p for p in WEAK_PHRASES if p in full_text.lower()]
        if weak_found:
            feedback["weak_phrases"].extend(weak_found)
            feedback["improvements"].append(f"Replace weak phrases: {', '.join(weak_found[:3])}")
            score -= len(weak_found)

        return max(0, min(score, 25))

    def _score_education(self, data, feedback):
        edu = data.get("education", [])
        if not edu:
            feedback["improvements"].append("Add education history")
            return 0
        score = 5
        for e in edu:
            if isinstance(e, dict):
                if e.get("degree"): score += 2
                if e.get("institution"): score += 1
                if e.get("year"): score += 1
                if e.get("gpa"): score += 1; feedback["strengths"].append("GPA included in education")
        return min(score, 10)

    def _score_formatting(self, data, feedback):
        score = 0
        sections = ["personal", "skills", "experience", "education", "projects", "certifications"]
        present = [s for s in sections if data.get(s)]
        score += len(present) * 2

        if data.get("summary"):
            score += 3
            feedback["strengths"].append("Professional summary/objective section present")
        else:
            feedback["improvements"].append("Add a professional summary (2-3 lines) at the top of your resume")
            feedback["suggestions"].append("AI Tip: A tailored summary with your top skills and years of experience greatly improves ATS matching")

        if data.get("projects"):
            score += 2
            feedback["strengths"].append("Projects section adds technical credibility")

        if data.get("certifications"):
            feedback["strengths"].append("Certifications boost ATS keyword matching")

        return min(score, 15)

    def _score_keywords(self, full_text, token_set, feedback):
        score = 0
        text_lower = full_text.lower()

        # Action verb density
        verb_count = sum(1 for v in ACTION_VERBS if v in text_lower)
        score += min(verb_count * 0.8, 6)

        # Industry keyword density
        all_industry = []
        for skills in TECH_SKILLS.values():
            all_industry.extend(skills)
        found_industry = [k for k in all_industry if k in text_lower]
        score += min(len(found_industry) * 0.5, 6)

        # Length check
        word_count = len(full_text.split())
        if 300 <= word_count <= 700:
            score += 3
            feedback["strengths"].append(f"Good resume length ({word_count} words)")
        elif word_count < 200:
            feedback["improvements"].append("Resume is too short — add more detail to experience and projects")
        elif word_count > 800:
            feedback["improvements"].append("Resume may be too long — focus on the last 5 years of experience")

        return min(score, 15)

    def _score_jd_match(self, resume_text, jd_text, feedback):
        sim = text_similarity(resume_text, jd_text)
        score = round(sim * 20, 1)  # up to 20 bonus pts but we'll blend

        jd_keywords = set(extract_keywords(jd_text))
        resume_keywords = set(extract_keywords(resume_text))
        missing = jd_keywords - resume_keywords - STOPWORDS
        # filter to meaningful words
        meaningful_missing = [k for k in missing if len(k) > 4 and not k.isdigit()][:8]
        if meaningful_missing:
            feedback["missing_keywords"].extend(meaningful_missing)
            feedback["suggestions"].append(f"Add JD-specific keywords: {', '.join(meaningful_missing[:5])}")

        if sim > 0.4:
            feedback["strengths"].append(f"Strong job description match ({round(sim*100)}%)")
        elif sim > 0.2:
            feedback["improvements"].append("Tailor resume keywords to better match the job description")

        return min(score, 10)

    def _get_rating(self, score):
        if score >= 85:
            return "Excellent", "#22c55e"
        elif score >= 70:
            return "Good", "#84cc16"
        elif score >= 55:
            return "Average", "#f59e0b"
        elif score >= 40:
            return "Needs Work", "#f97316"
        else:
            return "Poor", "#ef4444"

    def _keyword_cloud(self, token_set):
        all_tech = []
        for skills in TECH_SKILLS.values():
            all_tech.extend(skills)
        found = [k for k in all_tech if k in token_set]
        return found[:20]


# ──────────────────────────────────────────────
# SUGGESTION ENGINE
# ──────────────────────────────────────────────
class SuggestionEngine:
    ROLE_SKILLS = {
        "software engineer": ["algorithms", "data structures", "system design", "oop", "rest api",
                              "git", "ci/cd", "testing", "agile", "docker"],
        "data scientist": ["machine learning", "python", "sql", "statistics", "tensorflow",
                           "data visualization", "pandas", "numpy", "feature engineering", "a/b testing"],
        "web developer": ["html", "css", "javascript", "react", "node.js", "rest api",
                          "responsive design", "git", "webpack", "testing"],
        "devops engineer": ["docker", "kubernetes", "ci/cd", "aws", "terraform", "linux",
                            "bash", "monitoring", "ansible", "jenkins"],
        "data analyst": ["sql", "python", "excel", "tableau", "power bi", "data cleaning",
                         "statistics", "reporting", "data visualization", "etl"],
        "machine learning engineer": ["python", "tensorflow", "pytorch", "mlops", "scikit-learn",
                                      "feature engineering", "model deployment", "docker", "sql", "statistics"],
        "frontend developer": ["react", "typescript", "css", "html", "figma", "responsive design",
                               "webpack", "testing", "performance optimization", "accessibility"],
        "backend developer": ["python", "java", "node.js", "sql", "rest api", "microservices",
                              "docker", "caching", "message queues", "system design"],
    }

    def get_role_suggestions(self, role, current_skills):
        role_lower = role.lower()
        best_match = None
        best_score = 0
        for r, skills in self.ROLE_SKILLS.items():
            score = text_similarity(role_lower, r)
            if score > best_score:
                best_score = score
                best_match = r

        if not best_match:
            # fuzzy match by word overlap
            for r in self.ROLE_SKILLS:
                if any(word in role_lower for word in r.split()):
                    best_match = r
                    break

        if not best_match:
            best_match = "software engineer"

        recommended = self.ROLE_SKILLS[best_match]
        current_lower = [s.lower() for s in current_skills]
        missing = [s for s in recommended if s not in current_lower]

        return {
            "matched_role": best_match,
            "recommended_skills": recommended,
            "missing_skills": missing[:8],
            "tips": self._get_tips(best_match)
        }

    def _get_tips(self, role):
        TIPS = {
            "software engineer": [
                "Mention design patterns you've used (MVC, Singleton, Observer)",
                "Include system design experience (load balancing, caching, databases)",
                "Show open source contributions or personal projects on GitHub",
            ],
            "data scientist": [
                "Quantify model performance (e.g., 'Improved accuracy from 82% to 94%')",
                "Mention dataset sizes and complexity to show scale",
                "Include both technical skills and domain expertise",
            ],
            "web developer": [
                "Include a link to your portfolio or live projects",
                "Mention performance optimization techniques used",
                "Show experience with responsive design and cross-browser compatibility",
            ],
        }
        return TIPS.get(role, [
            "Tailor your resume keywords to each job description",
            "Quantify your achievements with numbers and percentages",
            "Use a clean, ATS-friendly format without tables or graphics",
        ])

    def generate_ai_summary(self, data):
        """Generate a professional summary from resume data"""
        name = data.get("personal", {}).get("name", "Professional")
        skills = data.get("skills", [])[:5]
        exp = data.get("experience", [])
        edu = data.get("education", [])

        years_exp = len(exp)  # simplified
        top_skills = ", ".join(skills[:3]) if skills else "multiple technologies"
        degree = ""
        if edu and isinstance(edu[0], dict):
            degree = edu[0].get("degree", "")

        role = data.get("personal", {}).get("desired_role", "Software Professional")

        # Import the role-aware fallback from groq_ai_engine
        try:
            from groq_ai_engine import _fallback_summary
            return _fallback_summary(name, role, skills, exp)
        except Exception:
            pass

        # Last-resort generic fallback
        role_lower = role.lower()
        if "data" in role_lower and "sci" in role_lower:
            domain_phrase = "building machine learning models and extracting insights from complex datasets"
            skill_phrase = f"including {top_skills}" if top_skills else "across the full data science lifecycle"
            goal_phrase = f"applying advanced analytics to solve impactful business problems as a {role}"
        elif "frontend" in role_lower or "ui" in role_lower:
            domain_phrase = "delivering responsive, user-centric web interfaces"
            skill_phrase = f"using {top_skills}" if top_skills else "with modern frontend technologies"
            goal_phrase = f"crafting pixel-perfect user experiences in a {role} capacity"
        elif "devops" in role_lower or "cloud" in role_lower:
            domain_phrase = "automating infrastructure, CI/CD pipelines, and cloud deployments"
            skill_phrase = f"with {top_skills}" if top_skills else "across major cloud platforms"
            goal_phrase = f"bridging development and operations as a {role}"
        elif "backend" in role_lower:
            domain_phrase = "designing scalable APIs, microservices, and server-side systems"
            skill_phrase = f"with {top_skills}" if top_skills else "using modern backend frameworks"
            goal_phrase = f"building robust backend infrastructure as a {role}"
        else:
            domain_phrase = f"delivering high-quality work as a {role}"
            skill_phrase = f"skilled in {top_skills}" if top_skills else "with a versatile technical background"
            goal_phrase = f"bringing proven expertise to a {role} position"

        edu_note = (f"Holding a {degree}, " if degree else "") + "brings"
        summary = (
            f"{role} with {years_exp}+ years of experience {domain_phrase}, {skill_phrase}. "
            f"{edu_note} strong problem-solving skills and a track record of delivering measurable results. "
            f"Looking to apply this expertise to {goal_phrase} at a forward-thinking organization."
        )
        return summary
