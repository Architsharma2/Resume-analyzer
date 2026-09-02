def get_feedback(score, missing_skills):
    if score >= 75:
        level = "Excellent Match"
        message = "Your resume is strongly aligned with this job. Keep polishing projects and quantified achievements."
    elif score >= 50:
        level = "Moderate Match"
        message = "Your resume partially matches. Add missing skills and mirror keywords from the job description."
    else:
        level = "Low Match"
        message = "Low overlap with the job description. Update skills, tools, and experience based on the role."

    if missing_skills:
        message += f" Priority skills to add: {', '.join(missing_skills[:5])}."

    return {"level": level, "message": message}

def format_skills(skills):
    if not skills:
        return "None"
    return ", ".join(skills)