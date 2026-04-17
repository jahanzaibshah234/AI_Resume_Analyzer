import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
import os
import re
from dotenv import load_dotenv

load_dotenv(override=True)

current_key = os.getenv("GEMINI_API_KEY")
if current_key:
    print(f"DEBUG: Currently loaded key starts with: {current_key[:10]}...")
else:
    print("DEBUG: NO KEY FOUND AT ALL!")

client = genai.Client()

# -----------------------------
# Extract text from PDF
# -----------------------------
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# -----------------------------
# Clean text
# -----------------------------
def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    return text

# -----------------------------
# Calculate similarity
# -----------------------------
def calculate_similarity(resume, job_desc):
    texts = [resume, job_desc]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    
    return round(score[0][0] * 100, 2)

# -----------------------------
# Find missing skills
# -----------------------------
SKILLS = [
    "python", "machine learning", "data analysis", "pandas",
    "numpy", "sql", "fastapi", "nlp", "deep learning",
    "tensorflow", "docker", "git", "api"
]

def missing_skills(resume, job_desc):
    resume = resume.lower()
    job = job_desc.lower()

    missing = [skill for skill in SKILLS if skill in job and skill not in resume]

    return missing

def generate_suggestions(resume_text):
    try:
        # Using the current standard fast model
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=f"""
            You are a professional career coach. Provide 5 short, specific resume tips as a simple list.
            Do not use bolding or markdown. 
            Analyze this resume: {resume_text[:1500]}
            """
        )
        
        # Split the text by newlines and clean it up
        tips = response.text.strip().split("\n")
        clean_tips = [
            tip.strip("* -12345. ")
            for tip in tips
            if len(tip.strip()) > 20 and "here are" not in tip.lower()
        ][:5]
        
        if not clean_tips:
            raise ValueError("Model returned empty or poorly formatted tips.")
            
        return clean_tips

    except Exception as e:
        print(f"GenAI Error: {e}")
        # Fallback tips
        return [
            "Quantify your impact using percentages and numbers.",
            "Tailor your skills section to match the specific job description keywords.",
            "Use strong action verbs like 'Architected', 'Spearheaded', or 'Optimized'.",
            "Ensure your resume is ATS-friendly by using a standard layout.",
            "Add a 'Professional Summary' to highlight your top achievements."
        ]


def ats_score(resume_text, job_desc):
    score = 0
    resume = resume_text.lower()
    job = job_desc.lower()

    # -------------------------
    # 1. Skills Match (40 pts)
    # -------------------------
    job_words = set(job.split())
    resume_words = set(resume.split())

    matched = job_words.intersection(resume_words)

    if len(job_words) > 0:
        skill_score = (len(matched) / len(job_words)) * 40
        score += skill_score

    # -------------------------
    # 2. Sections Check (20 pts)
    # -------------------------
    sections = ["education", "experience", "project", "skills"]
    section_score = sum([1 for sec in sections if sec in resume]) * 5
    score += section_score

    # -------------------------
    # 3. Keyword Density (15 pts)
    # -------------------------
    keyword_count = sum([resume.count(word) for word in job_words])
    if keyword_count > 20:
        score += 15
    elif keyword_count > 10:
        score += 10
    else:
        score += 5

    # -------------------------
    # 4. Resume Length (10 pts)
    # -------------------------
    word_count = len(resume.split())
    if 300 <= word_count <= 800:
        score += 10
    elif 150 <= word_count < 300:
        score += 5

    # -------------------------
    # 5. Action Words (15 pts)
    # -------------------------
    strong_words = ["developed", "built", "implemented", "designed", "created"]
    action_score = sum([1 for word in strong_words if word in resume]) * 3
    score += min(action_score, 15)

    return round(score, 2)