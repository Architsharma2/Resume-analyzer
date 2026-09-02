def get_feedback(score):
    if score >= 75:
        return {
            "level": "Excellent Match",
            "message": "Your resume is well aligned with the job description. You have a strong chance!"
        }
    elif score >= 50:
        return {
            "level": "Moderate Match",
            "message": "Your resume partially matches the job. Add the missing skills and use more keywords from the job description."
        }
    else:
        return {
            "level": "Low Match",
            "message": "Your resume has low match. Please update your skills, projects, and experience according to the job requirements."
        }


def format_skills(skills):
    if not skills:
        return "None"
    return ", ".join(skills)