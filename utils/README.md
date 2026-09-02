# AI Resume Analyzer & Job Matcher

Final Year BCA Honors Project

## Overview
This project analyzes a resume against a job description and gives:
- Match score (0–100%)
- Candidate email and phone extraction
- Matched skills
- Missing skills
- Personalized feedback
- Downloadable analysis report

## Tech Stack
- Python
- Streamlit
- spaCy
- sentence-transformers
- scikit-learn
- pdfplumber
- python-docx

## How to Run
1. Create and activate virtual environment
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm