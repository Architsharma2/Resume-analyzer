import streamlit as st
from utils.parser import extract_text
from utils.matcher import get_match_score, get_skill_gap
from utils.extractor import extract_basic_info
from utils.scorer import get_feedback, format_skills

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
    }
    h1, h2, h3 {
        color: #f8fafc !important;
    }
    .info-box {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 8px;
    }
    .skill-chip {
        display: inline-block;
        padding: 6px 12px;
        margin: 4px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
    }
    .chip-ok {
        background: rgba(34,197,94,0.15);
        color: #4ade80;
        border: 1px solid rgba(34,197,94,0.35);
    }
    .chip-missing {
        background: rgba(239,68,68,0.15);
        color: #f87171;
        border: 1px solid rgba(239,68,68,0.35);
    }
    .chip-extra {
        background: rgba(59,130,246,0.15);
        color: #60a5fa;
        border: 1px solid rgba(59,130,246,0.35);
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Resume Analyzer")
    st.write("Upload resume + paste job description")
    st.markdown("---")
    st.write("Features:")
    st.write("- Match score")
    st.write("- Skill gap")
    st.write("- Contact extraction")
    st.write("- Report download")
    st.markdown("---")
    st.caption("BCA Final Year Project")

st.title("AI Resume Analyzer & Job Matcher")
st.markdown("### Upload resume and paste job description")

uploaded_file = st.file_uploader("Upload Resume (PDF / DOCX)", type=["pdf", "docx"])
job_description = st.text_area(
    "Paste Job Description",
    height=180,
    placeholder="Example: Python, JavaScript, React, SQL, Git, Firebase, REST API, communication"
)

# Use normal button click only (no Ctrl+Enter needed)
analyze = st.button("Analyze Resume", use_container_width=True)

if analyze:
    if uploaded_file is None:
        st.warning("Please upload a resume.")
    elif not job_description.strip():
        st.warning("Please paste a job description.")
    else:
        with st.spinner("Analyzing..."):
            resume_text = extract_text(uploaded_file)

            score = get_match_score(resume_text, job_description)

            # IMPORTANT: 3 values
            matched_skills, missing_skills, extra_skills = get_skill_gap(resume_text, job_description)

            basic_info = extract_basic_info(resume_text)
            feedback = get_feedback(score, missing_skills)

        st.success("Analysis complete")

        st.markdown("## Candidate Profile")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='info-box'><b>Name</b><br>{basic_info.get('name', 'Not found')}</div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='info-box'><b>Email</b><br>{basic_info.get('email', 'Not found')}</div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='info-box'><b>Phone</b><br>{basic_info.get('phone', 'Not found')}</div>", unsafe_allow_html=True)

        st.markdown("## Match Score")
        m1, m2 = st.columns([1, 2])
        with m1:
            st.metric("Overall Match", f"{score}%")
        with m2:
            if score >= 75:
                st.success(feedback["level"])
            elif score >= 50:
                st.warning(feedback["level"])
            else:
                st.error(feedback["level"])
            st.progress(min(score / 100, 1.0))

        st.markdown("## Skills Analysis")
        s1, s2, s3 = st.columns(3)

        with s1:
            st.markdown("### Matched Skills")
            if matched_skills:
                chips = "".join([f"<span class='skill-chip chip-ok'>{s}</span>" for s in matched_skills])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.write("No matched skills")

        with s2:
            st.markdown("### Missing Skills")
            if missing_skills:
                chips = "".join([f"<span class='skill-chip chip-missing'>{s}</span>" for s in missing_skills])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.write("No missing skills")

        with s3:
            st.markdown("### Extra Skills")
            if extra_skills:
                chips = "".join([f"<span class='skill-chip chip-extra'>{s}</span>" for s in extra_skills])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.write("No extra skills")

        st.markdown("## Feedback")
        if score >= 75:
            st.success(feedback["message"])
        elif score >= 50:
            st.warning(feedback["message"])
        else:
            st.error(feedback["message"])

        report = f"""AI Resume Analyzer Report
==============================
Name: {basic_info.get('name', 'Not found')}
Email: {basic_info.get('email', 'Not found')}
Phone: {basic_info.get('phone', 'Not found')}
Match Score: {score}%
Level: {feedback['level']}

Matched Skills:
{format_skills(matched_skills)}

Missing Skills:
{format_skills(missing_skills)}

Extra Skills:
{format_skills(extra_skills)}

Feedback:
{feedback['message']}
"""
        st.download_button(
            label="Download Analysis Report",
            data=report,
            file_name="resume_analysis_report.txt",
            mime="text/plain",
            use_container_width=True
        )

        with st.expander("View Extracted Resume Text"):
            st.text_area("Resume Content", resume_text, height=300)

st.markdown("---")
st.caption("Built as Final Year BCA Honors Project")