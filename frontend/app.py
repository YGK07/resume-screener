import streamlit as st
import tempfile
import os
import sys
import pandas as pd
import plotly.express as px

# ==================================
# ADD BACKEND FOLDER TO PYTHON PATH
# ==================================

backend_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "backend"
    )
)

sys.path.append(backend_path)

# ==================================
# IMPORT BACKEND MODULES
# ==================================

from main import screen_resume

from database import (
    initialize_database,
    save_result,
    load_history
)

# ==================================
# INITIALIZE DATABASE
# ==================================

initialize_database()

# ==================================
# STREAMLIT PAGE
# ==================================

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

# ==================================
# ANALYSIS BUTTON AND SESSION STATE
# ==================================

analyze = st.button("Analyze Resumes")
if analyze:
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

            # Store all information from the result with error handling for questions
            results.append({
                "name": uploaded_file.name,
                "score": result.get("score", 0),
                "semantic_score": result.get("semantic_score", 0),
                "skill_score": result.get("skill_score", 0),
                "experience": result.get("experience", 0),
                "projects": result.get("projects", 0),
                "education_score": result.get("education_score", 0),
                "certification_score": result.get("certification_score", 0),
                "matched": result.get("matched", []),
                "missing": result.get("missing", []),
                "resume_text": result.get("resume_text", ""),
                "explanation": result.get("explanation", "No explanation available."),
                "questions": result.get("questions", "## Interview Questions\n\nNo interview questions could be generated for this resume.")
            })
            save_result(results[-1])
            os.unlink(temp_path)

    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Save results to session state
    st.session_state["results"] = results
    st.session_state["job_description"] = job_description

# ==================================
# RESTORE RESULTS FROM SESSION STATE
# ==================================

if "results" in st.session_state:
    results = st.session_state["results"]
    job_description = st.session_state.get("job_description", "")
else:
    results = []

# ==================================
# DISPLAY RESULTS IF AVAILABLE
# ==================================

