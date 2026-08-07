import streamlit as st
from utils.api_client import api_client
from utils.styles import inject_custom_css

# Page Configuration
st.set_page_config(
    page_title="Admin Panel - PlaceMentor AI",
    page_icon="⚙️",
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

# Enforce RBAC by calling /auth/me
is_admin = False
try:
    me_response = api_client.get("/auth/me")
    if me_response.status_code == 200:
        user_info = me_response.json()
        if user_info.get("role") == "admin":
            is_admin = True
except Exception:
    pass

if not is_admin:
    st.markdown(
        """
        <div class="glass-card" style="border-color: rgba(244, 63, 94, 0.4); background: rgba(244, 63, 94, 0.05); text-align:center; padding: 40px 20px;">
            <h1 style="color:#FB7185; margin-top:0; font-weight:800;">🚫 Administrator Access Required</h1>
            <p style="color:#94A3B8; font-size:1.05rem; line-height:1.6; max-width:600px; margin: 15px auto;">
                Only accounts registered with the <b>Administrator</b> role can access recruiter management tools and seed placement criteria.
            </p>
            <div style="margin-top:20px; padding:16px; background:rgba(15,23,42,0.7); border-radius:12px; border:1px solid rgba(255,255,255,0.08); display:inline-block; text-align:left;">
                💡 <b>Testing Tip:</b> Sign out and authenticate using the seeded superuser account:<br>
                • <b>Email:</b> <code style="color:#818CF8;">admin@placementor.ai</code><br>
                • <b>Password:</b> <code style="color:#818CF8;">AdminSecretPass123!</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# Header Bar
st.markdown(
    """
    <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span style="font-size:0.75rem; color:#64748B; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">ADMIN CONSOLE / RECRUITER MANAGEMENT</span>
            <h2 style="margin:0; font-size:1.6rem; font-weight:800; color:#F8FAFC;" class="neon-text-indigo">Placement Administrator Console</h2>
        </div>
        <span class="badge badge-eligible">RBAC Verified: Admin</span>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_comp, tab_role = st.tabs(["🏢 Register Corporation", "💼 Define Job Role & Rules"])

# TAB 1: Register Company
with tab_comp:
    st.subheader("Register Recruiting Corporation")
    with st.form("create_company_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Company Name *", placeholder="e.g. Netflix")
            website_url = st.text_input("Website URL", placeholder="https://netflix.com")
            careers_url = st.text_input("Careers Portal URL", placeholder="https://jobs.netflix.com")
            industry = st.text_input("Industry", placeholder="e.g. Media / Streaming")
        with col2:
            hq_location = st.text_input("HQ Location", placeholder="e.g. Los Gatos, CA")
            hiring_frequency = st.selectbox("Hiring Frequency", ["Yearly", "Bi-yearly", "Off-campus", "On-campus Only"])
            remote_onsite = st.selectbox("Work Arrangement", ["Onsite", "Remote", "Hybrid"])
            internship_ppo = st.checkbox("Internship-to-PPO Offers Available", value=True)

        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Save Corporation Record", type="primary")
        if submitted:
            if not name.strip():
                st.error("Company Name is a required field.")
            else:
                payload = {
                    "name": name,
                    "website_url": website_url,
                    "careers_url": careers_url,
                    "industry": industry,
                    "hq_location": hq_location,
                    "hiring_frequency": hiring_frequency,
                    "remote_onsite": remote_onsite,
                    "internship_ppo_available": internship_ppo
                }
                with st.spinner("Saving company metadata..."):
                    res = api_client.post("/companies/", json=payload)
                    if res.status_code == 201:
                        st.success(f"✓ Successfully registered: **{name}**")
                    else:
                        st.error(f"Error: {res.json().get('detail', 'Failed to create company.')}")


# TAB 2: Register Job Role & Eligibility Rules
with tab_role:
    st.subheader("Add Placement Role & Eligibility Specifications")
    
    companies_list = []
    companies_map = {}
    try:
        c_res = api_client.get("/companies/")
        if c_res.status_code == 200:
            for c in c_res.json():
                companies_list.append(c["name"])
                companies_map[c["name"]] = c["id"]
    except Exception:
        pass

    if not companies_list:
        st.warning("Please register at least one company first in Tab 1.")
    else:
        with st.form("create_role_form"):
            selected_company_name = st.selectbox("Select Recruiting Company", companies_list)
            
            st.write("---")
            st.markdown("#### 1. Job Role Parameters")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                title = st.text_input("Job Title *", placeholder="e.g. Frontend Engineer")
                ctc = st.number_input("CTC Compensation (LPA) *", min_value=0.0, step=0.5, value=12.0)
                difficulty = st.selectbox("Exam Difficulty Level", ["Easy", "Medium", "Hard"])
            with col_r2:
                application_link = st.text_input("Application Link", placeholder="URL to job posting")
                selection_rounds = st.number_input("Number of Interview Rounds", min_value=1, max_value=10, value=3)
                
            description = st.text_area("Role Description", placeholder="Summary of responsibilities...")
            hiring_pattern = st.text_area("Hiring Round Stages", placeholder="e.g. Round 1: OA, Round 2: Technical...")
            expected_oa_pattern = st.text_area("Expected OA Syllabus", placeholder="e.g. 2 Coding questions (Arrays, Trees)...")
            
            col_topics1, col_topics2 = st.columns(2)
            with col_topics1:
                tech_topics = st.text_input("Technical Syllabus Topics (comma-separated)", placeholder="DSA, SQL, OOP")
            with col_topics2:
                hr_topics = st.text_input("Soft Skill Topics (comma-separated)", placeholder="Teamwork, Ownership")

            interview_experience = st.text_area("Interview Experience Tidbit", placeholder="Candidate reviews...")
            prep_resources = st.text_input("Prep Resources List (comma-separated)", placeholder="LeetCode 75, GeeksforGeeks")

            st.write("---")
            st.markdown("#### 2. Academic Eligibility Constraints")
            col_el1, col_el2, col_el3 = st.columns(3)
            with col_el1:
                min_cgpa = st.number_input("Minimum CGPA required *", min_value=0.0, max_value=10.0, step=0.1, value=8.0)
                max_backlogs = st.number_input("Maximum Allowed Backlogs *", min_value=0, max_value=10, value=0)
            with col_el2:
                min_tenth = st.number_input("Min 10th Grade Percentage", min_value=0.0, max_value=100.0, step=1.0, value=0.0)
                min_twelfth = st.number_input("Min 12th Grade Percentage", min_value=0.0, max_value=100.0, step=1.0, value=0.0)
            with col_el3:
                min_resume_score = st.number_input("Min Resume ATS score *", min_value=0, max_value=100, value=70)
                
            allowed_branches = st.multiselect(
                "Allowed Academic Branches *", 
                ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL", "MTECH"],
                default=["CSE", "IT"]
            )

            st.write("---")
            st.markdown("#### 3. Core Technical Skill Weights (Define up to 3)")
            
            col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
            with col_s1:
                skill1_name = st.text_input("Skill 1 Name", value="Python")
                skill2_name = st.text_input("Skill 2 Name", value="SQL")
                skill3_name = st.text_input("Skill 3 Name", value="Git")
            with col_s2:
                skill1_imp = st.slider("Importance 1", 1, 5, 5, key="imp1")
                skill2_imp = st.slider("Importance 2", 1, 5, 4, key="imp2")
                skill3_imp = st.slider("Importance 3", 1, 5, 3, key="imp3")
            with col_s3:
                skill1_lvl = st.selectbox("Level 1", ["Beginner", "Intermediate", "Expert"], index=1, key="lvl1")
                skill2_lvl = st.selectbox("Level 2", ["Beginner", "Intermediate", "Expert"], index=1, key="lvl2")
                skill3_lvl = st.selectbox("Level 3", ["Beginner", "Intermediate", "Expert"], index=0, key="lvl3")

            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            role_submitted = st.form_submit_button("Save Role Specifications & Rules", type="primary")
            
            if role_submitted:
                if not title.strip():
                    st.error("Job Title is a required field.")
                elif not allowed_branches:
                    st.error("At least one allowed branch must be selected.")
                else:
                    skill_weights = []
                    for sname, simp, slvl in [
                        (skill1_name, skill1_imp, skill1_lvl),
                        (skill2_name, skill2_imp, skill2_lvl),
                        (skill3_name, skill3_imp, skill3_lvl)
                    ]:
                        if sname.strip():
                            skill_weights.append({
                                "skill_name": sname.strip(),
                                "importance": simp,
                                "required_level": slvl
                            })
                            
                    tech_topics_list = [t.strip() for t in tech_topics.split(",") if t.strip()]
                    hr_topics_list = [t.strip() for t in hr_topics.split(",") if t.strip()]
                    prep_res_list = [t.strip() for t in prep_resources.split(",") if t.strip()]

                    payload = {
                        "title": title,
                        "ctc": ctc,
                        "description": description,
                        "application_link": application_link,
                        "difficulty": difficulty,
                        "selection_rounds": selection_rounds,
                        "hiring_pattern": hiring_pattern,
                        "expected_oa_pattern": expected_oa_pattern,
                        "technical_interview_topics": tech_topics_list,
                        "hr_interview_topics": hr_topics_list,
                        "interview_experience": interview_experience,
                        "preparation_resources": prep_res_list,
                        "eligibility_rule": {
                            "min_cgpa": min_cgpa,
                            "min_tenth_percentage": min_tenth,
                            "min_twelfth_percentage": min_twelfth,
                            "allowed_branches": allowed_branches,
                            "max_active_backlogs": max_backlogs,
                            "min_resume_match_score": min_resume_score
                        },
                        "skill_weights": skill_weights
                    }

                    with st.spinner("Saving role specifications..."):
                        company_uuid = companies_map[selected_company_name]
                        res = api_client.post(f"/companies/{company_uuid}/roles", json=payload)
                        if res.status_code == 201:
                            st.success(f"✓ Role **{title}** registered for **{selected_company_name}**!")
                        else:
                            st.error(f"Error: {res.json().get('detail', 'Failed to save role.')}")
