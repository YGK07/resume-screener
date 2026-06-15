import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def improve_resume(
    job_description,
    resume_text,
    matched_skills,
    missing_skills
):

    prompt = f"""
You are an expert ATS resume reviewer.

Job Description:

{job_description}

Candidate Resume:

{resume_text}

Matched Skills:

{", ".join(matched_skills)}

Missing Skills:

{", ".join(missing_skills)}

Give professional resume improvement suggestions.

Your response MUST follow this structure.

## Overall Feedback

(2-3 sentences)

## Improvement Suggestions

- bullet
- bullet
- bullet
- bullet

## ATS Keyword Suggestions

- keyword
- keyword

## Estimated ATS Improvement

Explain how much the ATS score could improve after implementing the suggestions.

Do NOT rewrite the resume.
Do NOT mention that you are an AI.
Keep the response under 250 words.
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.4
    )

    return response.choices[0].message.content