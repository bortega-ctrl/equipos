import streamlit as st
import sqlite3
import pandas as pd

st.header("🗑 Eliminar Bloque, Laboratorio o Aula con su contenido")

delete_type = st.radio("¿Qué deseas eliminar?", ["Bloque completo", "Laboratorio", "Aula"])

conn = sqlite3.connect("data.db")
aulas_df = pd.read_sql_query("SELECT * FROM aulas", conn)
labs_df = pd.read_sql_query("SELECT * FROM laboratorios", conn)
conn.close()

if delete_type == "Bloque completo":
    bloque = st.selectbox("Selecciona el bloque", [chr(i) for i in range(ord('A'), ord('L')+1)])
    if st.button("Eliminar Bloque Completo"):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM aulas WHERE bloque=?", (bloque,))
        cursor.execute("DELETE FROM laboratorios WHERE bloque LIKE ?", (bloque + "%",))
        cursor.execute("DELETE FROM equipos WHERE ubicacion LIKE ? OR ubicacion LIKE ?", (bloque + "%", "Lab-" + bloque + "%"))
        conn.commit()
        conn.close()
        st.success(f"Bloque {bloque} eliminado junto con sus aulas, laboratorios y equipos.")

elif delete_type == "Laboratorio":
    if labs_df.empty:
        st.warning("No hay laboratorios registrados.")
    else:
        lab_id = st.selectbox("Selecciona el ID del laboratorio", labs_df['id'].tolist())
        lab_name = labs_df[labs_df['id'] == lab_id]['bloque'].values[0]
        if st.button("Eliminar Laboratorio"):
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM laboratorios WHERE id=?", (lab_id,))
            cursor.execute("DELETE FROM equipos WHERE ubicacion=?", (lab_name,))
            conn.commit()
            conn.close()
            st.success(f"Laboratorio {lab_name} eliminado junto con sus equipos.")

elif delete_type == "Aula":
    if aulas_df.empty:
        st.warning("No hay aulas registradas.")
    else:
        aula_id = st.selectbox("Selecciona el ID del aula", aulas_df['id'].tolist())
        aula_name = aulas_df[aulas_df['id'] == aula_id].apply(lambda x: f"{x['bloque']}{x['numero']}", axis=1).values[0]
        if st.button("Eliminar Aula"):
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM aulas WHERE id=?", (aula_id,))
            cursor.execute("DELETE FROM equipos WHERE ubicacion=?", (aula_name,))
            conn.commit()
            conn.close()