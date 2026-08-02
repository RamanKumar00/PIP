import streamlit as st

def form_section(title, description=None):
    """
    Standard container section to divide form fields with clear typography and spacing.
    """
    st.markdown(f"""
    <div class="form-section-header" style="margin-top: 32px; margin-bottom: 16px;">
        <h3 style="margin: 0 0 4px 0; font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 600; color: #FFFFFF;">{title}</h3>
        {f'<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 14px; color: #94A3B8;">{description}</p>' if description else ''}
    </div>
    """, unsafe_allow_html=True)
