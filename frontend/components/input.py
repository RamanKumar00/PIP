import streamlit as st

def custom_text_input(label, value="", placeholder="", key=None, type="default", disabled=False):
    """
    Standard text input component following the global design system.
    """
    return st.text_input(
        label=label,
        value=value,
        placeholder=placeholder,
        key=key,
        type="password" if type == "password" else "default",
        disabled=disabled
    )

def custom_number_input(label, min_value=None, max_value=None, value=None, step=None, key=None, disabled=False):
    """
    Standard number input component following the global design system.
    """
    return st.number_input(
        label=label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        key=key,
        disabled=disabled
    )
