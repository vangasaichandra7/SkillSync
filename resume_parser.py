import re
import spacy
import pdfplumber

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_skills(text):
    skills_keywords = [
        'python', 'java', 'c++', 'machine learning', 'deep learning', 'data analysis',
        'sql', 'power bi', 'excel', 'nlp', 'tensorflow', 'keras', 'flask', 'django',
        'aws', 'azure', 'git', 'github', 'html', 'css', 'javascript'
    ]
    text = text.lower()
    skills_found = [skill for skill in skills_keywords if skill in text]
    return list(set(skills_found))

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    match = re.search(r'\+?\d[\d\- ]{8,}\d', text)
    return match.group(0) if match else "Not found"

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Not found"
