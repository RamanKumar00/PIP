import textwrap
import streamlit as st
import plotly.graph_objects as go
from utils.api_client import api_client
from utils.styles import inject_custom_css, apply_plotly_dark_theme

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="PlaceMentor AI — Campus Placement Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()

# ── SESSION STATE ──
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None


def handle_logout():
    try:
        api_client.post("/auth/logout")
    except Exception:
        pass
    for k in ["access_token", "refresh_token", "user_email"]:
        st.session_state[k] = None
    st.rerun()


# ─────────────────────────────────────────────────────────────────────
# SIDEBAR — Premium compact design (only shown after login)
# ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo bar
    st.markdown("""<div class="logo-container">
<div style="display:flex;align-items:center;gap:10px;">
<div style="width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#6366F1,#A855F7);display:flex;align-items:center;justify-content:center;font-size:1.1rem;box-shadow:0 0 16px rgba(99,102,241,0.45);flex-shrink:0;">🎓</div>
<div><div style="font-weight:800;font-size:0.95rem;color:#F0F6FC;letter-spacing:-0.01em;">PlaceMentor AI</div>
<div style="font-size:0.6rem;color:#4B5563;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">Campus Intelligence</div></div>
</div></div>""", unsafe_allow_html=True)

    if st.session_state.access_token:
        initials = (st.session_state.user_email or "U")[0].upper()
        st.markdown(f"""<div style="margin:10px 12px 14px;padding:12px 14px;background:rgba(99,102,241,0.07);border:1px solid rgba(99,102,241,0.18);border-radius:14px;">
<div style="display:flex;align-items:center;gap:10px;">
<div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#6366F1,#7C3AED);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.85rem;color:white;">{initials}</div>
<div style="min-width:0;flex:1;overflow:hidden;">
<div style="font-size:0.78rem;font-weight:700;color:#F0F6FC;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{st.session_state.user_email}</div>
<div style="display:inline-flex;align-items:center;gap:4px;margin-top:3px;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:1px 7px;">
<span style="width:5px;height:5px;background:#10B981;border-radius:50%;display:inline-block;"></span>
<span style="font-size:0.58rem;font-weight:700;color:#34D399;text-transform:uppercase;letter-spacing:0.08em;">Active</span>
</div></div></div></div>""", unsafe_allow_html=True)

        st.markdown("""<div style="padding:0 10px 6px;">
<div style="font-size:0.6rem;font-weight:700;color:#374151;letter-spacing:0.12em;text-transform:uppercase;padding:6px 4px 8px;">Main Navigation</div>
</div>""", unsafe_allow_html=True)

    # Premium widget
    st.markdown("""<div style="padding:0 12px;margin-top:20px;margin-bottom:16px;">
<div style="background:linear-gradient(135deg,rgba(99,102,241,0.12),rgba(124,58,237,0.08));border:1px solid rgba(99,102,241,0.22);border-radius:14px;padding:14px;">
<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;"><span style="font-size:0.9rem;">👑</span><span style="font-size:0.78rem;font-weight:800;color:#F0F6FC;">Premium Suite</span></div>
<div style="font-size:0.72rem;color:#94A3B8;line-height:1.5;margin-bottom:10px;">Unlock advanced AI analytics, unlimited resume checks &amp; mock interviews.</div>
<div style="background:linear-gradient(135deg,#6366F1,#7C3AED);border-radius:8px;padding:7px;text-align:center;font-size:0.75rem;font-weight:700;color:white;cursor:pointer;">Upgrade Now →</div>
</div>
<div style="margin-top:12px;padding:10px 4px;border-top:1px solid rgba(255,255,255,0.05);">
<div style="font-size:0.7rem;color:#64748B;margin-bottom:4px;">💬 Need help? <a href="mailto:support@placementor.ai" style="color:#6366F1!important;font-weight:600;">Contact support</a></div>
</div></div>""", unsafe_allow_html=True)

    if st.session_state.access_token:
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            handle_logout()


