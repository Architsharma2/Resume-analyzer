import streamlit as st
from utils.parser import extract_text
from utils.matcher import get_match_score, get_skill_gap
from utils.extractor import extract_basic_info
from utils.scorer import get_feedback, format_skills
from utils.resume_export import build_resume_text, export_docx, export_pdf

st.set_page_config(page_title="AI Resume Studio", page_icon="📄", layout="wide")

# ========== UI CSS ==========
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(160deg, #0b1220 0%, #111827 45%, #0f172a 100%);
        color: #e5e7eb;
    }
    h1,h2,h3,h4 { color: #f9fafb !important; }
    .hero {
        background: linear-gradient(135deg, rgba(59,130,246,0.18), rgba(16,185,129,0.12));
        border: 1px solid rgba(148,163,184,0.25);
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }
    .card {
        background: rgba(17,24,39,0.92);
        border: 1px solid rgba(55,65,81,0.95);
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .skill-chip {
        display:inline-block; padding:6px 12px; margin:4px; border-radius:999px;
        font-size:13px; font-weight:600;
    }
    .chip-ok { background:rgba(34,197,94,0.15); color:#4ade80; border:1px solid rgba(34,197,94,0.35); }
    .chip-missing { background:rgba(239,68,68,0.15); color:#f87171; border:1px solid rgba(239,68,68,0.35); }
    .chip-extra { background:rgba(59,130,246,0.15); color:#60a5fa; border:1px solid rgba(59,130,246,0.35); }
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: 1px solid rgba(148,163,184,0.25) !important;
        padding: 0.55rem 1rem !important;
    }
    div[data-testid="stSidebar"] {
        background: #0b1220;
        border-right: 1px solid rgba(55,65,81,0.8);
    }
</style>
""", unsafe_allow_html=True)

SAMPLE_JDS = {
    "AI Developer": """Hiring AI Developer Intern.
Required: Python, Machine Learning, NLP, Data Analysis, Pandas, NumPy, REST API, Git, communication.
Nice to have: TensorFlow, PyTorch, Deep Learning, FastAPI, AWS, Docker.""",
    "Full Stack Developer": """Hiring Full Stack Developer Intern.
Required: Python, JavaScript, React, HTML, CSS, SQL, Git, Firebase, REST API, communication.
Nice to have: Node.js, MongoDB, Docker, AWS.""",
    "Data Analyst": """Hiring Data Analyst Intern.
Required: Excel, SQL, Python, Pandas, Data Analysis, Power BI, communication.
Nice to have: Tableau, Machine Learning, statistics."""
}

ROLE_SKILLS = {
    "AI Developer": "Python, Machine Learning, Deep Learning, NLP, Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, REST API, Git, Data Analysis, Communication, Problem Solving",
    "Full Stack Developer": "Python, JavaScript, React, HTML, CSS, SQL, Git, Firebase, REST API, Node.js, MongoDB, Communication, Problem Solving",
    "Data Analyst": "Excel, SQL, Python, Pandas, Data Analysis, Power BI, Tableau, Communication, Problem Solving, Statistics",
    "Software Developer": "Python, Java, DSA, OOP, SQL, Git, REST API, Problem Solving, Communication, Linux"
}

def safe_skill_gap(resume_text, jd):
    result = get_skill_gap(resume_text, jd)
    if len(result) == 3:
        return result
    matched, missing = result
    return matched, missing, []

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("### AI Resume Studio")
    st.caption("BCA Final Year Project")
    page = st.radio("Navigation", ["Analyze Resume", "Make Resume", "About"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**Tips**")
    st.write("1. Make Resume → choose role")
    st.write("2. Download PDF/DOCX")
    st.write("3. Analyze against JD")

# ========== ANALYZE PAGE ==========
if page == "Analyze Resume":
    st.markdown('<div class="hero"><h1>Analyze Resume</h1><p>Upload resume and match it with a job description.</p></div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.1, 1])
    with c1:
        uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
        jd_choice = st.selectbox("Load sample JD", ["Custom"] + list(SAMPLE_JDS.keys()))
        if jd_choice != "Custom":
            st.session_state["job_description"] = SAMPLE_JDS[jd_choice]
        job_description = st.text_area("Job Description", value=st.session_state.get("job_description", SAMPLE_JDS["AI Developer"]), height=170)
        st.session_state["job_description"] = job_description

        b1, b2, b3 = st.columns(3)
        analyze_btn = b1.button("Analyze", use_container_width=True, type="primary")
        clear_btn = b2.button("Clear", use_container_width=True)
        show_btn = b3.button("Show Text", use_container_width=True)

    with c2:
        st.markdown("#### Live Status")
        if st.session_state.get("analysis_done"):
            st.metric("Match Score", f"{st.session_state['score']}%")
            st.progress(min(st.session_state["score"] / 100, 1.0))
            st.success("Analysis ready")
        else:
            st.info("Waiting for analysis...")

    if clear_btn:
        for k in ["analysis_done", "resume_text", "score", "matched", "missing", "extra", "basic_info", "feedback"]:
            st.session_state.pop(k, None)
        st.rerun()

    if analyze_btn:
        if not uploaded_file:
            st.warning("Upload a resume first.")
        elif not job_description.strip():
            st.warning("Paste a job description.")
        else:
            with st.spinner("Analyzing..."):
                resume_text = extract_text(uploaded_file)
                score = get_match_score(resume_text, job_description)
                matched, missing, extra = safe_skill_gap(resume_text, job_description)
                basic_info = extract_basic_info(resume_text)
                feedback = get_feedback(score, missing)
                st.session_state.update({
                    "analysis_done": True,
                    "resume_text": resume_text,
                    "score": score,
                    "matched": matched,
                    "missing": missing,
                    "extra": extra,
                    "basic_info": basic_info,
                    "feedback": feedback
                })
            st.rerun()

    if st.session_state.get("analysis_done"):
        info = st.session_state["basic_info"]
        matched = st.session_state["matched"]
        missing = st.session_state["missing"]
        extra = st.session_state["extra"]
        feedback = st.session_state["feedback"]
        score = st.session_state["score"]

        st.markdown("### Candidate Profile")
        x1, x2, x3 = st.columns(3)
        x1.markdown(f"<div class='card'><b>Name</b><br>{info.get('name','Not found')}</div>", unsafe_allow_html=True)
        x2.markdown(f"<div class='card'><b>Email</b><br>{info.get('email','Not found')}</div>", unsafe_allow_html=True)
        x3.markdown(f"<div class='card'><b>Phone</b><br>{info.get('phone','Not found')}</div>", unsafe_allow_html=True)

        st.markdown("### Skills Intelligence")
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown("**Matched**")
            st.markdown("".join([f"<span class='skill-chip chip-ok'>{s}</span>" for s in matched]) or "None", unsafe_allow_html=True)
        with s2:
            st.markdown("**Missing**")
            st.markdown("".join([f"<span class='skill-chip chip-missing'>{s}</span>" for s in missing]) or "None", unsafe_allow_html=True)
        with s3:
            st.markdown("**Extra**")
            st.markdown("".join([f"<span class='skill-chip chip-extra'>{s}</span>" for s in extra]) or "None", unsafe_allow_html=True)

        if score >= 75:
            st.success(feedback["message"])
        elif score >= 50:
            st.warning(feedback["message"])
        else:
            st.error(feedback["message"])

        report = f"""AI Resume Analyzer Report
Name: {info.get('name')}
Email: {info.get('email')}
Phone: {info.get('phone')}
Score: {score}%
Matched: {format_skills(matched)}
Missing: {format_skills(missing)}
Feedback: {feedback['message']}
"""
        st.download_button("Download Analysis Report", report, "analysis_report.txt", "text/plain", use_container_width=True)

        if show_btn:
            st.text_area("Extracted Resume Text", st.session_state["resume_text"], height=260)

# ========== MAKE RESUME PAGE ==========
elif page == "Make Resume":
    st.markdown('<div class="hero"><h1>Make Resume</h1><p>Fill details, target a role, generate and download PDF or DOCX.</p></div>', unsafe_allow_html=True)

    st.markdown("### 1) Profile")
    c1, c2, c3 = st.columns(3)
    name = c1.text_input("Full Name", "Archit Sharma")
    email = c2.text_input("Email", "archit@example.com")
    phone = c3.text_input("Phone", "+91 9876543210")

    c4, c5, c6 = st.columns(3)
    location = c4.text_input("Location", "Kharagpur, India")
    role = c5.selectbox("Target Role", list(ROLE_SKILLS.keys()))
    links = c6.text_input("LinkedIn / GitHub", "linkedin.com/in/yourid")

    st.markdown("### 2) Skills & Content")
    if st.button("Auto-fill skills for selected role"):
        st.session_state["make_skills"] = ROLE_SKILLS[role]
        st.rerun()

    skills = st.text_area("Technical Skills (comma separated)", value=st.session_state.get("make_skills", ROLE_SKILLS[role]), height=70)
    soft_skills = st.text_area("Soft Skills (comma separated)", "Communication, Problem Solving, Teamwork, Leadership", height=60)

    d1, d2 = st.columns(2)
    with d1:
        projects = st.text_area("Projects (one per line)", "AI Resume Analyzer using Python & Streamlit\nStudent Learning Platform with Firebase", height=110)
        experience = st.text_area("Experience (one per line)", "Fresher | Built academic and personal projects", height=90)
    with d2:
        education = st.text_area("Education", "BCA (Honours) | Your College | 2023-2026", height=90)
        certifications = st.text_area("Certifications (one per line)", "Google Data Analytics (optional)\nPython for Everybody (optional)", height=90)

    achievements = st.text_area("Achievements (one per line)", "Ranked top in class\nBuilt and deployed personal projects", height=70)
    languages = st.text_input("Languages", "English, Hindi")
    summary = st.text_area("Professional Summary (optional)", "", placeholder="Leave blank to auto-generate", height=70)

    st.markdown("### 3) Actions")
    a1, a2, a3, a4 = st.columns(4)
    generate_btn = a1.button("Generate Resume", use_container_width=True, type="primary")
    match_btn = a2.button("Skill Match", use_container_width=True)
    preview_btn = a3.button("Preview Text", use_container_width=True)
    clear_btn = a4.button("Reset Form", use_container_width=True)

    if clear_btn:
        for k in ["make_skills", "generated_data", "generated_text"]:
            st.session_state.pop(k, None)
        st.rerun()

    data = {
        "name": name, "email": email, "phone": phone, "location": location,
        "role": role, "links": links, "skills": skills, "soft_skills": soft_skills,
        "projects": projects, "experience": experience, "education": education,
        "certifications": certifications, "achievements": achievements,
        "languages": languages, "summary": summary
    }

    if generate_btn:
        st.session_state["generated_data"] = data
        st.session_state["generated_text"] = build_resume_text(data)
        st.success("Resume generated successfully")

    if match_btn:
        user_skills = [s.strip().lower() for s in skills.split(",") if s.strip()]
        role_required = [s.strip().lower() for s in ROLE_SKILLS[role].split(",") if s.strip()]
        matched = sorted(set(user_skills) & set(role_required))
        missing = sorted(set(role_required) - set(user_skills))
        coverage = round((len(matched) / len(role_required)) * 100, 1) if role_required else 0

        st.markdown("### Role Skill Match")
        st.metric("Coverage", f"{coverage}%")
        st.progress(min(coverage / 100, 1.0))
        m1, m2 = st.columns(2)
        with m1:
            st.markdown("**Matched**")
            st.markdown("".join([f"<span class='skill-chip chip-ok'>{s.title()}</span>" for s in matched]) or "None", unsafe_allow_html=True)
        with m2:
            st.markdown("**Missing for role**")
            st.markdown("".join([f"<span class='skill-chip chip-missing'>{s.title()}</span>" for s in missing]) or "None", unsafe_allow_html=True)

    if st.session_state.get("generated_data"):
        gdata = st.session_state["generated_data"]
        st.markdown("### Download Resume")
        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                "Download DOCX",
                data=export_docx(gdata),
                file_name=f"{name.replace(' ', '_').lower()}_resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        with d2:
            st.download_button(
                "Download PDF",
                data=export_pdf(gdata),
                file_name=f"{name.replace(' ', '_').lower()}_resume.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        if preview_btn or True:
            with st.expander("Preview Resume Text", expanded=False):
                st.text(st.session_state.get("generated_text", build_resume_text(gdata)))

# ========== ABOUT ==========
else:
    st.markdown('<div class="hero"><h1>About</h1><p>AI Resume Studio for BCA final year submission and viva demo.</p></div>', unsafe_allow_html=True)
    st.markdown("""
    ### Features
    - Resume analysis with semantic matching
    - Skill gap detection
    - Role-based resume generator
    - PDF and DOCX export
    - Sample JDs and role skill packs

    ### Tech
    Python, Streamlit, sentence-transformers, spaCy, pdfplumber, python-docx, fpdf2
    """)

st.markdown("---")
st.caption("AI Resume Studio | Final Year BCA Honors Project")