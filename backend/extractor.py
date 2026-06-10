import pdfplumber
import re


def extract_text(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    # DEBUG: show raw extracted text
    print("\n===== RAW TEXT =====")
    print(text[:1000])
    print("====================\n")

    # Replace email addresses
    text = re.sub(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "[EMAIL]",
        text
    )

    # Replace Indian phone numbers
    text = re.sub(
        r"\b(?:\+91[\s\-]?)?[6-9]\d{9}\b",
        "[PHONE]",
        text
    )

    return text


if __name__ == "__main__":

    pdf_path = "../data/uploads/sample_resume.pdf"

    extracted_text = extract_text(pdf_path)

    print("===== CLEANED TEXT =====")
    print(extracted_text)
    print("========================")