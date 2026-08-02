import streamlit as st
import plotly.graph_objects as go


def inject_custom_css():
    """Ultra-Professional Minimalist Design System — Vercel / Shadcn Aesthetic."""
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── KEYFRAME ANIMATIONS ── */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ── ROOT VARIABLES ── */
:root {
  --bg-dark: #000000;
  --bg-darker: #000000;
  --sidebar-bg: #09090B;
  --card-bg: #09090B;
  --card-bg-solid: #09090B;
  --card-border: #27272A;
  --card-border-hover: #3F3F46;
  --primary: #FAFAFA;
  --primary-dark: #F4F4F5;
  --secondary: #A1A1AA;
  --accent-blue: #3B82F6;
  --accent-purple: #8B5CF6;
  --success: #10B981;
  --success-light: rgba(16, 185, 129, 0.1);
  --warning: #F59E0B;
  --warning-light: rgba(245, 158, 11, 0.1);
  --danger: #EF4444;
  --danger-light: rgba(239, 68, 68, 0.1);
  --text-main: #FAFAFA;
  --text-muted: #A1A1AA;
  --text-dim: #71717A;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* ── GLOBAL RESET & TYPOGRAPHY ── */
html, body, [class*="css"], .stMarkdown {
  font-family: 'Geist', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  color: var(--text-main);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ── APP BACKGROUND ── */
.stApp {
  background-color: var(--bg-dark) !important;
}

/* ── HIDE DEFAULT STREAMLIT CHROME ── */
#MainMenu, footer, header, [data-testid="stHeader"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"],
[data-testid="stToolbar"], button[kind="header"] {
  display: none !important;
  height: 0 !important;
  visibility: hidden !important;
}

/* ── MAIN CONTAINER (centered on the page, content itself stays readable) ── */
.block-container {
  max-width: 1200px !important;
  margin: 0 auto !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
  padding-top: 32px !important;
  padding-bottom: 64px !important;
}

/* ── MODERN SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #3F3F46; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #52525B; }

/* ── SIDEBAR STYLING ── */
section[data-testid="stSidebar"] {
  background: var(--sidebar-bg) !important;
  border-right: 1px solid var(--card-border) !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

/* Sidebar Navigation Items */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
  border-radius: var(--radius-md) !important;
  padding: 10px 14px !important;
  color: var(--text-muted) !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  transition: all 0.15s ease !important;
  border: 1px solid transparent !important;
  margin-bottom: 2px !important;
  display: flex !important;
  align-items: center !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
  background: #18181B !important;
  color: var(--text-main) !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
  background: #18181B !important;
  color: var(--text-main) !important;
  font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul {
  padding: 0 16px !important;
  list-style: none !important;
  gap: 4px !important;
}

/* ── CARDS & MINIMALISM ── */
.glass-card {
  background: var(--card-bg) !important;
  border: 1px solid var(--card-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 24px !important;
  margin-bottom: 24px !important;
  transition: border-color 0.15s ease !important;
}
.glass-card:hover {
  border-color: var(--card-border-hover) !important;
}

.kpi-card {
  background: var(--card-bg) !important;
  border: 1px solid var(--card-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 24px !important;
  transition: border-color 0.15s ease, transform 0.15s ease !important;
  animation: fadeInUp 0.4s ease both !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 4px !important;
}
.kpi-card:hover {
  border-color: var(--card-border-hover) !important;
  transform: translateY(-2px) !important;
}

.stat-val {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.1;
  color: var(--text-main) !important;
}
.stat-lbl {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-top: 4px;
}
.stat-delta {
  font-size: 0.8125rem;
  font-weight: 500;
  margin-top: 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  width: fit-content;
}
.stat-delta.up { color: #34D399; }
.stat-delta.down { color: #F87171; }

/* Page Header Component — title/subtitle on the left, actions on the right, vertically aligned */
.page-header {
  display: flex !important;
  align-items: flex-end !important;
  justify-content: space-between !important;
  flex-wrap: wrap !important;
  gap: 16px !important;
  padding: 0 0 24px 0 !important;
  margin-bottom: 24px !important;
  border-bottom: 1px solid var(--card-border) !important;
}
.page-header .page-title {
  font-size: 1.5rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.02em !important;
  color: var(--text-main) !important;
  margin: 0 !important;
}
.page-header .page-subtitle {
  font-size: 0.875rem !important;
  color: var(--text-muted) !important;
  margin-top: 4px !important;
}

/* Hero Banner — centered content block, professional landing-page feel */
.hero-banner {
  background: #09090B;
  border: 1px solid var(--card-border);
  border-radius: var(--radius-lg);
  padding: 48px 32px;
  margin-bottom: 24px;
  animation: fadeInUp 0.4s ease;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.hero-banner .hero-eyebrow {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-bottom: 12px;
}
.hero-banner .hero-title {
  font-size: 2.25rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.15;
  color: var(--text-main);
  max-width: 640px;
}
.hero-banner .hero-subtitle {
  font-size: 1rem;
  font-weight: 400;
  color: var(--text-muted);
  margin-top: 12px;
  max-width: 560px;
  line-height: 1.5;
}
.hero-banner .hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 24px;
  flex-wrap: wrap;
}

/* Left-aligned variant, opt-in via class="hero-banner hero-banner-left" */
.hero-banner-left,
.hero-banner-left .hero-title,
.hero-banner-left .hero-subtitle,
.hero-banner-left .hero-actions {
  text-align: left !important;
  align-items: flex-start !important;
  justify-content: flex-start !important;
}

/* Generic alignment utilities for markdown blocks */
.text-center { text-align: center !important; }
.text-left { text-align: left !important; }
.text-right { text-align: right !important; }
.flex-center {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

/* Section title used above groups of cards/charts */
.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--text-main);
  margin: 8px 0 16px 0;
}

/* Empty state block, centered */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 64px 24px;
  color: var(--text-muted);
}

/* ── BADGES ── */
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  border-radius: var(--radius-md);
  padding: 2px 8px;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1.5;
  border: 1px solid var(--card-border);
  background: #18181B;
  color: var(--text-main);
}
.badge-indigo { background: rgba(59, 130, 246, 0.1); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.2); }
.badge-purple { background: rgba(139, 92, 246, 0.1); color: #A78BFA; border: 1px solid rgba(139, 92, 246, 0.2); }
.badge-eligible { background: rgba(16, 185, 129, 0.1); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.2); }
.badge-warning { background: rgba(245, 158, 11, 0.1); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.2); }
.badge-ineligible { background: rgba(239, 68, 68, 0.1); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.2); }
.badge-info { background: #18181B; color: var(--text-main); border: 1px solid var(--card-border); }
.badge-cyan { background: rgba(6, 182, 212, 0.1); color: #22D3EE; border: 1px solid rgba(6, 182, 212, 0.2); }

/* Gradient Text Helpers */
.neon-text-indigo {
  color: var(--text-main);
}
.neon-text-cyan {
  color: var(--text-main);
}

/* ── FORM INPUTS & SELECTS ── */
div[data-testid="stTextInput"],
div[data-testid="stNumberInput"],
div[data-testid="stSelectbox"],
div[data-testid="stTextArea"] {
  position: relative !important;
  margin-top: 4px !important;
  margin-bottom: 16px !important;
}

div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stWidgetLabel"] label,
div[data-testid="stWidgetLabel"] label p,
div[data-testid="stWidgetLabel"] p {
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  color: var(--text-main) !important;
  margin-bottom: 6px !important;
}

div[data-testid="stTextInput"]:focus-within label,
div[data-testid="stNumberInput"]:focus-within label,
div[data-testid="stSelectbox"]:focus-within label,
div[data-testid="stTextArea"]:focus-within label {
  color: var(--text-main) !important;
}

/* BaseWeb Input styling */
div[data-baseweb="input"] {
  background: #09090B !important;
  border: 1px solid var(--card-border) !important;
  border-radius: var(--radius-md) !important;
  transition: border-color 0.15s ease !important;
}
div[data-baseweb="input"] input {
  background: transparent !important;
  color: var(--text-main) !important;
  font-size: 0.875rem !important;
  padding: 8px 12px !important;
}
div[data-baseweb="input"]:focus-within {
  border-color: var(--text-main) !important;
  background: #09090B !important;
}
div[data-baseweb="input"] input::placeholder {
  color: var(--text-dim) !important;
}

/* Textarea wrapper */
div[data-baseweb="textarea"] {
  background: #09090B !important;
  border: 1px solid var(--card-border) !important;
  border-radius: var(--radius-md) !important;
}
div[data-baseweb="textarea"] textarea {
  background: transparent !important;
  color: var(--text-main) !important;
  font-size: 0.875rem !important;
  padding: 8px 12px !important;
}
div[data-baseweb="textarea"]:focus-within {
  border-color: var(--text-main) !important;
  background: #09090B !important;
}

/* Selectbox dropdown */
div[data-baseweb="select"] > div {
  background: #09090B !important;
  border: 1px solid var(--card-border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--text-main) !important;
  font-size: 0.875rem !important;
  padding: 0 8px !important;
}
div[data-baseweb="select"] > div:focus-within {
  border-color: var(--text-main) !important;
  background: #09090B !important;
}
div[data-baseweb="popover"] { background: #09090B !important; border: 1px solid var(--card-border) !important; border-radius: var(--radius-md) !important; }

/* Form wrapper reset */
div[data-testid="stForm"] {
  border: none !important;
  padding: 0 !important;
  background: transparent !important;
}

/* ── BUTTON SYSTEM ── */
.stButton > button, .stFormSubmitButton > button {
  padding: 8px 16px !important;
  font-size: 0.875rem !important;
  font-weight: 500 !important;
  border-radius: var(--radius-md) !important;
  background: var(--text-main) !important;
  border: 1px solid var(--text-main) !important;
  color: var(--bg-dark) !important;
  transition: all 0.15s ease !important;
  margin-top: 16px !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
  background: #E4E4E7 !important;
  border-color: #E4E4E7 !important;
}

/* Secondary Button */
.stButton > button[kind="secondary"] {
  background: #09090B !important;
  border: 1px solid var(--card-border) !important;
  color: var(--text-main) !important;
}
.stButton > button[kind="secondary"]:hover {
  background: #18181B !important;
  border-color: #3F3F46 !important;
}

/* ── TABS SYSTEM ── */
.stTabs [data-baseweb="tab-list"] {
  background: #09090B !important;
  border-bottom: 1px solid var(--card-border) !important;
  gap: 16px !important;
  padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  color: var(--text-muted) !important;
  font-weight: 500 !important;
  font-size: 0.875rem !important;
  padding: 8px 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
}
.stTabs [aria-selected="true"] {
  color: var(--text-main) !important;
  border-bottom: 2px solid var(--text-main) !important;
  background: transparent !important;
  box-shadow: none !important;
}

/* ── CONTAINER BORDERS (st.container border=True) ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--card-bg) !important;
  border: 1px solid var(--card-border) !important;
  border-radius: var(--radius-lg) !important;
  margin-bottom: 16px !important;
}

/* ── METRICS & ALERTS ── */
[data-testid="stMetric"] {
  background: var(--card-bg) !important;
  border: 1px solid var(--card-border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 16px !important;
}
[data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 700 !important; color: var(--text-main) !important; }
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; }

div[data-testid="stInfoMessage"] { background: rgba(59, 130, 246, 0.1) !important; border-color: rgba(59, 130, 246, 0.2) !important; color: #60A5FA !important; border-radius: var(--radius-md) !important; }
div[data-testid="stSuccessMessage"] { background: rgba(16, 185, 129, 0.1) !important; border-color: rgba(16, 185, 129, 0.2) !important; color: #34D399 !important; border-radius: var(--radius-md) !important; }
div[data-testid="stWarningMessage"] { background: rgba(245, 158, 11, 0.1) !important; border-color: rgba(245, 158, 11, 0.2) !important; color: #FBBF24 !important; border-radius: var(--radius-md) !important; }
div[data-testid="stErrorMessage"] { background: rgba(239, 68, 68, 0.1) !important; border-color: rgba(239, 68, 68, 0.2) !important; color: #F87171 !important; border-radius: var(--radius-md) !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] > section {
  background: #09090B !important;
  border: 1px dashed #3F3F46 !important;
  border-radius: var(--radius-lg) !important;
  padding: 24px !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  text-align: center !important;
}
[data-testid="stFileUploader"] > section:hover {
  border-color: var(--text-muted) !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div {
  background: var(--text-main) !important;
  border-radius: 99px !important;
}

/* ── PLOTLY CHART CONTAINERS ── */
.stPlotlyChart { border-radius: var(--radius-lg) !important; overflow: hidden !important; border: 1px solid var(--card-border) !important;}
[data-testid="stPlotlyChart"] > div { border-radius: var(--radius-lg) !important; }

/* ── DATAFRAMES / TABLES ── */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  border: 1px solid var(--card-border) !important;
  border-radius: var(--radius-lg) !important;
  overflow: hidden !important;
}

/* ── DIVIDER ── */
hr { border-color: var(--card-border) !important; margin: 24px 0 !important; }

/* ── LINK ── */
a { color: var(--text-main) !important; text-decoration: underline !important; }
a:hover { color: var(--text-muted) !important; }

/* ── COLUMN GAP ── */
[data-testid="stColumns"] { gap: 1rem !important; }
</style>""", unsafe_allow_html=True)


def apply_plotly_dark_theme(fig: go.Figure, height: int = 300) -> go.Figure:
    """Apply premium minimalistic dark theme to Plotly figures matching the design system."""
    fig.update_layout(
        height=height,
        paper_bgcolor="#09090B",
        plot_bgcolor="#09090B",
        font=dict(family="Geist, Inter, sans-serif", color="#A1A1AA", size=12),
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(
            bgcolor="#09090B",
            bordercolor="#27272A",
            borderwidth=1,
            font=dict(color="#FAFAFA", size=11),
        ),
        xaxis=dict(
            showgrid=True, gridcolor="#27272A", gridwidth=1,
            zeroline=False, showline=False,
            tickfont=dict(color="#71717A", size=11),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#27272A", gridwidth=1,
            zeroline=False, showline=False,
            tickfont=dict(color="#71717A", size=11),
        ),
    )
    return fig


def hero_banner(title: str, subtitle: str = "", eyebrow: str = "", centered: bool = True):
    """Render a polished hero banner. Set centered=False for a left-aligned variant."""
    css_class = "hero-banner" if centered else "hero-banner hero-banner-left"
    eyebrow_html = f'<div class="hero-eyebrow">{eyebrow}</div>' if eyebrow else ""
    subtitle_html = f'<div class="hero-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="{css_class}">{eyebrow_html}'
        f'<div class="hero-title">{title}</div>{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    """Render the standard page header row (title/subtitle left, bottom border)."""
    subtitle_html = f'<div class="page-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="page-header"><div><div class="page-title">{title}</div>'
        f'{subtitle_html}</div></div>',
        unsafe_allow_html=True,
    )
