import time
import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.api_client import api_client
from utils.styles import inject_custom_css, apply_plotly_dark_theme
from utils.components import (
    draw_score_card,
    draw_radar_chart,
    draw_simplified_bar_chart,
    draw_recruiter_card,
    draw_interview_panel,
    draw_benchmark_chart,
    draw_heatmap
)

# Page configuration
st.set_page_config(
    page_title="AI Resume Intelligence - PlaceMentor AI",
    page_icon="🔍",
    layout="wide",
)

# Apply Custom Design System
inject_custom_css()

# Inject meta viewport tag for mobile browser responsiveness
st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">', unsafe_allow_html=True)

# Auth guard check
if "access_token" not in st.session_state or not st.session_state.access_token:
    st.warning("Please log in first from the Command Center Home Page.")
    st.stop()

# Caching fetchers with short TTLs and isolated user sessions (user email hash keys)
@st.cache_data(ttl=60)
def get_cached_profile(user_email: str) -> dict:
    try:
        p_response = api_client.get("/profile/")
        if p_response.status_code == 200:
            return p_response.json()
    except Exception:
        pass
    return {}

@st.cache_data(ttl=30)
def get_cached_latest_resume(user_email: str) -> dict:
    try:
        latest_response = api_client.get("/resume/latest")
        if latest_response.status_code == 200:
            return latest_response.json()
    except Exception:
        pass
    return {}

@st.cache_data(ttl=60)
def get_cached_resume_history(user_email: str) -> list:
    try:
        history_response = api_client.get("/resume/history")
        if history_response.status_code == 200:
            return history_response.json()
    except Exception:
        pass
    return []

