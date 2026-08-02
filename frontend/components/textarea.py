import streamlit as st

def custom_textarea(label, value="", placeholder="", key=None, disabled=False, height=120):
    """
    Standard textarea component following the global spacing guidelines.
    """
    return st.text_area(
        label=label,
        value=value,
        placeholder=placeholder,
        key=key,
        disabled=disabled,
        height=height
    )
