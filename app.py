import streamlit as st
from utils.parser import extract_text
from utils.matcher import get_match_score, get_skill_gap
from utils.extractor import extract_basic_info
from utils.scorer import get_feedback, format_skills
from utils.resume_export import export_docx

st.set_page_config(page_title="AI Resume Studio", page_icon="📄", layout="wide")

st.markdown("""
<style>
.stApp {
  background:
    radial-gradient(circle at 8% 0%, rgba(59,130,246,.28), transparent 32%),
    radial-gradient(circle at 95% 0%, rgba(168,85,247,.18), transparent 28%),
    linear-gradient(160deg,#07111f,#0b1730 50%,#020617);
  color:#eaf0ff;
}
h1,h2,h3 { color:#f8fbff !important; }
.hero {
  background: linear-gradient(135deg, rgba(59,130,246,.22), rgba(99,102,241,.12));
  border:1px solid rgba(147,197,253,.28);
  border-radius:18px; padding:18px 20px; margin-bottom:14px;
  backdrop-filter: blur(14px);
}
.glass {
  background: rgba(255,255,255,.07);
  border:1px solid rgba(255,255,255,.14);
  border-radius:16px; padding:14px 16px; margin-bottom:10px;
  backdrop-filter: blur(12px);
}
.skill-chip {display:inline-block;padding:6px 12px;margin:4px;border-radius:999px;font-size:13px;font-weight:700;}
.chip-ok {background:rgba(34,197,94,.16);color:#4ade80;border:1px solid rgba(34,197,94,.35);}
.chip-missing {background:rgba(239,68,68,.16);color:#f87171;border:1px solid rgba(239,68,68,.35);}
.chip-extra {background:rgba(59,130,246,.16);color:#60a5fa;border:1px solid rgba(59,130,246,.35);}
.chip-tip {background:rgba(250,204,21,.14);color:#fde68a;border:1px solid rgba(250,204,21,.28);}
.stButton > button {
  background: linear-gradient(135deg,#2563eb,#3b82f6)!important;
  color:#fff!important; border:1px solid rgba(147,197,253,.45)!important;
  border-radius:14px!important; font-weight:800!important;
  box-shadow:0 8px 22px rgba(37,99,235,.35);
}
div[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#0a1628,#07101d);
  border-right:1px solid rgba(59,130,246,.25);
}
.hint {color:#93c5fd;font-size:.86rem;margin-bottom:8px;}
.friendly {
  background: rgba(16,185,129,.12);
  border:1px solid rgba(52,211,153,.25);
  border-radius:14px; padding:12px 14px; margin-bottom:12px;
}
</style>
""", unsafe_allow_html=True)

SAMPLE_JDS = {
    "AI Developer": "Required: Python, Machine Learning, NLP, Pandas, NumPy, REST API, Git, communication. Nice: TensorFlow, PyTorch, FastAPI, AWS.",
    "Full Stack Developer": "Required: Python, JavaScript, React, HTML, CSS, SQL, Git, Firebase, REST API, communication.",
    "Web Developer": "Required: HTML, CSS, JavaScript, Firebase, Git, GitHub, communication. Nice: React, Python.",
    "Data Analyst": "Required: Excel, SQL, Python, Pandas, Data Analysis, Power BI, communication."
}

