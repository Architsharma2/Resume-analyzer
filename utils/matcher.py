from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# Expanded skills list
COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "html", "css", "react", "angular", "vue",
    "node.js", "express", "django", "flask", "fastapi", "spring boot", "sql", "mysql",
    "postgresql", "mongodb", "redis", "sqlite", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "machine learning", "deep learning", "nlp", "computer vision",
    "data analysis", "data science", "excel", "power bi", "tableau", "aws", "azure",
    "google cloud", "docker", "kubernetes", "git", "github", "linux", "bash", "c++", "c#",
    "php", "laravel", "android", "kotlin", "swift", "flutter", "react native", "firebase",
    "rest api", "graphql", "json", "xml", "agile", "scrum", "jira", "communication",
    "leadership", "problem solving", "teamwork", "critical thinking", "time management",
    "oop", "data structures", "algorithms", "api", "frontend", "backend", "full stack"
]

def get_match_score(resume_text, job_description):
    resume_embedding = model.encode([resume_text])
    job_embedding = model.encode([job_description])
    similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]
    score = round(float(similarity) * 100, 2)
    return score

def extract_skills(text):
    text = text.lower()
    found_skills = []
    for skill in COMMON_SKILLS:
        if skill in text:
            found_skills.append(skill.title())
    return sorted(list(set(found_skills)))

def get_skill_gap(resume_text, job_description):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)
    
    matched = sorted(list(set(resume_skills) & set(job_skills)))
    missing = sorted(list(set(job_skills) - set(resume_skills)))
    
    return matched, missing