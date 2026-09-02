from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

model = SentenceTransformer('all-MiniLM-L6-v2')

COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "html", "css", "react", "angular", "vue",
    "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring boot", "sql", "mysql",
    "postgresql", "mongodb", "redis", "sqlite", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "machine learning", "deep learning", "nlp", "computer vision",
    "data analysis", "data science", "excel", "power bi", "tableau", "aws", "azure",
    "google cloud", "gcp", "docker", "kubernetes", "git", "github", "linux", "bash", "c++", "c#",
    "php", "laravel", "android", "kotlin", "swift", "flutter", "react native", "firebase",
    "rest api", "graphql", "json", "agile", "scrum", "jira", "communication",
    "leadership", "problem solving", "teamwork", "critical thinking", "time management",
    "oop", "dsa", "data structures", "algorithms", "api", "frontend", "backend", "full stack",
    "html5", "css3", "bootstrap", "tailwind", "chatgpt", "gemini", "copilot"
]

SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "nodejs": "node.js",
    "node js": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "mongo": "mongodb",
    "postgres": "postgresql",
    "powerbi": "power bi",
    "gcp": "google cloud",
    "ml": "machine learning",
    "dl": "deep learning",
    "dsa": "data structures",
    "html5": "html",
    "css3": "css",
    "cpp": "c++",
}

def normalize_skill(skill):
    skill = skill.lower().strip()
    return SKILL_ALIASES.get(skill, skill)

def get_match_score(resume_text, job_description):
    resume_embedding = model.encode([resume_text])
    job_embedding = model.encode([job_description])
    similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
    return round(float(similarity) * 100, 2)

def extract_skills(text):
    text_lower = " " + text.lower() + " "
    found = set()

    # Check aliases first
    for alias, canonical in SKILL_ALIASES.items():
        if f" {alias} " in text_lower or f" {alias}," in text_lower or f" {alias}." in text_lower or f"/{alias}" in text_lower or f"{alias}/" in text_lower:
            found.add(canonical)

    # Check all skills with simple contains (more reliable for resumes)
    for skill in COMMON_SKILLS:
        s = skill.lower()
        if s in text_lower:
            found.add(normalize_skill(s))

    return sorted(list(found))

def get_skill_gap(resume_text, job_description):
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))

    matched = sorted(list(resume_skills & job_skills))
    missing = sorted(list(job_skills - resume_skills))
    extra = sorted(list(resume_skills - job_skills))

    # Always return 3 lists
    return (
        [s.title() for s in matched],
        [s.title() for s in missing],
        [s.title() for s in extra]
    )