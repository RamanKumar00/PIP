import streamlit as st
import plotly.graph_objects as go


def inject_custom_css():
    """Premium SaaS Design System — Linear / Stripe / Vercel / Notion aesthetic."""
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── ANIMATIONS ── */
@keyframes floatA {
  0%,100%{transform:translate(0,0) scale(1);}
  33%{transform:translate(25px,-35px) scale(1.04);}
  66%{transform:translate(-18px,18px) scale(0.96);}
}
@keyframes floatB {
  0%,100%{transform:translate(0,0) scale(1);}
  50%{transform:translate(-30px,-15px) scale(1.08);}
}
@keyframes floatC {
  0%,100%{transform:translate(0,0) rotate(0deg);}
  50%{transform:translate(20px,25px) rotate(180deg);}
}
@keyframes fadeInUp {
  from{opacity:0;transform:translateY(24px);}
  to{opacity:1;transform:translateY(0);}
}
@keyframes fadeInRight {
  from{opacity:0;transform:translateX(24px);}
  to{opacity:1;transform:translateX(0);}
}
@keyframes slideDown {
  from{opacity:0;transform:translateY(-12px);}
  to{opacity:1;transform:translateY(0);}
}
@keyframes pulseGlow {
  0%,100%{box-shadow:0 0 8px rgba(99,102,241,0.3);}
  50%{box-shadow:0 0 20px rgba(99,102,241,0.7);}
}
@keyframes shimmer {
  0%{background-position:-400% 0;}
  100%{background-position:400% 0;}
}
@keyframes countUp {
  from{opacity:0;transform:scale(0.8);}
  to{opacity:1;transform:scale(1);}
}
@keyframes orbPulse {
  0%,100%{opacity:0.3;transform:scale(1);}
  50%{opacity:0.6;transform:scale(1.05);}
}
@keyframes borderGlow {
  0%,100%{border-color:rgba(99,102,241,0.2);}
  50%{border-color:rgba(99,102,241,0.5);}
}
@keyframes spin {
  from{transform:rotate(0deg);}
  to{transform:rotate(360deg);}
}

/* ── ROOT VARIABLES ── */
:root {
  --bg-dark: #0B1020;
  --bg-darker: #070C16;
  --sidebar-bg: #0F172A;
  --card-bg: rgba(17,24,39,0.8);
  --card-bg-solid: #111827;
  --card-border: rgba(255,255,255,0.07);
  --card-border-hover: rgba(99,102,241,0.35);
  --card-border-glow: rgba(99,102,241,0.4);
  --primary: #6366F1;
  --primary-dark: #4F46E5;
  --primary-glow: rgba(99,102,241,0.25);
  --secondary: #7C3AED;
  --accent-blue: #38BDF8;
  --accent-purple: #A855F7;
  --accent-pink: #EC4899;
  --success: #10B981;
  --success-light: rgba(16,185,129,0.15);
  --warning: #F59E0B;
  --warning-light: rgba(245,158,11,0.15);
  --danger: #F43F5E;
  --danger-light: rgba(244,63,94,0.15);
  --text-main: #F0F6FC;
  --text-muted: #94A3B8;
  --text-dim: #64748B;
  --text-dimmer: #374151;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 24px;
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.3);
  --shadow-md: 0 8px 24px rgba(0,0,0,0.4);
  --shadow-lg: 0 16px 48px rgba(0,0,0,0.5);
  --shadow-glow: 0 0 30px rgba(99,102,241,0.25);
}

/* ── GLOBAL RESET ── */
html, body, [class*="css"], .stMarkdown {
  font-family: 'Plus Jakarta Sans','Inter',-apple-system,BlinkMacSystemFont,sans-serif !important;
  color: var(--text-main);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ── APP BACKGROUND ── */
.stApp {
  background-color: var(--bg-dark) !important;
  background-image:
    radial-gradient(ellipse at 0% 0%, rgba(99,102,241,0.07) 0%, transparent 55%),
    radial-gradient(ellipse at 100% 100%, rgba(168,85,247,0.05) 0%, transparent 55%),
    radial-gradient(ellipse at 50% 100%, rgba(56,189,248,0.03) 0%, transparent 50%);
  background-attachment: fixed;
}

/* ── HIDE DEFAULT STREAMLIT CHROME ── */
#MainMenu, footer, header, [data-testid="stHeader"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] {
  display: none !important;
  height: 0 !important;
  visibility: hidden !important;
}

/* ── BLOCK CONTAINER ── */
div.block-container {
  max-width: 1400px !important;
  margin: auto !important;
  padding-left: 40px !important;
  padding-right: 40px !important;
  padding-top: 32px !important;
  padding-bottom: 40px !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.5); }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
  background: #0d1117 !important;
  border-right: 1px solid rgba(255,255,255,0.06) !important;
  box-shadow: 4px 0 30px rgba(0,0,0,0.4) !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

