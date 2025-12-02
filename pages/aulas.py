import streamlit as st
import sqlite3
import pandas as pd

st.header("📚 Registrar Aula o Laboratorio")

bloque = st.selectbox("Bloque", [chr(i) for i in range(ord('A'), ord('L')+1)])
tipo = st.radio("Tipo", ["Aula", "Laboratorio"])
numero = st.text_input("Número (solo para aulas)")

if st.button("Guardar Aula/Lab"):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    if tipo == "Aula":
        cursor.execute("INSERT INTO aulas (bloque, numero) VALUES (?, ?)", (bloque, numero))
    else:
        cursor.execute("INSERT INTO laboratorios (bloque) VALUES (?)", (bloque,))
    conn.commit()
    conn.close()
    st.success(f"{tipo} registrado correctamente")

conn = sqlite3.connect("data.db")
aulas_df = pd.read_sql_query("SELECT * FROM aulas", conn)
labs_df = pd.read_sql_query("SELECT * FROM laboratorios", conn)
conn.close()

st.write("Aulas registradas:")
st.data_editor(aulas_df, use_container_width=True, disabled=True)
st.write("Laboratorios registrados:")
st.data_editor(labs_df, use_container_width=True, disabled=True)