
import streamlit as st

def set_page_style():
    st.set_page_config(page_title="Gestión Aulas", layout="wide")
    st.markdown("""
    <style>
    body { font-size: 18px; }
    button { font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)
