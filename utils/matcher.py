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
    "rest api", "restful api", "graphql", "json", "agile", "scrum", "jira", "communication",
    "leadership", "problem solving", "teamwork", "critical thinking", "time management",
    "oop", "object oriented programming", "data structures", "algorithms", "dsa",
    "frontend", "backend", "full stack", "full-stack", "api", "html5", "css3",
    "chatgpt", "gemini", "claude", "copilot", "vscode", "vs code", "postman",
    "three.js", "threejs", "bootstrap", "tailwind", "next.js", "nextjs"
]

# Map variants to one clean name
SKILL_ALIASES = {
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "html5": "HTML",
    "css3": "CSS",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "restful api": "REST API",
    "rest api": "REST API",
    "dsa": "Data Structures",
    "data structures": "Data Structures",
    "object oriented programming": "OOP",
    "oop": "OOP",
    "full-stack": "Full Stack",
    "full stack": "Full Stack",
    "vs code": "VS Code",
    "vscode": "VS Code",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "threejs": "Three.js",
    "three.js": "Three.js",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "power bi": "Power BI",
    "scikit-learn": "Scikit-learn",
    "c++": "C++",
    "c#": "C#",
}


def clean_skill_name(skill):
    key = skill.lower().strip()
    if key in SKILL_ALIASES:
        return SKILL_ALIASES[key]
    return skill.title()


def get_match_score(resume_text, job_description):
    resume_embedding = model.encode([resume_text])
    job_embedding = model.encode([job_description])
    similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
    score = round(float(similarity) * 100, 2)
    return score


def extract_skills(text):
    text_lower = text.lower()
    found = set()

    # Sort longer skills first so "machine learning" beats "learning"
    skills_sorted = sorted(COMMON_SKILLS, key=len, reverse=True)

    for skill in skills_sorted:
        pattern = r'(?<![a-z0-9])' + re.escape(skill.lower()) + r'(?![a-z0-9])'
        if re.search(pattern, text_lower):
            found.add(clean_skill_name(skill))

    return sorted(list(found))


def get_skill_gap(resume_text, job_description):
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))

    matched = sorted(list(resume_skills & job_skills))
    missing = sorted(list(job_skills - resume_skills))
    extra = sorted(list(resume_skills - job_skills))

    return matched, missing, extra


def get_keyword_score(resume_text, job_description):
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))
    if not job_skills:
        return 50
    return round((len(resume_skills & job_skills) / len(job_skills)) * 100, 1)