import pdfplumber


def extract_text(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    # DEBUG
    print("\n========== EXTRACTED RESUME ==========\n")
    print(text[:2000])
    print("\n======================================\n")

    return text


if __name__ == "__main__":

    pdf_path = "../data/uploads/sample_resume.pdf"

    extracted_text = extract_text(pdf_path)

    print(extracted_text)