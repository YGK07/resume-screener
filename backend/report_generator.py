from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER


def generate_pdf(result, filename):

    styles = getSampleStyleSheet()

    title = styles["Heading1"]
    title.alignment = TA_CENTER

    heading = styles["Heading2"]

    normal = styles["BodyText"]

    pdf = SimpleDocTemplate(filename)

    elements = []

    elements.append(
        Paragraph(
            "AI Resume Screening Report",
            title
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        Paragraph(
            f"<b>Candidate:</b> {result['candidate_name']}",
            normal
        )
    )

    elements.append(
        Paragraph(
            f"<b>Overall ATS Score:</b> {result['score']:.2f}%",
            normal
        )
    )

    elements.append(
        Paragraph(
            f"<b>Semantic Score:</b> {result['semantic_score']:.2f}%",
            normal
        )
    )

    elements.append(
        Paragraph(
            f"<b>Skill Score:</b> {result['skill_score']:.2f}%",
            normal
        )
    )

    elements.append(
        Paragraph(
            f"<b>Experience:</b> {result['experience']} years",
            normal
        )
    )

    elements.append(
        Paragraph(
            f"<b>Projects:</b> {result['projects']}",
            normal
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        Paragraph(
            "Matched Skills",
            heading
        )
    )

    elements.append(
        Paragraph(
            ", ".join(result["matched"]),
            normal
        )
    )

    elements.append(
        Spacer(1, 15)
    )

    elements.append(
        Paragraph(
            "Missing Skills",
            heading
        )
    )

    elements.append(
        Paragraph(
            ", ".join(result["missing"]),
            normal
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        Paragraph(
            "AI Evaluation",
            heading
        )
    )

    elements.append(
        Paragraph(
            result["explanation"],
            normal
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        Paragraph(
            "Resume Improvement Suggestions",
            heading
        )
    )

    elements.append(
        Paragraph(
            result["improvements"],
            normal
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        Paragraph(
            "Interview Questions",
            heading
        )
    )

    elements.append(
        Paragraph(
            result["questions"].replace("\n", "<br/>"),
            normal
        )
    )

    pdf.build(elements)