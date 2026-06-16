# 📄 AI Resume Screener

An AI-powered Applicant Tracking System (ATS) built using **Python, Streamlit, LangChain, Sentence Transformers, Groq LLM, and SQLite**.

The application analyzes multiple resumes against a job description using semantic similarity, skill matching, and AI-generated insights to help recruiters identify the best candidates efficiently.

---

## 🚀 Features

### Resume Screening
- Upload and analyze multiple PDF resumes
- ATS-style resume scoring
- Semantic similarity matching
- Skill matching against job description
- Experience, education, certification, and project scoring

### AI Features
- AI-generated candidate evaluation
- Resume improvement suggestions
- Technical interview question generation
- AI hiring recommendation
- AI comparison between top candidates

### Candidate Profile Extraction
- Candidate Name
- Email Address
- Phone Number
- LinkedIn Profile
- GitHub Profile

### Recruiter Dashboard
- Resume ranking
- Interactive analytics dashboard
- Candidate comparison
- Search and filtering
- Resume history stored in SQLite

### Reports
- PDF report generation
- CSV export
- Resume ranking table

---

# 🏗️ System Architecture

```
                     Job Description
                            │
                            ▼
                  Sentence Embeddings
                            │
                            ▼
PDF Resume ──► Text Extraction ──► Semantic Matching
                            │
                            ▼
                     Skill Matching
                            │
                            ▼
                    ATS Score Engine
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
 AI Evaluation      Interview Questions   Hiring Decision
          │
          ▼
 Recruiter Dashboard
          │
          ▼
SQLite Database + PDF Reports
```

---

# 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| Frontend | Streamlit |
| LLM | Groq (Llama 3.3 70B) |
| Framework | LangChain |
| Embeddings | Sentence Transformers |
| Database | SQLite |
| PDF Processing | pdfplumber |
| Data Visualization | Plotly |
| Report Generation | ReportLab |
| Data Processing | Pandas |

---

# 📂 Project Structure

```
resume-screener/
│
├── backend/
│   ├── main.py
│   ├── extractor.py
│   ├── scorer.py
│   ├── skill_matcher.py
│   ├── explainer.py
│   ├── interview_generator.py
│   ├── comparison.py
│   ├── hiring_decision.py
│   ├── report_generator.py
│   ├── database.py
│   └── ...
│
├── frontend/
│   └── app.py
│
├── data/
│   ├── uploads/
│   └── skills.txt
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/resume-screener.git
```

Navigate to the project:

```bash
cd resume-screener
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```text
GROQ_API_KEY=YOUR_API_KEY
```

Run the application:

```bash
streamlit run frontend/app.py
```

---

# 📊 ATS Scoring Formula

| Component | Weight |
|-----------|---------|
| Semantic Matching | 40% |
| Skill Matching | 30% |
| Experience | 10% |
| Projects | 10% |
| Education | 5% |
| Certifications | 5% |

**Final Score =**

```
40% Semantic Match
+ 30% Skill Match
+ 10% Experience
+ 10% Projects
+ 5% Education
+ 5% Certifications
```

---

# 🔄 Workflow

```
Upload Resume PDFs
        │
        ▼
Extract Resume Text
        │
        ▼
Generate Embeddings
        │
        ▼
Semantic Matching
        │
        ▼
Skill Matching
        │
        ▼
ATS Score Calculation
        │
        ▼
AI Evaluation
        │
        ▼
Interview Questions
        │
        ▼
Hiring Recommendation
        │
        ▼
Recruiter Dashboard
        │
        ▼
PDF & CSV Export
```

---

# 🎯 Key Highlights

- AI-powered ATS scoring system
- Semantic resume-job matching using embeddings
- Intelligent skill gap analysis
- Automated recruiter insights using LLMs
- AI-generated interview questions and hiring recommendations
- Candidate comparison dashboard
- Searchable recruiter database with SQLite
- Exportable PDF reports and CSV summaries

---

# 👨‍💻 Author

**Yohan George**

B.Tech Computer Science  (AI & Machine Learning)

VIT Vellore

---