/* Logo top breathing room */
section[data-testid="stSidebar"] .logo-container {
  padding: 32px 24px 20px 24px !important;
  border-bottom: 1px solid rgba(255,255,255,0.05) !important;
  margin-bottom: 24px !important;
}

/* Sidebar navigation padding and gap */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
  border-radius: 12px !important;
  padding: 16px 20px !important;
  color: #94A3B8 !important;
  font-size: 0.9rem !important;
  font-weight: 500 !important;
  transition: all 0.2s ease !important;
  border: 1px solid transparent !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
  background: rgba(99,102,241,0.08) !important;
  color: #C7D2FE !important;
  border-color: rgba(99,102,241,0.18) !important;
  transform: translateX(2px) !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
  background: rgba(99,102,241,0.15) !important;
  color: #A5B4FC !important;
  border-color: rgba(99,102,241,0.3) !important;
  font-weight: 700 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul {
  padding: 0 16px !important;
  list-style: none !important;
  gap: 12px !important; /* 12px gap between nav items */
}

/* Sidebar button */
section[data-testid="stSidebar"] div.stButton > button {
  width: 100% !important;
  border-radius: 12px !important;
  font-size: 0.83rem !important;
  font-weight: 600 !important;
  transition: all 0.2s ease !important;
}

/* ── CARD COMPONENTS ── */
.glass-card {
  background: #111827 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 18px !important;
  padding: 32px !important;
  margin-bottom: 24px !important;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
  backdrop-filter: blur(24px) !important;
  -webkit-backdrop-filter: blur(24px) !important;
  transition: all 0.25s ease !important;
}
.glass-card:hover {
  border-color: rgba(99,102,241,0.3) !important;
  box-shadow: 0 10px 30px rgba(99,102,241,0.12) !important;
  transform: translateY(-2px) !important;
}

.kpi-card {
  background: #111827 !important;
  border: 1px solid rgba(255,255,255,0.08) !important;
  border-radius: 18px !important;
  padding: 32px !important;
  backdrop-filter: blur(24px) !important;
  transition: all 0.25s ease !important;
  animation: fadeInUp 0.5s ease both !important;
}
.kpi-card:hover {
  border-color: var(--card-border-hover) !important;
  box-shadow: var(--shadow-glow) !important;
  transform: translateY(-2px) !important;
}

.stat-val {
  font-size: 2rem;
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1.1;
}
.stat-lbl {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-dim);
  margin-top: 4px;
}

/* Page Header Bar Styling */
.page-header {
  padding: 32px 24px 24px 24px !important;
  margin-bottom: 24px !important;
  background: rgba(15,23,42,0.4) !important;
  border-radius: 18px !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
}

/* ── HERO BANNER ── */
.hero-banner {
  background: linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(124,58,237,0.08) 50%, rgba(168,85,247,0.06) 100%);
  border: 1px solid rgba(99,102,241,0.2);
  border-radius: 18px;
  padding: 32px;
  margin-bottom: 24px;
  animation: fadeInUp 0.5s ease;
}

