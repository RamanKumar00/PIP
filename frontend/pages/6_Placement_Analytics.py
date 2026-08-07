import streamlit as st
import plotly.graph_objects as go
from utils.api_client import api_client
from utils.styles import inject_custom_css, apply_plotly_dark_theme

# Page Configuration
st.set_page_config(
    page_title="Placement Analytics - PlaceMentor AI",
    page_icon="📊",
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
            <span style="font-size:0.75rem; color:#64748B; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">PORTAL / PLACEMENT BI ANALYTICS</span>
            <h2 style="margin:0; font-size:1.6rem; font-weight:800; color:#F8FAFC;" class="neon-text-indigo">Placement Analytics Console</h2>
        </div>
        <span class="badge badge-indigo">Real-Time Analytical BI</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# 1. Fetch Analytics data
metrics = {}
skills = []
interviews = []

with st.spinner("Compiling placement analytical logs..."):
    try:
        dash_res = api_client.get("/roadmap/dashboard-analytics")
        if dash_res.status_code == 200:
            metrics = dash_res.json()
    except Exception:
        pass

    try:
        skills_res = api_client.get("/roadmap/skills")
        if skills_res.status_code == 200:
            skills = skills_res.json()
    except Exception:
        pass

    try:
        int_res = api_client.get("/roadmap/interviews/history")
        if int_res.status_code == 200:
            interviews = int_res.json()
    except Exception:
        pass

if not metrics:
    st.info("Please set up your profile and evaluate company rules to populate placement logs.")
    st.stop()

# 2. Summary KPI cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="stat-lbl">READINESS SCORE</div>
            <div class="stat-val" style="color:#6366F1;">{metrics.get('placement_readiness_percentage', 0)}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="stat-lbl">RESUME ATS SCORE</div>
            <div class="stat-val" style="color:#10B981;">{metrics.get('resume_ats_score', 0)}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="stat-lbl">INTERVIEWS ATTEMPTED</div>
            <div class="stat-val" style="color:#EC4899;">{len(interviews)} Runs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="stat-lbl">TOTAL STUDY TIME</div>
            <div class="stat-val" style="color:#F59E0B;">{metrics.get('total_study_hours', 0.0)} hrs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# 3. Main charts row
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Placement Readiness Trend")
    trend_keys = list(metrics.get("readiness_trend", {}).keys())
    trend_vals = list(metrics.get("readiness_trend", {}).values())
    
    if trend_vals:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend_keys,
            y=trend_vals,
            mode='lines+markers',
            name='Readiness %',
            line=dict(color='#6366F1', width=3),
            marker=dict(size=8, color='#818CF8'),
            fill='tozeroy',
            fillcolor='rgba(99, 102, 241, 0.1)'
        ))
        apply_plotly_dark_theme(fig_trend, height=270)
        fig_trend.update_layout(yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig_trend, use_container_width=True, config={'responsive': True})
    else:
        st.info("No readiness trend records seeded.")

with col_right:
    st.subheader("🛠️ Technical Skill Progress")
    if not skills:
        skills_mock = [
            {"skill_name": "Python", "confidence_score": 75, "mastery_level": "Intermediate"},
            {"skill_name": "Docker", "confidence_score": 30, "mastery_level": "Beginner"},
            {"skill_name": "SQL", "confidence_score": 85, "mastery_level": "Mastered"}
        ]
        s_names = [s["skill_name"] for s in skills_mock]
        s_scores = [s["confidence_score"] for s in skills_mock]
        s_colors = ['#F59E0B', '#FB7185', '#34D399']
    else:
        s_names = [s["skill_name"] for s in skills]
        s_scores = [s["confidence_score"] for s in skills]
        s_colors = []
        for s in skills:
            if s["mastery_level"] == "Mastered":
                s_colors.append('#34D399')
            elif s["mastery_level"] == "Intermediate":
                s_colors.append('#FBBF24')
            else:
                s_colors.append('#FB7185')

    fig_skills = go.Figure(go.Bar(
        x=s_scores,
        y=s_names,
        orientation='h',
        marker_color=s_colors,
        text=s_scores,
        texttemplate='%{text}%',
        textposition='inside',
        insidetextanchor='end'
    ))
    apply_plotly_dark_theme(fig_skills, height=270)
    fig_skills.update_layout(
        margin=dict(l=70, r=20, t=10, b=20),
        xaxis=dict(range=[0, 100]),
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig_skills, use_container_width=True, config={'responsive': True})