ROLE_PACKS = {
    "AI Developer": {
        "headline": "Student · AI / ML Enthusiast",
        "skills": "Python, Machine Learning, NLP, Pandas, NumPy, REST API, Git, Data Analysis",
        "tools": "VS Code, Jupyter, GitHub, Google Colab",
        "soft": "Communication, Problem Solving, Teamwork, Willingness to Learn",
        "summary": "Motivated student exploring AI and practical Python projects. Eager to learn, build, and contribute in an internship or fresher AI role.",
        "projects": "AI Resume Studio | Personal Project | 2026 | Built resume analyzer using Python and Streamlit.; Added skill-gap analysis and DOCX export."
    },
    "Full Stack Developer": {
        "headline": "Student · Full Stack Developer Aspirant",
        "skills": "Python, JavaScript, React, HTML, CSS, SQL, Git, Firebase, REST API",
        "tools": "VS Code, GitHub, Postman, Firebase",
        "soft": "Communication, Problem Solving, Teamwork, Time Management",
        "summary": "Student building web apps with frontend and backend tools. Looking for full-stack internship opportunities to grow through real work.",
        "projects": "College Portal | Academic Project | 2025 | Built login and dashboard features.; Used Firebase and responsive UI."
    },
    "Web Developer": {
        "headline": "Student · Web Developer",
        "skills": "HTML5, CSS3, JavaScript, Firebase, Git, GitHub",
        "tools": "VS Code, MS Office, Firebase Console",
        "soft": "Communication, Team Collaboration, Time Management",
        "summary": "Web development student with hands-on practice in HTML, CSS and JavaScript. Focused on clean UI and practical project building.",
        "projects": "Personal Portfolio | Personal Project | 2026 | Created responsive portfolio website.; Added project showcase and contact section."
    },
    "Data Analyst": {
        "headline": "Student · Data Analyst Aspirant",
        "skills": "Excel, SQL, Python, Pandas, Data Analysis, Power BI, Communication",
        "tools": "Excel, Power BI, Google Sheets",
        "soft": "Communication, Attention to Detail, Problem Solving",
        "summary": "Student interested in data analysis using Excel, SQL and Python. Seeking internship opportunities to practice dashboards and insights.",
        "projects": "Sales Insights Dashboard | Academic Project | 2025 | Cleaned sample data and built basic dashboard.; Practiced charts and KPI summary."
    },
    "General Fresher": {
        "headline": "Student · Fresher",
        "skills": "MS Office, Communication, Internet Research, Basic Computer Skills",
        "tools": "MS Word, MS Excel, PowerPoint, Google Workspace",
        "soft": "Communication, Teamwork, Time Management, Willingness to Learn",
        "summary": "Dedicated student and fresher ready to learn quickly, work hard, and contribute to team goals in an entry-level role.",
        "projects": "Academic Assignments & Presentations | College Work | 2024-2026 | Completed coursework projects and presentations.; Practiced teamwork and deadlines."
    }
}


def safe_skill_gap(resume_text, jd):
    result = get_skill_gap(resume_text, jd)
    return result if len(result) == 3 else (result[0], result[1], [])


def suggest_improvements(score, missing, basic_info, resume_text):
    tips = []
    if basic_info.get("email") in ["", "Not found", None]:
        tips.append("Add a clear email at the top.")
    if basic_info.get("phone") in ["", "Not found", None]:
        tips.append("Add your phone number.")
    if missing:
        tips.append("If you know these, add them: " + ", ".join(missing[:5]) + ".")
    if score < 55:
        tips.append("Rewrite objective for this exact job.")
        tips.append("Add 2 project points with tools you used.")
    else:
        tips.append("Good start. Keep skills matched to the JD.")
    if len(resume_text or "") < 450:
        tips.append("Add a bit more detail in projects/education.")
    out = []
    for t in tips:
        if t not in out:
            out.append(t)
    return out[:7]


def detect_role_from_text(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["machine learning", "ai developer", "nlp", "deep learning", "data scientist"]):
        return "AI Developer"
    if any(k in t for k in ["full stack", "fullstack", "react", "node.js", "frontend", "backend"]):
        return "Full Stack Developer"
    if any(k in t for k in ["data analyst", "power bi", "excel", "sql analyst"]):
        return "Data Analyst"
    if any(k in t for k in ["web developer", "html", "css", "javascript", "website"]):
        return "Web Developer"
    return "General Fresher"


def auto_from_job(job_text, name, email, phone, location, style):
    role = detect_role_from_text(job_text)
    pack = ROLE_PACKS[role]
    base_skills = [s.strip() for s in pack["skills"].split(",")]
    job_l = job_text.lower()
    extra = []
    for skill in ["python", "java", "javascript", "react", "html", "css", "sql", "excel",
                  "firebase", "git", "docker", "aws", "pandas", "machine learning", "communication"]:
        if skill in job_l and skill not in ",".join(base_skills).lower():
            extra.append("SQL" if skill == "sql" else skill.title())
    skills = ", ".join(base_skills + extra[:6])
    return {
        "name": name, "email": email, "phone": phone, "location": location,
        "headline": pack["headline"], "role": role, "style": style,
        "linkedin": "LinkedIn", "github": "GitHub", "portfolio": "",
        "summary": pack["summary"] + " This resume is tailored toward the provided job description.",
        "skills": skills, "tools": pack["tools"], "soft_skills": pack["soft"],
        "languages": "English, Hindi",
        "experience": "Student / Fresher | Academic & Personal Work | Present | Focused on learning by building practical projects.; Ready for internship responsibilities.",
        "projects": pack["projects"],
        "education": "Your Degree | Your College / School | Year | Add your stream and key subjects",
        "achievements": "Academic coursework completed\nCertificates (add if any)\nProjects completed",
        "availability": "Immediate — internship / full-time / part-time / remote",
        "interests": "Learning, projects, teamwork",
        "references": "Available on request"
    }