if results:
    st.success("Ranking Complete")

    # ==================================
    # RECRUITER DASHBOARD
    # ==================================

    st.subheader("📊 Recruiter Dashboard")
    
    # ==================================
    # RECRUITER FILTERS
    # ==================================
    
    st.subheader("🔍 Recruiter Filters")
    
    min_score = st.slider(
        "Minimum Match Score",
        0,
        100,
        0
    )
    
    min_experience = st.slider(
        "Minimum Experience (Years)",
        0,
        20,
        0
    )
    
    must_have_skill = st.selectbox(
        "Required Skill",
        [
            "None",
            "Python",
            "FastAPI",
            "AWS",
            "Docker",
            "PostgreSQL",
            "Git",
            "Redis",
            "Kubernetes",
            "Linux"
        ]
    )
    
    # Apply filters
    filtered_results = []
    
    for r in results:
        if r["score"] < min_score:
            continue
        if r["experience"] < min_experience:
            continue
        if (
            must_have_skill != "None"
            and must_have_skill not in r["matched"]
        ):
            continue
        filtered_results.append(r)
    
    results = filtered_results
    
    st.info(
        f"Showing {len(results)} matching resumes."
    )

    total_resumes = len(results)
    
    # Only show metrics if there are results after filtering
    if total_resumes > 0:
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

        # ==================================
        # SIDE BY SIDE RESUME COMPARISON
        # ==================================

        st.subheader("⚔️ Compare Two Resumes")

        resume_names = [
            r["name"]
            for r in results
        ]

        col1, col2 = st.columns(2)

        with col1:
            resume1 = st.selectbox(
                "Resume 1",
                resume_names,
                key="resume1"
            )

        with col2:
            resume2 = st.selectbox(
                "Resume 2",
                resume_names,
                index=1 if len(resume_names) > 1 else 0,
                key="resume2"
            )

        if st.button("Compare Selected Resumes"):
            r1 = next(
                r for r in results
                if r["name"] == resume1
            )

            r2 = next(
                r for r in results
                if r["name"] == resume2
            )

            comparison = pd.DataFrame({
                "Metric": [
                    "Overall Score",
                    "Semantic Score",
                    "Skill Score",
                    "Experience",
                    "Projects",
                    "Education Score",
                    "Certification Score",
                    "Matched Skills",
                    "Missing Skills"
                ],
                resume1: [
                    f"{r1['score']:.2f}%",
                    f"{r1['semantic_score']:.2f}%",
                    f"{r1['skill_score']:.2f}%",
                    f"{r1['experience']} Years",
                    r1["projects"],
                    f"{r1['education_score']}%",
                    f"{r1['certification_score']}%",
                    len(r1["matched"]),
                    len(r1["missing"])
                ],
                resume2: [
                    f"{r2['score']:.2f}%",
                    f"{r2['semantic_score']:.2f}%",
                    f"{r2['skill_score']:.2f}%",
                    f"{r2['experience']} Years",
                    r2["projects"],
                    f"{r2['education_score']}%",
                    f"{r2['certification_score']}%",
                    len(r2["matched"]),
                    len(r2["missing"])
                ]
            })

            st.dataframe(
                comparison,
                use_container_width=True
            )

            st.subheader("🏅 Winner")

            if r1["score"] > r2["score"]:
                st.success(
                    f"🏆 {resume1} is the stronger candidate."
                )
            elif r2["score"] > r1["score"]:
                st.success(
                    f"🏆 {resume2} is the stronger candidate."
                )
            else:
                st.info(
                    "Both resumes have the same overall score."
                )

        st.subheader("🏆 Detailed Resume Analysis")

        # ==================================
        # DETAILED ANALYSIS
        # ==================================

        for rank, result in enumerate(results, start=1):
            st.markdown(f"## #{rank} - {result['name']}")
            st.metric("Match Score", f"{result['score']:.2f}%")

            # ==================================
            # ATS BREAKDOWN
            # ==================================

            st.subheader("📈 ATS Score Breakdown")

            col1, col2 = st.columns(2)

            with col1:
                # Semantic Match
                semantic_value = max(0, min(100, int(result["semantic_score"])))
                st.progress(semantic_value)
                st.write(f"Semantic Match: {result['semantic_score']:.2f}%")

                # Skill Match
                skill_value = max(0, min(100, int(result["skill_score"])))
                st.progress(skill_value)
                st.write(f"Skill Match: {result['skill_score']:.2f}%")

                # Experience
                exp_score = min(result["experience"] * 20, 100)
                exp_value = max(0, min(100, int(exp_score)))
                st.progress(exp_value)
                st.write(f"Experience: {result['experience']} Years")

            with col2:
                # Projects
                project_score = min(result["projects"] * 10, 100)
                project_value = max(0, min(100, int(project_score)))
                st.progress(project_value)
                st.write(f"Projects: {result['projects']}")

                # Education
                edu_value = max(0, min(100, int(result["education_score"])))
                st.progress(edu_value)
                st.write(f"Education Score: {result['education_score']}%")

                # Certification
                cert_value = max(0, min(100, int(result["certification_score"])))
                st.progress(cert_value)
                st.write(f"Certification Score: {result['certification_score']}%")

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

            # ==================================
            # AI INTERVIEW QUESTIONS
            # ==================================

            st.subheader("🎤 AI Interview Questions")
            
            # Check if questions exist and display them
            if result.get("questions"):
                st.markdown(result["questions"])
            else:
                st.info("No interview questions generated for this resume.")

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
    else:
        st.warning("No resumes match the current filter criteria. Please adjust your filters.")
else:
    if analyze:
        st.error("No results to display. Please check your inputs and try again.")
    else:
        st.info("👈 Click 'Analyze Resumes' to start screening")
st.subheader("🔍 Search Candidate Database")

search_candidate = st.text_input(
    "Candidate Name"
)

minimum_score = st.slider(
    "Minimum Score",
    0,
    100,
    0
)

minimum_experience = st.slider(
    "Minimum Experience",
    0,
    20,
    0
)
st.subheader("📚 Analysis History")

history = load_history(
    search_candidate,
    minimum_score,
    minimum_experience
)
st.success(
    f"{len(history)} candidate(s) found."
)

if history:
    history_df = pd.DataFrame(
        history,
        columns=[
            "ID",
            "Candidate",
            "Score",
            "Semantic",
            "Skill",
            "Experience",
            "Projects",
            "Education",
            "Certification",
            "Matched",
            "Missing",
            "Date"
        ]
    )
    st.dataframe(
        history_df,
        use_container_width=True
    )
else:
    st.info("No history available.")