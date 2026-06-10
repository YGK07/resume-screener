import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_explanation(score, matched, missing):

    prompt = f"""
You are an HR recruitment assistant.

Candidate Match Score: {score}%

Matched Skills:
{', '.join(matched)}

Missing Skills:
{', '.join(missing) if missing else 'None'}

Write a professional evaluation in 3-4 sentences.

Rules:
- If no skills are missing, clearly state that the candidate possesses all required skills.
- Do not mention missing skills if the missing list is empty.
- Explain the match score separately from the skill match.
- End with a hiring recommendation.
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


if __name__ == "__main__":

    score = 64

    matched = [
        "Python",
        "FastAPI",
        "Docker"
    ]

    missing = [
        "AWS",
        "PostgreSQL"
    ]

    explanation = generate_explanation(
        score,
        matched,
        missing
    )

    print(explanation)