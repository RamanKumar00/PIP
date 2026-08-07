import streamlit as st
from utils.api_client import api_client
from utils.styles import inject_custom_css

# Page Configuration
st.set_page_config(
    page_title="Profile - PlaceMentor AI",
    page_icon="👤",
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
            <span style="font-size:0.75rem; color:#64748B; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">PORTAL / CANDIDATE PROFILE</span>
            <h2 style="margin:0; font-size:1.6rem; font-weight:800; color:#F8FAFC;" class="neon-text-indigo">Academic & Placement Profile</h2>
        </div>
        <span class="badge badge-indigo">Evaluation Parameters</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# Fetch current profile if it exists
profile_exists = False
initial_data = {}

with st.spinner("Fetching profile record..."):
    try:
        response = api_client.get("/profile/")
        if response.status_code == 200:
            initial_data = response.json()
            profile_exists = True
    except Exception as e:
        st.error(f"Error fetching profile details: {e}")

# Calculate profile strength score based on filled fields
filled_count = sum(1 for v in [
    initial_data.get("full_name"), initial_data.get("phone"), initial_data.get("college"),
    initial_data.get("university"), initial_data.get("branch"), initial_data.get("cgpa"),
    initial_data.get("tenth_percentage"), initial_data.get("twelfth_percentage"),
    initial_data.get("linkedin_url"), initial_data.get("github_url"), initial_data.get("preferred_role")
] if v)

profile_strength_pct = int((filled_count / 11) * 100) if initial_data else 0

# Profile Strength Card
st.markdown(
    f"""
    <div class="glass-card" style="margin-bottom: 24px; border-left: 4px solid #6366F1;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <h3 style="margin:0; color:#F8FAFC; font-weight:700;">Candidate Completeness Meter</h3>
                <p style="color:#94A3B8; font-size:0.85rem; margin-top:4px;">
                    These parameters are directly evaluated by recruiter company eligibility rule engines.
                </p>
            </div>
            <div style="text-align:right;">
                <span class="badge badge-eligible" style="font-size:0.85rem; padding:6px 14px;">Profile Strength: {profile_strength_pct}%</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.progress(profile_strength_pct / 100)
st.write("")

# Form to compile details - separated into spacious glass-cards
with st.container(border=True):
    st.markdown("### 📇 Contact & Personal Information")
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name *", value=initial_data.get("full_name", ""), placeholder="e.g. Alex Chen")
    with col2:
        phone = st.text_input("Phone Number *", value=initial_data.get("phone", ""), placeholder="+91 98765 43210")

with st.container(border=True):
    st.markdown("### 🎓 Academic Credentials")
    col3, col4, col5 = st.columns(3)
    with col3:
        college = st.text_input("College *", value=initial_data.get("college", ""), placeholder="e.g. Institute of Technology")
    with col4:
        university = st.text_input("University *", value=initial_data.get("university", ""), placeholder="e.g. State University")
    with col5:
        branch_options = ["Computer Science & Engineering", "Information Technology", "Electronics & Communication", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Other"]
        cur_branch = initial_data.get("branch", "Computer Science & Engineering")
        branch_idx = branch_options.index(cur_branch) if cur_branch in branch_options else 0
        branch = st.selectbox("Academic Branch *", branch_options, index=branch_idx)

    col6, col7, col8 = st.columns(3)
    with col6:
        current_year = st.number_input("Current Year of Study *", min_value=1, max_value=5, value=initial_data.get("current_year", 3))
    with col7:
        cgpa = st.number_input("Current CGPA (Scale 0-10) *", min_value=0.0, max_value=10.0, value=float(initial_data.get("cgpa", 0.0)), step=0.01)
    with col8:
        backlogs = st.number_input("Active Backlogs Count *", min_value=0, value=initial_data.get("backlogs", 0))

    col9, col10 = st.columns(2)
    with col9:
        tenth_pct = st.number_input("10th Grade Percentage *", min_value=0.0, max_value=100.0, value=float(initial_data.get("tenth_percentage", 0.0)), step=0.1)
    with col10:
        twelfth_pct = st.number_input("12th Grade Percentage *", min_value=0.0, max_value=100.0, value=float(initial_data.get("twelfth_percentage", 0.0)), step=0.1)

with st.container(border=True):
    st.markdown("### 💼 Placement Preferences & Links")
    col11, col12 = st.columns(2)
    with col11:
        linkedin = st.text_input("LinkedIn Profile URL", value=initial_data.get("linkedin_url", ""), placeholder="https://linkedin.in/in/username")
        portfolio = st.text_input("Portfolio Website URL", value=initial_data.get("portfolio_url", ""), placeholder="https://alexchen.dev")
    with col12:
        github = st.text_input("GitHub Profile URL", value=initial_data.get("github_url", ""), placeholder="https://github.com/username")
        role_options = ["Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer", "Data Analyst", "Data Scientist", "DevOps Engineer", "Product Manager"]
        cur_role = initial_data.get("preferred_role", "Software Engineer")
        role_idx = role_options.index(cur_role) if cur_role in role_options else 0
        pref_role = st.selectbox("Target Placement Role *", role_options, index=role_idx)

    pref_companies_str = st.text_input(
        "Target Companies (Comma-separated, e.g. Amazon, Google, Microsoft)", 
        value=", ".join(initial_data.get("preferred_companies", []))
    )

st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
submit = st.button("Save Profile Parameters", type="primary", use_container_width=True)

if submit:
    if not full_name or not college or not university or not phone:
        st.error("Please fill in all required fields (Name, Phone, College, University).")
    else:
        pref_companies = [c.strip() for c in pref_companies_str.split(",") if c.strip()]
        
        payload = {
            "full_name": full_name,
            "college": college,
            "university": university,
            "branch": branch,
            "current_year": int(current_year),
            "cgpa": float(cgpa),
            "tenth_percentage": float(tenth_pct),
            "twelfth_percentage": float(twelfth_pct),
            "phone": phone,
            "linkedin_url": linkedin if linkedin else None,
            "github_url": github if github else None,
            "portfolio_url": portfolio if portfolio else None,
            "preferred_role": pref_role,
            "preferred_companies": pref_companies,
            "backlogs": int(backlogs),
        }

        success = False
        with st.spinner("Saving updated profile parameters..."):
            try:
                response = api_client.put("/profile/", data=payload)
                if response.status_code == 200:
                    success = True
                else:
                    st.error(f"Failed to save profile: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error connecting to backend API: {e}")

        if success:
            st.success("✓ Academic & Placement Profile saved successfully!")
            st.rerun()
