import streamlit as st

def custom_search_input(placeholder="Search...", key=None, disabled=False):
    """
    Standardized search bar component for lists, cards, and tables.
    """
    return st.text_input(
        label="", # Search inputs usually omit labels for a cleaner inline appearance
        placeholder=placeholder,
        key=key,
        disabled=disabled
    )
