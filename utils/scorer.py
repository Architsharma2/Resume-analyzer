def get_feedback(score, missing_skills=None):
    if missing_skills is None:
        missing_skills = []

    if score >= 75:
        level = "Excellent Match"
        message = "Your resume is strongly aligned with this job."
    elif score >= 50:
        level = "Moderate Match"
        message = "Your resume partially matches the job."
    else:
        level = "Low Match"
        message = "Your resume has low match with this job."

    if missing_skills:
        message += " Priority skills to add: " + ", ".join(missing_skills[:5]) + "."

    return {"level": level, "message": message}


def format_skills(skills):
    if not skills:
        return "None"
    return ", ".join(skills)