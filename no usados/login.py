
import streamlit as st
from utils.config import set_page_style
from utils.database import init_db
import sqlite3

# Configuración global
set_page_style()
init_db()

# --- LOGIN ---
st.title("Gestión de Aulas y Laboratorios")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Bienvenido {username}!")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
else:
    st.success(f"Sesión iniciada como {st.session_state.username}")
    st.write("Usa el menú lateral para navegar entre las secciones.")
