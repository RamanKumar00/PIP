import streamlit as st

def custom_password_input(label, value="", placeholder="Enter your password", key=None, disabled=False):
    """
    Standard password input component with integrated hide/show button styling.
    """
    return st.text_input(
        label=label,
        value=value,
        placeholder=placeholder,
        type="password",
        key=key,
        disabled=disabled
    )
