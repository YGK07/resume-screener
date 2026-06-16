import streamlit as st
import tempfile
import os
import sys
import pandas as pd
import plotly.express as px
from hiring_decision import generate_hiring_decision
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
from report_generator import generate_pdf
from comparison import compare_candidates  # ADD THIS IMPORT

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

# Initialize session state for tracking if analysis was just performed
if "analysis_performed" not in st.session_state:
    st.session_state["analysis_performed"] = False

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
                "candidate_name": result.get("candidate_name", uploaded_file.name.replace(".pdf", "")),
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
                "questions": result.get("questions", "## Interview Questions\n\nNo interview questions could be generated for this resume."),
                "improvements": result.get("improvements", "No improvement suggestions available."),
                "email": result.get("email", "Not Found"),
                "phone": result.get("phone", "Not Found"),
                "linkedin": result.get("linkedin", "Not Found"),
                "github": result.get("github", "Not Found")
            })
            save_result(results[-1])
            os.unlink(temp_path)

    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Save results to session state
    st.session_state["results"] = results
    st.session_state["job_description"] = job_description
    st.session_state["analysis_performed"] = True

# ==================================
# RESTORE RESULTS FROM SESSION STATE
# ==================================

if "results" in st.session_state:
    results = st.session_state["results"]
    job_description = st.session_state.get("job_description", "")
else:
    results = []

# ==================================
# HELPER FUNCTION FOR SAFE FLOAT CONVERSION
# ==================================

