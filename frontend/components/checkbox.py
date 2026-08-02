import streamlit as st

def custom_checkbox(label, value=False, key=None, disabled=False):
    """
    Standard modern custom checkbox component wrapper.
    """
    return st.checkbox(
        label=label,
        value=value,
        key=key,
        disabled=disabled
    )
