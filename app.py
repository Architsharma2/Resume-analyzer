import streamlit as st
from utils.parser import extract_text
from utils.matcher import get_match_score, get_skill_gap
from utils.extractor import extract_basic_info
from utils.scorer import get_feedback, format_skills
from utils.resume_export import export_docx

st.set_page_config(
    page_title="AI Resume Studio",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# GLASS UI + MOBILE FRIENDLY
# =========================
st.markdown("""
<style>
  .stApp {
    background:
      radial-gradient(circle at 0% 0%, rgba(56,189,248,0.18), transparent 35%),
      radial-gradient(circle at 100% 0%, rgba(99,102,241,0.16), transparent 30%),
      linear-gradient(160deg, #0b1220 0%, #0f172a 50%, #020617 100%);
    color: #e5e7eb;
  }

  h1, h2, h3, h4 { color: #f8fafc !important; }

  .hero {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.14);
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 18px 18px;
    margin-bottom: 14px;
  }

  .glass-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.13);
    box-shadow: 0 8px 24px rgba(0,0,0,0.22);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 10px;
  }

  .skill-chip {
    display: inline-block;
    padding: 6px 12px;
    margin: 4px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
  }
  .chip-ok { background: rgba(34,197,94,0.16); color:#4ade80; border:1px solid rgba(34,197,94,0.35); }
  .chip-missing { background: rgba(239,68,68,0.16); color:#f87171; border:1px solid rgba(239,68,68,0.35); }
  .chip-extra { background: rgba(59,130,246,0.16); color:#60a5fa; border:1px solid rgba(59,130,246,0.35); }
  .chip-tip { background: rgba(250,204,21,0.14); color:#fde047; border:1px solid rgba(250,204,21,0.3); }

  /* Glass buttons */
  .stButton > button {
    background: rgba(255,255,255,0.08) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.2);
    transition: 0.2s ease;
  }
  .stButton > button:hover {
    background: rgba(56,189,248,0.18) !important;
    border-color: rgba(56,189,248,0.45) !important;
    transform: translateY(-1px);
  }

  div[data-testid="stSidebar"] {
    background: rgba(2,6,23,0.92);
    border-right: 1px solid rgba(255,255,255,0.08);
  }

  .hint {
    color: #93c5fd;
    font-size: 0.86rem;
    margin: 0 0 8px 0;
  }

  @media (max-width: 768px) {
    .hero { padding: 14px; border-radius: 14px; }
    .glass-card { padding: 12px; }
  }
</style>
""", unsafe_allow_html=True)

SAMPLE_JDS = {
    "AI Developer": "Required: Python, Machine Learning, NLP, Pandas, NumPy, REST API, Git, communication. Nice: TensorFlow, PyTorch, FastAPI, AWS.",
    "Full Stack Developer": "Required: Python, JavaScript, React, HTML, CSS, SQL, Git, Firebase, REST API, communication. Nice: Node.js, MongoDB, Docker.",
    "Web Developer": "Required: HTML, CSS, JavaScript, Firebase, Git, GitHub, communication. Nice: React, Python, UI design."
}

ROLE_SKILLS = {
    "AI Developer": "Python, Machine Learning, NLP, Pandas, NumPy, REST API, Git, Communication",
    "Full Stack Developer": "Python, JavaScript, React, HTML, CSS, SQL, Git, Firebase, REST API",
    "Web Developer": "HTML, CSS, JavaScript, Firebase, Git, GitHub, Communication"
}

def safe_skill_gap(resume_text, jd):
    result = get_skill_gap(resume_text, jd)
    if len(result) == 3:
        return result
    return result[0], result[1], []

def suggest_improvements(score, missing, basic_info, resume_text):
    tips = []

    if basic_info.get("email") in [None, "", "Not found"]:
        tips.append("Add a professional email at the top of your resume.")
    if basic_info.get("phone") in [None, "", "Not found"]:
        tips.append("Add your phone number near the header.")
    if missing:
        tips.append("Add these missing skills if you know them: " + ", ".join(missing[:5]) + ".")
        tips.append("Use the same skill words from the job description in Projects and Skills.")
    if score < 50:
        tips.append("Rewrite your objective for this exact job role.")
        tips.append("Add 2–3 project bullet points with tools and results.")
    elif score < 75:
        tips.append("Improve project lines with impact (what you built + tools used).")
        tips.append("Keep skills section clean and role-focused.")
    else:
        tips.append("Strong match. Keep formatting clean and consistent.")

    text_l = (resume_text or "").lower()
    if "project" not in text_l:
        tips.append("Add a Projects section with 2 strong projects.")
    if "experience" not in text_l and "intern" not in text_l:
        tips.append("If you have internship/freelance work, add an Experience section.")
    if len(resume_text or "") < 500:
        tips.append("Your resume looks short. Add more detail to projects and experience.")

    # unique tips
    final = []
    for t in tips:
        if t not in final:
            final.append(t)
    return final[:7]

with st.sidebar:
    st.markdown("### AI Resume Studio")
    st.caption("Simple for every student")
    page = st.radio(
        "Choose page",
        ["Home", "Analyze Resume", "Make Resume", "Improvement Tips", "About"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Quick help**")
    st.write("1. Make Resume")
    st.write("2. Download DOCX")
    st.write("3. Analyze Resume")

# ================= HOME =================
if page == "Home":
    st.markdown("""
    <div class="hero">
      <h1>AI Resume Studio</h1>
      <p>Easy tools for school, college, and final-year students. Build a clean resume, check job match, and get improvement tips.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='glass-card'><h3>Analyze</h3><p>Upload resume + job description and get score, matched skills, missing skills.</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='glass-card'><h3>Make Resume</h3><p>Fill simple form and download a clean professional DOCX resume.</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='glass-card'><h3>Improve</h3><p>Get clear suggestions to make your resume stronger for the job.</p></div>", unsafe_allow_html=True)

    st.markdown("### Start here")
    s1, s2, s3 = st.columns(3)
    if s1.button("Go to Analyze", use_container_width=True):
        st.session_state["force_page"] = "Analyze Resume"
        st.rerun()
    if s2.button("Go to Make Resume", use_container_width=True):
        st.session_state["force_page"] = "Make Resume"
        st.rerun()
    if s3.button("Go to Tips", use_container_width=True):
        st.session_state["force_page"] = "Improvement Tips"
        st.rerun()

# ================= ANALYZE =================
elif page == "Analyze Resume":
    st.markdown("""
    <div class="hero">
      <h1>Analyze Resume</h1>
      <p>Upload your resume and paste a job description. Get match score and skill gaps in one click.</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        uploaded = st.file_uploader("Step 1: Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
        jd_choice = st.selectbox("Step 2: Load sample job (optional)", ["Custom"] + list(SAMPLE_JDS.keys()))
        if jd_choice != "Custom":
            st.session_state["jd"] = SAMPLE_JDS[jd_choice]
        jd = st.text_area("Step 3: Job Description", value=st.session_state.get("jd", SAMPLE_JDS["Web Developer"]), height=150)
        st.session_state["jd"] = jd
        b1, b2, b3 = st.columns(3)
        analyze = b1.button("Analyze Now", use_container_width=True, type="primary")
        clear = b2.button("Clear Result", use_container_width=True)
        show = b3.button("Show Resume Text", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='glass-card'><h4>Result</h4>", unsafe_allow_html=True)
        if st.session_state.get("done"):
            st.metric("Match Score", f"{st.session_state['score']}%")
            st.progress(min(st.session_state["score"] / 100, 1.0))
            st.caption(st.session_state["feedback"]["level"])
        else:
            st.info("Your result will appear here.")
        st.markdown("</div>", unsafe_allow_html=True)

    if clear:
        for k in ["done", "text", "score", "matched", "missing", "extra", "info", "feedback", "tips"]:
            st.session_state.pop(k, None)
        st.rerun()

    if analyze:
        if not uploaded:
            st.warning("Please upload a resume first.")
        elif not jd.strip():
            st.warning("Please paste a job description.")
        else:
            with st.spinner("Analyzing your resume..."):
                text = extract_text(uploaded)
                score = get_match_score(text, jd)
                matched, missing, extra = safe_skill_gap(text, jd)
                info = extract_basic_info(text)
                feedback = get_feedback(score, missing)
                tips = suggest_improvements(score, missing, info, text)
                st.session_state.update(
                    done=True, text=text, score=score, matched=matched, missing=missing,
                    extra=extra, info=info, feedback=feedback, tips=tips
                )
            st.success("Analysis complete")
            st.rerun()

    if st.session_state.get("done"):
        info = st.session_state["info"]
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='glass-card'><b>Name</b><br>{info.get('name','Not found')}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='glass-card'><b>Email</b><br>{info.get('email','Not found')}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='glass-card'><b>Phone</b><br>{info.get('phone','Not found')}</div>", unsafe_allow_html=True)

        st.markdown("### Skills")
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown("**Matched**")
            st.markdown("".join([f"<span class='skill-chip chip-ok'>{s}</span>" for s in st.session_state["matched"]]) or "None", unsafe_allow_html=True)
        with s2:
            st.markdown("**Missing**")
            st.markdown("".join([f"<span class='skill-chip chip-missing'>{s}</span>" for s in st.session_state["missing"]]) or "None", unsafe_allow_html=True)
        with s3:
            st.markdown("**Extra**")
            st.markdown("".join([f"<span class='skill-chip chip-extra'>{s}</span>" for s in st.session_state["extra"]]) or "None", unsafe_allow_html=True)

        st.markdown("### Feedback")
        st.write(st.session_state["feedback"]["message"])

        st.markdown("### Suggested Improvements")
        for tip in st.session_state.get("tips", []):
            st.markdown(f"<span class='skill-chip chip-tip'>{tip}</span>", unsafe_allow_html=True)

        report = f"""Resume Analysis Report
Score: {st.session_state['score']}%
Name: {info.get('name')}
Email: {info.get('email')}
Phone: {info.get('phone')}
Matched: {format_skills(st.session_state['matched'])}
Missing: {format_skills(st.session_state['missing'])}
Tips: {' | '.join(st.session_state.get('tips', []))}
"""
        st.download_button("Download Analysis Report", report, "analysis_report.txt", "text/plain", use_container_width=True)

        if show:
            st.text_area("Extracted Resume Text", st.session_state["text"], height=240)

# ================= MAKE RESUME =================
elif page == "Make Resume":
    st.markdown("""
    <div class="hero">
      <h1>Make Resume</h1>
      <p>Fill simple boxes. Generate a clean professional DOCX resume.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("#### 1) Basic Info")
    a1, a2, a3 = st.columns(3)
    name = a1.text_input("Full Name", "Archit Sharma")
    email = a2.text_input("Email", "archits243@gmail.com")
    phone = a3.text_input("Phone", "+91 78478 07169")
    b1, b2, b3 = st.columns(3)
    location = b1.text_input("Location", "Kharagpur, WB")
    headline = b2.text_input("Headline", "BCA (Honours) Student · Web Developer")
    role = b3.selectbox("Target Role", list(ROLE_SKILLS.keys()))

    st.markdown("#### 2) Links")
    c1, c2, c3 = st.columns(3)
    linkedin = c1.text_input("LinkedIn", "LinkedIn")
    github = c2.text_input("GitHub", "GitHub")
    portfolio = c3.text_input("Portfolio", "")

    st.markdown("#### 3) Objective & Skills")
    summary = st.text_area("Objective", "Motivated student with project and internship experience, seeking a fresher role to learn and contribute.", height=80)
    if st.button("Auto-fill skills for role", use_container_width=True):
        st.session_state["skills_auto"] = ROLE_SKILLS[role]
        st.rerun()
    skills = st.text_input("Technical Skills", st.session_state.get("skills_auto", ROLE_SKILLS[role]))
    tools = st.text_input("Tools", "VS Code, GitHub, MS Office")
    soft_skills = st.text_input("Soft Skills", "Communication, Teamwork, Time Management")
    languages = st.text_input("Languages", "English, Hindi")

    st.markdown("#### 4) Experience / Projects / Education")
    st.markdown('<div class="hint">Use format: Title | Company/Type | Dates | point1; point2</div>', unsafe_allow_html=True)
    experience = st.text_area("Experience", "Web Development Intern | Company Name | 2025 | Built website using HTML & CSS.; Worked with team and fixed UI issues.", height=90)
    projects = st.text_area("Projects", "AI Resume Studio | Personal Project | 2026 | Built resume analyzer using Python and Streamlit.; Added skill gap and DOCX export.", height=90)
    education = st.text_area("Education", "BCA (Honours) | Your College | 2023-2026 | Relevant: DSA, OOP, Web Technologies", height=80)
    achievements = st.text_area("Achievements", "Hackathon Medal\nInternship Certificate", height=70)
    availability = st.text_input("Availability", "Immediate — internship / full-time / remote")
    interests = st.text_input("Interests", "Web projects, AI tools, design")
    references = st.text_input("References", "Available on request")
    st.markdown("</div>", unsafe_allow_html=True)

    g1, g2, g3 = st.columns(3)
    gen = g1.button("Generate Resume", use_container_width=True, type="primary")
    match = g2.button("Check Role Skills", use_container_width=True)
    reset = g3.button("Reset Form", use_container_width=True)

    if reset:
        st.session_state.pop("generated_data", None)
        st.session_state.pop("skills_auto", None)
        st.rerun()

    data = {
        "name": name, "email": email, "phone": phone, "location": location,
        "headline": headline, "role": role, "linkedin": linkedin, "github": github,
        "portfolio": portfolio, "summary": summary, "skills": skills, "tools": tools,
        "soft_skills": soft_skills, "languages": languages, "experience": experience,
        "projects": projects, "education": education, "achievements": achievements,
        "availability": availability, "interests": interests, "references": references
    }

    if gen:
        st.session_state["generated_data"] = data
        st.success("Resume generated")

    if match:
        user = [s.strip().lower() for s in skills.split(",") if s.strip()]
        need = [s.strip().lower() for s in ROLE_SKILLS[role].split(",") if s.strip()]
        matched = sorted(set(user) & set(need))
        missing = sorted(set(need) - set(user))
        coverage = round(len(matched) / len(need) * 100, 1) if need else 0
        st.metric("Role Skill Coverage", f"{coverage}%")
        st.progress(min(coverage/100, 1.0))
        st.markdown("".join([f"<span class='skill-chip chip-ok'>{s.title()}</span>" for s in matched]) or "No matched skills", unsafe_allow_html=True)
        st.markdown("".join([f"<span class='skill-chip chip-missing'>{s.title()}</span>" for s in missing]) or "No missing skills", unsafe_allow_html=True)

    if st.session_state.get("generated_data"):
        st.download_button(
            "Download DOCX Resume",
            data=export_docx(st.session_state["generated_data"]),
            file_name=f"{name.replace(' ', '_').lower()}_resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            type="primary"
        )

# ================= TIPS =================
elif page == "Improvement Tips":
    st.markdown("""
    <div class="hero">
      <h1>Improvement Tips</h1>
      <p>Simple advice for students of all ages. First analyze a resume, then open this page.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("done"):
        st.info("Go to Analyze Resume first. After analysis, tips will appear here automatically.")
        st.markdown("""
        <div class="glass-card">
        <b>General tips</b><br>
        1. Keep resume to 1 page if possible.<br>
        2. Use clear section headings.<br>
        3. Add phone, email, LinkedIn.<br>
        4. Write project points with tools used.<br>
        5. Match skills with the job description.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.metric("Your Match Score", f"{st.session_state['score']}%")
        st.markdown("### Personalized suggestions")
        for tip in st.session_state.get("tips", []):
            st.markdown(f"<div class='glass-card'>{tip}</div>", unsafe_allow_html=True)

        st.markdown("### Missing skills to consider")
        st.markdown("".join([f"<span class='skill-chip chip-missing'>{s}</span>" for s in st.session_state.get("missing", [])]) or "None", unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="hero">
      <h1>About</h1>
      <p>AI Resume Studio helps students create and improve resumes easily.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card">
    <b>Features</b><br>
    - Resume analysis and skill gap<br>
    - Clean DOCX resume builder<br>
    - Improvement suggestions<br>
    - Mobile + desktop friendly glass UI
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("AI Resume Studio | BCA Final Year Project | Easy for every student")