import streamlit as st

def custom_selectbox(label, options, index=0, format_func=str, key=None, disabled=False):
    """
    Standard dropdown selectbox component following the global design system height.
    """
    return st.selectbox(
        label=label,
        options=options,
        index=index,
        format_func=format_func,
        key=key,
        disabled=disabled
    )
