import streamlit as st
import tempfile
import os
import sys

backend_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "backend"
    )
)

sys.path.append(backend_path)

from main import screen_resume

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Screener")

st.markdown(
    """
    Upload multiple resumes and compare them
    against a job description using AI-powered
    semantic matching and skill analysis.
    """
)

job_description = st.text_area(
    "Enter Job Description",
    height=200,
    placeholder="Paste the job description here..."
)

uploaded_files = st.file_uploader(
    "Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("Analyze Resumes"):

    if not uploaded_files:
        st.warning("Please upload at least one resume.")
        st.stop()

    if not job_description.strip():
        st.warning("Please enter a job description.")
        st.stop()

    results = []

    with st.spinner("Analyzing resumes..."):

        for uploaded_file in uploaded_files:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp_file:

                tmp_file.write(
                    uploaded_file.getvalue()
                )

                temp_path = tmp_file.name

            result = screen_resume(
                temp_path,
                job_description
            )

            results.append({
                "name": uploaded_file.name,
                "score": result["score"],
                "matched": result["matched"],
                "missing": result["missing"],
                "explanation": result["explanation"]
            })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    st.success("Ranking Complete")

    st.subheader("🏆 Resume Rankings")

    for rank, result in enumerate(
        results,
        start=1
    ):

        st.markdown(
            f"## #{rank} - {result['name']}"
        )

        st.metric(
            "Match Score",
            f"{result['score']}%"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("✅ Matched Skills")

            if result["matched"]:
                for skill in result["matched"]:
                    st.write(f"• {skill}")
            else:
                st.write("No matched skills")

        with col2:

            st.subheader("❌ Missing Skills")

            if result["missing"]:
                for skill in result["missing"]:
                    st.write(f"• {skill}")
            else:
                st.write("No missing skills")

        st.subheader("🤖 AI Evaluation")

        st.write(
            result["explanation"]
        )

        st.divider()