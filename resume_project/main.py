from fastapi import FastAPI, Request, Form, UploadFile, File
from model import extract_text_from_pdf, preprocess, calculate_similarity, missing_skills, generate_suggestions, ats_score
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus import HRFlowable
from reportlab.lib import colors
import shutil
import os
import io
import time


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="static")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------------------------
# Home Page
# -------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={}
    )

# -------------------------
# Analyze Resume
# -------------------------
@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    job_desc: str = Form(...),
    file: UploadFile = File(...)
):
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    resume_text = extract_text_from_pdf(file_path)

    resume_clean = preprocess(resume_text)
    job_clean = preprocess(job_desc)

    ats = ats_score(resume_text, job_desc)

    score = calculate_similarity(resume_clean, job_clean)
    missing = missing_skills(resume_clean, job_clean)
    
    # ADD THIS LINE:
    tips = generate_suggestions(resume_text)

    # Use the keyword argument style to avoid the TypeError
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "score": score,
            "missing": missing,
            "suggestions": tips,  # PASS TIPS HERE
            "ats_score": ats,
            "job_desc": job_desc
        }
    )


@app.post("/download")
async def download_report(
    job_desc: str = Form(...), 
    ats_score: float = Form(...),
    missing_skills: str = Form(""), 
    suggestions: str = Form("")
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    # Custom fonts and colors for the PDF
    title_style = ParagraphStyle('Title', fontSize=22, textColor=colors.HexColor("#2C3E50"), spaceAfter=20, fontName="Helvetica-Bold")
    label_style = ParagraphStyle('Label', fontSize=14, textColor=colors.HexColor("#2980B9"), fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=5)
    body_style = ParagraphStyle('Body', fontSize=11, leading=14, fontName="Helvetica")
    bullet_style = ParagraphStyle('Bullet', fontSize=11, leading=16, fontName="Helvetica", leftIndent=20)

    elements = []

    # 1. Title
    elements.append(Paragraph("AI Resume Analysis Report", title_style))
    
    # 2. ATS Score Card
    elements.append(Paragraph(f"<b>ATS Match Score:</b> {ats_score}/100", body_style))
    elements.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # 3. MISSING SKILLS (This actually draws them on the page)
    # ---------------------------------------------------------
    if missing_skills:
        elements.append(Paragraph("Missing Skills:", label_style))
        skills_list = missing_skills.split('||')
        for skill in skills_list:
            if skill.strip():
                elements.append(Paragraph(f"• {skill}", bullet_style))
        elements.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # 4. AI SUGGESTIONS (This actually draws them on the page)
    # ---------------------------------------------------------
    if suggestions:
        elements.append(Paragraph("AI Suggestions:", label_style))
        tips_list = suggestions.split('||')
        for tip in tips_list:
            if tip.strip():
                elements.append(Paragraph(f"• {tip}", bullet_style))
        elements.append(Spacer(1, 10))

    # 5. Job Description Context
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey, spaceBefore=15, spaceAfter=15))
    elements.append(Paragraph("Job Description Context:", label_style))
    elements.append(Paragraph(job_desc, body_style))

   # Build the final PDF document
    doc.build(elements)
    buffer.seek(0)
    
    # Create a unique filename so the browser CANNOT cache it!
    timestamp = int(time.time())
    
    return StreamingResponse(
        buffer, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Resume_Report_{timestamp}.pdf"}
    )