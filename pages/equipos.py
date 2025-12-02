
import streamlit as st
import sqlite3
import pandas as pd

st.header("💻 Registrar y Editar Equipos")

conn = sqlite3.connect("data.db")
cursor = conn.cursor()
cursor.execute("SELECT bloque, numero FROM aulas")
aulas = [f"{row[0]}{row[1]}" for row in cursor.fetchall()]
cursor.execute("SELECT bloque FROM laboratorios")
laboratorios = [f"Lab-{row[0]}" for row in cursor.fetchall()]
conn.close()

ubicaciones = aulas + laboratorios

if ubicaciones:
    st.subheader("Registrar nuevo equipo")
    ubicacion = st.selectbox("Selecciona ubicación", ubicaciones)
    tipo = st.selectbox("Tipo", ["PC", "Pantalla"])
    mac = st.text_input("MAC Address")
    serie = st.text_input("Número de serie")
    control = st.text_input("Número de control")

    if st.button("Guardar Equipo"):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO equipos (tipo, ubicacion, mac, serie, control) VALUES (?, ?, ?, ?, ?)",
                       (tipo, ubicacion, mac, serie, control))
        conn.commit()
        conn.close()
        st.success(f"Equipo registrado en {ubicacion}")
else:
    st.warning("No hay aulas ni laboratorios registrados.")

st.subheader("Editar equipos existentes")
conn = sqlite3.connect("data.db")
equipos_df = pd.read_sql_query("SELECT * FROM equipos", conn)
conn.close()

if equipos_df.empty:
    st.info("No hay equipos registrados.")
else:
    edited_df = st.data_editor(
        equipos_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={"id": st.column_config.NumberColumn("ID", disabled=True)}
    )

    if st.button("Guardar cambios"):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        for _, row in edited_df.iterrows():
            cursor.execute("""
                UPDATE equipos SET tipo=?, ubicacion=?, mac=?, serie=?, control=?, estado=?, motivo=? WHERE id=?
            """, (
                row['tipo'], row['ubicacion'], row['mac'], row['serie'], row['control'], row['estado'], row['motivo'], row['id']
            ))
        conn.commit()
        conn.close()
        st.success("Cambios guardados correctamente")