/* ── BADGE SYSTEM ── */
.badge {
  display: inline-flex; align-items: center;
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
}
.badge-indigo { background: rgba(99,102,241,0.15); color: #A5B4FC; border: 1px solid rgba(99,102,241,0.3); }
.badge-purple { background: rgba(168,85,247,0.15); color: #D8B4FE; border: 1px solid rgba(168,85,247,0.3); }
.badge-eligible { background: rgba(16,185,129,0.15); color: #34D399; border: 1px solid rgba(16,185,129,0.3); }
.badge-warning { background: rgba(245,158,11,0.15); color: #FCD34D; border: 1px solid rgba(245,158,11,0.3); }
.badge-ineligible { background: rgba(244,63,94,0.15); color: #FB7185; border: 1px solid rgba(244,63,94,0.3); }
.badge-info { background: rgba(56,189,248,0.15); color: #7DD3FC; border: 1px solid rgba(56,189,248,0.3); }

.neon-text-indigo {
  background: linear-gradient(135deg, #818CF8 0%, #A78BFA 50%, #C084FC 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ── FORM COMPONENTS ── */
/* Container blocks */
div[data-testid="stTextInput"], 
div[data-testid="stNumberInput"], 
div[data-testid="stSelectbox"], 
div[data-testid="stTextArea"] {
  position: relative !important;
  margin-top: 12px !important;
  margin-bottom: 20px !important;
  display: flex !important;
  flex-direction: column !important;
}

/* Reusable Standard Labels System (Label above input) */
div[data-testid="stTextInput"] label, 
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stWidgetLabel"] label,
div[data-testid="stWidgetLabel"] label p,
div[data-testid="stWidgetLabel"] p {
  position: static !important; /* Standard static flow positioning */
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  color: #94A3B8 !important; /* Accessible muted gray label */
  margin-bottom: 8px !important; /* 8px breathing space below label */
  text-transform: none !important;
  letter-spacing: normal !important;
  display: block !important;
  width: auto !important;
  transform: none !important;
}

/* Focus color change for labels */
div[data-testid="stTextInput"]:focus-within label, 
div[data-testid="stNumberInput"]:focus-within label,
div[data-testid="stSelectbox"]:focus-within label,
div[data-testid="stTextArea"]:focus-within label {
  color: #6366F1 !important; /* Active label turns indigo */
}

/* BaseWeb Input box container styling */
div[data-baseweb="input"] {
  height: 56px !important; /* 56px container height */
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 14px !important; /* 14px rounded corners */
  transition: all 0.25s ease !important;
  box-sizing: border-box !important;
}
div[data-baseweb="input"] input {
  height: 100% !important;
  background: transparent !important;
  border: none !important;
  padding: 0 18px !important; /* 18px horizontal padding */
  color: var(--text-main) !important;
  font-size: 16px !important; /* 16px text size */
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  caret-color: var(--primary) !important;
  box-sizing: border-box !important;
}
div[data-baseweb="input"]:focus-within {
  border-color: rgba(99,102,241,0.65) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important; /* Indigo glow focus ring */
  background: rgba(99,102,241,0.04) !important;
}
div[data-baseweb="input"] input::placeholder {
  color: #4B5563 !important; /* Muted gray placeholder */
}

/* Center password visibility icon vertically */
div[data-baseweb="input"] [data-testid="InputAdornment"] button {
  height: auto !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  background: transparent !important;
  border: none !important;
  color: #94A3B8 !important;
  margin-right: 8px !important;
}

/* Textarea styling wrapper */
div[data-baseweb="textarea"] {
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 14px !important;
  transition: all 0.25s ease !important;
  box-sizing: border-box !important;
}
div[data-baseweb="textarea"] textarea {
  background: transparent !important;
  border: none !important;
  padding: 16px 18px !important; /* 16px top/bottom, 18px left/right padding */
  color: var(--text-main) !important;
  font-size: 16px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  min-height: 120px !important;
  box-sizing: border-box !important;
}
div[data-baseweb="textarea"]:focus-within {
  border-color: rgba(99,102,241,0.65) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
  background: rgba(99,102,241,0.04) !important;
}

/* Selectbox styling wrapper */
div[data-baseweb="select"] > div {
  height: 56px !important;
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 14px !important;
  padding: 0 18px !important; /* 18px horizontal padding */
  color: var(--text-main) !important;
  font-size: 16px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  display: flex !important;
  align-items: center !important;
  transition: all 0.25s ease !important;
  box-sizing: border-box !important;
}
div[data-baseweb="select"] > div:focus-within {
  border-color: rgba(99,102,241,0.65) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
  background: rgba(99,102,241,0.04) !important;
}
div[data-baseweb="popover"] { background: #1E293B !important; border-color: rgba(255,255,255,0.1) !important; border-radius: var(--radius-lg) !important; }

/* Form container — no leaked border */
div[data-testid="stForm"] {
  border: none !important;
  padding: 0 !important;
  background: transparent !important;
}

/* ── BUTTON SYSTEM ── */
.stButton > button, .stFormSubmitButton > button {
  min-height: 48px !important;
  padding: 14px 24px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  border-radius: 12px !important;
  background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
  border: none !important;
  color: white !important;
  transition: all 0.25s ease !important;
  box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
  margin-top: 24px !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
  box-shadow: 0 8px 28px rgba(99,102,241,0.5) !important;
  transform: translateY(-2px) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.04) !important;
  border-radius: var(--radius-md) !important;
  padding: 4px !important;
  gap: 3px !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: var(--radius-sm) !important;
  color: var(--text-dim) !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  padding: 7px 18px !important;
  transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #6366F1, #7C3AED) !important;
  color: white !important;
  box-shadow: 0 3px 12px rgba(99,102,241,0.35) !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── CHECKBOX ── */
.stCheckbox label { color: var(--text-muted) !important; font-size: 0.82rem !important; }
.stCheckbox [data-testid="stWidgetLabel"] { color: var(--text-muted) !important; }

/* ── TABLES ── */
.stDataFrame { background: transparent !important; }
.stDataFrame [data-testid="stDataFrameGlide"] { background: var(--card-bg) !important; border-radius: var(--radius-lg) !important; }

/* ── ALERTS ── */
.stAlert {
  border-radius: var(--radius-lg) !important;
  border-left-width: 3px !important;
  background: rgba(17,24,39,0.6) !important;
}

/* ── METRIC ── */
[data-testid="stMetric"] {
  background: rgba(17,24,39,0.6) !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: var(--radius-lg) !important;
  padding: 16px !important;
}
[data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 900 !important; }

/* ── EXPANDER ── */
.streamlit-expanderHeader {
  background: rgba(17,24,39,0.6) !important;
  border: 1px solid rgba(255,255,255,0.06) !important;
  border-radius: var(--radius-lg) !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div {
  background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
  border-radius: 6px !important;
}

/* ── BORDER WRAPPER (st.container border) ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(17,24,39,0.75) !important;
  border: 1px solid rgba(99,102,241,0.2) !important;
  border-radius: var(--radius-2xl) !important;
  backdrop-filter: blur(24px) !important;
  transition: border-color 0.25s ease !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: rgba(99,102,241,0.35) !important;
}

/* Reset container-like styles on nested columns to avoid capsule borders */
div[data-testid="stColumn"] div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stColumn"] div[data-testid="stVerticalBlock"],
div[data-testid="stColumn"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
  padding: 0 !important;
}

/* ── PLOTLY CHART CONTAINERS ── */
.stPlotlyChart { border-radius: var(--radius-lg) !important; overflow: hidden !important; }
[data-testid="stPlotlyChart"] > div { border-radius: var(--radius-lg) !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] > section {
  background: rgba(99,102,241,0.04) !important;
  border: 2px dashed rgba(99,102,241,0.3) !important;
  border-radius: var(--radius-xl) !important;
  transition: all 0.25s ease !important;
}
[data-testid="stFileUploader"] > section:hover {
  background: rgba(99,102,241,0.08) !important;
  border-color: rgba(99,102,241,0.5) !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-color: var(--primary) transparent transparent transparent !important; }

/* ── RADIO ── */
.stRadio label { color: var(--text-muted) !important; }

/* ── SLIDER ── */
.stSlider [data-baseweb="slider"] div[role="slider"] { background: var(--primary) !important; }

/* ── INFO/SUCCESS/WARNING/ERROR OVERRIDES ── */
div[data-testid="stInfoMessage"] { background: rgba(56,189,248,0.08) !important; border-color: rgba(56,189,248,0.3) !important; color: #7DD3FC !important; border-radius: var(--radius-lg) !important; }
div[data-testid="stSuccessMessage"] { background: rgba(16,185,129,0.08) !important; border-color: rgba(16,185,129,0.3) !important; color: #34D399 !important; border-radius: var(--radius-lg) !important; }
div[data-testid="stWarningMessage"] { background: rgba(245,158,11,0.08) !important; border-color: rgba(245,158,11,0.3) !important; color: #FCD34D !important; border-radius: var(--radius-lg) !important; }
div[data-testid="stErrorMessage"] { background: rgba(244,63,94,0.08) !important; border-color: rgba(244,63,94,0.3) !important; color: #FB7185 !important; border-radius: var(--radius-lg) !important; }

/* ── DIVIDER ── */
hr { border-color: rgba(255,255,255,0.07) !important; margin: 20px 0 !important; }

/* ── LINK ── */
a { color: var(--primary) !important; text-decoration: none !important; }
a:hover { color: #818CF8 !important; text-decoration: underline !important; }

/* ── COLUMN GAP FIX ── */
[data-testid="stColumns"] { gap: 1.5rem !important; }

/* ── HIDE STREAMLIT DEPLOY/MENU BUTTONS ── */
[data-testid="stToolbar"] { display: none !important; }
button[kind="header"] { display: none !important; }
</style>""", unsafe_allow_html=True)


def apply_plotly_dark_theme(fig: go.Figure, height: int = 300) -> go.Figure:
    """Apply premium dark theme to Plotly figures matching the design system."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(17,24,39,0.0)",
        plot_bgcolor="rgba(17,24,39,0.0)",
        font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color="#94A3B8", size=11),
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            bgcolor="rgba(17,24,39,0.6)",
            bordercolor="rgba(255,255,255,0.08)",
            borderwidth=1,
            font=dict(color="#94A3B8", size=11),
        ),
        xaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.05)", gridwidth=1,
            zeroline=False, showline=False,
            tickfont=dict(color="#64748B", size=10),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.05)", gridwidth=1,
            zeroline=False, showline=False,
            tickfont=dict(color="#64748B", size=10),
        ),
    )
    return fig
