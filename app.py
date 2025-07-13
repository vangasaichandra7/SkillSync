import streamlit as st
import fitz  # PyMuPDF
import re
import os
import base64
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from io import BytesIO
from fpdf import FPDF
from datetime import datetime

# ------------------- SETTINGS -------------------
RESUME_DIR = "uploaded_resume.pdf"
BG_IMAGE = "streamlit_bg.png"

# ------------------- ENHANCED BACKGROUND -------------------
def set_bg(png_file):
    if os.path.exists(png_file):
        with open(png_file, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        bg_css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{b64}");
            background-size: cover;
            background-attachment: fixed;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .main .block-container {{
            background: rgba(255, 255, 255, 0.75);
            border-radius: 20px;
            padding: 2rem 3rem;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(6px);
        }}
        .css-1d391kg {{
            padding: 2rem 3rem;
        }}
        .skill-card {{
            padding: 12px 16px;
            border-radius: 12px;
            margin: 8px 0;
            font-weight: 600;
            font-size: 15px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }}
        .beginner {{
            background-color: #e8f5e9;
            color: #2e7d32;
        }}
        .intermediate {{
            background-color: #fff8e1;
            color: #f9a825;
        }}
        .advanced {{
            background-color: #ffebee;
            color: #c62828;
        }}
        </style>
        """
        st.markdown(bg_css, unsafe_allow_html=True)


# ------------------- RESUME PARSER -------------------
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# ------------------- EXPERIENCE EXTRACTOR -------------------
def extract_experience(text):
    exp_pattern = re.findall(
        r"(?i)([A-Z][\w\s,&-]+?)\s*[\n\-–]\s*([\w\s]+)?\s*(?:\(|\-)?(20\d{2})\s*(?:to|–|-)\s*(Present|20\d{2})",
        text
    )
    experiences = []
    for match in exp_pattern:
        title, company, start, end = match
        experiences.append({
            "Job Title": title.strip(),
            "Company": company.strip() if company else "Not specified",
            "Start Year": start,
            "End Year": end
        })
    return experiences

# ------------------- JD Skill Extractor -------------------
def extract_jd_skills(jd_text):
    keywords = ["python", "sql", "machine learning", "data analysis", "excel", "git", "power bi",
                "java", "c++", "tensorflow", "deep learning", "flask", "django", "aws", "devops", "cloud"]
    return [kw.lower() for kw in keywords if kw.lower() in jd_text.lower()]

# ------------------- RESUME FRESHNESS CHECK -------------------
def check_resume_freshness(text):
    years = re.findall(r"\b(20\d{2})\b", text)
    years = [int(y) for y in years if 2000 <= int(y) <= datetime.now().year]
    if years:
        last_year = max(years)
        gap = datetime.now().year - last_year
        if gap > 2:
            return f"⚠ Resume seems outdated (last year mentioned: {last_year}). Consider updating it."
        else:
            return f"✅ Resume includes recent experience (up to {last_year})."
    else:
        return "⚠ Couldn't detect any years. Please ensure job dates are included."

# ------------------- SKILL MATCHING -------------------
def get_skills(text):
    keywords = ["python", "sql", "machine learning", "data analysis", "excel", "git", "power bi",
                "java", "c++", "tensorflow", "deep learning", "flask", "django", "aws", "devops", "cloud"]
    return [kw for kw in keywords if kw.lower() in text.lower()]

def calculate_score(user_skills, required_skills):
    vectorizer = CountVectorizer().fit_transform([" ".join(user_skills), " ".join(required_skills)])
    vectors = vectorizer.toarray()
    return round(cosine_similarity([vectors[0]], [vectors[1]])[0][0] * 100, 2)

# ------------------- FEEDBACK -------------------
def generate_feedback(matched, missing):
    feedback = ""
    if missing:
        feedback += "\nSkill Improvement Tips:\n"
        for skill in missing:
            feedback += f"- Consider learning {skill} via Coursera, Udemy, or YouTube.\n"
    if not matched:
        feedback += "\nFormatting Tip:\n- Highlight your skills in a separate 'Skills' section.\n"
    return feedback

# ------------------- JOB MARKET FIT -------------------
def job_market_fit(job_title):
    job_roles = {
        "software engineer": ("₹80,000 - ₹130,000", "High"),
        "devops engineer": ("₹50,000 - ₹100,000", "High"),
        "cloud engineer": ("₹50,000 - ₹80,000", "Medium"),
        "data scientist": ("₹60,000 - ₹120,000", "High"),
        "front-end developer": ("₹30,000 - ₹80,000", "Medium"),
        "back-end developer": ("₹40,000 - ₹100,000", "High"),
        "full-stack developer": ("₹50,000 - ₹110,000", "High"),
        "mobile app developer": ("₹40,000 - ₹90,000", "Medium")
    }
    job_title = job_title.lower().strip()
    return job_roles.get(job_title, ("Data not available", "Unknown"))

# ------------------- SKILL DETECTIVE -------------------
def skill_level_detection(skills):
    skill_levels = {
        "Beginner": ["python", "java", "sql", "c++", "html", "css", "javascript"],
        "Intermediate": ["machine learning", "data analysis", "git", "excel", "tensorflow", "flask", "django"],
        "Advanced": ["deep learning", "power bi", "aws", "cloud", "devops"]
    }
    detected_skills = {"Beginner": [], "Intermediate": [], "Advanced": []}
    for skill in skills:
        for level in skill_levels:
            if skill.lower() in skill_levels[level]:
                detected_skills[level].append(skill)
    return detected_skills

def estimate_proficiency(resume_text, skill):
    count = len(re.findall(rf'\b{re.escape(skill)}\b', resume_text, re.IGNORECASE))
    if count >= 5:
        return "Expert"
    elif count >= 3:
        return "Intermediate"
    elif count >= 1:
        return "Beginner"
    return "Not Mentioned"

def suggest_technical_improvements(missing_skills):
    if not missing_skills:
        return ["Great! Your resume already aligns well with the required technical areas."]
    return [f"Consider improving your expertise in: {', '.join(missing_skills)}"]

# ------------------- PDF FEEDBACK GENERATOR -------------------
def create_feedback_pdf(score, matched, missing, feedback):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "SkillSync - Feedback Report", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(0, 10, f"Match Score: {score}%", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, "Matched Skills:", ln=True)
    for skill in matched:
        pdf.cell(0, 10, f"- {skill}", ln=True)
    pdf.ln(5)

    pdf.cell(0, 10, "Missing Skills:", ln=True)
    for skill in missing:
        pdf.cell(0, 10, f"- {skill}", ln=True)
    pdf.ln(5)

    pdf.multi_cell(0, 10, f"Feedback:\n{feedback}")

    buffer = BytesIO()
    buffer.write(pdf.output(dest='S').encode('latin1'))
    buffer.seek(0)
    return buffer

# ------------------- MAIN -------------------
def main():
    set_bg(BG_IMAGE)
    st.title("📄 SkillSync")
    st.markdown("Match your resume with company expectations and get instant feedback!")

    st.sidebar.header("💼 HR / CEO Input")
    job_description = st.sidebar.text_area("Paste Job Description")
    if job_description:
        required_skills = extract_jd_skills(job_description)
    else:
        required_skills_input = st.sidebar.text_area("Enter Required Skills (comma-separated)",
                                                    "Python, SQL, Machine Learning, Power BI")
        required_skills = [x.strip().lower() for x in required_skills_input.split(",")]

    st.header("📤 Upload Resume")
    uploaded_file = st.file_uploader("Upload a PDF Resume", type=["pdf"])

    if uploaded_file:
        with open(RESUME_DIR, "wb") as f:
            f.write(uploaded_file.read())

        resume_text = extract_text_from_pdf(open(RESUME_DIR, "rb"))
        st.subheader("📋 Resume Content")
        st.text_area("Extracted Resume Text", resume_text, height=250)

        st.subheader("💼 Work Experience")
        experiences = extract_experience(resume_text)
        if experiences:
            exp_df = pd.DataFrame(experiences)
            st.dataframe(exp_df)
        else:
            st.info("No work experience details could be extracted. Ensure proper formatting in your resume.")

        st.subheader("🕰 Resume Freshness Check")
        st.info(check_resume_freshness(resume_text))

        user_skills = get_skills(resume_text)
        matched = [s for s in user_skills if s in required_skills]
        missing = [s for s in required_skills if s not in user_skills]
        score = calculate_score(matched, required_skills)

        st.subheader("✅ Skill Match Results")
        st.success(f"🔢 Match Score: {score}%")
        st.markdown(f"✅ Matched Skills: {', '.join(matched) if matched else 'None'}")
        st.markdown(f"❌ Missing Skills: {', '.join(missing) if missing else 'None'}")

        st.subheader("📈 Skill Proficiency")
        prof = {s: estimate_proficiency(resume_text, s) for s in matched}
        st.table(pd.DataFrame(prof.items(), columns=["Skill", "Level"]))

        feedback = generate_feedback(matched, missing)
        if feedback:
            st.subheader("🧠 Feedback & Learning Tips")
            st.markdown(feedback)

            st.subheader("🧪 Technical Areas to Improve")
            for tip in suggest_technical_improvements(missing):
                st.markdown(f"- {tip}")

            pdf_buffer = create_feedback_pdf(score, matched, missing, feedback)
            st.download_button("📥 Download Feedback as PDF", data=pdf_buffer,
                               file_name="Resume_Feedback_Report.pdf", mime="application/pdf")

        st.subheader("🔍 Predictive Job Market Fit")
        job_title = st.text_input("Enter Job Title for Market Fit Prediction", "software engineer")
        salary_range, demand = job_market_fit(job_title)
        st.markdown(f"*Estimated Salary Range:* {salary_range}")
        st.markdown(f"*Market Demand:* {demand}")

        st.subheader("🕵‍♂ Skill Detective")
        detected = skill_level_detection(user_skills)
        for level, skills_list in detected.items():
            if skills_list:
                st.markdown(f"<div class='skill-card {level.lower()}'>{level} Skills**: {', '.join(skills_list)}</div>", unsafe_allow_html=True)

        st.subheader("📊 Analytics Dashboard")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Skill Match Pie Chart")
            fig1, ax1 = plt.subplots()
            ax1.pie([len(matched), len(missing)], labels=["Matched", "Missing"],
                    colors=["#00C49F", "#FF5C5C"], autopct="%1.1f%%", startangle=140)
            ax1.axis("equal")
            st.pyplot(fig1)

        with col2:
            st.markdown("### Skills Summary Table")
            if matched or missing:
                df = pd.DataFrame({
                    "Skill": matched + missing,
                    "Status": ["Matched"] * len(matched) + ["Missing"] * len(missing)
                })
                st.dataframe(df.style.map(
                    lambda x: 'background-color: #d4edda' if x == "Matched" else 'background-color: #f8d7da',
                    subset=["Status"]
                ))
            else:
                st.write("No skills to display in summary.")

if __name__ == "__main__":
    main()
os.system("streamlit run app.py --server.port=8500 --server.address=0.0.0.0")