# Header Bar
st.markdown(
    """
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span style="font-size:0.75rem; color:#64748B; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">PORTAL / RESUME INTELLIGENCE</span>
            <h2 style="margin:0; font-size:1.6rem; font-weight:800; color:#F8FAFC;" class="neon-text-indigo">AI Resume Intelligence Platform</h2>
        </div>
        <span class="badge badge-indigo">Modular Sub-Analyzers & TF-IDF Semantic matching</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Fetch current target role from profile to prepopulate
profile_data = get_cached_profile(st.session_state.user_email or "default_user")
target_role_default = profile_data.get("preferred_role", "Software Engineer")

# Main Tabs
tab_analyzer, tab_jd_matcher, tab_history = st.tabs([
    "🔍 AI Resume Analyzer", "💼 Job Description Matcher", "⏳ Version History Log"
])


def local_tfidf_similarity(doc1: str, doc2: str) -> int:
    """Computes basic TF-IDF similarity locally for frontend JD matching.
    """
    # Simple tokenization
    def get_tokens(text):
        return re.findall(r"\b[a-z]{2,}\b", text.lower())
        
    t1, t2 = get_tokens(doc1), get_tokens(doc2)
    vocab = set(t1 + t2)
    if not vocab:
        return 0
        
    # Count vectors
    vec1 = {w: t1.count(w) for w in vocab}
    vec2 = {w: t2.count(w) for w in vocab}
    
    # Dot product
    dot = sum(vec1[w] * vec2[w] for w in vocab)
    mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v**2 for v in vec2.values()))
    
    if mag1 == 0 or mag2 == 0:
        return 0
    return int((dot / (mag1 * mag2)) * 100)


def render_analysis_report(resume_data: dict):
    """Render the full redesigned dashboard analysis report.
    """
    analysis = resume_data.get("analysis")
    if not analysis:
        st.warning("Analysis results not found.")
        return

    ats_score = analysis.get("ats_score", 0)
    breakdown = analysis.get("detailed_breakdown") or {}
    strength = analysis.get("strength_meter") or {}
    suggestions = analysis.get("suggestions") or []
    proj_analyses = analysis.get("project_analyses") or []
    skills = analysis.get("detected_skills") or {}
    role_match = analysis.get("role_match") or {}
    
    # Redesigned Fields
    recruiter_report = analysis.get("recruiter_report") or {}
    semantic_analysis = analysis.get("semantic_analysis") or {}
    interview_preparation = analysis.get("interview_preparation") or {}
    analytics_data = analysis.get("analytics_data") or {}
    explanations = analytics_data.get("explanations") or {}

    # Define inner sub-tabs for structured presentation
    sub_dashboard, sub_competencies, sub_coach, sub_prep = st.tabs([
        "📊 Score Dashboard", "🧬 Competency Analytics", "💡 AI Suggestion Coach", "⚔️ Recruiter Sim & Prep"
    ])

    # 1. SUB-TAB: Dashboard Overview
    with sub_dashboard:
        col_gauge, col_rec_decision = st.columns([1, 1.8])
        
        with col_gauge:
            overall_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ats_score,
                title={'text': "OVERALL ATS SCORE", 'font': {'size': 14, 'color': '#818CF8', 'weight': 'bold'}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
                    'bar': {'color': '#6366F1'},
                    'bgcolor': "rgba(15, 23, 42, 0.6)",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(244, 63, 94, 0.1)'},
                        {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.1)'},
                        {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
                    ],
                }
            ))
            apply_plotly_dark_theme(overall_fig, height=220)
            overall_fig.update_layout(margin=dict(l=30, r=30, t=50, b=15))
            st.plotly_chart(overall_fig, use_container_width=True, config={'responsive': True})

        with col_rec_decision:
            draw_recruiter_card(recruiter_report)

        st.write("")
        st.markdown("### Sub-Score Category Breakdown")
        
        # Horizontal Bar Chart for Sub-Scores
        score_labels = [
            "Formatting", "Grammar", "Keywords", "Projects", 
            "Experience", "Achievements", "Contact Info"
        ]
        score_values = [
            breakdown.get("formatting_score", 0),
            breakdown.get("grammar_score", 0),
            breakdown.get("keyword_score", 0),
            breakdown.get("project_score", 0),
            breakdown.get("experience_score", 0),
            breakdown.get("achievements_score", 0),
            breakdown.get("contact_score", 0)
        ]
        # Normalize relative weights to percentage representation
        max_bounds = [20, 20, 20, 20, 10, 10, 10]
        percentages = [int((val / limit) * 100) for val, limit in zip(score_values, max_bounds)]

        fig_breakdown = go.Figure(go.Bar(
            x=percentages,
            y=score_labels,
            orientation='h',
            marker=dict(
                color=['#818CF8', '#34D399', '#FBBF24', '#EC4899', '#10B981', '#6366F1', '#A855F7'],
                line=dict(color='rgba(255,255,255,0.1)', width=1)
            )
        ))
        fig_breakdown.update_layout(
            xaxis=dict(range=[0, 100], gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(autorange="reversed"),
            margin=dict(l=100, r=20, t=10, b=10)
        )
        apply_plotly_dark_theme(fig_breakdown, height=220)
        st.plotly_chart(fig_breakdown, use_container_width=True, config={'responsive': True})

    # 2. SUB-TAB: Competency Analytics
    with sub_competencies:
        col_radar, col_bench = st.columns([1, 1.3])
        
        with col_radar:
            st.markdown("#### Tech Capability Distribution")
            
            # Desktop-only radar chart
            st.markdown('<div class="desktop-only-radar">', unsafe_allow_html=True)
            draw_radar_chart(skills)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Mobile-only simplified bar chart
            st.markdown('<div class="mobile-only-bar">', unsafe_allow_html=True)
            draw_simplified_bar_chart(skills)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_bench:
            draw_benchmark_chart(analytics_data)
            
            # Semantic Similarity indicators
            st.write("")
            sem_pct = semantic_analysis.get("match_percentage", 0)
            st.markdown(
                f"""
                <div class="glass-card" style="border-left: 4px solid #EC4899;">
                    <span style="font-size:0.75rem; color:#94A3B8; font-weight:700;">SEMANTIC COMPATIBILITY RATE</span>
                    <h3 style="margin:4px 0; color:#F8FAFC;">{role_match.get("role_name")}</h3>
                    <h2 style="margin:6px 0; color:#EC4899; font-weight:800;">{sem_pct}% Similarity</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 3. SUB-TAB: AI Coach (Formatting & Rewrite suggestions)
    with sub_coach:
        col_formats, col_heat = st.columns([1, 1])
        
        with col_formats:
            st.markdown("#### Structural Formatting Compliance")
            
            # Sub-analyzers explanations
            for key, val in explanations.items():
                st.markdown(f"**{key.capitalize()} Check:** {val}")
                
        with col_heat:
            draw_heatmap(resume_data.get("sections") or {})

        st.write("---")
        st.markdown("#### Action-Oriented Resume Rewrite suggestions")
        
        if suggestions:
            for idx, sug in enumerate(suggestions):
                cat = sug.get("category", "grammar").upper()
                badge_style = "badge-ineligible" if cat in ["GRAMMAR", "SPELLING"] else "badge-warning"
                
                st.markdown(
                    f"""
                    <div class="glass-card" style="margin-bottom: 12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span class="badge {badge_style}">{cat}</span>
                            <span style="color:#94A3B8; font-size:0.8rem;">Target Area: {sug.get("target", "Global")}</span>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:8px;">
                            <div style="color: #FB7185; font-size:0.88rem;"><b>✖ Current Bullet:</b> <i>"{sug.get("current", "")}"</i></div>
                            <div style="color: #34D399; font-size:0.88rem;"><b>✔ AI Recommended Rewrite:</b> <b>"{sug.get("suggested", "")}"</b></div>
                            <div style="color: #64748B; font-size:0.8rem; border-top:1px solid rgba(255,255,255,0.06); padding-top:6px; margin-top:4px;">
                                💡 <b>Recruiter Rationale:</b> {sug.get("rationale", "")}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("✓ Excellent content! No spelling mistakes or weak project descriptions detected.")

    # 4. SUB-TAB: Recruiter Simulation & Interview Preparation
    with sub_prep:
        draw_interview_panel(interview_preparation)


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
                        max_checks = 120  # 120 checks * 0.5s = 60s total timeout
                        for i in range(1, max_checks + 1):
                            status_response = api_client.get(f"/resume/{resume_id}/status")
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                status = status_data["status"]
                                
                                if status == "pending":
                                    status_box.info("⏳ Queue pending (Celery worker task initializing)...")
                                    progress_bar.progress(15)
                                elif status == "processing":
                                    status_box.info("⚙️ AI Pipeline processing: Extracting PDF text and parsing skills...")
                                    progress_bar.progress(min(40 + i * 2, 95))
                                elif status == "completed":
                                    status_box.success("🎉 Analysis complete! Rendering report...")
                                    progress_bar.progress(100)
                                    # Invalidate cached assets
                                    get_cached_latest_resume.clear()
                                    get_cached_resume_history.clear()
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
                            
                            time.sleep(0.5)
                        
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
    
    try:
        latest_resume = get_cached_latest_resume(st.session_state.user_email or "default_user")
        if latest_resume and latest_resume.get("analysis") and latest_resume["analysis"]["status"] == "completed":
            st.info(f"Showing report for: **{latest_resume['original_filename']}** (Uploaded: {latest_resume['created_at'][:10]})")
            render_analysis_report(latest_resume)
        else:
            st.info("No analyses loaded yet. Upload a resume PDF to trigger the AI Intelligence pipeline.")
    except Exception as e:
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
                    import math # required for local tfidf math
                    latest_resume = get_cached_latest_resume(st.session_state.user_email or "default_user")
                    if latest_resume:
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
                            
                            # Computes local TF-IDF cosine similarity between resume text and pasted JD text
                            similarity_rate = local_tfidf_similarity(latest_resume.get("parsed_text") or "", jd_text)
                            
                            st.markdown(
                                f"""
                                <div class="glass-card" style="border-left:4px solid #10B981;">
                                    <h4 style="margin:0; color:#E2E8F0;">Custom Job Description Semantic Match Score</h4>
                                    <h2 style="margin: 10px 0; color: #10B981; font-weight:800;">{similarity_rate}% Similarity</h2>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            
                            st.markdown(
                                f"""
                                <div class="responsive-grid" style="margin-top: 15px;">
                                    <div>
                                        <b style="color: #FAFAFA;">Matched Technical Skills:</b><br><br>
                                        {" ".join([f"<span class='badge badge-eligible' style='margin-bottom:6px;'>{s}</span>" for s in matched]) if matched else "<span style='color: #71717A;'>No matching skills found in this JD.</span>"}
                                    </div>
                                    <div>
                                        <b style="color: #FAFAFA;">Missing Technical Skills:</b><br><br>
                                        {" ".join([f"<span class='badge badge-ineligible' style='margin-bottom:6px;'>{s}</span>" for s in missing]) if missing else "<span class='badge badge-eligible'>✓ Perfect Match! You have all skills mentioned in the job description.</span>"}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.error("No resumes uploaded. Please upload a resume first.")
                except Exception as e:
                    st.error(f"Error performing comparison: {e}")


# TAB 3. Version History Tab
with tab_history:
    st.subheader("Upload History & Version Restoration Tracker")
    st.write("Track how your ATS and Role Match scores improve across successive uploads. Select any past upload to activate and restore it.")

    try:
        history_list = get_cached_resume_history(st.session_state.user_email or "default_user")
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
                    apply_plotly_dark_theme(fig_history, height=280)
                    st.plotly_chart(fig_history, use_container_width=True, config={'responsive': True})
                
                st.write("")
                st.write("**Restoration Control Log:**")
                for r in history_list:
                    analysis = r.get("analysis")
                    score_text = f"ATS Score: {analysis['ats_score']}%" if analysis and analysis["status"] == "completed" else "Pending/Failed"
                    active_badge = '<span class="badge badge-eligible">ACTIVE VERSION</span>' if r["is_active"] else ""
                    
                    st.markdown(
                        f"""
                        <div class="glass-card" style="padding: 12px 20px; margin-bottom: 8px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                                <div>
                                    <span class="badge badge-indigo" style="margin-right:10px;">Version {r['version']}</span>
                                    <b>{r['original_filename']}</b>
                                    <span style="color:#94A3B8; font-size:0.8rem; margin-left:15px;">({r['created_at'][:10]})</span>
                                    {active_badge}
                                </div>
                                <span style="font-weight:700; color:#818CF8;">{score_text}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # Activate option for inactive ones
                    if not r["is_active"] and analysis and analysis["status"] == "completed":
                        if st.button(f"Activate Version {r['version']}", key=f"act_btn_{r['id']}"):
                            act_res = api_client.put(f"/resume/{r['id']}/activate")
                            if act_res.status_code == 200:
                                st.success(f"Restored Version {r['version']} as the active resume.")
                                st.rerun()
                            else:
                                st.error("Failed to restore version.")
    except Exception:
        st.info("No upload history loaded. Upload a resume to start tracking versions.")