with st.sidebar:
    st.markdown("### AI Resume Studio")
    st.caption("For every student — school, college, fresher")
    page = st.radio("Navigation", ["Analyze Resume", "Make Resume", "About"], index=0, label_visibility="collapsed")
    st.markdown("---")
    st.write("No fancy background needed. Clear details + honest projects are enough.")


if page == "Analyze Resume":
    st.markdown('<div class="hero"><h1>Resume Analyzer</h1><p>Upload resume + job description. Get score, skills and simple improvement tips.</p></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Analyze", "Improvements", "Extracted Text"])

    with tab1:
        left, right = st.columns([1.2, 1])
        with left:
            st.markdown("<div class='glass'>", unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
            jd_choice = st.selectbox("Sample JD", ["Custom"] + list(SAMPLE_JDS.keys()))
            if jd_choice != "Custom":
                st.session_state["jd"] = SAMPLE_JDS[jd_choice]
            jd = st.text_area("Job Description", value=st.session_state.get("jd", SAMPLE_JDS["Web Developer"]), height=150)
            st.session_state["jd"] = jd
            b1, b2 = st.columns(2)
            analyze = b1.button("Analyze Now", use_container_width=True)
            clear = b2.button("Clear", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown("<div class='glass'><h4>Result</h4>", unsafe_allow_html=True)
            if st.session_state.get("done"):
                st.metric("Match Score", f"{st.session_state['score']}%")
                st.progress(min(st.session_state["score"] / 100, 1.0))
            else:
                st.info("Result will appear here.")
            st.markdown("</div>", unsafe_allow_html=True)

        if clear:
            for k in ["done", "text", "score", "matched", "missing", "extra", "info", "feedback", "tips"]:
                st.session_state.pop(k, None)
            st.rerun()

        if analyze:
            if not uploaded:
                st.warning("Please upload a resume.")
            elif not jd.strip():
                st.warning("Please paste a job description.")
            else:
                with st.spinner("Analyzing..."):
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
                st.rerun()

        if st.session_state.get("done"):
            info = st.session_state["info"]
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<div class='glass'><b>Name</b><br>{info.get('name')}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='glass'><b>Email</b><br>{info.get('email')}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='glass'><b>Phone</b><br>{info.get('phone')}</div>", unsafe_allow_html=True)
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
            st.write(st.session_state["feedback"]["message"])

    with tab2:
        if not st.session_state.get("done"):
            st.info("Analyze first to get personalized tips.")
        else:
            for tip in st.session_state.get("tips", []):
                st.markdown(f"<div class='glass'><span class='skill-chip chip-tip'>Tip</span> {tip}</div>", unsafe_allow_html=True)

    with tab3:
        if st.session_state.get("text"):
            st.text_area("Extracted Text", st.session_state["text"], height=300)
        else:
            st.info("No text yet.")

elif page == "Make Resume":
    st.markdown('<div class="hero"><h1>Make Resume</h1><p>Built for every student — not only top colleges. Honest skills + clear projects are enough.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="friendly"><b>You belong here.</b> School student, college student, fresher, career switcher — use Auto mode or fill manually.</div>', unsafe_allow_html=True)

    mode = st.radio("Choose mode", ["Auto from Job / Request", "Fill Manually"], horizontal=True)

    st.markdown("#### Common details")
    d1, d2, d3, d4 = st.columns(4)
    name = d1.text_input("Your Name", "Your Name")
    email = d2.text_input("Email", "you@email.com")
    phone = d3.text_input("Phone", "+91 9000000000")
    location = d4.text_input("Location", "Your City")

    style = st.selectbox(
        "Resume Format",
        ["modern", "minimal", "classic"],
        format_func=lambda x: {
            "modern": "Modern (blue headings)",
            "minimal": "Minimal (clean gray)",
            "classic": "Classic (formal black)"
        }[x]
    )

    photo = st.file_uploader("Optional Photo (JPG/PNG)", type=["jpg", "jpeg", "png"])
    photo_bytes = photo.read() if photo is not None else None

    if mode == "Auto from Job / Request":
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("#### Auto Create")
        st.markdown('<div class="hint">Examples:<br>• I want an AI developer resume<br>• I want resume for this job: [paste full JD]</div>', unsafe_allow_html=True)
        request_text = st.text_area(
            "Write your request or paste job description",
            placeholder="I want resume for this job:\nWe are hiring a Web Developer Intern. Required: HTML, CSS, JavaScript, Git...",
            height=160
        )
        if st.button("Create Resume Automatically", use_container_width=True):
            if not request_text.strip():
                st.warning("Please type a request or paste a job description.")
            else:
                data = auto_from_job(request_text, name, email, phone, location, style)
                st.session_state["generated_data"] = data
                st.session_state["photo_bytes"] = photo_bytes
                st.success(f"Auto resume created for: {data['role']} ({style} format)")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("#### Manual Builder")
        role = st.selectbox("Target Role", list(ROLE_PACKS.keys()))
        if st.button("Load simple template for this role"):
            pack = ROLE_PACKS[role]
            st.session_state["m_summary"] = pack["summary"]
            st.session_state["m_skills"] = pack["skills"]
            st.session_state["m_tools"] = pack["tools"]
            st.session_state["m_soft"] = pack["soft"]
            st.session_state["m_projects"] = pack["projects"]
            st.session_state["m_headline"] = pack["headline"]
            st.rerun()

        headline = st.text_input("Headline", st.session_state.get("m_headline", ROLE_PACKS[role]["headline"]))
        summary = st.text_area("Objective", st.session_state.get("m_summary", ROLE_PACKS[role]["summary"]), height=80)
        skills = st.text_input("Technical Skills", st.session_state.get("m_skills", ROLE_PACKS[role]["skills"]))
        tools = st.text_input("Tools", st.session_state.get("m_tools", ROLE_PACKS[role]["tools"]))
        soft_skills = st.text_input("Soft Skills", st.session_state.get("m_soft", ROLE_PACKS[role]["soft"]))
        languages = st.text_input("Languages", "English, Hindi")
        linkedin = st.text_input("LinkedIn (optional)", "")
        github = st.text_input("GitHub (optional)", "")
        portfolio = st.text_input("Portfolio (optional)", "")

        st.markdown('<div class="hint">Experience/Projects line format: Title | Company/Type | Dates | point1; point2</div>', unsafe_allow_html=True)
        experience = st.text_area("Experience (optional for freshers)", "Student / Fresher | College & Personal Work | Present | Completed coursework and practical assignments.; Learning by building small projects.", height=90)
        projects = st.text_area("Projects", st.session_state.get("m_projects", ROLE_PACKS[role]["projects"]), height=100)
        education = st.text_area("Education", "Your Course | Your School/College | Year | Stream / key subjects", height=70)
        achievements = st.text_area("Achievements / Certificates", "Any certificate\nAny competition / volunteer work", height=70)
        availability = st.text_input("Availability", "Immediate — internship / full-time / part-time")
        interests = st.text_input("Interests", "Learning, teamwork, technology")
        references = st.text_input("References", "Available on request")

        if st.button("Generate Resume from Form", use_container_width=True):
            st.session_state["generated_data"] = {
                "name": name, "email": email, "phone": phone, "location": location,
                "headline": headline, "role": role, "style": style,
                "linkedin": linkedin, "github": github, "portfolio": portfolio,
                "summary": summary, "skills": skills, "tools": tools, "soft_skills": soft_skills,
                "languages": languages, "experience": experience, "projects": projects,
                "education": education, "achievements": achievements,
                "availability": availability, "interests": interests, "references": references
            }
            st.session_state["photo_bytes"] = photo_bytes
            st.success("Manual resume generated")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("generated_data"):
        g = st.session_state["generated_data"]
        g["style"] = style
        st.markdown("<div class='glass'><h4>Download your resume</h4>", unsafe_allow_html=True)
        st.write(f"Role: **{g.get('role')}** · Format: **{style}** · Photo: **{'Yes' if st.session_state.get('photo_bytes') else 'No'}**")
        st.download_button(
            "Download DOCX",
            data=export_docx(g, st.session_state.get("photo_bytes")),
            file_name=f"{name.replace(' ', '_').lower()}_resume.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
        st.caption("Open in Word/Google Docs if you want tiny spacing edits.")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown('<div class="hero"><h1>About</h1><p>Made for every student — simple, honest, practical resume help.</p></div>', unsafe_allow_html=True)
    st.write("Auto mode, manual mode, optional photo, 3 formats, analyzer + tips.")

st.markdown("---")
st.caption("AI Resume Studio | For every student | Archit sharma")