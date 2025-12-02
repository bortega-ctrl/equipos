
import streamlit as st
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from database import init_db

# Inicializar la base de datos
init_db()

# --- LOGIN ---
st.markdown("<h1 style='color:#4CAF50;'>Gestión de Aulas y Laboratorios</h1>", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h3 style='color:#2196F3;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar", help="Haz clic para iniciar sesión"):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Bienvenido {username}!")
            st.rerun()  # Recarga inmediata
        else:
            st.error("Usuario o contraseña incorrectos")
else:
    st.markdown(f"<h3 style='color:#FF9800;'>Usuario: {st.session_state.username}</h3>", unsafe_allow_html=True)

    # --- Pestañas ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📚 Registrar Aula/Lab",
        "💻 Registrar Equipo",
        "📊 Reporte y Edición",
        "🗑 Eliminar",
        "👤 Gestionar Usuarios"
    ])

    # --- Tab 1: Registrar Aula/Lab ---
    with tab1:
        st.markdown("<h4 style='color:#4CAF50;'>Registrar Aula o Laboratorio</h4>", unsafe_allow_html=True)
        bloque = st.selectbox("Bloque", [chr(i) for i in range(ord('A'), ord('L')+1)])
        tipo = st.radio("Tipo", ["Aula", "Laboratorio"])
        numero = st.text_input("Número (solo para aulas)")
        if st.button("Guardar Aula/Lab", key="guardar_aula", help="Registra el aula o laboratorio"):
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            if tipo == "Aula":
                cursor.execute("INSERT INTO aulas (bloque, numero) VALUES (?, ?)", (bloque, numero))
            else:
                cursor.execute("INSERT INTO laboratorios (bloque) VALUES (?)", (bloque,))
            conn.commit()
            conn.close()
            st.success(f"{tipo} registrado correctamente")

    # --- Tab 2: Registrar Equipo ---
    with tab2:
        st.markdown("<h4 style='color:#2196F3;'>Registrar Equipo</h4>", unsafe_allow_html=True)
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT bloque, numero FROM aulas")
        aulas = [f"{row[0]}{row[1]}" for row in cursor.fetchall()]
        cursor.execute("SELECT bloque FROM laboratorios")
        laboratorios = [f"Lab-{row[0]}" for row in cursor.fetchall()]
        conn.close()