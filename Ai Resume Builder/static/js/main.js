/* Smart Resume Builder AI - Main JavaScript */

// ── STATE ─────────────────────────────────────────────────────────────────
const state = {
  currentStep: 0,
  skills: [],
  languages: [],
  experiences: [],
  educations: [],
  projects: [],
  certifications: [],
  achievements: [],
  selectedTemplate: 'modern_blue',
  atsScore: 0,
  resumeId: null,
  atsReport: null,
  aiSummary: null,
};

const STEPS = [
  "Personal Information", "Work Experience", "Education",
  "Skills", "Projects", "Certifications & Achievements", "Finalize & Export"
];

const SKILL_SUGGESTIONS = [
  "Python", "JavaScript", "React", "Node.js", "SQL", "Git", "Docker",
  "AWS", "Machine Learning", "TypeScript", "HTML/CSS", "REST APIs",
  "MongoDB", "PostgreSQL", "Java", "C++", "TensorFlow", "Kubernetes",
  "Flask", "Django", "Vue.js", "Angular", "Linux", "Agile/Scrum"
];

// ── INIT ──────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  renderSkillSuggestions();
  addExperience();
  addEducation();
});

// ── NAVIGATION ────────────────────────────────────────────────────────────
function goToStep(n) {
  document.querySelectorAll('.step-panel').forEach(p => p.classList.remove('active'));
  document.getElementById(`step-${n}`).classList.add('active');

  document.querySelectorAll('.nav-item').forEach((item, i) => {
    item.classList.toggle('active', i === n);
  });

  state.currentStep = n;
  document.getElementById('breadcrumb').textContent = STEPS[n];

  const pct = Math.round(((n + 1) / 7) * 100);
  document.getElementById('progress-fill').style.width = pct + '%';

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function nextStep(current) {
  if (!validateStep(current)) return;
  updateBadge(current);
  goToStep(current + 1);
}

function prevStep(current) {
  goToStep(current - 1);
}

function validateStep(step) {
  if (step === 0) {
    const name = document.getElementById('p-name').value.trim();
    const email = document.getElementById('p-email').value.trim();
    if (!name) { showToast('⚠️ Please enter your full name', 'error'); return false; }
    if (!email || !isValidEmail(email)) { showToast('⚠️ Please enter a valid email address', 'error'); return false; }
  }
  return true;
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validateEmail(input) {
  if (input.value && !isValidEmail(input.value)) {
    input.classList.add('error');
  } else {
    input.classList.remove('error');
    if (input.value) input.classList.add('success');
  }
}

function updateBadge(step) {
  const badge = document.getElementById(`badge-${step}`);
  if (badge) {
    badge.classList.add('visible');
    badge.textContent = '✓';
  }
}

// ── COLLECT RESUME DATA ───────────────────────────────────────────────────
function collectResumeData() {
  return {
    personal: {
      name:         document.getElementById('p-name').value.trim(),
      email:        document.getElementById('p-email').value.trim(),
      phone:        document.getElementById('p-phone').value.trim(),
      location:     document.getElementById('p-location').value.trim(),
      desired_role: document.getElementById('p-role').value.trim(),
      linkedin:     document.getElementById('p-linkedin').value.trim(),
      github:       document.getElementById('p-github').value.trim(),
      website:      document.getElementById('p-website').value.trim(),
    },
    summary:        document.getElementById('p-summary').value.trim(),
    skills:         [...state.skills],
    languages:      [...state.languages],
    experience:     collectExperiences(),
    education:      collectEducation(),
    projects:       collectProjects(),
    certifications: collectCertifications(),
    achievements:   collectAchievements(),
  };
}

// ── EXPERIENCE ────────────────────────────────────────────────────────────
let expCount = 0;

function addExperience() {
  const id = ++expCount;
  const container = document.getElementById('experience-container');
  const card = document.createElement('div');
  card.className = 'card';
  card.id = `exp-${id}`;
  card.innerHTML = `
    <div class="card-header">
      <div class="card-title">
        <span class="card-number">${id}</span>
        Work Experience ${id}
      </div>
      <button class="btn-remove" onclick="removeCard('exp-${id}')">✕ Remove</button>
    </div>
    <div class="form-grid">
      <div class="form-group">
        <label>Job Title <span class="req">*</span></label>
        <input type="text" class="input-field exp-title" placeholder="Software Engineer">
      </div>
      <div class="form-group">
        <label>Company Name <span class="req">*</span></label>
        <input type="text" class="input-field exp-company" placeholder="Google Inc.">
      </div>
      <div class="form-group">
        <label>Start Date</label>
        <input type="text" class="input-field exp-start" placeholder="Jan 2022">
      </div>
      <div class="form-group">
        <label>End Date</label>
        <input type="text" class="input-field exp-end" placeholder="Dec 2023 (or Present)">
      </div>
      <div class="form-group full">
        <label>Responsibilities & Achievements</label>
        <textarea class="input-field textarea exp-desc" rows="4"
          placeholder="• Developed RESTful APIs serving 50k+ daily users using Python and Flask&#10;• Led a team of 4 engineers to deliver a payment module 2 weeks ahead of schedule&#10;• Optimized database queries reducing response time by 40%"></textarea>
        <span class="field-hint">Start each bullet with an action verb. Add numbers for impact.</span>
      </div>
    </div>`;
  container.appendChild(card);
}

function collectExperiences() {
  return Array.from(document.querySelectorAll('[id^="exp-"]')).map(card => ({
    title:       card.querySelector('.exp-title')?.value.trim(),
    company:     card.querySelector('.exp-company')?.value.trim(),
    start_date:  card.querySelector('.exp-start')?.value.trim(),
    end_date:    card.querySelector('.exp-end')?.value.trim() || 'Present',
    description: card.querySelector('.exp-desc')?.value.trim(),
  })).filter(e => e.title || e.company);
}

// ── EDUCATION ─────────────────────────────────────────────────────────────
let eduCount = 0;

function addEducation() {
  const id = ++eduCount;
  const container = document.getElementById('education-container');
  const card = document.createElement('div');
  card.className = 'card';
  card.id = `edu-${id}`;
  card.innerHTML = `
    <div class="card-header">
      <div class="card-title">
        <span class="card-number">${id}</span>
        Education ${id}
      </div>
      <button class="btn-remove" onclick="removeCard('edu-${id}')">✕ Remove</button>
    </div>
    <div class="form-grid">
      <div class="form-group">
        <label>Degree / Qualification <span class="req">*</span></label>
        <input type="text" class="input-field edu-degree" placeholder="B.Tech Computer Science">
      </div>
      <div class="form-group">
        <label>Institution <span class="req">*</span></label>
        <input type="text" class="input-field edu-institution" placeholder="IIT Bombay">
      </div>
      <div class="form-group">
        <label>Year of Graduation</label>
        <input type="text" class="input-field edu-year" placeholder="2023">
      </div>
      <div class="form-group">
        <label>GPA / Percentage</label>
        <input type="text" class="input-field edu-gpa" placeholder="8.7 / 10 or 87%">
      </div>
    </div>`;
  container.appendChild(card);
}

function collectEducation() {
  return Array.from(document.querySelectorAll('[id^="edu-"]')).map(card => ({
    degree:      card.querySelector('.edu-degree')?.value.trim(),
    institution: card.querySelector('.edu-institution')?.value.trim(),
    year:        card.querySelector('.edu-year')?.value.trim(),
    gpa:         card.querySelector('.edu-gpa')?.value.trim(),
  })).filter(e => e.degree || e.institution);
}

// ── PROJECTS ──────────────────────────────────────────────────────────────
let projCount = 0;

function addProject() {
  const id = ++projCount;
  const container = document.getElementById('projects-container');
  const card = document.createElement('div');
  card.className = 'card';
  card.id = `proj-${id}`;
  card.innerHTML = `
    <div class="card-header">
      <div class="card-title">
        <span class="card-number">${id}</span>
        Project ${id}
      </div>
      <button class="btn-remove" onclick="removeCard('proj-${id}')">✕ Remove</button>
    </div>
    <div class="form-grid">
      <div class="form-group">
        <label>Project Name <span class="req">*</span></label>
        <input type="text" class="input-field proj-name" placeholder="E-Commerce Platform">
      </div>
      <div class="form-group">
        <label>Technologies Used</label>
        <input type="text" class="input-field proj-tech" placeholder="React, Node.js, MongoDB">
      </div>
      <div class="form-group full">
        <label>Project Description</label>
        <textarea class="input-field textarea proj-desc" rows="3"
          placeholder="• Built a full-stack e-commerce application with 1000+ products&#10;• Implemented JWT authentication and Stripe payment integration&#10;• Achieved 95% test coverage with Jest and React Testing Library"></textarea>
      </div>
      <div class="form-group full">
        <label>Project Link / GitHub</label>
        <input type="url" class="input-field proj-link" placeholder="https://github.com/user/project">
      </div>
    </div>`;
  container.appendChild(card);
}

function collectProjects() {
  return Array.from(document.querySelectorAll('[id^="proj-"]')).map(card => ({
    name:         card.querySelector('.proj-name')?.value.trim(),
    technologies: card.querySelector('.proj-tech')?.value.trim(),
    description:  card.querySelector('.proj-desc')?.value.trim(),
    link:         card.querySelector('.proj-link')?.value.trim(),
  })).filter(p => p.name);
}

// ── CERTIFICATIONS ────────────────────────────────────────────────────────
let certCount = 0;

function addCertification() {
  const id = ++certCount;
  const container = document.getElementById('certifications-container');
  const card = document.createElement('div');
  card.className = 'card';
  card.id = `cert-${id}`;
  card.innerHTML = `
    <div class="card-header">
      <div class="card-title">
        <span class="card-number">${id}</span>
        Certification ${id}
      </div>
      <button class="btn-remove" onclick="removeCard('cert-${id}')">✕ Remove</button>
    </div>
    <div class="form-grid">
      <div class="form-group">
        <label>Certification Name <span class="req">*</span></label>
        <input type="text" class="input-field cert-name" placeholder="AWS Solutions Architect">
      </div>
      <div class="form-group">
        <label>Issuing Organization</label>
        <input type="text" class="input-field cert-issuer" placeholder="Amazon Web Services">
      </div>
      <div class="form-group">
        <label>Year Obtained</label>
        <input type="text" class="input-field cert-year" placeholder="2024">
      </div>
    </div>`;
  container.appendChild(card);
}

function collectCertifications() {
  return Array.from(document.querySelectorAll('[id^="cert-"]')).map(card => ({
    name:   card.querySelector('.cert-name')?.value.trim(),
    issuer: card.querySelector('.cert-issuer')?.value.trim(),
    year:   card.querySelector('.cert-year')?.value.trim(),
  })).filter(c => c.name);
}

// ── ACHIEVEMENTS ──────────────────────────────────────────────────────────
let achCount = 0;

function addAchievement() {
  const id = ++achCount;
  const container = document.getElementById('achievements-container');
  const card = document.createElement('div');
  card.className = 'card';
  card.id = `ach-${id}`;
  card.style.padding = '14px 20px';
  card.innerHTML = `
    <div style="display:flex; gap:10px; align-items:center;">
      <span class="card-number">${id}</span>
      <input type="text" class="input-field ach-text" placeholder="1st Place - National Hackathon 2024, IIT Delhi" style="flex:1">
      <button class="btn-remove" onclick="removeCard('ach-${id}')">✕</button>
    </div>`;
  container.appendChild(card);
}

function collectAchievements() {
  return Array.from(document.querySelectorAll('[id^="ach-"]'))
    .map(card => card.querySelector('.ach-text')?.value.trim())
    .filter(Boolean);
}

// ── SKILLS ────────────────────────────────────────────────────────────────
function renderSkillSuggestions() {
  const container = document.getElementById('suggestion-chips');
  SKILL_SUGGESTIONS.forEach(skill => {
    const chip = document.createElement('button');
    chip.className = 'suggestion-chip';
    chip.textContent = skill;
    chip.onclick = () => addSkillByName(skill);
    container.appendChild(chip);
  });
}

function addSkill() {
  const input = document.getElementById('skill-input');
  const val = input.value.trim();
  if (val) { addSkillByName(val); input.value = ''; }
}

function addSkillByName(skill) {
  if (state.skills.includes(skill)) return;
  state.skills.push(skill);
  renderSkillTags();
  updateBadge(3);
}

function removeSkill(skill) {
  state.skills = state.skills.filter(s => s !== skill);
  renderSkillTags();
}

function renderSkillTags() {
  const container = document.getElementById('skill-tags');
  container.innerHTML = state.skills.map(s => `
    <div class="skill-tag">
      <span>${s}</span>
      <button onclick="removeSkill('${s}')" title="Remove">✕</button>
    </div>`).join('');
}

function addLanguage() {
  const input = document.getElementById('lang-input');
  const val = input.value.trim();
  if (val && !state.languages.includes(val)) {
    state.languages.push(val);
    renderLanguageTags();
    input.value = '';
  }
}

function removeLanguage(lang) {
  state.languages = state.languages.filter(l => l !== lang);
  renderLanguageTags();
}

function renderLanguageTags() {
  const container = document.getElementById('lang-tags');
  container.innerHTML = state.languages.map(l => `
    <div class="skill-tag">
      <span>${l}</span>
      <button onclick="removeLanguage('${l}')" title="Remove">✕</button>
    </div>`).join('');
}

// ── REMOVE CARD ───────────────────────────────────────────────────────────
function removeCard(id) {
  const el = document.getElementById(id);
  if (el) { el.style.opacity = '0'; setTimeout(() => el.remove(), 200); }
}

// ── TEMPLATE SELECTION ────────────────────────────────────────────────────
function selectTemplate(card) {
  document.querySelectorAll('.template-card').forEach(c => c.classList.remove('active'));
  card.classList.add('active');
  state.selectedTemplate = card.dataset.theme;
  // Also keep window.selectedTemplate in sync for editor export path
  window.selectedTemplate = card.dataset.theme;
  const label = card.querySelector('span')?.innerText || card.dataset.theme;
  showToast('🎨 Template: ' + label);
}

// ── ATS ANALYSIS ──────────────────────────────────────────────────────────
async function analyzeResume() {
  const btn = document.querySelector('.btn-analyze');
  btn.classList.add('btn-loading');
  btn.textContent = '  Analyzing...';
  btn.disabled = true;

  const resumeData = collectResumeData();
  const jd = document.getElementById('jd-input').value.trim();

  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume: resumeData, job_description: jd })
    });

    const report = await res.json();
    state.atsReport = report;
    state.atsScore = report.total_score;
    state.aiSummary = report.ai_summary;

    renderATSResults(report);
    showToast(`✅ Analysis complete! ATS Score: ${report.total_score}/100`);

    // Update pill
    document.getElementById('ats-pill').style.display = 'flex';
    document.getElementById('pill-score').textContent = `${report.total_score}/100`;

  } catch (err) {
    showToast('❌ Analysis failed. Please try again.', 'error');
    console.error(err);
  } finally {
    btn.classList.remove('btn-loading');
    btn.innerHTML = '🔍 Analyze Resume';
    btn.disabled = false;
  }
}

