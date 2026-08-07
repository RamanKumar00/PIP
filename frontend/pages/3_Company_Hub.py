import streamlit as st
import plotly.graph_objects as go
from utils.api_client import api_client
from utils.styles import inject_custom_css, apply_plotly_dark_theme

# Page configuration
st.set_page_config(
    page_title="Company Hub - PlaceMentor AI",
    page_icon="🏢",
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

# Header Bar
st.markdown(
    """
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span style="font-size:0.75rem; color:#64748B; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">PORTAL / RECRUITER DIRECTORY</span>
            <h2 style="margin:0; font-size:1.6rem; font-weight:800; color:#F8FAFC;" class="neon-text-indigo">Company Placement Hub</h2>
        </div>
        <span class="badge badge-indigo">Weighted Eligibility Engine</span>
    </div>
    """,
    unsafe_allow_html=True,
)


def draw_eligibility_gauge(score: int, title: str, is_eligible: bool):
    """Draw circular gauge for eligibility compatibility.
    """
    color = '#10B981' if is_eligible else '#F43F5E'
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 14, 'color': '#E2E8F0', 'weight': 'bold'}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': color},
            'bgcolor': "rgba(15, 23, 42, 0.6)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.08)",
        }
    ))
    apply_plotly_dark_theme(fig, height=170)
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    return fig


# 1. Check profile/resume completeness
profile_ok = True
resume_ok = True

try:
    p_res = api_client.get("/profile/")
    if p_res.status_code != 200:
        profile_ok = False
except Exception:
    profile_ok = False

try:
    r_res = api_client.get("/resume/latest")
    if r_res.status_code != 200:
        resume_ok = False
except Exception:
    resume_ok = False

