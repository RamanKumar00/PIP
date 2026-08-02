import time
import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.api_client import api_client
from utils.styles import inject_custom_css, apply_plotly_dark_theme

# Page Configuration
st.set_page_config(
    page_title="AI Resume Analyzer - PlaceMentor AI",
    page_icon="📄",
    layout="wide",
)

# Apply Custom Design System
inject_custom_css()

# Auth guard check
if "access_token" not in st.session_state or not st.session_state.access_token:
    st.warning("Please log in first from the Command Center Home Page.")
    st.stop()

# Header Bar
st.markdown(
    """
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span style="font-size:0.75rem; color:#64748B; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">PORTAL / RESUME INTELLIGENCE</span>
            <h2 style="margin:0; font-size:1.6rem; font-weight:800; color:#F8FAFC;" class="neon-text-indigo">AI Resume Intelligence Engine</h2>
        </div>
        <span class="badge badge-indigo">PyMuPDF & spaCy Core</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Fetch current target role from profile to prepopulate
target_role_default = "Software Engineer"
try:
    p_response = api_client.get("/profile/")
    if p_response.status_code == 200:
        target_role_default = p_response.json().get("preferred_role", "Software Engineer")
except Exception:
    pass

# Main Tabs
tab_analyzer, tab_jd_matcher, tab_history = st.tabs([
    "🔍 AI Resume Analyzer", "💼 Job Description Matcher", "⏳ Version History Log"
])


def draw_gauge_chart(score: int, title: str, color: str):
    """Draw circular gauge chart for sub-scores using Plotly.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 13, 'color': '#E2E8F0', 'bold': True}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': color},
            'bgcolor': "rgba(15, 23, 42, 0.6)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.08)",
        }
    ))
    apply_plotly_dark_theme(fig, height=145)
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    return fig