# ─────────────────────────────────────────────────────────────────────
# AUTH SCREEN — Premium Split-Screen SaaS Landing Page
# ─────────────────────────────────────────────────────────────────────
def render_auth_screen():
    # Hide sidebar completely on auth page
    st.markdown("""<style>
section[data-testid="stSidebar"]{display:none!important;}
button[data-testid="collapsedControl"]{display:none!important;}
.main .block-container{padding:0!important;max-width:100%!important;}
.stApp{overflow-x:hidden;}
</style>""", unsafe_allow_html=True)

    # Two column split: 55% hero | 45% form
    col_hero, col_form = st.columns([1.25, 1], gap="medium")

    # ── LEFT: Full Hero Section ──
    with col_hero:
        st.markdown("""
<div style="padding:36px 12px 36px 40px;min-height:90vh;position:relative;overflow:hidden;display:flex;flex-direction:column;justify-content:center;">

<!-- Animated ambient orbs -->
<div style="position:absolute;top:-120px;left:-80px;width:500px;height:500px;border-radius:50%;background:radial-gradient(circle,rgba(99,102,241,0.13) 0%,transparent 68%);animation:floatA 14s ease-in-out infinite;pointer-events:none;z-index:0;"></div>
<div style="position:absolute;bottom:-60px;right:60px;width:380px;height:380px;border-radius:50%;background:radial-gradient(circle,rgba(168,85,247,0.10) 0%,transparent 68%);animation:floatB 11s ease-in-out infinite;pointer-events:none;z-index:0;"></div>

<div style="position:relative;z-index:1;">

<!-- AI Badge -->
<div style="display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,rgba(99,102,241,0.14),rgba(168,85,247,0.09));border:1px solid rgba(99,102,241,0.28);border-radius:50px;padding:6px 16px;margin-bottom:22px;animation:slideDown 0.5s ease;">
<span style="width:7px;height:7px;background:#6366F1;border-radius:50%;box-shadow:0 0 10px rgba(99,102,241,0.8);display:inline-block;animation:orbPulse 2s ease-in-out infinite;"></span>
<span style="font-size:0.68rem;font-weight:700;color:#A5B4FC;letter-spacing:0.1em;text-transform:uppercase;">AI-Powered Campus Intelligence Platform</span>
</div>

<!-- Hero Heading -->
<h1 style="font-size:3.1rem;font-weight:900;line-height:1.07;margin:0 0 18px;color:#F0F6FC;letter-spacing:-0.03em;animation:fadeInUp 0.6s ease 0.1s both;">
Ace Your Placement<br>Journey
<span style="background:linear-gradient(135deg,#6366F1 0%,#A855F7 50%,#38BDF8 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;"> with AI</span>
</h1>

<!-- Subtitle -->
<p style="font-size:0.97rem;color:#94A3B8;line-height:1.72;margin:0 0 30px;max-width:500px;animation:fadeInUp 0.6s ease 0.2s both;">
Analyze your resume, discover eligible companies, build personalized learning roadmaps, and ace interviews — all powered by enterprise-grade AI intelligence.
</p>

<!-- ── PREVIEW METRICS COMPACT DASHBOARD ── -->
<div style="background:rgba(17,24,39,0.55);border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:22px;backdrop-filter:blur(20px);margin-bottom:10px;animation:fadeInUp 0.6s ease 0.3s both;max-width:520px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.05);padding-bottom:10px;">
     <div style="font-weight:800;font-size:0.78rem;color:#F0F6FC;display:flex;align-items:center;gap:6px;">
        <span style="width:6px;height:6px;background:#10B981;border-radius:50%;display:inline-block;"></span>
        PLACEMENT ANALYTICS PREVIEW
     </div>
     <div style="font-size:0.6rem;color:#64748B;font-weight:700;">STUDENT DRIVES</div>
  </div>
  <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:16px;">
     <!-- Widget 1: ATS -->
     <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);border-radius:12px;padding:12px;display:flex;align-items:center;gap:10px;">
        <div style="position:relative;width:42px;height:42px;flex-shrink:0;">
          <svg width="42" height="42" viewBox="0 0 54 54" style="transform:rotate(-90deg);">
            <circle cx="27" cy="27" r="23" fill="none" stroke="rgba(99,102,241,0.15)" stroke-width="4"/>
            <circle cx="27" cy="27" r="23" fill="none" stroke="url(#grad_auth)" stroke-width="4" stroke-dasharray="144.5" stroke-dashoffset="26" stroke-linecap="round"/>
            <defs><linearGradient id="grad_auth" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#6366F1"/><stop offset="100%" style="stop-color:#A855F7"/></linearGradient></defs>
          </svg>
          <span style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:0.65rem;font-weight:800;color:#A5B4FC;">92%</span>
        </div>
        <div>
           <div style="font-size:0.55rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;">ATS Fit</div>
           <div style="font-size:1.15rem;font-weight:900;color:#F0F6FC;line-height:1;">92%</div>
        </div>
     </div>
     <!-- Widget 2: Readiness -->
     <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);border-radius:12px;padding:12px;display:flex;flex-direction:column;justify-content:center;">
        <div style="font-size:0.55rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:3px;">Readiness</div>
        <div style="font-size:1.15rem;font-weight:900;color:#F0F6FC;line-height:1;margin-bottom:4px;">84%</div>
        <div style="background:rgba(16,185,129,0.12);border-radius:2px;height:3px;overflow:hidden;">
           <div style="background:linear-gradient(90deg,#10B981,#34D399);height:100%;width:84%;"></div>
        </div>
     </div>
     <!-- Widget 3: Eligibility -->
     <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);border-radius:12px;padding:12px;display:flex;align-items:center;gap:8px;">
        <span style="font-size:1rem;">🏆</span>
        <div>
           <div style="font-size:0.55rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:2px;">Google Status</div>
           <div style="background:rgba(16,185,129,0.15);border-radius:10px;padding:1px 6px;font-size:0.58rem;font-weight:800;color:#34D399;display:inline-block;">✓ Eligible</div>
        </div>
     </div>
     <!-- Widget 4: Streak -->
     <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);border-radius:12px;padding:12px;display:flex;align-items:center;gap:8px;">
        <span style="font-size:1rem;">🔥</span>
        <div>
           <div style="font-size:0.55rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:2px;">Study Streak</div>
           <div style="font-size:1.05rem;font-weight:900;color:#F59E0B;line-height:1;">14 Days</div>
        </div>
     </div>
  </div>
</div>

</div>
</div>
""", unsafe_allow_html=True)

    # ── RIGHT: Authentication Card ──
    with col_form:
        # Inject right-column card styling
        st.markdown("""<style>
/* Tabs: full width */
.stTabs { width: 100% !important; }
.stTabs [data-baseweb="tab-list"] { width: 100% !important; }
.stTabs [data-baseweb="tab"] { flex: 1 !important; justify-content: center !important; }


/* Auth utility row styling */
.auth-utility-row {
  display: flex !important;
  flex-direction: row !important;
  justify-content: space-between !important;
  align-items: center !important;
  width: 100% !important;
  padding: 12px 0 !important; /* Zero horizontal padding to align with inputs and prevent clipping */
  box-sizing: border-box !important;
  margin-top: 8px !important;
  margin-bottom: 8px !important;
}
.remember-me-label {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  color: #94A3B8 !important;
  cursor: pointer !important;
  user-select: none !important;
  text-transform: none !important;
  letter-spacing: normal !important;
  line-height: 1 !important;
  height: 20px !important; /* Fixed height matching the line-height for exact centering */
}
.remember-me-label input[type="checkbox"] {
  width: 16px !important;
  height: 16px !important;
  accent-color: #6366F1 !important;
  border-radius: 4px !important;
  margin: 0 !important;
  padding: 0 !important;
  cursor: pointer !important;
}
.forgot-pw-link {
  display: inline-flex !important;
  align-items: center !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  color: #6366F1 !important;
  text-decoration: none !important;
  white-space: nowrap !important;
  line-height: 1 !important;
  height: 20px !important; /* Matches the height of the checkbox label for perfect vertical centering */
  transition: color 0.2s ease, text-decoration 0.2s ease !important;
}
.forgot-pw-link:hover {
  color: #818CF8 !important;
  text-decoration: underline !important;
}

@media (max-width: 767px) {
  .auth-utility-row {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 12px !important;
    padding: 12px 0 !important;
  }
}
</style>""", unsafe_allow_html=True)

        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            # Security badge at top
            st.markdown("""<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:28px;padding-top:10px;">
<div style="display:inline-flex;align-items:center;gap:6px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);border-radius:20px;padding:4px 12px;">
<span style="font-size:0.7rem;">🛡️</span>
<span style="font-size:0.65rem;font-weight:700;color:#34D399;letter-spacing:0.08em;text-transform:uppercase;">Enterprise Secured</span>
</div>
<div style="width:32px;height:32px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:0.9rem;cursor:pointer;">🌙</div>
</div>""", unsafe_allow_html=True)

            # Logo + heading
            st.markdown("""<div style="margin-bottom:24px;">
<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
<div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#6366F1,#A855F7);display:flex;align-items:center;justify-content:center;font-size:1.2rem;box-shadow:0 0 16px rgba(99,102,241,0.5);">🎓</div>
<span style="font-weight:800;font-size:1rem;color:#F0F6FC;letter-spacing:-0.01em;">PlaceMentor AI</span>
</div>
<h2 style="margin:0 0 5px;font-size:1.55rem;font-weight:900;color:#F0F6FC;letter-spacing:-0.02em;">Welcome back</h2>
<p style="margin:0;font-size:0.84rem;color:#64748B;">Continue your placement journey. Your progress is saved.</p>
</div>""", unsafe_allow_html=True)

            tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

            # ── SIGN IN FORM ──
            with tab_login:
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                with st.form("login_form", clear_on_submit=False):
                    email = st.text_input(
                        "Email Address",
                        placeholder="you@university.edu",
                        key="li_email",
                    )
                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password",
                        key="li_pw",
                    )
                    st.markdown("""
                    <div class="auth-utility-row">
                        <label class="remember-me-label">
                            <input type="checkbox" id="remember-me">
                            Remember me
                        </label>
                        <a href="#" class="forgot-pw-link">Forgot password?</a>
                    </div>
                    """, unsafe_allow_html=True)
                    submit = st.form_submit_button("Sign In to Portal", use_container_width=True, type="primary")

                    if submit:
                        if not email or not password:
                            st.error("Please enter both email and password.")
                        else:
                            login_success = False
                            with st.spinner("Authenticating…"):
                                try:
                                    resp = api_client.post("/auth/login", data={"email": email, "password": password})
                                    if resp.status_code == 200:
                                        data = resp.json()
                                        st.session_state.access_token = data["access_token"]
                                        st.session_state.refresh_token = data["refresh_token"]
                                        st.session_state.user_email = email
                                        st.success("Signed in successfully!")
                                        login_success = True
                                    else:
                                        st.error(resp.json().get("detail", "Authentication failed. Check credentials."))
                                except Exception as e:
                                    st.error(f"Connection error: {e}")
                            
                            if login_success:
                                st.rerun()

            # ── CREATE ACCOUNT FORM ──
            with tab_signup:
                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                with st.form("signup_form", clear_on_submit=False):
                    reg_email = st.text_input(
                        "Email Address",
                        placeholder="student@college.edu",
                        key="su_email",
                    )
                    reg_pw = st.text_input(
                        "Password",
                        type="password",
                        placeholder="At least 8 characters",
                        key="su_pw",
                    )
                    conf_pw = st.text_input(
                        "Confirm Password",
                        type="password",
                        placeholder="Re-enter your password",
                        key="su_cpw",
                    )
                    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
                    reg_submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")

                    if reg_submit:
                        if not reg_email or not reg_pw:
                            st.error("Please fill in all fields.")
                        elif reg_pw != conf_pw:
                            st.error("Passwords do not match.")
                        elif len(reg_pw) < 8:
                            st.error("Password must be at least 8 characters.")
                        else:
                            with st.spinner("Creating your account…"):
                                try:
                                    resp = api_client.post("/auth/signup", data={"email": reg_email, "password": reg_pw})
                                    if resp.status_code == 201:
                                        st.success("Account created! Please sign in.")
                                    else:
                                        st.error(resp.json().get("detail", "Signup failed."))
                                except Exception as e:
                                    st.error(f"Connection error: {e}")

            # ── DIVIDER + SSO ──
            st.markdown("""<div style="margin:20px 0;">
<div style="display:flex;align-items:center;gap:12px;">
<div style="flex:1;height:1px;background:rgba(255,255,255,0.07);"></div>
<span style="font-size:0.65rem;color:#374151;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;white-space:nowrap;">Or continue with</span>
<div style="flex:1;height:1px;background:rgba(255,255,255,0.07);"></div>
</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:14px;">
<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.09);border-radius:10px;padding:9px 6px;text-align:center;cursor:pointer;transition:all 0.2s;font-size:0.75rem;font-weight:700;color:#C7D2FE;display:flex;align-items:center;justify-content:center;gap:5px;">
<span>🌐</span> Google</div>
<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.09);border-radius:10px;padding:9px 6px;text-align:center;cursor:pointer;transition:all 0.2s;font-size:0.75rem;font-weight:700;color:#C7D2FE;display:flex;align-items:center;justify-content:center;gap:5px;">
<span>🐙</span> GitHub</div>
<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.09);border-radius:10px;padding:9px 6px;text-align:center;cursor:pointer;transition:all 0.2s;font-size:0.75rem;font-weight:700;color:#C7D2FE;display:flex;align-items:center;justify-content:center;gap:5px;">
<span>🔗</span> LinkedIn</div>
</div>
</div>""", unsafe_allow_html=True)

            # ── SECURITY INDICATORS ──
            st.markdown("""<div style="background:rgba(17,24,39,0.6);border:1px solid rgba(255,255,255,0.06);border-radius:14px;padding:14px 16px;margin-top:4px;">
<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;">
<div style="display:flex;align-items:center;gap:7px;">
<span style="font-size:0.8rem;">🔐</span>
<div><div style="font-size:0.66rem;font-weight:700;color:#94A3B8;">JWT Auth</div>
<div style="font-size:0.6rem;color:#4B5563;">Secure token sessions</div></div></div>
<div style="display:flex;align-items:center;gap:7px;">
<span style="font-size:0.8rem;">🔒</span>
<div><div style="font-size:0.66rem;font-weight:700;color:#94A3B8;">Encrypted</div>
<div style="font-size:0.6rem;color:#4B5563;">AES-256 data at rest</div></div></div>
<div style="display:flex;align-items:center;gap:7px;">
<span style="font-size:0.8rem;">🛡️</span>
<div><div style="font-size:0.66rem;font-weight:700;color:#94A3B8;">Enterprise Grade</div>
<div style="font-size:0.6rem;color:#4B5563;">ISO-27001 compliant</div></div></div>
<div style="display:flex;align-items:center;gap:7px;">
<span style="font-size:0.8rem;">☁️</span>
<div><div style="font-size:0.66rem;font-weight:700;color:#94A3B8;">Secure Storage</div>
<div style="font-size:0.6rem;color:#4B5563;">Encrypted resume vault</div></div></div>
</div></div>""", unsafe_allow_html=True)

            # Footer
            st.markdown("""<div style="text-align:center;margin-top:18px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.05);">
<div style="font-size:0.65rem;color:#374151;margin-bottom:6px;">© 2025 PlaceMentor AI · All rights reserved</div>
<div style="display:flex;justify-content:center;gap:16px;">
<a href="#" style="font-size:0.62rem;color:#4B5563!important;text-decoration:none!important;font-weight:600;">Privacy</a>
<a href="#" style="font-size:0.62rem;color:#4B5563!important;text-decoration:none!important;font-weight:600;">Terms</a>
<a href="#" style="font-size:0.62rem;color:#4B5563!important;text-decoration:none!important;font-weight:600;">Security</a>
<a href="#" style="font-size:0.62rem;color:#4B5563!important;text-decoration:none!important;font-weight:600;">Contact</a>
</div></div>""", unsafe_allow_html=True)

    # ── FULL WIDTH MARKETING LAYOUT ──
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

    # 1. PLATFORM STATISTICS SECTION
    st.markdown("<h3 style='text-align:center; font-weight:900; font-size:1.8rem; color:#F0F6FC; margin: 40px 0 30px; letter-spacing:-0.02em;'>Platform Metric Analytics</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""<div class="kpi-card" style="text-align:center; margin-bottom: 20px;">
<div style="font-size:2.2rem;font-weight:900;background:linear-gradient(135deg,#6366F1,#A855F7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-0.02em;">50+</div>
<div style="font-size:0.68rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.08em;margin-top:5px;">Recruiting Partners</div>
</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="kpi-card" style="text-align:center; margin-bottom: 20px;">
<div style="font-size:2.2rem;font-weight:900;background:linear-gradient(135deg,#10B981,#34D399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-0.02em;">15K+</div>
<div style="font-size:0.68rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.08em;margin-top:5px;">Resumes Parsed</div>
</div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="kpi-card" style="text-align:center; margin-bottom: 20px;">
<div style="font-size:2.2rem;font-weight:900;background:linear-gradient(135deg,#F59E0B,#FCD34D);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-0.02em;">500+</div>
<div style="font-size:0.68rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.08em;margin-top:5px;">Practice Questions</div>
</div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""<div class="kpi-card" style="text-align:center; margin-bottom: 20px;">
<div style="font-size:2.2rem;font-weight:900;background:linear-gradient(135deg,#38BDF8,#7DD3FC);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-0.02em;">95%</div>
<div style="font-size:0.68rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.08em;margin-top:5px;">ATS Accuracy</div>
</div>""", unsafe_allow_html=True)

    # 2. KEY CAPABILITIES (3 columns)
    st.markdown("<h3 style='text-align:center; font-weight:900; font-size:1.8rem; color:#F0F6FC; margin: 40px 0 30px; letter-spacing:-0.02em;'>Engineered Core Capabilities</h3>", unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.markdown("""<div class="glass-card" style="margin-bottom: 20px; min-height: 150px;">
<div style="font-size:1.8rem;margin-bottom:8px;">📄</div>
<h4 style="margin:0 0 6px;color:#F0F6FC;font-size:0.95rem;font-weight:700;">Resume AI Parsing</h4>
<p style="color:#94A3B8;font-size:0.8rem;margin:0;line-height:1.5;">Automated text extraction, section segmentation, and keyword density mapping.</p>
</div>""", unsafe_allow_html=True)
        st.markdown("""<div class="glass-card" style="margin-bottom: 20px; min-height: 150px;">
<div style="font-size:1.8rem;margin-bottom:8px;">⚔️</div>
<h4 style="margin:0 0 6px;color:#F0F6FC;font-size:0.95rem;font-weight:700;">Interview Simulator</h4>
<p style="color:#94A3B8;font-size:0.8rem;margin:0;line-height:1.5;">Practice mock technical sessions with detailed AI scoring feedback loops.</p>
</div>""", unsafe_allow_html=True)
        
    with col_f2:
        st.markdown("""<div class="glass-card" style="margin-bottom: 20px; min-height: 150px;">
<div style="font-size:1.8rem;margin-bottom:8px;">🎯</div>
<h4 style="margin:0 0 6px;color:#F0F6FC;font-size:0.95rem;font-weight:700;">Eligibility Engine</h4>
<p style="color:#94A3B8;font-size:0.8rem;margin:0;line-height:1.5;">Evaluate CGPA, branches, and backlog constraints against recruiter models.</p>
</div>""", unsafe_allow_html=True)
        st.markdown("""<div class="glass-card" style="margin-bottom: 20px; min-height: 150px;">
<div style="font-size:1.8rem;margin-bottom:8px;">📊</div>
<h4 style="margin:0 0 6px;color:#F0F6FC;font-size:0.95rem;font-weight:700;">Placement Analytics</h4>
<p style="color:#94A3B8;font-size:0.8rem;margin:0;line-height:1.5;">Visualise readiness velocity, streak metrics, and technical skill gaps.</p>
</div>""", unsafe_allow_html=True)
        
    with col_f3:
        st.markdown("""<div class="glass-card" style="margin-bottom: 20px; min-height: 150px;">
<div style="font-size:1.8rem;margin-bottom:8px;">🗺️</div>
<h4 style="margin:0 0 6px;color:#F0F6FC;font-size:0.95rem;font-weight:700;">Learning Roadmaps</h4>
<p style="color:#94A3B8;font-size:0.8rem;margin:0;line-height:1.5;">Personalized study tasks generated dynamically from recruiter criteria.</p>
</div>""", unsafe_allow_html=True)
        st.markdown("""<div class="glass-card" style="margin-bottom: 20px; min-height: 150px;">
<div style="font-size:1.8rem;margin-bottom:8px;">🏢</div>
<h4 style="margin:0 0 6px;color:#F0F6FC;font-size:0.95rem;font-weight:700;">Recruiter Directory</h4>
<p style="color:#94A3B8;font-size:0.8rem;margin:0;line-height:1.5;">Direct insights into 50+ company selection metrics and interview guides.</p>
</div>""", unsafe_allow_html=True)

    # 3. ENTERPRISE TECH STACK SECTION (centered horizontal layout)
    st.markdown("<h3 style='text-align:center; font-weight:900; font-size:1.8rem; color:#F0F6FC; margin: 40px 0 20px; letter-spacing:-0.02em;'>Enterprise-Grade Stack</h3>", unsafe_allow_html=True)
    st.markdown("""
<div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap; margin-bottom: 40px;">
<span style="background:rgba(99,102,241,0.09);border:1px solid rgba(99,102,241,0.22);border-radius:20px;padding:6px 16px;font-size:0.75rem;font-weight:700;color:#A5B4FC;">⚡ FastAPI</span>
<span style="background:rgba(56,189,248,0.09);border:1px solid rgba(56,189,248,0.22);border-radius:20px;padding:6px 16px;font-size:0.75rem;font-weight:700;color:#7DD3FC;">🐍 Python</span>
<span style="background:rgba(16,185,129,0.09);border:1px solid rgba(16,185,129,0.22);border-radius:20px;padding:6px 16px;font-size:0.75rem;font-weight:700;color:#34D399;">🐘 PostgreSQL</span>
<span style="background:rgba(56,189,248,0.09);border:1px solid rgba(56,189,248,0.22);border-radius:20px;padding:6px 16px;font-size:0.75rem;font-weight:700;color:#7DD3FC;">🐳 Docker</span>
<span style="background:rgba(244,63,94,0.09);border:1px solid rgba(244,63,94,0.22);border-radius:20px;padding:6px 16px;font-size:0.75rem;font-weight:700;color:#FB7185;">⚡ Redis</span>
<span style="background:rgba(168,85,247,0.09);border:1px solid rgba(168,85,247,0.22);border-radius:20px;padding:6px 16px;font-size:0.75rem;font-weight:700;color:#D8B4FE;">🤖 AI Engine</span>
</div>
""", unsafe_allow_html=True)

    # 4. TESTIMONIALS SECTION (centered layout)
    st.markdown("<h3 style='text-align:center; font-weight:900; font-size:1.8rem; color:#F0F6FC; margin: 40px 0 20px; letter-spacing:-0.02em;'>Student Success Stories</h3>", unsafe_allow_html=True)
    st.markdown("""
<div style="display:flex; justify-content:center; padding: 0 20px 60px;">
<div style="max-width:700px;background:rgba(17,24,39,0.7);border:1px solid rgba(255,255,255,0.07);border-radius:20px;padding:28px;backdrop-filter:blur(20px);text-align:center;">
<div style="font-size:2.5rem;color:#6366F1;line-height:1;margin-bottom:8px;font-family:Georgia,serif;">"</div>
<div style="font-size:1.05rem;color:#C7D2FE;line-height:1.7;margin-bottom:20px;font-style:italic;">PlaceMentor AI analyzed my resume gaps, showed me exactly which companies I qualified for, and built my entire 3-month prep roadmap. Got placed at Google in my first attempt.</div>
<div style="display:flex;align-items:center;justify-content:center;gap:12px;">
<div style="width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#6366F1,#A855F7);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.9rem;color:white;">P</div>
<div style="text-align:left;"><div style="font-size:0.85rem;font-weight:700;color:#F0F6FC;">Priya Sharma</div><div style="font-size:0.72rem;color:#64748B;">IIT Bombay · Placed at Google SWE</div></div>
<div style="margin-left:20px;display:flex;gap:2px;"><span style="color:#F59E0B;font-size:0.9rem;">★★★★★</span></div>
</div></div></div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# DASHBOARD — Premium Command Center (post-login)
# ─────────────────────────────────────────────────────────────────────
def render_dashboard():
    # Top header bar
    email_display = st.session_state.user_email or "User"
    st.markdown(textwrap.dedent(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                margin-bottom:28px;background:rgba(17,24,39,0.6);
                padding:14px 22px;border-radius:16px;
                border:1px solid rgba(255,255,255,0.06);
                backdrop-filter:blur(20px);">
        <div>
            <div style="font-size:0.65rem;color:#4B5563;font-weight:700;
                        text-transform:uppercase;letter-spacing:0.1em;">PORTAL · COMMAND CENTER</div>
            <h2 style="margin:2px 0 0;font-size:1.5rem;font-weight:900;color:#F0F6FC;">
                Placement Command Center</h2>
        </div>
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="display:inline-flex;align-items:center;gap:5px;
                        background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.28);
                        border-radius:20px;padding:4px 12px;">
                <span style="width:6px;height:6px;background:#10B981;border-radius:50%;
                             display:inline-block;"></span>
                <span style="font-size:0.65rem;color:#34D399;font-weight:700;
                             letter-spacing:0.06em;">SYSTEM ONLINE</span>
            </div>
            <div style="width:36px;height:36px;border-radius:50%;
                        background:linear-gradient(135deg,#6366F1,#38BDF8);
                        display:flex;align-items:center;justify-content:center;
                        font-weight:800;color:#FFF;font-size:0.9rem;
                        box-shadow:0 0 14px rgba(99,102,241,0.4);">
                {email_display[0].upper()}</div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    # Fetch analytics
    metrics = {
        "placement_readiness_percentage": 0,
        "resume_ats_score": 0,
        "study_streak_days": 0,
        "total_study_hours": 0.0,
        "top_missing_skills": [],
        "eligible_companies_count": 0,
        "almost_eligible_companies_count": 0,
        "recommended_next_action": "Upload your resume and complete your profile to unlock AI placement scoring.",
        "readiness_trend": {"Month 1": 15, "Month 2": 45, "Month 3": 75},
    }
    try:
        res = api_client.get("/roadmap/dashboard-analytics")
        if res.status_code == 200:
            metrics = res.json()
    except Exception:
        pass

    # AI Recommendation Banner
    st.markdown(textwrap.dedent(f"""
    <div style="background:linear-gradient(135deg,rgba(99,102,241,0.12),rgba(124,58,237,0.08));
                border:1px solid rgba(99,102,241,0.2);border-radius:16px;
                padding:18px 22px;margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;">
            <div>
                <div style="display:inline-block;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);
                            border-radius:20px;padding:3px 10px;font-size:0.62rem;font-weight:700;
                            color:#FCD34D;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:7px;">
                    💡 AI Coaching Recommendation</div>
                <div style="font-size:0.92rem;font-weight:700;color:#F0F6FC;">
                    {metrics['recommended_next_action']}</div>
                <div style="font-size:0.8rem;color:#94A3B8;margin-top:5px;">
                    AI evaluated your profile, resume & role specifications.</div>
            </div>
            <div style="background:linear-gradient(135deg,#6366F1,#7C3AED);border-radius:20px;
                        padding:6px 16px;font-size:0.78rem;font-weight:800;color:white;
                        white-space:nowrap;">
                Readiness: {metrics['placement_readiness_percentage']}%</div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        (c1, "PLACEMENT READINESS", f"{metrics['placement_readiness_percentage']}%", "#6366F1",
         f"Eligible: {metrics['eligible_companies_count']} Companies", "badge-indigo"),
        (c2, "RESUME ATS SCORE", f"{metrics['resume_ats_score']}%", "#10B981",
         "PyMuPDF + spaCy Verified", "badge-eligible"),
        (c3, "STUDY STREAK", f"🔥 {metrics['study_streak_days']}d", "#F59E0B",
         f"Logged: {metrics['total_study_hours']} hrs", "badge-warning"),
        (c4, "NEAR FIT COMPANIES", f"{metrics['almost_eligible_companies_count']}", "#EC4899",
         "Match threshold ≥ 70%", "badge-purple"),
    ]
    for col, label, val, color, sub, badge in kpis:
        with col:
            st.markdown(textwrap.dedent(f"""
            <div class="kpi-card">
                <div class="stat-lbl">{label}</div>
                <div class="stat-val" style="color:{color};margin:8px 0 10px;">{val}</div>
                <div style="color:#94A3B8;font-size:0.75rem;display:flex;
                            align-items:center;justify-content:space-between;">
                    <span>{sub}</span>
                </div>
            </div>
            """), unsafe_allow_html=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Charts + Skill Gaps
    col_chart, col_skills = st.columns([1.6, 1])
    with col_chart:
        st.markdown("""<div style="font-size:1rem;font-weight:800;color:#F0F6FC;
                        margin-bottom:14px;letter-spacing:-0.01em;">
            📈 Placement Readiness Velocity</div>""", unsafe_allow_html=True)
        trend_keys = list(metrics["readiness_trend"].keys())
        trend_vals = list(metrics["readiness_trend"].values())
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend_keys, y=trend_vals, mode="lines+markers", name="Readiness",
            line=dict(color="#6366F1", width=3),
            marker=dict(size=7, color="#818CF8", line=dict(color="#6366F1", width=2)),
            fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
        ))
        apply_plotly_dark_theme(fig, height=260)
        fig.update_layout(yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig, use_container_width=True)

    with col_skills:
        st.markdown("""<div style="font-size:1rem;font-weight:800;color:#F0F6FC;
                        margin-bottom:14px;letter-spacing:-0.01em;">
            🛠️ Key Skill Gaps</div>""", unsafe_allow_html=True)
        if not metrics["top_missing_skills"]:
            st.markdown("""<div class="glass-card" style="border-color:rgba(16,185,129,0.3);
                                background:rgba(16,185,129,0.04)!important;">
                <div style="font-weight:800;color:#34D399;margin-bottom:6px;">✓ No Skill Gaps</div>
                <div style="color:#94A3B8;font-size:0.82rem;">You satisfy all tech requirements
                    for your targeted recruiters.</div></div>""", unsafe_allow_html=True)
        else:
            for i, skill in enumerate(metrics["top_missing_skills"][:5]):
                st.markdown(f"""<div class="glass-card" style="padding:12px 16px;
                    margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-weight:700;color:#F0F6FC;font-size:0.85rem;">{i+1}. {skill}</span>
                    <span class="badge badge-ineligible">Gap</span></div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Onboarding Checklist
    st.markdown("""<div style="font-size:1rem;font-weight:800;color:#F0F6FC;
                    margin-bottom:16px;letter-spacing:-0.01em;">
        🎓 Getting Started — Placement Checklist</div>""", unsafe_allow_html=True)
    steps = [
        ("STEP 1", "badge-indigo", "📄 Resume Analyzer",
         "Upload your PDF resume to extract skills, parse ATS score, and get improvement feedback."),
        ("STEP 2", "badge-purple", "🏢 Company Hub",
         "Browse 50+ recruiter profiles. Missing skills auto-populate your learning roadmap."),
        ("STEP 3", "badge-eligible", "📚 Learning Roadmap",
         "Complete tasks, take MCQ quizzes, log study hours, and practice AI mock interviews."),
    ]
    sc1, sc2, sc3 = st.columns(3)
    for col, (tag, badge, title, desc) in zip([sc1, sc2, sc3], steps):
        with col:
            st.markdown(textwrap.dedent(f"""
            <div class="glass-card" style="min-height:140px;">
                <span class="badge {badge}" style="margin-bottom:10px;">{tag}</span>
                <h4 style="margin:0 0 8px;color:#F0F6FC;font-size:0.95rem;">{title}</h4>
                <p style="color:#94A3B8;font-size:0.8rem;margin:0;line-height:1.55;">{desc}</p>
            </div>
            """), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# ROUTE
# ─────────────────────────────────────────────────────────────────────
if not st.session_state.access_token:
    render_auth_screen()
else:
    render_dashboard()