function renderATSResults(report) {
  const container = document.getElementById('ats-results');
  container.style.display = 'block';
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Animate score ring
  const score = report.total_score;
  const fill = document.getElementById('score-ring-fill');
  const circumference = 327;
  const offset = circumference - (score / 100 * circumference);
  fill.style.strokeDashoffset = offset;
  fill.style.stroke = report.color;

  // Animate number
  animateNumber('score-display', 0, score, 1200);

  document.getElementById('score-rating').textContent = report.rating;
  document.getElementById('score-rating').style.color = report.color;

  // Breakdown bars
  const LABELS = {
    contact: 'Contact Info (10pt)',
    skills: 'Skills Coverage (25pt)',
    experience: 'Experience Quality (25pt)',
    education: 'Education (10pt)',
    formatting: 'Sections & Format (15pt)',
    keywords: 'Keywords & Verbs (15pt)',
    jd_match: 'JD Match Bonus',
  };
  const MAX = {
    contact: 10, skills: 25, experience: 25, education: 10,
    formatting: 15, keywords: 15, jd_match: 10
  };

  const barsContainer = document.getElementById('breakdown-bars');
  barsContainer.innerHTML = '';
  Object.entries(report.breakdown).forEach(([key, val]) => {
    const max = MAX[key] || 10;
    const pct = Math.round((val / max) * 100);
    const div = document.createElement('div');
    div.className = 'breakdown-item';
    div.innerHTML = `
      <div class="breakdown-label">
        <span>${LABELS[key] || key}</span>
        <span>${val}/${max}</span>
      </div>
      <div class="breakdown-bar-bg">
        <div class="breakdown-bar-fill" style="width:0%" data-target="${pct}%"></div>
      </div>`;
    barsContainer.appendChild(div);
  });

  // Animate bars
  setTimeout(() => {
    document.querySelectorAll('.breakdown-bar-fill').forEach(bar => {
      bar.style.width = bar.dataset.target;
    });
  }, 100);

  // Show tab content
  renderTabContent('strengths', report);

  // AI Summary
  if (report.ai_summary) {
    document.getElementById('ai-summary-box').style.display = 'block';
    document.getElementById('ai-summary-text').textContent = report.ai_summary;
  }

  // Role suggestions
  if (report.role_suggestions && report.role_suggestions.missing_skills) {
    const box = document.getElementById('role-suggestions-box');
    box.style.display = 'block';
    document.getElementById('role-match-label').textContent =
      `For ${report.role_suggestions.matched_role}: you may want to add these skills:`;
    const chips = document.getElementById('role-skill-chips');
    chips.innerHTML = report.role_suggestions.missing_skills
      .map(s => `<span class="role-skill-chip">+ ${s}</span>`).join('');
  }
}

