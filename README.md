# 🚀 AI Resume Analyzer & ATS Optimizer

An intelligent web application that analyzes resumes against job descriptions using Google Gemini 2.5 Flash, calculates ATS compatibility scores, and generates professional PDF reports.

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![FastAPI](https://img.shields.io/badge/Framework-FastAPI-green.svg)

## 🌟 Features

- **AI-Powered Analysis**: Uses Large Language Models (LLMs) to extract intent and context from resumes.
- **ATS Scoring**: Calculates a match percentage based on keyword density and semantic similarity.
- **Skill Gap Detection**: Automatically identifies missing technical and soft skills required for the role.
- **PDF Report Generation**: Professional, downloadable feedback reports for users.
- **Modern UI**: Dark-mode dashboard with real-time loading states and progress bars.
- **CI/CD Ready**: Integrated with GitHub Actions for automated testing.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **AI Engine**: Google Gemini 2.5 Flash API
- **NLP/Math**: Scikit-Learn (TF-IDF & Cosine Similarity), PyMuPDF
- **PDF Generation**: ReportLab
- **Frontend**: Jinja2 Templates, CSS3, JavaScript
- **Testing**: Pytest

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- A Google AI Studio API Key ([Get one here](https://aistudio.google.com/))

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/jahanzaibshah234/AI_Resume_Analyzer.git](https://github.com/jahanzaibshah234/AI_Resume_Analyzer.git)
   cd AI_Resume_Analyzer