# 4. Mock Interview detailed logs
st.write("---")
col_int_left, col_int_right = st.columns([1.5, 2.5])

with col_int_left:
    st.subheader("🎯 Mock Interview Assessment")
    
    avg_tech, avg_comm, avg_comp, avg_gram = 80.0, 75.0, 85.0, 70.0
    if interviews:
        avg_tech = sum(i["technical_score"] for i in interviews) / len(interviews)
        avg_comm = sum(i["communication_score"] for i in interviews) / len(interviews)
        avg_comp = sum(i["completeness_score"] for i in interviews) / len(interviews)
        avg_gram = sum(i["grammar_score"] for i in interviews) / len(interviews)
        
    # Desktop-only radar chart
    st.markdown('<div class="desktop-only-radar">', unsafe_allow_html=True)
    categories = ["Technical", "Communication", "Completeness", "Grammar"]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[avg_tech, avg_comm, avg_comp, avg_gram],
        theta=categories,
        fill='toself',
        line_color='#6366F1'
    ))
    apply_plotly_dark_theme(fig_radar, height=280)
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.05)"),
            bgcolor="rgba(15,23,42,0.6)"
        ),
        margin=dict(l=40, r=40, t=20, b=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={'responsive': True})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mobile-only summary scorecard
    st.markdown('<div class="mobile-only-bar">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="glass-card" style="border-left: 4px solid #6366F1; margin-bottom: 20px;">
            <span style="font-size:0.75rem; color:#94A3B8; font-weight:700; text-transform: uppercase;">Average Strengths</span><br><br>
            <b>Technical Capability:</b> <span style="color:#34D399; font-weight:700;">{int(avg_tech)}%</span><br>
            <b>Communication Skill:</b> <span style="color:#818CF8; font-weight:700;">{int(avg_comm)}%</span><br>
            <b>Content Completeness:</b> <span style="color:#A855F7; font-weight:700;">{int(avg_comp)}%</span><br>
            <b>Grammatical Polish:</b> <span style="color:#EC4899; font-weight:700;">{int(avg_gram)}%</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_int_right:
    st.subheader("📋 Interview Feedback History Log")
    if not interviews:
        st.info("No mock interview attempts recorded yet. Head to the Learning Platform page to practice and learn.")
    else:
        rows_html = ""
        for item in interviews[:5]:
            dt_str = item["created_at"][:16].replace("T", " ")
            rows_html += f"""
            <tr>
                <td style="padding:10px; border-bottom:1px solid rgba(255,255,255,0.06); color:#F8FAFC; white-space:nowrap;">{dt_str}</td>
                <td style="padding:10px; border-bottom:1px solid rgba(255,255,255,0.06); text-align:center;">
                    <span class="badge badge-eligible">{item['overall_score']}%</span>
                </td>
                <td style="padding:10px; border-bottom:1px solid rgba(255,255,255,0.06); color:#94A3B8;">{item['ai_feedback'][:100]}...</td>
            </tr>
            """
        
        table_html = f"""
        <div class="scrollable-table-wrapper">
            <table style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr style="background:rgba(255,255,255,0.03); text-align:left;">
                        <th style="padding:10px; border-bottom:1px solid rgba(255,255,255,0.1); color:#818CF8; white-space:nowrap;">Session Date</th>
                        <th style="padding:10px; border-bottom:1px solid rgba(255,255,255,0.1); color:#818CF8; text-align:center; white-space:nowrap;">Score</th>
                        <th style="padding:10px; border-bottom:1px solid rgba(255,255,255,0.1); color:#818CF8;">Feedback Summary</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)