function renderTabContent(tab, report) {
  // Update tab active state
  document.querySelectorAll('.tab-btn').forEach((btn, i) => {
    const tabs = ['strengths', 'improvements', 'missing', 'suggestions'];
    btn.classList.toggle('active', tabs[i] === tab);
  });

  const content = document.getElementById('tab-content');
  const r = report || state.atsReport;
  if (!r) return;

  const feedback = r.feedback;
  let items = [];

  if (tab === 'strengths') {
    items = (feedback.strengths || []).map(s => ({icon: '✅', text: s}));
    if (!items.length) items = [{icon: '—', text: 'No specific strengths detected. Complete more sections.'}];
  } else if (tab === 'improvements') {
    items = (feedback.improvements || []).map(s => ({icon: '🔧', text: s}));
    if (!items.length) items = [{icon: '🎉', text: 'Great! No major improvements detected.'}];
  } else if (tab === 'missing') {
    const missing = [...(feedback.missing_keywords || []), ...(feedback.weak_phrases || [])];
    if (missing.length) {
      content.innerHTML = `<div style="margin-bottom:8px;font-size:13px;color:var(--text-muted)">
        Add these keywords to your resume to improve ATS matching:</div>
        <div>${missing.map(k => `<span class="keyword-badge">${k}</span>`).join('')}</div>`;
      return;
    }
    items = [{icon: '✅', text: 'No critical missing keywords detected!'}];
  } else if (tab === 'suggestions') {
    items = (feedback.suggestions || []).map(s => ({icon: '💡', text: s}));
    if (r.role_suggestions && r.role_suggestions.tips) {
      r.role_suggestions.tips.forEach(t => items.push({icon: '🎯', text: t}));
    }
    if (!items.length) items = [{icon: '—', text: 'Run the analysis to see suggestions.'}];
  }

  content.innerHTML = items.map(item => `
    <div class="tab-item">
      <span class="tab-item-icon">${item.icon}</span>
      <span>${item.text}</span>
    </div>`).join('');
}

function switchTab(tab) {
  renderTabContent(tab, state.atsReport);
}

function applyAISummary() {
  if (state.aiSummary) {
    document.getElementById('p-summary').value = state.aiSummary;
    showToast('✅ AI summary applied!');
    goToStep(0);
  }
}

// ── AI SUMMARY GENERATION ─────────────────────────────────────────────────
async function generateSummary() {
  const btn = document.querySelector('.btn-ai');
  btn.textContent = '...';
  btn.disabled = true;

  const resumeData = collectResumeData();
  try {
    const res = await fetch('/api/generate-summary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume: resumeData })
    });
    const data = await res.json();
    document.getElementById('p-summary').value = data.summary;
    showToast('✨ AI summary generated!');
  } catch (err) {
    showToast('❌ Failed to generate summary', 'error');
  } finally {
    btn.textContent = '✨ Generate with AI';
    btn.disabled = false;
  }
}

// ── SAVE RESUME ───────────────────────────────────────────────────────────
async function saveResume() {
  const resumeData = collectResumeData();
  if (!resumeData.personal.name) {
    showToast('⚠️ Please fill in at least your name before saving', 'error');
    return;
  }

  try {
    const res = await fetch('/api/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume: resumeData,
        ats_score: state.atsScore,
        template: state.selectedTemplate,
        resume_id: state.resumeId,
      })
    });
    const data = await res.json();
    state.resumeId = data.resume_id;
    showToast(`✅ ${data.message}!`);
  } catch (err) {
    showToast('❌ Save failed. Please try again.', 'error');
  }
}

