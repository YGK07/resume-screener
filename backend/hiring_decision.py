import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_hiring_decision(candidate, jd):

    prompt = f"""
You are a senior technical recruiter.

Job Description:

{jd}

Candidate Information:

Name: {candidate["candidate_name"]}

ATS Score: {candidate["score"]}

Semantic Score: {candidate["semantic_score"]}

Skill Score: {candidate["skill_score"]}

Experience: {candidate["experience"]} years

Projects: {candidate["projects"]}

Matched Skills:
{", ".join(candidate["matched"])}

Missing Skills:
{", ".join(candidate["missing"])}

Provide:

1. Hire / Maybe Hire / Reject

2. Confidence Percentage

3. Key Strengths

4. Potential Risks

5. Recommended Interview Round

6. Short Recruiter Summary

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

        temperature=0.2
    )

    return response.choices[0].message.content