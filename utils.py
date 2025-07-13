def calculate_score(required_skills, resume_skills):
    matched = list(set(required_skills).intersection(set(resume_skills)))
    missing = list(set(required_skills) - set(resume_skills))
    score = int((len(matched) / len(required_skills)) * 100) if required_skills else 0
    return matched, missing, score

def feedback_tips(missing_skills):
    if not missing_skills:
        return "Excellent! All required skills are present."
    return f"Improve your resume by learning: {', '.join(missing_skills)}. Consider adding project experiences and formatting with bullet points and sections."

def format_resume_analytics(resume_skills, missing_skills):
    return {
        "Total Resume Skills": len(resume_skills),
        "Matched Skills": len(set(resume_skills) - set(missing_skills)),
        "Missing Skills": len(missing_skills)
    }