def safe_float(value, default=0.0):
    """Safely convert a value to float."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

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
        0,
        key="recruiter_min_score"
    )
    
    min_experience = st.slider(
        "Minimum Experience (Years)",
        0,
        20,
        0,
        key="recruiter_min_experience"
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
        ],
        key="recruiter_must_have_skill"
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
    
    current_results = filtered_results
    
    st.info(
        f"Showing {len(current_results)} matching resumes."
    )

    total_resumes = len(current_results)
    
    # Only show metrics if there are results after filtering
    if total_resumes > 0:
        average_score = round(sum(r["score"] for r in current_results) / total_resumes, 2)
        best_score = round(current_results[0]["score"], 2)
        qualified_count = len([r for r in current_results if r["score"] >= 70])

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
            "Resume": [r["candidate_name"] for r in current_results],
            "Score": [r["score"] for r in current_results]
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

        for rank, result in enumerate(current_results, start=1):
            table_data.append({
                "Rank": rank,
                "Candidate": result["candidate_name"],
                "Resume File": result["name"],
                "Score (%)": round(result["score"], 2),
                "Matched Skills": len(result["matched"]),
                "Missing Skills": len(result["missing"]),
                "Email": result.get("email", "Not Found"),
                "Phone": result.get("phone", "Not Found")
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

        candidate_names = [
            r["candidate_name"]
            for r in current_results
        ]

        if len(candidate_names) >= 2:
            col1, col2 = st.columns(2)

            with col1:
                candidate1 = st.selectbox(
                    "Candidate 1",
                    candidate_names,
                    key="compare_candidate1"
                )

            with col2:
                candidate2 = st.selectbox(
                    "Candidate 2",
                    candidate_names,
                    index=1 if len(candidate_names) > 1 else 0,
                    key="compare_candidate2"
                )

            if st.button("Compare Selected Candidates", key="compare_button"):
                r1 = next(
                    r for r in current_results
                    if r["candidate_name"] == candidate1
                )

                r2 = next(
                    r for r in current_results
                    if r["candidate_name"] == candidate2
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
                        "Missing Skills",
                        "Email",
                        "Phone",
                        "LinkedIn",
                        "GitHub"
                    ],
                    candidate1: [
                        f"{r1['score']:.2f}%",
                        f"{r1['semantic_score']:.2f}%",
                        f"{r1['skill_score']:.2f}%",
                        f"{r1['experience']} Years",
                        r1["projects"],
                        f"{r1['education_score']}%",
                        f"{r1['certification_score']}%",
                        len(r1["matched"]),
                        len(r1["missing"]),
                        r1.get("email", "Not Found"),
                        r1.get("phone", "Not Found"),
                        r1.get("linkedin", "Not Found"),
                        r1.get("github", "Not Found")
                    ],
                    candidate2: [
                        f"{r2['score']:.2f}%",
                        f"{r2['semantic_score']:.2f}%",
                        f"{r2['skill_score']:.2f}%",
                        f"{r2['experience']} Years",
                        r2["projects"],
                        f"{r2['education_score']}%",
                        f"{r2['certification_score']}%",
                        len(r2["matched"]),
                        len(r2["missing"]),
                        r2.get("email", "Not Found"),
                        r2.get("phone", "Not Found"),
                        r2.get("linkedin", "Not Found"),
                        r2.get("github", "Not Found")
                    ]
                })

                st.dataframe(
                    comparison,
                    use_container_width=True
                )

                st.subheader("🏅 Winner")

                if r1["score"] > r2["score"]:
                    st.success(
                        f"🏆 {candidate1} is the stronger candidate."
                    )
                elif r2["score"] > r1["score"]:
                    st.success(
                        f"🏆 {candidate2} is the stronger candidate."
                    )
                else:
                    st.info(
                        "Both candidates have the same overall score."
                    )
        else:
            st.info("Need at least 2 candidates to compare.")

        st.subheader("🏆 Detailed Candidate Analysis")

        # ==================================
        # DETAILED ANALYSIS
        # ==================================

        for rank, result in enumerate(current_results, start=1):
            display_name = result.get("candidate_name", result["name"].replace(".pdf", ""))
            st.markdown(f"## #{rank} - {display_name}")
            st.caption(f"📄 File: {result['name']}")
            
            # ==================================
            # CANDIDATE PROFILE
            # ==================================
            
            st.subheader("👤 Candidate Profile")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Safely get score as float
                score = safe_float(result.get("score", 0))
                
                st.metric(
                    "ATS Score",
                    f"{score:.2f}%"
                )
                # Ensure progress value is between 0.0 and 1.0
                progress_value = max(0.0, min(1.0, score / 100))
                st.progress(progress_value)
            
            with col2:
                # Display contact information
                st.write(f"**📧 Email:** {result.get('email', 'Not Found')}")
                st.write(f"**📞 Phone:** {result.get('phone', 'Not Found')}")
                st.write(f"**💼 Experience:** {safe_float(result.get('experience', 0)):.1f} years")
                st.write(f"**📂 Projects:** {result.get('projects', 0)}")
                
                # Display LinkedIn if available
                linkedin = result.get('linkedin', 'Not Found')
                if linkedin != "Not Found" and linkedin:
                    st.markdown(f"**🔗 LinkedIn:** {linkedin}")
                else:
                    st.write("**🔗 LinkedIn:** Not Found")
                
                # Display GitHub if available
                github = result.get('github', 'Not Found')
                if github != "Not Found" and github:
                    st.markdown(f"**💻 GitHub:** {github}")
                else:
                    st.write("**💻 GitHub:** Not Found")
            
            st.divider()

            # ==================================
            # ATS BREAKDOWN
            # ==================================

            st.subheader("📈 ATS Score Breakdown")

            col1, col2 = st.columns(2)

            with col1:
                # Semantic Match
                semantic_score = safe_float(result.get("semantic_score", 0))
                semantic_value = max(0, min(100, int(semantic_score)))
                st.progress(semantic_value / 100)
                st.write(f"Semantic Match: {semantic_score:.2f}%")

                # Skill Match
                skill_score = safe_float(result.get("skill_score", 0))
                skill_value = max(0, min(100, int(skill_score)))
                st.progress(skill_value / 100)
                st.write(f"Skill Match: {skill_score:.2f}%")

                # Experience
                exp_years = safe_float(result.get("experience", 0))
                exp_score = min(exp_years * 20, 100)
                exp_value = max(0, min(100, int(exp_score)))
                st.progress(exp_value / 100)
                st.write(f"Experience: {exp_years:.1f} Years")

            with col2:
                # Projects
                projects = result.get("projects", 0)
                if isinstance(projects, str):
                    try:
                        projects = int(projects)
                    except (ValueError, TypeError):
                        projects = 0
                project_score = min(projects * 10, 100)
                project_value = max(0, min(100, int(project_score)))
                st.progress(project_value / 100)
                st.write(f"Projects: {projects}")

                # Education
                edu_score = safe_float(result.get("education_score", 0))
                edu_value = max(0, min(100, int(edu_score)))
                st.progress(edu_value / 100)
                st.write(f"Education Score: {edu_score:.2f}%")

                # Certification
                cert_score = safe_float(result.get("certification_score", 0))
                cert_value = max(0, min(100, int(cert_score)))
                st.progress(cert_value / 100)
                st.write(f"Certification Score: {cert_score:.2f}%")

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
                title=f"{display_name} - Skill Match"
            )

            st.plotly_chart(
                pie_fig,
                use_container_width=True
            )

            st.subheader("🤖 AI Evaluation")
            st.write(result["explanation"])
            # ==================================
	    # AI HIRING DECISION
 	    # ==================================

	    st.subheader("🎯 AI Hiring Decision")

	    with st.spinner("Evaluating candidate..."):

   	        hiring_decision = generate_hiring_decision(
                    result,
                    job_description
                )

            st.markdown(hiring_decision)
            st.subheader("💡 AI Resume Improvement Suggestions")
            st.info(result["improvements"])

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

            # ==================================
            # PDF REPORT - ADDED HERE
            # ==================================
            
            st.subheader("📄 Download Report")
            
            # Generate PDF report for this candidate
            pdf_name = f"{result['candidate_name']}_report.pdf"
            
            try:
                generate_pdf(result, pdf_name)
                
                with open(pdf_name, "rb") as pdf_file:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_file,
                        file_name=pdf_name,
                        mime="application/pdf",
                        key=f"pdf_{rank}_{result['candidate_name']}"
                    )
                
                # Clean up the PDF file after download button is created
                if os.path.exists(pdf_name):
                    os.remove(pdf_name)
                    
            except Exception as e:
                st.error(f"Could not generate PDF report: {str(e)}")
            
            st.divider()
        
        # ============================================================
        # AI CANDIDATE COMPARISON (ADDED AFTER THE DETAILED ANALYSIS LOOP)
        # ============================================================
        
        if len(current_results) >= 2:
            st.header("⚖️ AI Candidate Comparison")
            
            # Get the top 2 candidates for comparison
            candidate1 = current_results[0]
            candidate2 = current_results[1]
            
            # Create comparison table
            comparison_df = pd.DataFrame({
                "Metric": [
                    "ATS Score",
                    "Semantic Score",
                    "Skill Score",
                    "Experience",
                    "Projects",
                    "Education Score",
                    "Certification Score",
                    "Matched Skills",
                    "Missing Skills",
                    "Email",
                    "Phone",
                    "LinkedIn",
                    "GitHub"
                ],
                candidate1["candidate_name"]: [
                    f"{safe_float(candidate1['score']):.2f}%",
                    f"{safe_float(candidate1['semantic_score']):.2f}%",
                    f"{safe_float(candidate1['skill_score']):.2f}%",
                    f"{safe_float(candidate1['experience']):.1f} Years",
                    candidate1["projects"],
                    f"{safe_float(candidate1['education_score']):.2f}%",
                    f"{safe_float(candidate1['certification_score']):.2f}%",
                    len(candidate1["matched"]),
                    len(candidate1["missing"]),
                    candidate1.get("email", "Not Found"),
                    candidate1.get("phone", "Not Found"),
                    candidate1.get("linkedin", "Not Found"),
                    candidate1.get("github", "Not Found")
                ],
                candidate2["candidate_name"]: [
                    f"{safe_float(candidate2['score']):.2f}%",
                    f"{safe_float(candidate2['semantic_score']):.2f}%",
                    f"{safe_float(candidate2['skill_score']):.2f}%",
                    f"{safe_float(candidate2['experience']):.1f} Years",
                    candidate2["projects"],
                    f"{safe_float(candidate2['education_score']):.2f}%",
                    f"{safe_float(candidate2['certification_score']):.2f}%",
                    len(candidate2["matched"]),
                    len(candidate2["missing"]),
                    candidate2.get("email", "Not Found"),
                    candidate2.get("phone", "Not Found"),
                    candidate2.get("linkedin", "Not Found"),
                    candidate2.get("github", "Not Found")
                ]
            })
            
            st.dataframe(
                comparison_df,
                use_container_width=True
            )
            
            # ==================================
            # AI COMPARISON SUMMARY
            # ==================================
            
            st.subheader("🤖 AI Recruiter Comparison")
            
            with st.spinner("Comparing candidates..."):
                try:
                    comparison = compare_candidates(
                        candidate1,
                        candidate2,
                        job_description
                    )
                    st.write(comparison)
                except Exception as e:
                    st.error(f"Error during AI comparison: {str(e)}")
                    st.info("Showing fallback comparison instead.")
                    
                    # Fallback comparison
                    st.write(f"**{candidate1['candidate_name']}** vs **{candidate2['candidate_name']}**")
                    st.write(f"- ATS Score: {candidate1['score']:.1f}% vs {candidate2['score']:.1f}%")
                    st.write(f"- Experience: {candidate1['experience']} years vs {candidate2['experience']} years")
                    st.write(f"- Matched Skills: {len(candidate1['matched'])} vs {len(candidate2['matched'])}")
                    st.write(f"- Missing Skills: {len(candidate1['missing'])} vs {len(candidate2['missing'])}")
                    
                    if candidate1['score'] > candidate2['score']:
                        st.success(f"**Recommended: {candidate1['candidate_name']}**")
                    elif candidate2['score'] > candidate1['score']:
                        st.success(f"**Recommended: {candidate2['candidate_name']}**")
                    else:
                        st.info("Both candidates are equally matched.")
            
            # ==================================
            # AI COMPARISON INSIGHTS
            # ==================================
            
            st.subheader("📊 Comparison Insights")
            
            # Generate insights based on comparison
            insights = []
            
            # Score comparison
            score1 = safe_float(candidate1['score'])
            score2 = safe_float(candidate2['score'])
            score_diff = abs(score1 - score2)
            
            if score_diff > 10:
                if score1 > score2:
                    insights.append(f"📊 **{candidate1['candidate_name']}** has a significantly higher ATS score ({score1:.1f}% vs {score2:.1f}%)")
                else:
                    insights.append(f"📊 **{candidate2['candidate_name']}** has a significantly higher ATS score ({score2:.1f}% vs {score1:.1f}%)")
            
            # Experience comparison
            exp1 = safe_float(candidate1['experience'])
            exp2 = safe_float(candidate2['experience'])
            if exp1 != exp2:
                if exp1 > exp2:
                    insights.append(f"💼 **{candidate1['candidate_name']}** has more experience ({exp1:.1f} years vs {exp2:.1f} years)")
                else:
                    insights.append(f"💼 **{candidate2['candidate_name']}** has more experience ({exp2:.1f} years vs {exp1:.1f} years)")
            
            # Projects comparison
            proj1 = candidate1.get('projects', 0)
            proj2 = candidate2.get('projects', 0)
            if isinstance(proj1, str):
                try:
                    proj1 = int(proj1)
                except:
                    proj1 = 0
            if isinstance(proj2, str):
                try:
                    proj2 = int(proj2)
                except:
                    proj2 = 0
            
            if proj1 != proj2:
                if proj1 > proj2:
                    insights.append(f"📂 **{candidate1['candidate_name']}** has more projects ({proj1} vs {proj2})")
                else:
                    insights.append(f"📂 **{candidate2['candidate_name']}** has more projects ({proj2} vs {proj1})")
            
            # Skills comparison
            matched1 = len(candidate1["matched"])
            matched2 = len(candidate2["matched"])
            if matched1 != matched2:
                if matched1 > matched2:
                    insights.append(f"✅ **{candidate1['candidate_name']}** has more matched skills ({matched1} vs {matched2})")
                else:
                    insights.append(f"✅ **{candidate2['candidate_name']}** has more matched skills ({matched2} vs {matched1})")
            
            # Missing skills comparison
            missing1 = len(candidate1["missing"])
            missing2 = len(candidate2["missing"])
            if missing1 != missing2:
                if missing1 < missing2:
                    insights.append(f"❌ **{candidate1['candidate_name']}** has fewer missing skills ({missing1} vs {missing2})")
                else:
                    insights.append(f"❌ **{candidate2['candidate_name']}** has fewer missing skills ({missing2} vs {missing1})")
            
            # Display insights
            if insights:
                for insight in insights:
                    st.write(f"• {insight}")
            else:
                st.info("Both candidates are closely matched in all metrics.")
            
            # ==================================
            # RECOMMENDATION
            # ==================================
            
            st.subheader("🎯 Recommendation")
            
            if score1 > score2:
                st.success(f"🏆 **Recommended Candidate:** {candidate1['candidate_name']}")
                st.write(f"**Reason:** {candidate1['candidate_name']} has a higher overall ATS score ({score1:.1f}%) compared to {candidate2['candidate_name']} ({score2:.1f}%).")
            elif score2 > score1:
                st.success(f"🏆 **Recommended Candidate:** {candidate2['candidate_name']}")
                st.write(f"**Reason:** {candidate2['candidate_name']} has a higher overall ATS score ({score2:.1f}%) compared to {candidate1['candidate_name']} ({score1:.1f}%).")
            else:
                st.info("Both candidates have the same ATS score. Consider interviewing both.")
            
            # Display shared skills
            shared_skills = set(candidate1["matched"]) & set(candidate2["matched"])
            if shared_skills:
                st.write(f"**Common Strengths:** {', '.join(sorted(shared_skills))}")
            
            # Display skills only candidate1 has
            unique_to_c1 = set(candidate1["matched"]) - set(candidate2["matched"])
            if unique_to_c1:
                st.write(f"**Unique to {candidate1['candidate_name']}:** {', '.join(sorted(unique_to_c1))}")
            
            # Display skills only candidate2 has
            unique_to_c2 = set(candidate2["matched"]) - set(candidate1["matched"])
            if unique_to_c2:
                st.write(f"**Unique to {candidate2['candidate_name']}:** {', '.join(sorted(unique_to_c2))}")
            
            st.divider()
        
    else:
        st.warning("No resumes match the current filter criteria. Please adjust your filters.")
else:
    if analyze or st.session_state.get("analysis_performed", False):
        st.error("No results to display. Please check your inputs and try again.")
    else:
        st.info("👈 Click 'Analyze Resumes' to start screening")

# ==================================
# CANDIDATE DATABASE SEARCH
# ==================================

st.subheader("🔍 Search Candidate Database")

search_candidate = st.text_input(
    "Candidate Name",
    key="search_candidate"
)

minimum_score = st.slider(
    "Minimum Score",
    0,
    100,
    0,
    key="search_min_score"
)

minimum_experience = st.slider(
    "Minimum Experience (Years)",
    0,
    20,
    0,
    key="search_min_experience"
)

# ==================================
# DISPLAY ANALYSIS HISTORY
# ==================================

st.subheader("📚 Analysis History")

# Pass search_candidate directly - empty string will match all records
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
            "PDF File",
            "Candidate Name",
            "Score",
            "Semantic Score",
            "Skill Score",
            "Experience",
            "Projects",
            "Education Score",
            "Certification Score",
            "Matched Skills",
            "Missing Skills",
            "Analyzed On"
        ]
    )
    st.dataframe(
        history_df,
        use_container_width=True
    )
    
    # Add download button for history
    csv_history = history_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download History as CSV",
        data=csv_history,
        file_name="resume_history.csv",
        mime="text/csv",
        key="download_history"
    )
else:
    st.info("No history available. Please analyze some resumes first.")