def render_analysis_report(resume_data: dict):
    """Render the full dashboard analysis report.
    """
    analysis = resume_data.get("analysis")
    if not analysis:
        st.warning("Analysis results not found.")
        return

    ats_score = analysis.get("ats_score", 0)
    breakdown = analysis.get("detailed_breakdown", {})
    strength = breakdown.get("strength_meter", {})
    suggestions = analysis.get("suggestions", [])
    proj_analyses = breakdown.get("project_analyses", [])
    skills = analysis.get("detected_skills", {})
    role_match = analysis.get("role_match", {})

    # 1. Top Section - ATS Score & Strength Meter
    col1, col2 = st.columns([1, 1.8])
    
    with col1:
        overall_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ats_score,
            title={'text': "OVERALL ATS SCORE", 'font': {'size': 15, 'color': '#818CF8', 'bold': True}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': '#6366F1'},
                'bgcolor': "rgba(15, 23, 42, 0.6)",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(244, 63, 94, 0.12)'},
                    {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.12)'},
                    {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.12)'}
                ],
            }
        ))
        apply_plotly_dark_theme(overall_fig, height=220)
        st.plotly_chart(overall_fig, use_container_width=True)

    with col2:
        quality_lbl = strength.get("quality_label", "Good")
        stars = strength.get("stars", 4)
        stars_str = "★" * stars + "☆" * (5 - stars)
        
        st.markdown(
            f"""
            <div class="glass-card" style="height: 100%; border-left:4px solid #6366F1;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin-top:0; color:#F8FAFC;">Quality Assessment: <span class="neon-text-indigo">{quality_lbl}</span></h3>
                    <span class="badge badge-indigo">{quality_lbl.upper()} LEVEL</span>
                </div>
                <div style="font-size: 1.5rem; color: #F59E0B; margin: 6px 0 12px 0;">{stars_str}</div>
                <div style="color: #94A3B8; font-size: 0.9rem; line-height: 1.6;">
                    {analysis.get("overall_feedback", "")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 2. Categorized Sub-Scores Row
    st.write("")
    st.markdown("### Score Breakdown Categories")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    categories = [
        ("Formatting", int((breakdown.get("formatting_score", 0) / 20) * 100), '#818CF8'),
        ("Grammar", int((breakdown.get("grammar_score", 0) / 20) * 100), '#34D399'),
        ("Keywords", int((breakdown.get("keyword_score", 0) / 20) * 100), '#FBBF24'),
        ("Projects", int((breakdown.get("project_score", 0) / 20) * 100), '#EC4899'),
        ("Experience", int((breakdown.get("experience_score", 0) / 10) * 100), '#10B981'),
        ("Achievements", int((breakdown.get("achievements_score", 0) / 10) * 100), '#6366F1'),
    ]

    for col, (title, score, color) in zip([c1, c2, c3, c4, c5, c6], categories):
        with col:
            st.plotly_chart(draw_gauge_chart(score, title, color), use_container_width=True)

    st.write("---")

    # 3. Role Matching & Extracted Skills
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### Target Role Alignment")
        role_name = role_match.get("role_name", "Software Engineer")
        match_pct = role_match.get("match_percentage", 0)
        
        st.markdown(
            f"""
            <div class="glass-card" style="border-left:4px solid #10B981;">
                <span style="font-size:0.75rem; color:#94A3B8; font-weight:700;">TARGET ROLE MATCH</span>
                <h3 style="margin:4px 0; color:#F8FAFC;">{role_name}</h3>
                <h1 style="margin:6px 0; color:#10B981; font-weight:800;">{match_pct}%</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.write("**Matched Core Skills:**")
        matched_skills = role_match.get("matched_skills", [])
        if matched_skills:
            st.markdown(" ".join([f"<span class='badge badge-eligible' style='margin-right:4px; margin-bottom:6px;'>{s}</span>" for s in matched_skills]), unsafe_allow_html=True)
        else:
            st.write("None matched yet.")
            
        st.write("")
        st.write("**Missing Core Skills (Add to boost match rate):**")
        missing_skills_list = role_match.get("missing_skills", [])
        if missing_skills_list:
            st.markdown(" ".join([f"<span class='badge badge-ineligible' style='margin-right:4px; margin-bottom:6px;'>{s}</span>" for s in missing_skills_list]), unsafe_allow_html=True)
        else:
            st.success("Perfect alignment! No missing core skills for this role.")

    with col_right:
        st.markdown("### Extracted Skills Matrix")
        with st.expander("💻 Programming Languages", expanded=True):
            st.markdown(" ".join([f"<span class='badge badge-indigo' style='margin-right:4px; margin-bottom:6px;'>{s}</span>" for s in skills.get("programming", [])]), unsafe_allow_html=True)
        with st.expander("⚙️ Backend Frameworks"):
            st.markdown(" ".join([f"<span class='badge badge-indigo' style='margin-right:4px; margin-bottom:6px;'>{s}</span>" for s in skills.get("backend", [])]), unsafe_allow_html=True)
        with st.expander("🎨 Frontend Technologies"):
            st.markdown(" ".join([f"<span class='badge badge-indigo' style='margin-right:4px; margin-bottom:6px;'>{s}</span>" for s in skills.get("frontend", [])]), unsafe_allow_html=True)
        with st.expander("🗄️ Databases"):
            st.markdown(" ".join([f"<span class='badge badge-indigo' style='margin-right:4px; margin-bottom:6px;'>{s}</span>" for s in skills.get("database", [])]), unsafe_allow_html=True)
        with st.expander("🛠️ Development Tools"):
            st.markdown(" ".join([f"<span class='badge badge-indigo' style='margin-right:4px; margin-bottom:6px;'>{s}</span>" for s in skills.get("tools", [])]), unsafe_allow_html=True)
        with st.expander("☁️ Cloud Providers"):
            st.markdown(" ".join([f"<span class='badge badge-indigo' style='margin-right:4px; margin-bottom:6px;'>{s}</span>" for s in skills.get("cloud", [])]), unsafe_allow_html=True)

    st.write("---")

    # 4. Project Quality Reviews
    st.markdown("### Project Description Reviews")
    if proj_analyses:
        for proj in proj_analyses:
            with st.container():
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0; color:#F8FAFC;">{proj.get("title", "Project Review")}</h4>
                            <span class="badge badge-eligible">Quality Score: {proj.get("score", 0)}/100</span>
                        </div>
                        <ul style="color:#94A3B8; margin-top:10px; line-height:1.6;">
                            {''.join([f"<li>{s}</li>" for s in proj.get("suggestions", [])])}
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No projects detected. Include a 'Projects' section header to analyze project descriptions.")

    st.write("---")

    # 5. Grammar & AI Metrics Suggestions
    st.markdown("### AI Action-Verb & Metric Recommendations")
    if suggestions:
        for idx, sug in enumerate(suggestions):
            with st.container():
                cat = sug.get("category", "grammar").upper()
                badge_style = "badge-ineligible" if cat in ["GRAMMAR", "SPELLING"] else "badge-warning"
                
                st.markdown(
                    f"""
                    <div class="glass-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span class="badge {badge_style}">{cat}</span>
                            <span style="color:#94A3B8; font-size:0.8rem;">Target Section: {sug.get("target", "Global")}</span>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:8px;">
                            <div style="color: #FB7185; font-size:0.9rem;"><b>✖ Current:</b> <i>"{sug.get("current", "")}"</i></div>
                            <div style="color: #34D399; font-size:0.9rem;"><b>✔ Suggested:</b> <b>"{sug.get("suggested", "")}"</b></div>
                            <div style="color: #94A3B8; font-size:0.8rem; border-top:1px solid rgba(255,255,255,0.06); padding-top:6px; margin-top:4px;">
                                💡 <b>Rationale:</b> {sug.get("rationale", "")}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.success("Clean Result! No grammar errors or suggestions found.")


# TAB 1. Analyzer Dashboard Tab
with tab_analyzer:
    col_up1, col_up2 = st.columns([1, 1])
    with col_up1:
        uploaded_file = st.file_uploader("Upload Resume PDF (Max 5MB)", type=["pdf"])
    with col_up2:
        target_role = st.selectbox(
            "Target Placement Role",
            ["Backend Developer", "Frontend Developer", "Full Stack Developer", "Data Scientist", "Data Analyst", "DevOps Engineer", "Product Manager"],
            index=["Backend Developer", "Frontend Developer", "Full Stack Developer", "Data Scientist", "Data Analyst", "DevOps Engineer", "Product Manager"].index(target_role_default) if target_role_default in ["Backend Developer", "Frontend Developer", "Full Stack Developer", "Data Scientist", "Data Analyst", "DevOps Engineer", "Product Manager"] else 0
        )

    if st.button("Trigger AI Analysis Engine", type="primary"):
        if not uploaded_file:
            st.error("Please select a PDF file first.")
        else:
            success = False
            with st.spinner("Uploading file and triggering Celery worker queue..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    data = {"target_role": target_role}
                    
                    response = api_client.post("/resume/upload", data=data, files=files)
                    if response.status_code == 201:
                        resume_info = response.json()
                        resume_id = resume_info["id"]
                        
                        status_box = st.empty()
                        progress_bar = st.progress(0)
                        
                        status = "pending"
                        for i in range(1, 21):
                            status_response = api_client.get(f"/resume/{resume_id}/status")
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                status = status_data["status"]
                                
                                if status == "pending":
                                    status_box.info("⏳ Queue pending (Celery worker task initializing)...")
                                    progress_bar.progress(15)
                                elif status == "processing":
                                    status_box.info("⚙️ AI Pipeline processing: Extracting PDF text and parsing skills...")
                                    progress_bar.progress(40 + i * 2)
                                elif status == "completed":
                                    status_box.success("🎉 Analysis complete! Rendering report...")
                                    progress_bar.progress(100)
                                    time.sleep(0.5)
                                    status_box.empty()
                                    progress_bar.empty()
                                    break
                                elif status == "failed":
                                    status_box.error(f"❌ Analysis failed: {status_data.get('error_message')}")
                                    progress_bar.empty()
                                    break
                            else:
                                status_box.error("Error fetching parser status from API server.")
                                break
                            
                            time.sleep(1.5)
                        
                        if status == "completed":
                            st.session_state.latest_analysis_id = resume_id
                            success = True
                    else:
                        st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Network Connection Error: {e}")

            if success:
                st.rerun()

    # Display latest report
    st.write("---")
    st.subheader("Latest Analysis Report")
    
    try:
        latest_response = api_client.get("/resume/latest")
        if latest_response.status_code == 200:
            latest_resume = latest_response.json()
            if latest_resume.get("analysis") and latest_resume["analysis"]["status"] == "completed":
                st.info(f"Showing report for: **{latest_resume['original_filename']}** (Uploaded: {latest_resume['created_at'][:10]})")
                render_analysis_report(latest_resume)
            else:
                st.warning("Latest resume upload is processing or failed.")
        else:
            st.info("No analyses loaded yet. Upload a resume PDF to trigger the AI Intelligence pipeline.")
    except Exception:
        st.info("No analyses loaded yet. Complete your profile and upload a resume to begin.")


# TAB 2. Job Description Matcher Tab
with tab_jd_matcher:
    st.subheader("Verify Custom Job Description Fit")
    st.write("Paste a job description below to check ATS keyword overlap and compatibility against your latest uploaded resume.")
    
    jd_text = st.text_area("Paste Job Description Text:", height=180, placeholder="Paste job requirements here...")
    
    if st.button("Compare Resume vs Job Description"):
        if not jd_text.strip():
            st.error("Please paste job description text.")
        else:
            with st.spinner("Matching skills against JD text..."):
                try:
                    latest_response = api_client.get("/resume/latest")
                    if latest_response.status_code == 200:
                        latest_resume = latest_response.json()
                        analysis = latest_resume.get("analysis")
                        
                        if not analysis:
                            st.error("Please complete the initial Resume Analysis tab first.")
                        else:
                            detected_skills_matrix = analysis.get("detected_skills", {})
                            flat_skills = []
                            for lst in detected_skills_matrix.values():
                                flat_skills.extend([s.lower() for s in lst])
                            
                            technical_vocab = [
                                "python", "java", "c++", "c#", "javascript", "typescript", "golang", "rust",
                                "fastapi", "flask", "django", "node.js", "express", "spring", "graphql", "rest api", "celery",
                                "react", "streamlit", "angular", "vue", "next.js", "tailwind", "redux",
                                "postgresql", "sqlite", "mysql", "redis", "mongodb", "cassandra", "dynamodb",
                                "docker", "git", "github", "gitlab", "ci/cd", "jenkins", "kubernetes", "terraform",
                                "aws", "gcp", "azure", "vercel", "heroku", "api security", "unit tests", "agile", "jira"
                            ]
                            
                            jd_lower = jd_text.lower()
                            required_jd_skills = []
                            for vocab in technical_vocab:
                                if re.search(r"\b" + re.escape(vocab) + r"\b", jd_lower):
                                    display_name = vocab.capitalize() if vocab not in ["fastapi", "next.js", "node.js", "ci/cd"] else vocab
                                    required_jd_skills.append(display_name)
                                    
                            required_jd_skills = list(set(required_jd_skills))
                            if not required_jd_skills:
                                required_jd_skills = ["SQL", "Git", "REST APIs"]
                                
                            matched = [s for s in required_jd_skills if s.lower() in flat_skills]
                            missing = [s for s in required_jd_skills if s.lower() not in flat_skills]
                                    
                            match_rate = int((len(matched) / len(required_jd_skills)) * 100) if required_jd_skills else 100
                            
                            st.markdown(
                                f"""
                                <div class="glass-card" style="border-left:4px solid #10B981;">
                                    <h4 style="margin:0; color:#E2E8F0;">Custom Job Description Match Score</h4>
                                    <h2 style="margin: 10px 0; color: #10B981; font-weight:800;">{match_rate}%</h2>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            
                            col_jd1, col_jd2 = st.columns(2)
                            with col_jd1:
                                st.write("**Matched Skills:**")
                                if matched:
                                    st.markdown(" ".join([f"<span class='badge badge-eligible'>{s}</span>" for s in matched]), unsafe_allow_html=True)
                                else:
                                    st.write("No matching skills found in this JD.")
                            with col_jd2:
                                st.write("**Missing Skills:**")
                                if missing:
                                    st.markdown(" ".join([f"<span class='badge badge-ineligible'>{s}</span>" for s in missing]), unsafe_allow_html=True)
                                else:
                                    st.success("Perfect Match! You have all skills mentioned in the job description.")
                    else:
                        st.error("No resumes uploaded. Please upload a resume first.")
                except Exception as e:
                    st.error(f"Error performing comparison: {e}")


# TAB 3. Version History Tab
with tab_history:
    st.subheader("Upload History & Progression Tracking")
    st.write("Track how your ATS and Role Match scores improve across successive uploads.")

    try:
        history_response = api_client.get("/resume/history")
        if history_response.status_code == 200:
            history_list = history_response.json()
            
            if not history_list:
                st.info("No upload logs found. Upload your first resume to start tracking versions.")
            else:
                chart_data = []
                for res_item in reversed(history_list):
                    analysis = res_item.get("analysis")
                    if analysis and analysis["status"] == "completed":
                        chart_data.append({
                            "Version": f"V{res_item['version']}",
                            "ATS Score": analysis["ats_score"],
                            "Role Match Score": analysis["role_match_score"],
                            "Filename": res_item["original_filename"]
                        })
                
                if chart_data:
                    df = pd.DataFrame(chart_data)
                    fig_history = px.line(
                        df, 
                        x="Version", 
                        y=["ATS Score", "Role Match Score"],
                        markers=True,
                        title="Placement Readiness Progression",
                        color_discrete_sequence=['#6366F1', '#10B981']
                    )
                    apply_plotly_dark_theme(fig_history, height=320)
                    st.plotly_chart(fig_history, use_container_width=True)
                
                st.write("")
                st.write("**Upload History Log:**")
                for r in history_list:
                    analysis = r.get("analysis")
                    score_text = f"ATS Score: {analysis['ats_score']}%" if analysis and analysis["status"] == "completed" else "Pending/Failed"
                    st.markdown(
                        f"""
                        <div class="glass-card" style="padding: 12px 20px; margin-bottom: 8px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <span class="badge badge-indigo" style="margin-right:10px;">Version {r['version']}</span>
                                    <b>{r['original_filename']}</b>
                                    <span style="color:#94A3B8; font-size:0.8rem; margin-left:15px;">({r['created_at'][:10]})</span>
                                </div>
                                <span style="font-weight:700; color:#818CF8;">{score_text}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.error("Error retrieving upload history logs.")
    except Exception:
        st.info("No upload history loaded. Upload a resume to start tracking versions.")