// ── EXPORT PDF ────────────────────────────────────────────────────────────
async function exportPDF() {
  const btn = document.querySelectorAll('.btn-export')[0];
  const resumeData = collectResumeData();

  if (!resumeData.personal.name) {
    showToast('⚠️ Please fill in your personal info first', 'error');
    return;
  }

  btn.style.opacity = '.6';
  btn.style.pointerEvents = 'none';
  showToast('📄 Generating your PDF...');

  try {
    const res = await fetch('/api/export-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume: resumeData,
        template: state.selectedTemplate,
        resume_id: state.resumeId,
      })
    });

    if (!res.ok) throw new Error('PDF generation failed');

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${resumeData.personal.name.replace(/\s+/g, '_')}_Resume.pdf`;
    a.click();
    URL.revokeObjectURL(url);

    showToast('✅ PDF downloaded successfully!');
  } catch (err) {
    showToast('❌ PDF generation failed. Please try again.', 'error');
    console.error(err);
  } finally {
    btn.style.opacity = '1';
    btn.style.pointerEvents = '';
  }
}

// ── SAVED RESUMES MODAL ───────────────────────────────────────────────────
async function openSavedResumes() {
  const overlay = document.getElementById('modal-overlay');
  const body = document.getElementById('modal-body');
  body.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⏳</div><p>Loading...</p></div>';
  overlay.classList.add('open');

  try {
    const res = await fetch('/api/resumes');
    const resumes = await res.json();

    if (!resumes.length) {
      body.innerHTML = `<div class="empty-state">
        <div class="empty-state-icon">📂</div>
        <p>No saved resumes yet.</p>
      </div>`;
      return;
    }

    body.innerHTML = resumes.map(r => `
      <div class="resume-list-item" onclick="loadResume(${r.id})">
        <div class="resume-list-info">
          <h4>${r.name}</h4>
          <p>${r.email || ''} &bull; Saved ${new Date(r.created_at).toLocaleDateString()}</p>
        </div>
        <div style="display:flex; align-items:center; gap:10px;">
          <div class="resume-score" style="color:#2563eb">${Math.round(r.ats_score)}</div>
          <button class="btn-remove" onclick="event.stopPropagation(); deleteResume(${r.id}, this)">🗑</button>
        </div>
      </div>`).join('');
  } catch (err) {
    body.innerHTML = `<div class="empty-state"><p>Failed to load resumes.</p></div>`;
  }
}

async function loadResume(id) {
  try {
    const res = await fetch(`/api/resumes/${id}`);
    const { data, ats_score, template } = await res.json();
    populateForm(data);
    state.resumeId = id;
    state.atsScore = ats_score;
    state.selectedTemplate = template || 'modern_blue';
    closeModal();
    showToast('✅ Resume loaded!');
    goToStep(0);
  } catch (err) {
    showToast('❌ Failed to load resume', 'error');
  }
}

async function deleteResume(id, btn) {
  if (!confirm('Delete this resume?')) return;
  await fetch(`/api/resumes/${id}`, { method: 'DELETE' });
  btn.closest('.resume-list-item').remove();
  showToast('🗑 Resume deleted');
}

function populateForm(data) {
  const p = data.personal || {};
  document.getElementById('p-name').value     = p.name || '';
  document.getElementById('p-email').value    = p.email || '';
  document.getElementById('p-phone').value    = p.phone || '';
  document.getElementById('p-location').value = p.location || '';
  document.getElementById('p-role').value     = p.desired_role || '';
  document.getElementById('p-linkedin').value = p.linkedin || '';
  document.getElementById('p-github').value   = p.github || '';
  document.getElementById('p-website').value  = p.website || '';
  document.getElementById('p-summary').value  = data.summary || '';

  state.skills = data.skills || [];
  state.languages = data.languages || [];
  renderSkillTags();
  renderLanguageTags();
}

// ── HELPERS ───────────────────────────────────────────────────────────────
function animateNumber(id, from, to, duration) {
  const el = document.getElementById(id);
  const start = performance.now();
  const step = (now) => {
    const t = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    el.textContent = Math.round(from + (to - from) * ease);
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

let toastTimer;
function showToast(msg, type = 'success') {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.style.background = type === 'error' ? '#dc2626' : '#0f172a';
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 3200);
}

function toggleDark() {
  const html = document.documentElement;
  html.setAttribute('data-theme', html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('open');
}

/* ══════════════════════════════════════════════════════════════════
   15-TEMPLATE GALLERY  +  MANUAL EDITOR  (enhancement)
══════════════════════════════════════════════════════════════════ */

// ── Load themes from server ──────────────────────────────────────
async function loadThemeGallery() {
  try {
    const res   = await fetch("/api/themes");
    const themes = await res.json();
    const grid  = document.getElementById("template-grid");
    if (!grid) return;

    grid.innerHTML = "";

    // Update badge
    const badge = document.getElementById("template-count-badge");
    if (badge) badge.textContent = themes.length + " templates";

    themes.forEach((theme, idx) => {
      const card = document.createElement("div");
      card.className = "template-card" + (idx === 0 ? " active" : "");
      card.dataset.theme = theme.id;
      card.onclick = () => selectTemplate(card);

      const layoutLabel = { standard:"Standard", two_column:"2-Col", classic:"Classic", minimal:"Minimal" }[theme.layout] || theme.layout;

      card.innerHTML = `
        <div class="template-preview-swatch">
          <div class="swatch-header" style="background:${theme.primary};"></div>
          <div class="swatch-lines">
            <div class="swatch-line" style="background:${theme.accent}; width:70%;"></div>
            <div class="swatch-line" style="background:${theme.primary}; width:90%; opacity:0.3;"></div>
            <div class="swatch-line" style="background:${theme.primary}; width:80%; opacity:0.3;"></div>
            <div class="swatch-line" style="background:${theme.accent}; width:50%; opacity:0.5;"></div>
          </div>
        </div>
        <span title="${theme.name}">${theme.name}</span>
        <span class="template-layout-badge">${layoutLabel}</span>`;
      grid.appendChild(card);
    });

    // Restore previously selected
    const saved = (typeof state !== "undefined" && state.selectedTemplate) ? state.selectedTemplate : (window.selectedTemplate || "modern_blue");
    const toActivate = grid.querySelector(`[data-theme="${saved}"]`);
    if (toActivate) { grid.querySelectorAll(".template-card").forEach(c=>c.classList.remove("active")); toActivate.classList.add("active"); }
  } catch(e) {
    console.warn("Could not load themes:", e);
  }
}

// selectTemplate is already defined above — this wires dynamic cards to the same state object
// (No override needed; the original function sets state.selectedTemplate correctly)

// ── Call gallery load when step 6 is opened ─────────────────────
const _origGoToStep = window.goToStep;
window.goToStep = function(step) {
  if (_origGoToStep) _origGoToStep(step);
  if (step === 6) {
    loadThemeGallery();
    refreshEditorFromData();
  }
};

// Auto-load if already on step 6 on page load
document.addEventListener("DOMContentLoaded", () => {
  const active = document.querySelector(".step-panel.active");
  if (active && active.id === "step-6") {
    loadThemeGallery();
    refreshEditorFromData();
  }
});


/* ══════════════════════════════════════════════════════════════════
   MANUAL EDITOR
══════════════════════════════════════════════════════════════════ */

function toggleEditor() {
  const body = document.getElementById("editor-body");
  const icon = document.getElementById("editor-toggle-icon");
  if (!body) return;
  const open = body.style.display !== "none";
  body.style.display = open ? "none" : "block";
  if (icon) icon.textContent = open ? "▼" : "▲";
  if (!open) refreshEditorFromData();
}

// Populate editor fields from current resumeData
function refreshEditorFromData() {
  const d = window.resumeData || {};
  const p = d.personal || {};
  const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ""; };

  setVal("ed-name",     p.name);
  setVal("ed-role",     p.desired_role);
  setVal("ed-email",    p.email);
  setVal("ed-phone",    p.phone);
  setVal("ed-location", p.location);
  setVal("ed-linkedin", p.linkedin);
  setVal("ed-github",   p.github);
  setVal("ed-summary",  d.summary);

  // Skills
  const skillsEl = document.getElementById("ed-skills");
  if (skillsEl) skillsEl.value = (d.skills || []).join(", ");

  // Languages
  const langEl = document.getElementById("ed-languages");
  if (langEl) langEl.value = (d.languages || []).join(", ");

  // Achievements
  const achEl = document.getElementById("ed-achievements");
  if (achEl) achEl.value = (d.achievements || []).join("\n");

  // Experience
  renderEditorExperience(d.experience || []);
  renderEditorEducation(d.education || []);
  renderEditorProjects(d.projects || []);
  renderEditorCerts(d.certifications || []);
}

// ── Sync helpers ────────────────────────────────────────────────
function syncEditorField(section, key, value) {
  if (!window.resumeData) window.resumeData = {};
  if (!window.resumeData[section]) window.resumeData[section] = {};
  window.resumeData[section][key] = value;
}

function syncEditorDirect(key, value) {
  if (!window.resumeData) window.resumeData = {};
  window.resumeData[key] = value;
}

function syncEditorSkills(value) {
  if (!window.resumeData) window.resumeData = {};
  window.resumeData.skills = value.split(",").map(s=>s.trim()).filter(Boolean);
}

function syncEditorLanguages(value) {
  if (!window.resumeData) window.resumeData = {};
  window.resumeData.languages = value.split(",").map(s=>s.trim()).filter(Boolean);
}

function syncEditorAchievements(value) {
  if (!window.resumeData) window.resumeData = {};
  window.resumeData.achievements = value.split("\n").map(s=>s.trim()).filter(Boolean);
}

// ── EXPERIENCE ──────────────────────────────────────────────────
function renderEditorExperience(list) {
  const container = document.getElementById("ed-experience-list");
  if (!container) return;
  container.innerHTML = "";
  (list || []).forEach((exp, i) => {
    container.appendChild(buildExpCard(exp, i));
  });
}

function buildExpCard(exp, i) {
  const card = document.createElement("div");
  card.className = "ed-entry-card";
  card.innerHTML = `
    <button class="remove-entry" onclick="removeEditorExp(${i})">✕</button>
    <div class="editor-row">
      <div class="editor-field"><label>Job Title</label>
        <input class="input-field ed-input" value="${esc(exp.title||'')}" oninput="updateEditorExp(${i},'title',this.value)"></div>
      <div class="editor-field"><label>Company</label>
        <input class="input-field ed-input" value="${esc(exp.company||'')}" oninput="updateEditorExp(${i},'company',this.value)"></div>
    </div>
    <div class="editor-row">
      <div class="editor-field"><label>Start Date</label>
        <input class="input-field ed-input" value="${esc(exp.start_date||'')}" oninput="updateEditorExp(${i},'start_date',this.value)"></div>
      <div class="editor-field"><label>End Date</label>
        <input class="input-field ed-input" value="${esc(exp.end_date||'Present')}" oninput="updateEditorExp(${i},'end_date',this.value)"></div>
    </div>
    <div class="editor-row">
      <div class="editor-field" style="flex:1"><label>Description (one bullet per line)</label>
        <textarea class="input-field textarea ed-input" rows="3" oninput="updateEditorExp(${i},'description',this.value)">${esc(exp.description||'')}</textarea>
      </div>
    </div>`;
  return card;
}

function addEditorExperience() {
  if (!window.resumeData) window.resumeData = {};
  if (!window.resumeData.experience) window.resumeData.experience = [];
  window.resumeData.experience.push({title:"",company:"",start_date:"",end_date:"Present",description:""});
  renderEditorExperience(window.resumeData.experience);
}
function removeEditorExp(i) {
  window.resumeData.experience.splice(i, 1);
  renderEditorExperience(window.resumeData.experience);
}
function updateEditorExp(i, key, val) {
  if (!window.resumeData.experience) return;
  window.resumeData.experience[i][key] = val;
}

// ── EDUCATION ───────────────────────────────────────────────────
function renderEditorEducation(list) {
  const container = document.getElementById("ed-education-list");
  if (!container) return;
  container.innerHTML = "";
  (list || []).forEach((edu, i) => {
    const card = document.createElement("div");
    card.className = "ed-entry-card";
    card.innerHTML = `
      <button class="remove-entry" onclick="removeEditorEdu(${i})">✕</button>
      <div class="editor-row">
        <div class="editor-field"><label>Degree</label>
          <input class="input-field ed-input" value="${esc(edu.degree||'')}" oninput="updateEditorEdu(${i},'degree',this.value)"></div>
        <div class="editor-field"><label>Institution</label>
          <input class="input-field ed-input" value="${esc(edu.institution||'')}" oninput="updateEditorEdu(${i},'institution',this.value)"></div>
      </div>
      <div class="editor-row">
        <div class="editor-field"><label>Year</label>
          <input class="input-field ed-input" value="${esc(edu.year||'')}" oninput="updateEditorEdu(${i},'year',this.value)"></div>
        <div class="editor-field"><label>GPA (optional)</label>
          <input class="input-field ed-input" value="${esc(edu.gpa||'')}" oninput="updateEditorEdu(${i},'gpa',this.value)"></div>
      </div>`;
    container.appendChild(card);
  });
}
function addEditorEducation() {
  if (!window.resumeData) window.resumeData = {};
  if (!window.resumeData.education) window.resumeData.education = [];
  window.resumeData.education.push({degree:"",institution:"",year:"",gpa:""});
  renderEditorEducation(window.resumeData.education);
}
function removeEditorEdu(i) { window.resumeData.education.splice(i,1); renderEditorEducation(window.resumeData.education); }
function updateEditorEdu(i, key, val) { if(window.resumeData.education) window.resumeData.education[i][key]=val; }

// ── PROJECTS ────────────────────────────────────────────────────
function renderEditorProjects(list) {
  const container = document.getElementById("ed-projects-list");
  if (!container) return;
  container.innerHTML = "";
  (list||[]).forEach((proj,i) => {
    const card = document.createElement("div");
    card.className = "ed-entry-card";
    card.innerHTML = `
      <button class="remove-entry" onclick="removeEditorProject(${i})">✕</button>
      <div class="editor-row">
        <div class="editor-field"><label>Project Name</label>
          <input class="input-field ed-input" value="${esc(proj.name||'')}" oninput="updateEditorProject(${i},'name',this.value)"></div>
        <div class="editor-field"><label>Technologies</label>
          <input class="input-field ed-input" value="${esc(proj.technologies||'')}" oninput="updateEditorProject(${i},'technologies',this.value)"></div>
      </div>
      <div class="editor-row">
        <div class="editor-field" style="flex:1"><label>Description</label>
          <textarea class="input-field textarea ed-input" rows="2" oninput="updateEditorProject(${i},'description',this.value)">${esc(proj.description||'')}</textarea>
        </div>
        <div class="editor-field"><label>Link</label>
          <input class="input-field ed-input" value="${esc(proj.link||'')}" oninput="updateEditorProject(${i},'link',this.value)"></div>
      </div>`;
    container.appendChild(card);
  });
}
function addEditorProject() {
  if (!window.resumeData) window.resumeData = {};
  if (!window.resumeData.projects) window.resumeData.projects = [];
  window.resumeData.projects.push({name:"",technologies:"",description:"",link:""});
  renderEditorProjects(window.resumeData.projects);
}
function removeEditorProject(i) { window.resumeData.projects.splice(i,1); renderEditorProjects(window.resumeData.projects); }
function updateEditorProject(i,key,val) { if(window.resumeData.projects) window.resumeData.projects[i][key]=val; }

// ── CERTIFICATIONS ──────────────────────────────────────────────
function renderEditorCerts(list) {
  const container = document.getElementById("ed-certs-list");
  if (!container) return;
  container.innerHTML = "";
  (list||[]).forEach((cert,i) => {
    const c = typeof cert === "string" ? {name:cert,issuer:"",year:""} : cert;
    const card = document.createElement("div");
    card.className = "ed-entry-card";
    card.innerHTML = `
      <button class="remove-entry" onclick="removeEditorCert(${i})">✕</button>
      <div class="editor-row">
        <div class="editor-field"><label>Certificate Name</label>
          <input class="input-field ed-input" value="${esc(c.name||'')}" oninput="updateEditorCert(${i},'name',this.value)"></div>
        <div class="editor-field"><label>Issuer</label>
          <input class="input-field ed-input" value="${esc(c.issuer||'')}" oninput="updateEditorCert(${i},'issuer',this.value)"></div>
        <div class="editor-field"><label>Year</label>
          <input class="input-field ed-input" style="max-width:100px" value="${esc(c.year||'')}" oninput="updateEditorCert(${i},'year',this.value)"></div>
      </div>`;
    container.appendChild(card);
  });
}
function addEditorCert() {
  if (!window.resumeData) window.resumeData = {};
  if (!window.resumeData.certifications) window.resumeData.certifications = [];
  window.resumeData.certifications.push({name:"",issuer:"",year:""});
  renderEditorCerts(window.resumeData.certifications);
}
function removeEditorCert(i) { window.resumeData.certifications.splice(i,1); renderEditorCerts(window.resumeData.certifications); }
function updateEditorCert(i,key,val) { if(window.resumeData.certifications) window.resumeData.certifications[i][key]=val; }

// ── Escape helper ────────────────────────────────────────────────
function esc(s) {
  return String(s||"").replace(/&/g,"&amp;").replace(/"/g,"&quot;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

// ═══════════════════════════════════════════════════════════════════════
// IMPROVEMENT 1: LIVE HTML PREVIEW
// ═══════════════════════════════════════════════════════════════════════

let previewVisible = false;
let previewDebounceTimer = null;

function togglePreview(forceState) {
  previewVisible = (forceState !== undefined) ? forceState : !previewVisible;
  const panel  = document.getElementById('preview-panel');
  const btn    = document.getElementById('preview-toggle-btn');

  if (previewVisible) {
    panel.classList.add('visible');
    if (btn) { btn.textContent = '✕ Hide Preview'; }
    refreshPreview();
  } else {
    panel.classList.remove('visible');
    if (btn) { btn.textContent = '👁 Preview'; }
  }
}

async function refreshPreview() {
  if (!previewVisible) return;

  const loading = document.getElementById('preview-loading');
  const iframe  = document.getElementById('preview-iframe');
  if (loading) loading.style.display = 'flex';

  const resumeData = collectResumeData();
  try {
    const res = await fetch('/api/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume: resumeData, template: state.selectedTemplate })
    });
    const data = await res.json();
    if (data.html) {
      const doc = iframe.contentDocument || iframe.contentWindow.document;
      doc.open();
      doc.write(data.html);
      doc.close();
    }
  } catch (err) {
    console.error('Preview error:', err);
  } finally {
    if (loading) loading.style.display = 'none';
  }
}

// Auto-refresh preview on input changes (debounced 1.5s)
function schedulePreviewRefresh() {
  if (!previewVisible) return;
  clearTimeout(previewDebounceTimer);
  previewDebounceTimer = setTimeout(refreshPreview, 1500);
}

// Hook auto-refresh on all input/textarea changes
document.addEventListener('DOMContentLoaded', () => {
  document.addEventListener('input', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      schedulePreviewRefresh();
    }
  });
});

// Also refresh when template changes
const _origSelectTemplate = window.selectTemplate;
if (typeof selectTemplate !== 'undefined') {
  const origFn = selectTemplate;
  window.selectTemplate = function(id) {
    origFn && origFn(id);
    setTimeout(refreshPreview, 300);
  };
}


// ═══════════════════════════════════════════════════════════════════════
// IMPROVEMENT 2a: AI SUMMARY (Groq)
// Override existing generateSummary to use Groq endpoint
// ═══════════════════════════════════════════════════════════════════════

async function generateSummary() {
  const btn = document.getElementById('btn-gen-summary') || document.querySelector('.btn-ai');
  if (btn) { btn.textContent = '⏳ Generating...'; btn.disabled = true; }

  const resumeData = collectResumeData();
  try {
    const res = await fetch('/api/generate-summary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume: resumeData })
    });
    const data = await res.json();
    document.getElementById('p-summary').value = data.summary;
    const badge = data.source === 'groq_ai' ? '✨ Groq AI' : '📝 Template';
    showToast(`${badge} summary generated!`);
    schedulePreviewRefresh();
  } catch (err) {
    showToast('❌ Failed to generate summary', 'error');
  } finally {
    if (btn) { btn.textContent = '✨ Generate with AI (Groq)'; btn.disabled = false; }
  }
}


// ═══════════════════════════════════════════════════════════════════════
// IMPROVEMENT 2b: AI ROLE SUGGESTIONS (Groq)
// ═══════════════════════════════════════════════════════════════════════

let roleSuggestDebounce = null;

function debouncedRoleSuggest() {
  clearTimeout(roleSuggestDebounce);
  roleSuggestDebounce = setTimeout(() => {
    const role = document.getElementById('p-role').value.trim();
    if (role.length > 3) getAIRoleSuggestions();
  }, 1200);
}

async function getAIRoleSuggestions() {
  const role  = document.getElementById('p-role').value.trim();
  const container = document.getElementById('ai-role-suggestions-inline');
  if (!role || !container) return;

  container.style.display = 'block';
  container.innerHTML = '<div style="font-size:12px;color:#64748b;padding:8px 0">🤖 Fetching AI suggestions for <strong>' + role + '</strong>...</div>';

  const resumeData = collectResumeData();
  try {
    const res = await fetch('/api/role-suggestions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role, skills: resumeData.skills, experience: resumeData.experience })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    const s = data.suggestions;
    const missingChips = (s.missing_skills || []).map(skill =>
      `<span class="skill-chip-missing" title="Click to add" onclick="addSkillFromSuggestion('${skill}')">${skill} +</span>`
    ).join('');

    const tips = (s.tips || []).map(t => `<div class="ai-tip">💡 ${t}</div>`).join('');

    const topCo = (s.top_companies || []).length
      ? `<div style="font-size:11px;color:#64748b;margin-top:8px">🏢 Top hiring companies: ${s.top_companies.join(', ')}</div>`
      : '';

    container.innerHTML = `
      <div class="ai-role-inline">
        <span class="role-match-tag">🎯 ${s.matched_role || role}</span>
        <div style="font-size:12px;color:#0369a1;font-weight:600;margin-bottom:6px">Missing skills — click to add:</div>
        <div class="skill-chips">${missingChips || '<span style="font-size:12px;color:#16a34a">✅ You have all key skills!</span>'}</div>
        ${tips}
        ${s.career_path ? `<div class="career-path">📈 ${s.career_path}</div>` : ''}
        ${topCo}
      </div>`;
  } catch (err) {
    container.innerHTML = '<div style="font-size:12px;color:#ef4444;padding:4px 0">Could not fetch AI suggestions. Please try again.</div>';
  }
}

function addSkillFromSuggestion(skill) {
  if (!state.skills.includes(skill)) {
    state.skills.push(skill);
    renderSkillTags();
    showToast(`✅ Added "${skill}" to skills`);
    schedulePreviewRefresh();
  }
}


// ═══════════════════════════════════════════════════════════════════════
// IMPROVEMENT 2c: BULLET REWRITER (Groq)
// ═══════════════════════════════════════════════════════════════════════

async function rewriteBullet() {
  const input   = document.getElementById('bullet-input');
  const results = document.getElementById('bullet-results');
  const btn     = document.querySelector('.bullet-rewriter-card .btn-ai');
  const bullet  = input ? input.value.trim() : '';
  const role    = document.getElementById('p-role').value.trim();

  if (!bullet) { showToast('⚠️ Please paste a bullet point first', 'error'); return; }

  if (btn) { btn.textContent = '⏳ Rewriting...'; btn.disabled = true; }
  results.style.display = 'none';

  try {
    const res = await fetch('/api/rewrite-bullet', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bullet, role })
    });
    const data = await res.json();
    if (!data.success && !data.versions) throw new Error(data.error);

    results.style.display = 'block';
    results.innerHTML = '<div style="font-size:12px;color:#64748b;margin-bottom:8px;font-weight:600">✨ 3 AI-Optimised Versions — click copy to use:</div>'
      + data.versions.map((v, i) => `
        <div class="bullet-version">
          <div style="padding-right:70px">${v}</div>
          <button class="bullet-copy-btn" onclick="copyBullet(this, \`${v.replace(/`/g,'\\`')}\`)">📋 Copy</button>
        </div>`).join('');
    showToast('✨ 3 stronger bullets generated!');
  } catch (err) {
    showToast('❌ Rewrite failed: ' + (err.message || 'Try again'), 'error');
  } finally {
    if (btn) { btn.textContent = '✨ Rewrite'; btn.disabled = false; }
  }
}

function copyBullet(btn, text) {
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = '✅ Copied!';
    setTimeout(() => { btn.textContent = '📋 Copy'; }, 2000);
  });
}


// ═══════════════════════════════════════════════════════════════════════
// IMPROVEMENT 3: LINKEDIN PDF IMPORT
// ═══════════════════════════════════════════════════════════════════════

async function importLinkedIn(input) {
  const file = input.files[0];
  if (!file) return;

  // Show loading overlay
  const overlay = document.createElement('div');
  overlay.className = 'import-overlay';
  overlay.innerHTML = `
    <div class="import-card">
      <div class="import-spinner"></div>
      <h3>Importing from LinkedIn...</h3>
      <p>Parsing your PDF and filling in all fields automatically.</p>
    </div>`;
  document.body.appendChild(overlay);

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch('/api/import-linkedin', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (!data.success || !data.resume) throw new Error(data.error || 'Parse failed');

    _populateFormFromImport(data.resume);
    document.body.removeChild(overlay);
    document.getElementById('linkedin-import-banner').style.display = 'none';
    showToast('✅ LinkedIn profile imported! Please review and adjust.', 'success');
    schedulePreviewRefresh();
  } catch (err) {
    document.body.removeChild(overlay);
    showToast('❌ ' + (err.message || 'Import failed. Ensure you upload a LinkedIn PDF export.'), 'error');
  }

  // Reset input so same file can be selected again
  input.value = '';
}

function _populateFormFromImport(resume) {
  const p = resume.personal || {};
  const setVal = (id, val) => { const el = document.getElementById(id); if (el && val) el.value = val; };

  setVal('p-name',     p.name);
  setVal('p-email',    p.email);
  setVal('p-phone',    p.phone);
  setVal('p-location', p.location);
  setVal('p-role',     p.desired_role);
  setVal('p-linkedin', p.linkedin);
  setVal('p-github',   p.github);
  setVal('p-summary',  resume.summary);

  // Skills
  if (resume.skills && resume.skills.length) {
    state.skills = [...new Set([...state.skills, ...resume.skills])];
    renderSkillTags();
  }
  // Languages
  if (resume.languages && resume.languages.length) {
    state.languages = resume.languages;
    renderLanguageTags();
  }

  // Experiences — clear + re-render
  if (resume.experience && resume.experience.length) {
    const container = document.getElementById('experience-container');
    container.innerHTML = '';
    expCount = 0;
    resume.experience.forEach(exp => {
      addExperience();
      const card = document.querySelector(`#exp-${expCount}`);
      if (!card) return;
      const setField = (cls, val) => { const el = card.querySelector(cls); if (el && val) el.value = val; };
      setField('.exp-title',   exp.title);
      setField('.exp-company', exp.company);
      setField('.exp-start',   exp.start_date);
      setField('.exp-end',     exp.end_date);
      setField('.exp-desc',    exp.description);
    });
  }

  // Education
  if (resume.education && resume.education.length) {
    const container = document.getElementById('education-container');
    container.innerHTML = '';
    eduCount = 0;
    resume.education.forEach(ed => {
      addEducation();
      const card = document.querySelector(`#edu-${eduCount}`);
      if (!card) return;
      const setField = (cls, val) => { const el = card.querySelector(cls); if (el && val) el.value = val; };
      setField('.edu-degree',      ed.degree);
      setField('.edu-institution', ed.institution);
      setField('.edu-year',        ed.year);
    });
  }

  // Certifications
  if (resume.certifications && resume.certifications.length) {
    resume.certifications.forEach(cert => {
      addCertification();
      const cards = document.querySelectorAll('[id^="cert-"]');
      const card  = cards[cards.length - 1];
      if (!card) return;
      const setField = (cls, val) => { const el = card.querySelector(cls); if (el && val) el.value = val; };
      setField('.cert-name',   cert.name);
      setField('.cert-issuer', cert.issuer);
    });
  }

  updateBadge(0);
}