if not profile_ok or not resume_ok:
    st.markdown(
        """
        <div class="glass-card" style="border-color: rgba(244, 63, 94, 0.4); background: rgba(244, 63, 94, 0.05);">
            <h4 style="margin:0; color:#FB7185;">⚠️ Profile Details or Resume PDF Missing</h4>
            <p style="color:#94A3B8; margin-top:6px; font-size:0.85rem; line-height:1.5;">
                In order to evaluate recruiter eligibility scores, complete your <b>Academic Profile</b> and upload a parsed <b>Resume PDF</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

# 2. Search & Filter Bar
search_term = st.text_input("🔍 Search Recruiter Directory by Company Name or Industry:", placeholder="e.g. Google, Amazon, Technology...", key="company_search")

# 3. Fetch Companies list
try:
    companies_response = api_client.get("/companies/")
    if companies_response.status_code == 200:
        companies = companies_response.json()
        
        if search_term.strip():
            sterm = search_term.lower().strip()
            companies = [c for c in companies if sterm in c["name"].lower() or (c["industry"] and sterm in c["industry"].lower())]

        if not companies:
            st.info("No recruiter profiles match your search filter.")
        else:
            for comp in companies:
                with st.expander(f"🏢 {comp['name']} — {comp['industry'] or 'Technology'} ({comp['hq_location'] or 'India'})", expanded=False):
                    col_det1, col_det2 = st.columns([2, 1])
                    with col_det1:
                        st.markdown(
                            f"""
                            <b>Website:</b> <a href="{comp['website_url']}" target="_blank" style="color:#818CF8;">{comp['website_url']}</a><br>
                            <b>Careers Portal:</b> <a href="{comp['careers_url']}" target="_blank" style="color:#818CF8;">{comp['careers_url']}</a><br>
                            <b>Hiring Frequency:</b> {comp['hiring_frequency']}<br>
                            <b>Internship/PPO Offerings:</b> {"Yes" if comp['internship_ppo_available'] else "No"}<br>
                            <b>Location Setup:</b> {comp['remote_onsite']}<br>
                            """,
                            unsafe_allow_html=True,
                        )
                    with col_det2:
                        st.markdown(
                            f"""
                            <div class="kpi-card" style="text-align:center;">
                                <span style="font-size:0.75rem; color:#94A3B8;">DATA SOURCE</span><br>
                                <span style="font-weight:700; color:#6366F1;">{comp['data_source']}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        
                    st.write("")
                    st.markdown("### Job Roles & Weighted Eligibility")
                    
                    if not comp["roles"]:
                        st.info("No active hiring roles registered for this company.")
                    else:
                        for role in comp["roles"]:
                            st.markdown(
                                f"""
                                <div class="glass-card" style="margin-bottom: 12px; border-left: 4px solid #6366F1;">
                                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                                        <div>
                                            <h4 style="margin:0; color:#F8FAFC; font-weight:700;">{role['title']}</h4>
                                            <span style="font-size:0.85rem; color:#94A3B8;">CTC Compensation: <b style="color:#10B981;">₹{role['ctc']} LPA</b> | Interview Stages: <b>{role['selection_rounds']} Rounds</b></span>
                                        </div>
                                        <span class="badge badge-indigo">Difficulty: {role['difficulty']}</span>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            
                            tab_el, tab_hiring, tab_topics = st.tabs([
                                "📊 Eligibility Scorecard", "⚔️ Selection Process", "📚 Syllabus & Resources"
                            ])
                            
                            with tab_el:
                                btn_key = f"check_{role['id']}"
                                if st.button(f"Analyze Compatibility Fit for {role['title']}", key=btn_key):
                                    with st.spinner("Executing Weighted Eligibility Engine..."):
                                        eval_res = api_client.get(f"/companies/roles/{role['id']}/check")
                                        if eval_res.status_code == 200:
                                            report = eval_res.json()
                                            
                                            col_gauge, col_report = st.columns([1, 1.8])
                                            with col_gauge:
                                                st.plotly_chart(
                                                    draw_eligibility_gauge(
                                                        report["overall_score"], 
                                                        "COMPATIBILITY FIT", 
                                                        report["is_eligible"]
                                                     ), 
                                                     use_container_width=True,
                                                     config={'responsive': True}
                                                )
                                                
                                            with col_report:
                                                status_html = (
                                                    '<span class="badge badge-eligible" style="font-size:0.9rem; padding:6px 14px;">✓ ELIGIBLE FOR CAMPUS DRIVE</span>'
                                                    if report["is_eligible"]
                                                    else '<span class="badge badge-ineligible" style="font-size:0.9rem; padding:6px 14px;">✖ NOT ELIGIBLE</span>'
                                                )
                                                
                                                st.markdown(
                                                    f"""
                                                    <div style="margin-bottom:12px;">
                                                        <b>Drive Eligibility:</b> {status_html}
                                                    </div>
                                                    <div style="margin-bottom:12px;">
                                                        <b>Estimated Prep Effort:</b> <span style="font-weight:700; color:#F59E0B;">{report['estimated_effort']}</span>
                                                    </div>
                                                    """,
                                                    unsafe_allow_html=True,
                                                )
                                                
                                                if not report["is_eligible"]:
                                                    st.markdown("##### ⚠️ Mismatch Explanations:")
                                                    for reason in report["reasons"]:
                                                        st.markdown(f"<li style='color:#FB7185; font-size:0.9rem;'>{reason}</li>", unsafe_allow_html=True)
                                                else:
                                                    st.success("✓ Excellent alignment! You satisfy all academic criteria and skill weight specifications for this role.")
                                                    
                                            st.write("")
                                            st.markdown("##### Weighted Category Breakdown")
                                            b_cgpa, b_branch, b_back, b_skills, b_resume = st.columns(5)
                                            breakdowns = [
                                                (b_cgpa, "CGPA (20%)", report["breakdown"]["cgpa_score"]),
                                                (b_branch, "Branch (15%)", report["breakdown"]["branch_score"]),
                                                (b_back, "Backlogs (15%)", report["breakdown"]["backlog_score"]),
                                                (b_skills, "Skills (30%)", report["breakdown"]["skills_score"]),
                                                (b_resume, "Resume (20%)", report["breakdown"]["resume_score"]),
                                            ]
                                            for b_col, name, b_score in breakdowns:
                                                with b_col:
                                                    st.markdown(f"<span style='font-size:0.75rem; color:#94A3B8; font-weight:600;'>{name}</span>", unsafe_allow_html=True)
                                                    st.progress(b_score / 100)
                                                    st.markdown(f"<span style='font-size:0.85rem; font-weight:700; color:#F8FAFC;'>{b_score}%</span>", unsafe_allow_html=True)

                                            if report["missing_skills"]:
                                                st.write("")
                                                st.markdown("##### 🛠️ Skill Gaps Detected (Added to your roadmap):")
                                                for m_skill in report["missing_skills"]:
                                                    importance_lbl = "Critical" if m_skill["importance"] == 5 else ("High" if m_skill["importance"] == 4 else "Nice-to-have")
                                                    badge_cls = "badge-ineligible" if m_skill["importance"] >= 4 else "badge-warning"
                                                    st.markdown(
                                                        f"""
                                                        <div class="glass-card" style="padding: 10px 16px; margin-bottom: 6px; display:flex; justify-content:space-between; align-items:center;">
                                                            <div>
                                                                <b>{m_skill['skill_name']}</b> 
                                                                <span style="font-size:0.8rem; color:#94A3B8; margin-left:10px;">(Required Level: {m_skill['required_level']})</span>
                                                            </div>
                                                            <span class="badge {badge_cls}">Importance: {importance_lbl}</span>
                                                        </div>
                                                        """,
                                                        unsafe_allow_html=True,
                                                    )
                                        else:
                                            st.error("Failed to run compatibility check: incomplete profile data.")
                                else:
                                    st.info("Click the button above to calculate eligibility compatibility against your profile and resume.")

                            with tab_hiring:
                                st.write("**Online Assessment (OA) Pattern:**")
                                st.info(role["expected_oa_pattern"] or "OA criteria details not seeded yet.")
                                
                                st.write("**Hiring Round Stages:**")
                                st.write(role["hiring_pattern"] or "Hiring structure details not seeded yet.")
                                
                                if role["interview_experience"]:
                                    st.write("**Candidate Interview Experiences:**")
                                    st.markdown(f"<i>'{role['interview_experience']}'</i>", unsafe_allow_html=True)

                            with tab_topics:
                                col_t1, col_t2 = st.columns(2)
                                with col_t1:
                                    st.write("**Technical Topics Tested:**")
                                    if role["technical_interview_topics"]:
                                        st.markdown(" ".join([f"<span class='badge badge-eligible' style='margin-right:4px; margin-bottom:6px;'>{t}</span>" for t in role["technical_interview_topics"]]), unsafe_allow_html=True)
                                    else:
                                        st.write("Not specified.")
                                with col_t2:
                                    st.write("**Soft Skill / HR Topics Tested:**")
                                    if role["hr_interview_topics"]:
                                        st.markdown(" ".join([f"<span class='badge badge-purple' style='margin-right:4px; margin-bottom:6px;'>{t}</span>" for t in role["hr_interview_topics"]]), unsafe_allow_html=True)
                                    else:
                                        st.write("Not specified.")
                                        
                                st.write("")
                                st.write("**Suggested Preparation Resources:**")
                                if role["preparation_resources"]:
                                    for res_item in role["preparation_resources"]:
                                        st.markdown(f"- {res_item}")
                                else:
                                    st.write("No resource suggestions compiled yet.")

                            st.write("---")
    else:
        st.error("Failed to fetch company details from server.")
except Exception as e:
    st.error(f"Network Connection Error: {e}")
