import streamlit as st
import tempfile
import os
import sys
import pandas as pd
import plotly.express as px

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
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name

            result = screen_resume(temp_path, job_description)

            results.append({
                "name": uploaded_file.name,
                "score": result["score"],
                "matched": result["matched"],
                "missing": result["missing"],
                "explanation": result["explanation"],
                "resume_text": result["resume_text"]
            })
            os.unlink(temp_path)

    results.sort(key=lambda x: x["score"], reverse=True)

    st.success("Ranking Complete")

    # ==================================
    # RECRUITER DASHBOARD
    # ==================================

    st.subheader("📊 Recruiter Dashboard")

    total_resumes = len(results)
    average_score = round(sum(r["score"] for r in results) / total_resumes, 2)
    best_score = round(results[0]["score"], 2)
    qualified_count = len([r for r in results if r["score"] >= 70])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Resumes", total_resumes)

    with col2:
        st.metric("Average Score", f"{average_score}%")

    with col3:
        st.metric("Top Score", f"{best_score}%")

    with col4:
        st.metric("Qualified", qualified_count)

    # ==================================
    # PLOTLY BAR CHART
    # ==================================

    chart_df = pd.DataFrame({
        "Resume": [r["name"] for r in results],
        "Score": [r["score"] for r in results]
    })

    fig = px.bar(
        chart_df,
        x="Resume",
        y="Score",
        title="Resume Ranking Scores"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==================================
    # RANKING TABLE
    # ==================================

    table_data = []

    for rank, result in enumerate(results, start=1):
        table_data.append({
            "Rank": rank,
            "Resume": result["name"],
            "Score (%)": round(result["score"], 2),
            "Matched Skills": len(result["matched"]),
            "Missing Skills": len(result["missing"])
        })

    ranking_df = pd.DataFrame(table_data)

    st.subheader("📊 Resume Ranking Table")
    st.dataframe(ranking_df, use_container_width=True)

    csv = ranking_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Rankings as CSV",
        data=csv,
        file_name="resume_rankings.csv",
        mime="text/csv"
    )

    st.subheader("🏆 Detailed Resume Analysis")

    # ==================================
    # DETAILED ANALYSIS
    # ==================================

    for rank, result in enumerate(results, start=1):
        st.markdown(f"## #{rank} - {result['name']}")
        st.metric("Match Score", f"{result['score']:.2f}%")

        if result["score"] >= 80:
            st.success("⭐ Strong Match")
        elif result["score"] >= 60:
            st.info("👍 Good Match")
        elif result["score"] >= 40:
            st.warning("⚠️ Needs Review")
        else:
            st.error("❌ Not Recommended")

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

        # ==================================
        # SKILL DISTRIBUTION PIE CHART
        # ==================================

        st.subheader("🥧 Skill Distribution")

        pie_df = pd.DataFrame({
            "Category": [
                "Matched Skills",
                "Missing Skills"
            ],
            "Count": [
                len(result["matched"]),
                len(result["missing"])
            ]
        })

        pie_fig = px.pie(
            pie_df,
            names="Category",
            values="Count",
            hole=0.45,
            title=f"{result['name']} Skill Match"
        )

        st.plotly_chart(
            pie_fig,
            use_container_width=True
        )

        st.subheader("🤖 AI Evaluation")
        st.write(result["explanation"])

        # ===========================
        # Resume Preview
        # ===========================

        st.subheader("🔍 Resume Preview")
        preview = result["resume_text"]

        # Highlight matched skills
        for skill in result["matched"]:
            preview = preview.replace(skill, f":green[{skill}]")

        # Highlight missing skills
        for skill in result["missing"]:
            preview = preview.replace(skill, f":red[{skill}]")

        st.markdown(preview)
        st.divider()