// Helper: render language tags (mirror of renderSkillTags)
function renderLanguageTags() {
  const container = document.getElementById('lang-tags');
  if (!container) return;
  container.innerHTML = state.languages.map(l =>
    `<span class="skill-tag">${l}<button onclick="removeLang('${l}')" class="tag-remove">×</button></span>`
  ).join('');
}
function removeLang(lang) {
  state.languages = state.languages.filter(l => l !== lang);
  renderLanguageTags();
}


// ══════════════════════════════════════════════════════════════════════════
// NEW AI FEATURES — Cover Letter, Keyword Gap, Interview Questions
// ══════════════════════════════════════════════════════════════════════════

async function runKeywordGap() {
  const jd = document.getElementById('jd-input').value.trim();
  if (!jd) { showToast('⚠️ Please paste a job description first', 'error'); return; }
  const btn = event.target;
  btn.textContent = '⏳ Analysing...'; btn.disabled = true;
  const resumeData = collectResumeData();
  try {
    const res  = await fetch('/api/keyword-gap', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ resume: resumeData, job_description: jd })
    });
    const data = await res.json();
    const a    = data.analysis || {};
    const panel = document.getElementById('keyword-gap-panel');
    const content = document.getElementById('keyword-gap-content');
    const score = a.match_score ?? '—';
    const matched = (a.matched_keywords || []).map(k => `<span class="kw-hit">${k}</span>`).join(' ');
    const missing = (a.missing_keywords || []).map(k => `<span class="kw-miss">${k}</span>`).join(' ');
    const tips = (a.top_suggestions || []).map(t => `<li>${t}</li>`).join('');
    content.innerHTML = `
      <div class="kw-score">ATS Match Score: <strong>${score}%</strong></div>
      ${matched ? `<div class="kw-section"><b>✅ Matched Keywords:</b><br>${matched}</div>` : ''}
      ${missing ? `<div class="kw-section"><b>❌ Missing Keywords:</b><br>${missing}</div>` : ''}
      ${tips    ? `<div class="kw-section"><b>💡 Suggestions:</b><ol style="padding-left:18px;margin-top:6px">${tips}</ol></div>` : ''}`;
    panel.style.display = 'block';
    showToast('🎯 Keyword gap analysis complete!');
  } catch(e) { showToast('❌ Analysis failed', 'error'); }
  finally { btn.textContent = '🎯 Keyword Gap Analysis'; btn.disabled = false; }
}

