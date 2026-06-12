import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_interview_questions(
    jd,
    resume_text
):

    prompt = f"""
You are a senior technical recruiter.

Job Description:

{jd}

Candidate Resume:

{resume_text}

Generate 5 technical interview questions.

Requirements:

- Questions should match the resume.
- Questions should match the job description.
- Do NOT include answers.
- Number them from 1 to 5.
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.5
    )

    return response.choices[0].message.content