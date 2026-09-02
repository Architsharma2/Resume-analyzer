def get_feedback(score):
    if score >= 75:
        return {
            "level": "Excellent Match",
            "message": "Your resume strongly matches this role. Highlight projects and quantify results even more."
        }
    elif score >= 50:
        return {
            "level": "Moderate Match",
            "message": "Good base, but add missing skills, stronger action verbs, and keywords from the job description."
        }
    else:
        return {
            "level": "Low Match",
            "message": "Weak overlap. Rewrite skills and experience to mirror the job description more closely."
        }


def format_skills(skills):
    if not skills:
        return "None"
    return ", ".join(skills)