async function generateCoverLetter() {
  const jd = document.getElementById('jd-input').value.trim();
  const btn = event.target;
  btn.textContent = '⏳ Writing...'; btn.disabled = true;
  const resumeData = collectResumeData();
  try {
    const res  = await fetch('/api/cover-letter', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ resume: resumeData, job_description: jd })
    });
    const data = await res.json();
    if (data.error) { showToast('⚠️ ' + data.error, 'error'); return; }
    document.getElementById('cover-letter-text').value = data.cover_letter;
    document.getElementById('cover-letter-panel').style.display = 'block';
    showToast('📝 Cover letter generated!');
  } catch(e) { showToast('❌ Failed to generate cover letter', 'error'); }
  finally { btn.textContent = '📝 Generate Cover Letter'; btn.disabled = false; }
}

function copyCoverLetter() {
  const txt = document.getElementById('cover-letter-text').value;
  navigator.clipboard.writeText(txt).then(() => showToast('📋 Copied to clipboard!'));
}

async function generateInterviewQuestions() {
  const jd  = document.getElementById('jd-input').value.trim();
  const btn = event.target;
  btn.textContent = '⏳ Generating...'; btn.disabled = true;
  const resumeData = collectResumeData();
  try {
    const res  = await fetch('/api/interview-questions', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ resume: resumeData, job_description: jd })
    });
    const data = await res.json();
    const list = document.getElementById('interview-list');
    list.innerHTML = (data.questions || []).map(q => `<li style="margin-bottom:8px">${q}</li>`).join('');
    document.getElementById('interview-panel').style.display = 'block';
    showToast('🎤 Interview questions ready!');
  } catch(e) { showToast('❌ Failed to generate questions', 'error'); }
  finally { btn.textContent = '🎤 Interview Questions'; btn.disabled = false; }
}


