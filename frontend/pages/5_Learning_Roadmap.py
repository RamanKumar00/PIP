import streamlit as st
import plotly.graph_objects as go
from utils.api_client import api_client
from utils.styles import inject_custom_css, apply_plotly_dark_theme

# Page Configuration
st.set_page_config(
    page_title="Learning Roadmap - PlaceMentor AI",
    page_icon="🎯",
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
            <span style="font-size:0.75rem; color:#64748B; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">PORTAL / LEARNING COACH</span>
            <h2 style="margin:0; font-size:1.6rem; font-weight:800; color:#F8FAFC;" class="neon-text-indigo">Placement Learning Coach</h2>
        </div>
        <span class="badge badge-indigo">Kanban & AI Quizzes</span>
    </div>
    """,
    unsafe_allow_html=True,
)


def draw_score_gauge(score: int, title: str):
    """Draw circular progress indicator for interview/quiz scores.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 14, 'color': '#E2E8F0', 'bold': True}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': '#6366F1'},
            'bgcolor': "rgba(15, 23, 42, 0.6)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.08)",
        }
    ))
    apply_plotly_dark_theme(fig, height=150)
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
    return fig


# 1. Fetch study tasks
tasks = []
try:
    res = api_client.get("/roadmap/tasks")
    if res.status_code == 200:
        tasks = res.json()
except Exception as e:
    st.error(f"Failed to fetch roadmap tasks: {e}")

# 2. Main layout tabs
tab_board, tab_quiz, tab_interview = st.tabs([
    "📋 Kanban Taskboard", "🎓 Practice Quiz Console", "⚔️ Mock Interview Simulator"
])

