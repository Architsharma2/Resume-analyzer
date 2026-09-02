import streamlit as st
from utils.parser import extract_text
from utils.matcher import get_match_score, get_skill_gap, get_keyword_score
from utils.extractor import extract_basic_info
from utils.scorer import get_feedback, format_skills

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 45%, #0f766e 100%);
        color: #e2e8f0;
    }
    h1, h2, h3, h4 {
        color: #f8fafc !important;
    }
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }
    .score-big {
        font-size: 3rem;
        font-weight: 800;
        color: #2dd4bf;
        line-height: 1;
    }
    .label {
        color: #94a3b8;
        font-size: 0.9rem;
    }
    .skill-chip {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        margin: 0.25rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .skill-ok {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.35);
    }
    .skill-missing {
        background: rgba(244, 63, 94, 0.12);
        color: #fb7185;
        border: 1px solid rgba(251, 113, 133, 0.35);
    }
    .skill-extra {
        background: rgba(56, 189, 248, 0.12);
        color: #7dd3fc;
        border: 1px solid rgba(125, 211, 252, 0.35);
    }
    .info-box {
        background: rgba(30, 41, 59, 0.9);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    section[data-testid="stSidebar"] {
        background: #0b1220;
    }
    .stTextArea textarea, .stTextInput input {
        background-color: #0b1220 !important;
        color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### How to use")
    st.write("1. Upload resume (PDF/DOCX)")
    st.write("2. Paste job description")
    st.write("3. Click **Analyze Resume**")
    st.markdown("---")
    st.write("Uses Sentence Transformers for semantic matching + skill gap analysis.")
    st.markdown("---")
    st.caption("Final Year BCA Honors Project")

# ---------- Header ----------
st.markdown('<div class="main-title">AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Smart matching • Skill gap detection • ATS-style feedback</div>', unsafe_allow_html=True)

# ---------- Inputs ----------
col_a, col_b = st.columns([1, 1])

with col_a:
    st.markdown("#### Upload Resume")
    uploaded_file = st.file_uploader("PDF or DOCX", type=["pdf", "docx"], label_visibility="collapsed")

with col_b:
    st.markdown("#### Job Description")
    job_description = st.text_area("Paste JD", height=180, label_visibility="collapsed",
                                   placeholder="Paste the complete job description here...")

analyze = st.button("Analyze Resume", use_container_width=True, type="primary")

if analyze:
    if uploaded_file is None:
        st.warning("Please upload a resume.")
    elif not job_description.strip():
        st.warning("Please paste a job description.")
    else:
        with st.spinner("Analyzing with AI... please wait"):
            resume_text = extract_text(uploaded_file)
            score = get_match_score(resume_text, job_description)
            matched, missing, extra = get_skill_gap(resume_text, job_description)
            keyword_score = get_keyword_score(resume_text, job_description)
            basic_info = extract_basic_info(resume_text)
            feedback = get_feedback(score)

        st.success("Analysis complete")

        # Top metrics
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="card"><div class="label">Match Score</div><div class="score-big">{score}%</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="card"><div class="label">Skill Match</div><div class="score-big">{keyword_score}%</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="card"><div class="label">Matched Skills</div><div class="score-big">{len(matched)}</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="card"><div class="label">Missing Skills</div><div class="score-big">{len(missing)}</div></div>', unsafe_allow_html=True)

        st.progress(min(score / 100, 1.0))

        # Candidate info
        st.markdown("### Candidate Information")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="info-box"><b>Name</b><br>{basic_info["name"]}</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="info-box"><b>Email</b><br>{basic_info["email"]}</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="info-box"><b>Phone</b><br>{basic_info["phone"]}</div>', unsafe_allow_html=True)

        # Skills
        st.markdown("### Skills Analysis")
        s1, s2 = st.columns(2)

        with s1:
            st.markdown("#### Matched Skills")
            if matched:
                chips = " ".join([f'<span class="skill-chip skill-ok">{s}</span>' for s in matched])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.info("No matched skills found. Try a more detailed job description.")

        with s2:
            st.markdown("#### Missing Skills")
            if missing:
                chips = " ".join([f'<span class="skill-chip skill-missing">{s}</span>' for s in missing])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.success("No major missing skills.")

        if extra:
            st.markdown("#### Extra skills on resume")
            chips = " ".join([f'<span class="skill-chip skill-extra">{s}</span>' for s in extra])
            st.markdown(chips, unsafe_allow_html=True)

        # Feedback
        st.markdown("### Feedback")
        if score >= 75:
            st.success(f"**{feedback['level']}** — {feedback['message']}")
        elif score >= 50:
            st.warning(f"**{feedback['level']}** — {feedback['message']}")
        else:
            st.error(f"**{feedback['level']}** — {feedback['message']}")

        tips = []
        if missing:
            tips.append("Add these missing skills if you truly have them: " + ", ".join(missing[:5]))
        if basic_info["phone"] == "Not found":
            tips.append("Add a phone number near the top of your resume.")
        if basic_info["email"] == "Not found":
            tips.append("Add a professional email address.")
        tips.append("Use strong action verbs: Built, Developed, Designed, Improved, Delivered.")
        tips.append("Mirror important keywords from the job description in your skills and project bullets.")

        st.markdown("### Improvement Tips")
        for t in tips:
            st.write(f"- {t}")

        # Report download
        report = f"""AI Resume Analyzer Report
==============================
Name: {basic_info['name']}
Email: {basic_info['email']}
Phone: {basic_info['phone']}

Match Score: {score}%
Skill Match: {keyword_score}%
Level: {feedback['level']}

Matched Skills:
{format_skills(matched)}

Missing Skills:
{format_skills(missing)}

Extra Skills:
{format_skills(extra)}

Feedback:
{feedback['message']}
"""
        st.download_button(
            "Download Analysis Report",
            data=report,
            file_name="resume_analysis_report.txt",
            mime="text/plain",
            use_container_width=True
        )

        with st.expander("View Extracted Resume Text"):
            st.text_area("Resume Content", resume_text, height=300)

st.markdown("---")
st.caption("Built as Final Year BCA Honors Project | AI Resume Analyzer & Job Matcher")