// ══════════════════════════════════════════════════════════════════════════
// FEATURE 3: Multiple Resume Versions — enhanced saved resumes modal
// ══════════════════════════════════════════════════════════════════════════

// Override openSavedResumes with a richer card-based UI
async function openSavedResumes() {
  const overlay = document.getElementById('modal-overlay');
  const body    = document.getElementById('modal-body');
  body.innerHTML = `<div style="text-align:center;padding:40px">
    <div style="font-size:32px">⏳</div><p style="margin-top:12px;color:#6b7280">Loading your resumes…</p>
  </div>`;
  overlay.classList.add('open');

  try {
    const res     = await fetch('/api/resumes');
    const resumes = await res.json();

    if (!resumes.length) {
      body.innerHTML = `<div class="empty-state">
        <div class="empty-state-icon">📂</div>
        <p>No saved resumes yet. Fill in your details and hit 💾 Save!</p>
      </div>`;
      return;
    }

    body.innerHTML = `
      <div style="margin-bottom:14px;font-size:13px;color:#6b7280">${resumes.length} saved resume${resumes.length>1?'s':''}</div>
      <div id="resume-cards-grid">
        ${resumes.map(r => {
          const score = Math.round(r.ats_score || 0);
          const scoreColor = score >= 70 ? '#16a34a' : score >= 50 ? '#d97706' : '#dc2626';
          const date = new Date(r.created_at).toLocaleDateString('en-IN', {day:'numeric',month:'short',year:'numeric'});
          return `
          <div class="resume-card-v3" id="rcard-${r.id}">
            <div class="rcard-top">
              <div class="rcard-avatar">${(r.name||'?')[0].toUpperCase()}</div>
              <div class="rcard-info">
                <div class="rcard-name">${r.name || 'Unnamed'}</div>
                <div class="rcard-meta">${r.email || ''}</div>
                <div class="rcard-meta">🗓 ${date}</div>
              </div>
              <div class="rcard-score" style="color:${scoreColor}">${score}<span style="font-size:10px;font-weight:500">/100</span></div>
            </div>
            <div class="rcard-actions">
              <button class="rcard-btn rcard-btn-primary" onclick="loadResume(${r.id})">📂 Load</button>
              <button class="rcard-btn rcard-btn-secondary" onclick="duplicateResume(${r.id})">📋 Duplicate</button>
              <button class="rcard-btn rcard-btn-danger" onclick="deleteResume(${r.id}, this)">🗑</button>
            </div>
          </div>`;
        }).join('')}
      </div>`;
  } catch (err) {
    body.innerHTML = `<div class="empty-state"><p>❌ Failed to load resumes.</p></div>`;
  }
}

async function duplicateResume(id) {
  try {
    const res  = await fetch(`/api/resumes/${id}/duplicate`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast('📋 Resume duplicated!');
      openSavedResumes(); // refresh modal
    }
  } catch (e) {
    showToast('❌ Duplication failed', 'error');
  }
}


// ══════════════════════════════════════════════════════════════════════════
// FEATURE 4: AI Bullet Point Suggestions while typing job title
// ══════════════════════════════════════════════════════════════════════════

let _bulletSuggestTimer = null;

function triggerBulletSuggestions(titleInput, card) {
  clearTimeout(_bulletSuggestTimer);
  const title = titleInput.value.trim();
  if (!title || title.length < 3) return;
  _bulletSuggestTimer = setTimeout(() => fetchBulletSuggestions(title, card), 800);
}

async function fetchBulletSuggestions(jobTitle, card) {
  const role = document.getElementById('p-role').value.trim() || jobTitle;
  let suggBox = card.querySelector('.bullet-suggest-box');
  if (!suggBox) {
    suggBox = document.createElement('div');
    suggBox.className = 'bullet-suggest-box';
    const descField = card.querySelector('textarea');
    if (descField) descField.parentNode.insertBefore(suggBox, descField);
  }
  suggBox.innerHTML = `<div class="bsug-label">💡 AI Bullet Suggestions for <em>${jobTitle}</em> <span class="bsug-loading">generating…</span></div>`;

  try {
    const res  = await fetch('/api/bullet-suggestions', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ job_title: jobTitle, role })
    });
    const data = await res.json();
    const bullets = data.bullets || [];
    if (!bullets.length) { suggBox.innerHTML = ''; return; }

    suggBox.innerHTML = `<div class="bsug-label">💡 Click to add bullet for <em>${jobTitle}</em>:</div>
      ${bullets.map(b => `<div class="bsug-item" onclick="addBulletToExp(this, '${b.replace(/'/g,"\\'")}')">+ ${b}</div>`).join('')}`;
  } catch (e) {
    suggBox.innerHTML = '';
  }
}

