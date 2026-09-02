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

with st.sidebar:
    st.header("How to use")
    st.write("1. Upload your Resume (PDF or DOCX)")
    st.write("2. Paste the Job Description")
    st.write("3. Wait for the AI analysis")
    st.write("---")
    st.write("This tool uses AI (Sentence Transformers) to calculate match score and find skill gaps.")
    st.write("---")
    st.caption("Final Year BCA Project")

st.title("AI Resume Analyzer & Job Matcher")
st.markdown("### Upload your resume and paste a job description to get detailed analysis")

uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])
job_description = st.text_area("Paste Job Description here", height=200)

if uploaded_file is not None and job_description.strip() != "":
    with st.spinner("Analyzing your resume with AI... Please wait"):
        resume_text = extract_text(uploaded_file)
        score = get_match_score(resume_text, job_description)
        matched_skills, missing_skills = get_skill_gap(resume_text, job_description)
        basic_info = extract_basic_info(resume_text)
        feedback = get_feedback(score)

    st.success("Analysis Complete!")

    st.subheader("Candidate Information")
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.write(f"**Email:** {basic_info['email']}")
    with info_col2:
        st.write(f"**Phone:** {basic_info['phone']}")

    st.subheader("Match Score")
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Resume Match Percentage", value=f"{score}%")

    with col2:
        if score >= 75:
            st.success(feedback["level"])
        elif score >= 50:
            st.warning(feedback["level"])
        else:
            st.error(feedback["level"])

    st.progress(min(score / 100, 1.0))

    st.subheader("Skills Analysis")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### Matched Skills")
        if matched_skills:
            for skill in matched_skills:
                st.success(skill)
        else:
            st.info("No matched skills found.")

    with col4:
        st.markdown("### Missing Skills")
        if missing_skills:
            for skill in missing_skills:
                st.error(skill)
        else:
            st.success("No missing skills. Great job!")

    st.subheader("Personalized Feedback")
    if score >= 75:
        st.success(feedback["message"])
    elif score >= 50:
        st.warning(feedback["message"])
    else:
        st.error(feedback["message"])

    report = f"""AI Resume Analyzer Report
==============================
Email: {basic_info['email']}
Phone: {basic_info['phone']}
Match Score: {score}%
Level: {feedback['level']}

Matched Skills:
{format_skills(matched_skills)}

Missing Skills:
{format_skills(missing_skills)}

Feedback:
{feedback['message']}
"""
    st.download_button(
        label="Download Analysis Report",
        data=report,
        file_name="resume_analysis_report.txt",
        mime="text/plain"
    )

    with st.expander("View Extracted Resume Text"):
        st.text_area("Resume Content", resume_text, height=300)

elif uploaded_file is not None:
    st.warning("Please also paste the Job Description.")
elif job_description.strip() != "":
    st.warning("Please upload a Resume.")

st.markdown("---")
st.caption("Built as Final Year BCA Honors Project | AI Resume Analyzer & Job Matcher")