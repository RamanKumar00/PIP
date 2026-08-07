import streamlit as st
import plotly.graph_objects as go
from utils.styles import apply_plotly_dark_theme

def draw_score_card(score: int, title: str, subtext: str, color_hex: str):
    """Draws a premium glass card displaying a metric score.
    """
    st.markdown(
        f"""
        <div class="glass-card" style="border-left: 4px solid {color_hex}; height: 100%;">
            <span style="font-size: 0.72rem; color: #94A3B8; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">{title}</span>
            <h1 style="margin: 6px 0; color: {color_hex}; font-weight: 800; font-size: 2.2rem; line-height: 1;">{score}%</h1>
            <span style="font-size: 0.78rem; color: #64748B;">{subtext}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def draw_radar_chart(skills_dict: dict):
    """Draws a Plotly Radar Chart mapping candidate skill distribution across domains.
    """
    if not skills_dict:
        skills_dict = {}
        
    categories = ["Programming", "Backend", "Frontend", "Databases", "Tools", "Cloud"]
    # Compute counts of skills extracted in each category
    values = [
        len(skills_dict.get("programming") or []),
        len(skills_dict.get("backend") or []),
        len(skills_dict.get("frontend") or []),
        len(skills_dict.get("database") or []),
        len(skills_dict.get("tools") or []),
        len(skills_dict.get("cloud") or [])
    ]
    
    # Pad to close the radar loop
    radar_categories = categories + [categories[0]]
    radar_values = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=radar_values,
        theta=radar_categories,
        fill='toself',
        fillcolor='rgba(99, 102, 241, 0.15)',
        line=dict(color='#818CF8', width=2),
        marker=dict(color='#6366F1', size=6),
        name='Your Profile'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max(values) + 1, 5)],
                showticklabels=False,
                ticks='',
                gridcolor='rgba(255, 255, 255, 0.06)'
            ),
            angularaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.06)',
                linecolor='rgba(255, 255, 255, 0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False
    )
    apply_plotly_dark_theme(fig, height=250)
    fig.update_layout(margin=dict(l=40, r=40, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})


def draw_simplified_bar_chart(skills_dict: dict):
    """Draws a simplified horizontal bar chart of skills for mobile devices.
    """
    if not skills_dict:
        skills_dict = {}
        
    categories = ["Programming", "Backend", "Frontend", "Databases", "Tools", "Cloud"]
    values = [
        len(skills_dict.get("programming") or []),
        len(skills_dict.get("backend") or []),
        len(skills_dict.get("frontend") or []),
        len(skills_dict.get("database") or []),
        len(skills_dict.get("tools") or []),
        len(skills_dict.get("cloud") or [])
    ]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker=dict(color='#818CF8')
    ))
    apply_plotly_dark_theme(fig, height=220)
    fig.update_layout(
        margin=dict(l=90, r=15, t=15, b=15),
        xaxis=dict(gridcolor='rgba(255,255,255,0.06)', dtick=1)
    )
    st.plotly_chart(fig, use_container_width=True, config={'responsive': True})


def draw_recruiter_card(report: dict):
    """Draws simulated recruiter screening analysis block.
    """
    if not report:
        report = {}
        
    decision = report.get("screening_decision", "Borderline Screen")
    strengths = report.get("strengths", [])
    reservations = report.get("reservations", [])
    
    # Decision badge class
    if "shortlist" in decision.lower():
        badge_cls = "badge-eligible"
        border_color = "#10B981"
    elif "borderline" in decision.lower():
        badge_cls = "badge-warning"
        border_color = "#F59E0B"
    else:
        badge_cls = "badge-ineligible"
        border_color = "#F43F5E"

    st.markdown(
        f"""
<div class="glass-card" style="border-left: 4px solid {border_color}; margin-bottom: 20px;">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom: 12px;">
<h4 style="margin: 0; color: #F8FAFC; font-weight: 800;">Simulated Recruiter Screen Decision</h4>
<span class="badge {badge_cls}" style="font-size:0.8rem; padding: 4px 12px;">{decision.upper()}</span>
</div>
<div style="margin-top: 15px;">
<span style="font-size:0.75rem; color:#34D399; font-weight:700;">PROS / CANDIDATE STRENGTHS:</span>
<ul style="color: #94A3B8; font-size:0.85rem; margin-top:6px; line-height:1.5; padding-left: 20px;">
{"".join([f"<li>{s}</li>" for s in strengths])}
</ul>
</div>
<div style="margin-top: 15px;">
<span style="font-size:0.75rem; color:#FB7185; font-weight:700;">CONS / RESERVATIONS & GAPS:</span>
<ul style="color: #94A3B8; font-size:0.85rem; margin-top:6px; line-height:1.5; padding-left: 20px;">
{"".join([f"<li>{r}</li>" for r in reservations])}
</ul>
</div>
</div>
        """,
        unsafe_allow_html=True
    )


def draw_interview_panel(prep: dict):
    """Draws custom technical/behavioral interview preparation guides.
    """
    if not prep:
        prep = {}
        
    readiness_score = prep.get("interview_readiness_score", 50)
    questions = prep.get("interview_questions", [])
    
    col_score, col_text = st.columns([1, 2.5])
    with col_score:
        draw_score_card(
            readiness_score, 
            "INTERVIEW READINESS", 
            "Combined technical capabilities and project scores", 
            "#818CF8"
        )
        
    with col_text:
        st.markdown(
            """
            <div class="glass-card" style="height: 100%;">
                <h4 style="margin-top: 0; color: #F8FAFC; font-weight: 700;">Placement Readiness Assessment</h4>
                <p style="color: #94A3B8; font-size: 0.85rem; line-height: 1.5; margin: 0;">
                    Your interview readiness rating is calculated by scaling your core technical skills volume, 
                    the structural quality scores of your technical projects description, and your grammatical formatting scores. 
                    Target reaching <b>80%+ Readiness</b> to maximize double-digit campus package conversions.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    st.markdown("#### Dynamic Mock Interview Prep Questions")
    if not questions:
        st.info("No practice questions compiled. Complete analysis to generate tailored interview prep guides.")
    else:
        for idx, q in enumerate(questions):
            qtype = q.get("type", "technical").upper()
            badge_style = "badge-indigo" if qtype == "TECHNICAL" else "badge-purple"
            st.markdown(
                f"""
                <div class="glass-card" style="margin-bottom: 12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span class="badge {badge_style}">{qtype}</span>
                        <span style="color:#64748B; font-size:0.75rem;">Source: {q.get('reason')}</span>
                    </div>
                    <p style="color:#F8FAFC; font-size:0.92rem; font-weight: 600; margin: 4px 0;">{idx+1}. {q.get('question')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


def draw_benchmark_chart(analytics: dict):
    """Draws target role eligibility constraints checklist.
    """
    if not analytics or "benchmark_comparison" not in analytics:
        st.info("Benchmark checks are only active when evaluating against specific registered recruiter requirements from the Company Hub.")
        return

    bench = analytics["benchmark_comparison"]
    if not bench.get("target_gpa"):
        st.info("Benchmark checks are only active when evaluating against specific registered recruiter requirements from the Company Hub.")
        return

    st.markdown("#### Recruiting Eligibility Threshold Checks")
    
    gpa_met = bench.get("gpa_met", False)
    gpa_color = "#10B981" if gpa_met else "#F43F5E"
    
    branch_met = bench.get("allowed_branch", False)
    branch_color = "#10B981" if branch_met else "#F43F5E"
    allowed_str = ", ".join(bench.get("target_branches") or [])
    
    back_met = bench.get("backlogs_checked", False)
    back_color = "#10B981" if back_met else "#F43F5E"
    
    st.markdown(
        f"""
        <div class="responsive-grid">
            <div class="kpi-card" style="text-align: center; border-top: 3px solid {gpa_color}; margin-bottom: 0;">
                <span style="font-size:0.7rem; color:#94A3B8; font-weight:700; text-transform: uppercase;">Academic CGPA</span>
                <h3 style="margin:6px 0; color:#F8FAFC;">{bench.get('student_gpa')} / 10</h3>
                <span class="badge {'badge-eligible' if gpa_met else 'badge-ineligible'}">Required: {bench.get('target_gpa')}</span>
            </div>
            <div class="kpi-card" style="text-align: center; border-top: 3px solid {branch_color}; margin-bottom: 0;">
                <span style="font-size:0.7rem; color:#94A3B8; font-weight:700; text-transform: uppercase;">Academic Branch</span>
                <h3 style="margin:6px 0; color:#F8FAFC;">{bench.get('student_branch')}</h3>
                <span class="badge {'badge-eligible' if branch_met else 'badge-ineligible'}" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;">Allowed: {allowed_str}</span>
            </div>
            <div class="kpi-card" style="text-align: center; border-top: 3px solid {back_color}; margin-bottom: 0;">
                <span style="font-size:0.7rem; color:#94A3B8; font-weight:700; text-transform: uppercase;">Active Backlogs</span>
                <h3 style="margin:6px 0; color:#F8FAFC;">Passed</h3>
                <span class="badge {'badge-eligible' if back_met else 'badge-ineligible'}">Criteria Satisfied</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def draw_heatmap(sections_dict: dict):
    """Draws horizontal heatmap indicating section character density ratios.
    """
    if not sections_dict:
        sections_dict = {}
        
    core_keys = ["education", "experience", "projects", "skills", "certifications"]
    lengths = []
    labels = []
    
    for key in core_keys:
        labels.append(key.capitalize())
        lengths.append(len(sections_dict.get(key) or ""))

    total_len = sum(lengths)
    if total_len == 0:
        st.info("No text content detected across core sections to render heatmap.")
        return

    percentages = [int((val / total_len) * 100) for val in lengths]

    st.markdown("#### Resume Section Density Heatmap")
    st.write("Skimming heatmaps trace the relative textual distribution of details across sections. A balanced resume has high experience and projects density.")

    # Renders a custom styled segmented progress bar resembling a horizontal heatmap
    heatmap_html = '<div style="display:flex; height: 26px; border-radius: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 12px;">'
    colors = ["#6366F1", "#A855F7", "#EC4899", "#10B981", "#F59E0B"]
    
    for label, pct, color in zip(labels, percentages, colors):
        if pct > 0:
            heatmap_html += f'<div style="width: {pct}%; background-color: {color}; display: flex; align-items: center; justify-content: center; font-size: 0.68rem; font-weight: 800; color: white;" title="{label}: {pct}%">{pct}%</div>'
    heatmap_html += '</div>'

    st.markdown(heatmap_html, unsafe_allow_html=True)
    
    # Legend
    legend_html = '<div style="display:flex; flex-wrap:wrap; gap: 12px; font-size:0.75rem;">'
    for label, color in zip(labels, colors):
        legend_html += f'<span style="display:inline-flex; align-items:center; gap:5px;"><span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:{color};"></span><span style="color:#94A3B8;">{label}</span></span>'
    legend_html += '</div>'
    st.markdown(legend_html, unsafe_allow_html=True)