# TAB 1: Taskboard & Timelines
with tab_board:
    if not tasks:
        st.markdown(
            """
            <div class="glass-card" style="text-align:center; padding: 40px 20px;">
                <h3 style="color:#F8FAFC; margin-top:0; font-weight:800;">📋 No Study Tasks Generated Yet</h3>
                <p style="color:#94A3B8; line-height:1.6; max-width:600px; margin: 10px auto;">
                    To populate your study board, navigate to the <b>Company Hub</b> page and evaluate your eligibility against any target role (like Google SDE). 
                    The Placement Coach will automatically detect skill gaps and build study schedules.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        completed_tasks = [t for t in tasks if t["status"] == "Completed"]
        total_tasks = len(tasks)
        completion_rate = int((len(completed_tasks) / total_tasks) * 100)
        
        st.markdown(f"**Overall Study Board Completion:** {len(completed_tasks)} / {total_tasks} Tasks finished ({completion_rate}%)")
        st.progress(completion_rate / 100)
        st.write("")

        # Display tasks in Kanban columns
        col_todo, col_progress, col_done = st.columns(3)
        
        with col_todo:
            st.markdown("<h4 style='color:#FB7185; border-bottom: 2px solid #FB7185; padding-bottom:6px; margin-bottom:16px; font-weight:700;'>Not Started</h4>", unsafe_allow_html=True)
            todo_tasks = [t for t in tasks if t["status"] == "Not Started"]
            if not todo_tasks:
                st.info("No pending tasks in this column.")
            else:
                for task in todo_tasks:
                    with st.container():
                        st.markdown(
                            f"""
                            <div class="glass-card" style="margin-bottom:12px; border-left:3px solid #FB7185;">
                                <span class="badge badge-ineligible" style="margin-bottom:6px;">{task['skill_name']}</span>
                                <h5 style="margin:4px 0; color:#F8FAFC; font-weight:700;">{task['title']}</h5>
                                <div style="font-size:0.8rem; color:#94A3B8; margin-top:6px;">
                                    Difficulty: <b>{task['difficulty']}</b> | Estimated: <b>{task['estimated_hours']} hrs</b>
                                </div>
                                <div style="font-size:0.8rem; color:#94A3B8; margin-top:2px;">
                                    Priority: <b>{task['priority']} / 5</b>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        
                        act_col1, act_col2 = st.columns(2)
                        with act_col1:
                            if st.button("Start Task", key=f"start_{task['id']}", use_container_width=True):
                                api_client.put(f"/roadmap/tasks/{task['id']}/status?status_str=In Progress")
                                st.rerun()
                        with act_col2:
                            if st.button("Finish", key=f"done_fast_{task['id']}", use_container_width=True):
                                api_client.put(f"/roadmap/tasks/{task['id']}/status?status_str=Completed")
                                st.rerun()

        with col_progress:
            st.markdown("<h4 style='color:#FBBF24; border-bottom: 2px solid #FBBF24; padding-bottom:6px; margin-bottom:16px; font-weight:700;'>In Progress</h4>", unsafe_allow_html=True)
            in_progress_tasks = [t for t in tasks if t["status"] == "In Progress"]
            if not in_progress_tasks:
                st.info("No active tasks in progress.")
            else:
                for task in in_progress_tasks:
                    with st.container():
                        res_link = f"<a href='{task['resource']['url']}' target='_blank' style='color:#818CF8;'>🔗 Open Resource</a>" if task["resource"] else "No URL linked"
                        st.markdown(
                            f"""
                            <div class="glass-card" style="margin-bottom:12px; border-left:3px solid #FBBF24;">
                                <span class="badge badge-warning" style="margin-bottom:6px;">{task['skill_name']}</span>
                                <h5 style="margin:4px 0; color:#F8FAFC; font-weight:700;">{task['title']}</h5>
                                <div style="font-size:0.8rem; color:#94A3B8; margin-top:6px;">
                                    Progress: <b>{task['progress_percentage']}%</b> | {res_link}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.progress(task["progress_percentage"] / 100)
                        
                        with st.expander("⏱️ Log Study Session"):
                            with st.form(f"session_form_{task['id']}"):
                                duration = st.number_input("Duration (minutes)", min_value=1, value=60, step=5)
                                focus = st.slider("Focus Score (1-5)", 1, 5, 4)
                                energy = st.slider("Energy Score (1-5)", 1, 5, 4)
                                notes = st.text_input("Session Notes", placeholder="e.g. Completed section on container mounts")
                                
                                log_btn = st.form_submit_button("Save Log")
                                if log_btn:
                                    payload = {
                                        "duration_minutes": duration,
                                        "focus_score": focus,
                                        "energy_level": energy,
                                        "resource_used": task["resource"]["title"] if task["resource"] else "Docs",
                                        "notes": notes
                                    }
                                    res_log = api_client.post(f"/roadmap/tasks/{task['id']}/study-sessions", json=payload)
                                    if res_log.status_code == 200:
                                        st.success("✓ Study session logged!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to log session.")

                        if st.button("Mark Completed", key=f"finish_{task['id']}", use_container_width=True):
                            api_client.put(f"/roadmap/tasks/{task['id']}/status?status_str=Completed")
                            st.rerun()

        with col_done:
            st.markdown("<h4 style='color:#34D399; border-bottom: 2px solid #34D399; padding-bottom:6px; margin-bottom:16px; font-weight:700;'>Completed</h4>", unsafe_allow_html=True)
            done_tasks = [t for t in tasks if t["status"] == "Completed"]
            if not done_tasks:
                st.info("No completed tasks yet.")
            else:
                for task in done_tasks:
                    with st.container():
                        st.markdown(
                            f"""
                            <div class="glass-card" style="margin-bottom:12px; border-left:3px solid #34D399; background: rgba(16, 185, 129, 0.03);">
                                <span class="badge badge-eligible" style="margin-bottom:6px;">{task['skill_name']}</span>
                                <h5 style="margin:4px 0; color:#94A3B8; text-decoration: line-through;">{task['title']}</h5>
                                <div style="font-size:0.8rem; color:#34D399; margin-top:6px; font-weight:700;">
                                    ✓ Mastered (+30% Confidence Boost)
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        
                        if st.button("Reset Task", key=f"reset_{task['id']}", use_container_width=True):
                            api_client.put(f"/roadmap/tasks/{task['id']}/status?status_str=Not Started")
                            st.rerun()


# TAB 2: MCQ Quiz Console
with tab_quiz:
    st.subheader("🎓 Practice Topic Quizzes")
    st.write("Evaluate your concept knowledge using topic-matched MCQs from the practice question bank.")

    roadmap_skills = list(set([t["skill_name"] for t in tasks]))
    if not roadmap_skills:
        roadmap_skills = ["Docker", "FastAPI", "Python"]

    selected_quiz_skill = st.selectbox("Select Quiz Topic", roadmap_skills)
    
    if "current_quiz_skill" not in st.session_state or st.session_state.current_quiz_skill != selected_quiz_skill:
        st.session_state.current_quiz_skill = selected_quiz_skill
        st.session_state.quiz_questions = []
        st.session_state.quiz_answers = {}
        st.session_state.quiz_evaluated = False

    if st.button("Fetch Quiz Questions", key="load_quiz_btn"):
        with st.spinner("Fetching question bank..."):
            quiz_res = api_client.get(f"/roadmap/quizzes/{selected_quiz_skill}")
            if quiz_res.status_code == 200:
                st.session_state.quiz_questions = quiz_res.json()
                st.session_state.quiz_answers = {}
                st.session_state.quiz_evaluated = False
            else:
                st.error("Failed to load questions.")

    if st.session_state.quiz_questions:
        st.write("---")
        with st.form("quiz_form"):
            for idx, q in enumerate(st.session_state.quiz_questions):
                st.write(f"**Q{idx+1}. {q['question_text']}**")
                user_ans = st.radio(
                    f"Select answer for Q{idx+1}:", 
                    q["options"], 
                    key=f"q_radio_{q['id']}"
                )
                st.session_state.quiz_answers[q["id"]] = user_ans
                st.write("")

            quiz_submit = st.form_submit_button("Submit Quiz Answers")
            if quiz_submit:
                st.session_state.quiz_evaluated = True

        if st.session_state.quiz_evaluated:
            correct_count = 0
            st.write("### Quiz Scorecard")
            for idx, q in enumerate(st.session_state.quiz_questions):
                ans = st.session_state.quiz_answers.get(q["id"])
                is_correct = (ans == q["correct_option"])
                if is_correct:
                    correct_count += 1
                    st.markdown(f"<span style='color:#34D399;'><b>✓ Q{idx+1} Correct!</b></span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:#FB7185;'><b>✖ Q{idx+1} Incorrect.</b> Selected: '{ans}' | Correct: '{q['correct_option']}'</span>", unsafe_allow_html=True)
                
                st.markdown(
                    f"""
                    <div class="glass-card" style="padding: 10px 16px; margin-top:5px; margin-bottom:15px; font-size:0.85rem;">
                        <b>Explanation:</b> {q['explanation']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            score_percent = int((correct_count / len(st.session_state.quiz_questions)) * 100)
            st.plotly_chart(draw_score_gauge(score_percent, "QUIZ SCORE"), use_container_width=True)
            if score_percent >= 80:
                st.success("Great job! You demonstrate high mastery of this topic.")
            else:
                st.warning("Review the suggested roadmap tutorials to build your skill confidence.")


# TAB 3: Mock Interview Simulator
with tab_interview:
    st.subheader("⚔️ Technical Interview Simulator")
    st.write("Compose written answers to typical campus placement questions and receive breakdown ratings and feedback reports.")

    interview_prompts = {
        "Docker": {
            "id": "d0c00000-0000-0000-0000-000000000001",
            "prompt": "Explain what a Dockerfile is and how layer caching speeds up application deployment container builds."
        },
        "FastAPI": {
            "id": "fa0a0000-0000-0000-0000-000000000001",
            "prompt": "Explain the differences between synchronous (def) and asynchronous (async def) endpoint routing in FastAPI."
        },
        "Python": {
            "id": "ca000000-0000-0000-0000-000000000001",
            "prompt": "Explain how memory management works in Python, focusing on reference counting and garbage collection."
        }
    }

    selected_interview_topic = st.selectbox("Select Interview Topic Domain", list(interview_prompts.keys()))
    prompt_details = interview_prompts[selected_interview_topic]

    st.markdown(
        f"""
        <div class="glass-card" style="border-left: 4px solid #6366F1; background: rgba(99,102,241,0.02); margin-bottom: 20px;">
            <span class="badge badge-indigo" style="margin-bottom:6px;">INTERVIEW QUESTION</span>
            <h4 style="margin:4px 0 0 0; color:#F8FAFC; font-weight:600;">{prompt_details['prompt']}</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("interview_form"):
        student_answer = st.text_area("Your Response *", height=150, placeholder="Write a detailed explanation (at least 15-20 words)...")
        submit_answer = st.form_submit_button("Submit Response for Evaluation")
        
        if submit_answer:
            if len(student_answer.strip()) < 10:
                st.error("Please compose a more complete answer before requesting evaluation.")
            else:
                with st.spinner("Analyzing response syntax, keywords compliance, and clarity..."):
                    payload = {"student_answer": student_answer}
                    res_ans = api_client.post(f"/roadmap/interviews/{prompt_details['id']}/answer", json=payload)
                    if res_ans.status_code == 200:
                        report = res_ans.json()
                        
                        st.markdown("### 📊 Performance Scorecard")
                        
                        col_g, col_details = st.columns([1, 1.8])
                        with col_g:
                            st.plotly_chart(draw_score_gauge(report["overall_score"], "OVERALL RATING"), use_container_width=True)
                            
                        with col_details:
                            st.markdown(
                                f"""
                                <b>Technical Accuracy:</b> {report['technical_score']}%<br>
                                <b>Communication Clarity:</b> {report['communication_score']}%<br>
                                <b>Answer Completeness:</b> {report['completeness_score']}%<br>
                                <b>Grammatical Correctness:</b> {report['grammar_score']}%<br>
                                """,
                                unsafe_allow_html=True,
                            )

                        st.markdown("#### Coaching Feedback")
                        st.info(report["ai_feedback"])
                        
                        col_weak, col_links = st.columns(2)
                        with col_weak:
                            st.write("**Weak Areas Identified:**")
                            st.error(report["weak_areas"])
                        with col_links:
                            st.write("**Suggested Study Readings:**")
                            if report["suggested_reading"]:
                                st.markdown(f"[🔗 Study Link Guide]({report['suggested_reading']})")
                            else:
                                st.write("Review official core docs.")
                                
                        if report["overall_score"] >= 75:
                            st.success("✓ Passed! This response satisfies candidate standards. +10% Skill Confidence added.")
                        else:
                            st.warning("Needs Improvement. Try revising your draft using the suggested study links.")
                    else:
                        st.error("Failed to compile answer evaluation.")