function addBulletToExp(el, bullet) {
  const card    = el.closest('.exp-card') || el.closest('[id^="exp-"]');
  const textarea = card ? card.querySelector('textarea') : null;
  if (textarea) {
    textarea.value = textarea.value ? textarea.value.trimEnd() + '\n• ' + bullet : '• ' + bullet;
  }
  el.style.opacity = '0.4';
  el.style.pointerEvents = 'none';
  el.textContent = '✅ ' + el.textContent.slice(2);
}


// ══════════════════════════════════════════════════════════════════════════
// FEATURE 5: Resume Completeness Meter
// ══════════════════════════════════════════════════════════════════════════

function calcCompleteness() {
  const scores = {
    name:      !!document.getElementById('p-name')?.value.trim(),
    email:     !!document.getElementById('p-email')?.value.trim(),
    phone:     !!document.getElementById('p-phone')?.value.trim(),
    role:      !!document.getElementById('p-role')?.value.trim(),
    summary:   !!document.getElementById('p-summary')?.value.trim(),
    location:  !!document.getElementById('p-location')?.value.trim(),
    linkedin:  !!document.getElementById('p-linkedin')?.value.trim(),
    github:    !!document.getElementById('p-github')?.value.trim(),
    skills:    state.skills.length >= 4,
    experience: state.experiences.length >= 1,
    education:  state.educations.length >= 1,
    projects:   state.projects.length >= 1,
    certs:      state.certifications.length >= 1,
  };
  const weights = { name:10, email:10, phone:8, role:10, summary:12, location:5,
                    linkedin:5, github:5, skills:10, experience:12, education:8, projects:5, certs:5 };
  let total = 0, max = 0;
  for (const k in weights) { max += weights[k]; if (scores[k]) total += weights[k]; }
  return { pct: Math.round((total/max)*100), scores, weights };
}

function updateCompletenessMeter() {
  const meter = document.getElementById('completeness-meter');
  if (!meter) return;
  const { pct, scores, weights } = calcCompleteness();
  const color = pct >= 80 ? '#16a34a' : pct >= 55 ? '#d97706' : '#dc2626';
  const label = pct >= 80 ? '🟢 Strong' : pct >= 55 ? '🟡 Good' : '🔴 Needs work';

  // Build missing items list
  const missing = Object.entries(scores)
    .filter(([k,v]) => !v)
    .map(([k]) => ({
      name: { name:'Full Name', email:'Email', phone:'Phone', role:'Job Role',
              summary:'Professional Summary', location:'Location', linkedin:'LinkedIn URL',
              github:'GitHub URL', skills:'4+ Skills', experience:'Work Experience',
              education:'Education', projects:'Project', certs:'Certification' }[k] || k,
      pts: weights[k]
    }))
    .sort((a,b) => b.pts - a.pts)
    .slice(0, 3);

  meter.innerHTML = `
    <div class="cm-header">
      <span class="cm-title">📊 Resume Completeness</span>
      <span class="cm-label" style="color:${color}">${label} — ${pct}%</span>
    </div>
    <div class="cm-bar-bg"><div class="cm-bar-fill" style="width:${pct}%;background:${color}"></div></div>
    ${missing.length ? `<div class="cm-tips">Add: ${missing.map(m=>`<span class="cm-tip">+${m.pts}pts ${m.name}</span>`).join('')}</div>` : '<div class="cm-tips" style="color:#16a34a">✅ Resume is complete!</div>'}
  `;
}

// Hook completeness meter to all input events
document.addEventListener('input', () => updateCompletenessMeter());
document.addEventListener('DOMContentLoaded', () => {
  updateCompletenessMeter();
  // Hook bullet suggestions to experience title fields (delegated)
  document.addEventListener('input', e => {
    if (e.target.matches('.exp-title-input, [placeholder*="Job Title"], [placeholder*="job title"]')) {
      const card = e.target.closest('.exp-card, [id^="exp-card-"], .card');
      if (card) triggerBulletSuggestions(e.target, card);
    }
  });
});


// ══════════════════════════════════════════════════════════════════════════
// FEATURE 6: LinkedIn Import — drag-and-drop upgrade
// ══════════════════════════════════════════════════════════════════════════

function setupLinkedInDragDrop() {
  const zone = document.getElementById('linkedin-drop-zone');
  if (!zone) return;

  ['dragenter','dragover'].forEach(ev => zone.addEventListener(ev, e => {
    e.preventDefault(); zone.classList.add('drop-active');
  }));
  ['dragleave','drop'].forEach(ev => zone.addEventListener(ev, e => {
    e.preventDefault(); zone.classList.remove('drop-active');
  }));
  zone.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.pdf')) processLinkedInFile(file);
    else showToast('⚠️ Please drop a PDF file', 'error');
  });
}

async function processLinkedInFile(file) {
  const zone  = document.getElementById('linkedin-drop-zone');
  const orig  = zone ? zone.innerHTML : '';
  if (zone) zone.innerHTML = `<div style="text-align:center;padding:20px"><div style="font-size:28px">⏳</div><p style="margin-top:8px">Importing from LinkedIn PDF…</p></div>`;

  const fd = new FormData();
  fd.append('file', file);
  try {
    const res  = await fetch('/api/import-linkedin', { method: 'POST', body: fd });
    const data = await res.json();
    if (data.success && data.resume) {
      populateForm(data.resume);
      document.getElementById('linkedin-import-banner') && (document.getElementById('linkedin-import-banner').style.display = 'none');
      document.getElementById('linkedin-drop-zone') && (document.getElementById('linkedin-drop-zone').style.display = 'none');
      showToast('✅ LinkedIn profile imported!');
      updateCompletenessMeter();
    } else {
      showToast('⚠️ ' + (data.error || 'Import failed'), 'error');
      if (zone) zone.innerHTML = orig;
    }
  } catch (e) {
    showToast('❌ Import failed', 'error');
    if (zone) zone.innerHTML = orig;
  }
}

// Patch importLinkedIn (called by file input onchange) to use processLinkedInFile
function importLinkedIn(input) {
  const file = input.files[0];
  if (file) processLinkedInFile(file);
}

document.addEventListener('DOMContentLoaded', setupLinkedInDragDrop);


// ══════════════════════════════════════════════════════════════════════════
// FEATURE 7: Job Role Autocomplete — enhanced with AI tips on select
// ══════════════════════════════════════════════════════════════════════════

const POPULAR_ROLES = [
  "Software Engineer","Frontend Developer","Backend Developer","Full Stack Developer",
  "Senior Software Engineer","Data Scientist","Machine Learning Engineer","AI Engineer",
  "MLOps Engineer","DevOps Engineer","Cloud Engineer","Site Reliability Engineer",
  "Data Analyst","Data Engineer","Business Analyst","Product Manager",
  "Technical Product Manager","UI/UX Designer","Product Designer","Mobile Developer",
  "Android Developer","iOS Developer","React Native Developer","Cybersecurity Analyst",
  "Network Engineer","Database Administrator","Blockchain Developer","QA Engineer",
  "Embedded Systems Engineer","Systems Architect","Solutions Architect","Scrum Master",
  "Technical Lead","Engineering Manager","Java Developer","Python Developer",
  "Node.js Developer","React Developer","Angular Developer","Vue.js Developer"
];

function initRoleAutocomplete() {
  const input = document.getElementById('p-role');
  if (!input) return;

  let dropdown = document.getElementById('role-autocomplete-dropdown');
  if (!dropdown) {
    dropdown = document.createElement('div');
    dropdown.id = 'role-autocomplete-dropdown';
    dropdown.className = 'role-ac-dropdown';
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(dropdown);
  }

  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    if (q.length < 1) { dropdown.style.display = 'none'; return; }
    const matches = POPULAR_ROLES.filter(r => r.toLowerCase().includes(q)).slice(0, 7);
    if (!matches.length) { dropdown.style.display = 'none'; return; }
    dropdown.innerHTML = matches.map(r =>
      `<div class="role-ac-item" onmousedown="selectRole('${r}')">${r}</div>`
    ).join('');
    dropdown.style.display = 'block';
  });

  input.addEventListener('blur', () => setTimeout(() => dropdown.style.display = 'none', 150));
}

function selectRole(role) {
  const input = document.getElementById('p-role');
  if (input) { input.value = role; input.dispatchEvent(new Event('input')); }
  const dd = document.getElementById('role-autocomplete-dropdown');
  if (dd) dd.style.display = 'none';
  updateCompletenessMeter();
}

document.addEventListener('DOMContentLoaded', initRoleAutocomplete);

