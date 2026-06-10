import streamlit as st
import tempfile
import sys
import os

sys.path.append("../backend")

from main import screen_resume



st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Screener")
st.markdown(
    "Upload a resume and compare it against a job description using AI-powered semantic matching and skill analysis."
)

job_description = st.text_area(
    "Enter Job Description",
    height=200,
    placeholder="Paste the job description here..."
)

uploaded_file = st.file_uploader(
    "Upload Resume PDF",
    type=["pdf"]
)

if st.button("Analyze Resume"):

    if uploaded_file is None:
        st.warning("Please upload a resume.")
        st.stop()

    if not job_description.strip():
        st.warning("Please enter a job description.")
        st.stop()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp_file:

        tmp_file.write(
            uploaded_file.getvalue()
        )

        temp_path = tmp_file.name

    with st.spinner("Analyzing Resume..."):

        result = screen_resume(
            temp_path,
            job_description
        )

    st.success("Analysis Complete")

    st.metric(
        "Match Score",
        f"{result['score']}%"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("✅ Matched Skills")

        for skill in result["matched"]:
            st.write(f"• {skill}")

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