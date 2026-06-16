import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def compare_candidates(candidate1, candidate2, jd):

    prompt = f"""
You are a senior HR recruiter.

Job Description:

{jd}

Candidate 1

Name: {candidate1["candidate_name"]}

ATS Score: {candidate1["score"]}

Experience: {candidate1["experience"]} years

Projects: {candidate1["projects"]}

Matched Skills:
{", ".join(candidate1["matched"])}

Missing Skills:
{", ".join(candidate1["missing"])}


Candidate 2

Name: {candidate2["candidate_name"]}

ATS Score: {candidate2["score"]}

Experience: {candidate2["experience"]} years

Projects: {candidate2["projects"]}

Matched Skills:
{", ".join(candidate2["matched"])}

Missing Skills:
{", ".join(candidate2["missing"])}


Compare both candidates.

Return:

1. Strengths of Candidate 1

2. Strengths of Candidate 2

3. Who is a better fit

4. Why

Keep it under 200 words.
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3
    )

    return response.choices[0].message.content