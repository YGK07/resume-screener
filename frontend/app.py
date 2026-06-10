import streamlit as st
import requests

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

    files = {
        "resume": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "application/pdf"
        )
    }

    data = {
        "job_description": job_description
    }

    try:

        with st.spinner("Analyzing Resume..."):

            response = requests.post(
                "http://127.0.0.1:8000/screen",
                files=files,
                data=data
            )

        if response.status_code != 200:
            st.error(
                f"Backend returned error {response.status_code}"
            )
            st.stop()

        result = response.json()

        st.success("Analysis Complete")

        score = result["score"]

        st.metric(
            "Match Score",
            f"{score}%"
        )

        st.progress(
            min(score / 100, 1.0)
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("✅ Matched Skills")

            if result["matched"]:

                for skill in result["matched"]:
                    st.success(skill)

            else:
                st.info("No matched skills found.")

        with col2:

            st.subheader("❌ Missing Skills")

            if result["missing"]:

                for skill in result["missing"]:
                    st.error(skill)

            else:
                st.success("No missing skills")

        st.divider()

        st.subheader("🤖 AI Evaluation")

        st.write(
            result["explanation"]
        )

    except Exception as e:

        st.error(
            "Unable to connect to FastAPI backend."
        )

        st.code(str(e))