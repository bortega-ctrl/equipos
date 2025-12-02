
import streamlit as st
import sqlite3
import pandas as pd

st.header("👤 Gestión de Usuarios")

conn = sqlite3.connect("data.db")
df_users = pd.read_sql_query("SELECT id, username, password FROM usuarios", conn)
conn.close()

st.subheader("Usuarios registrados")
if df_users.empty:
    st.info("No hay usuarios registrados.")
else:
    edited_users = st.data_editor(
        df_users,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "username": st.column_config.TextColumn("Usuario"),
            "password": st.column_config.TextColumn("Contraseña", type="password")
        }
    )

    if st.button("Guardar cambios en usuarios"):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        for _, row in edited_users.iterrows():
            cursor.execute("""
                UPDATE usuarios SET username=?, password=? WHERE id=?
            """, (row['username'], row['password'], row['id']))
        conn.commit()
        conn.close()
        st.success("Cambios en usuarios guardados correctamente")

st.subheader("Agregar nuevo usuario")
new_username = st.text_input("Nuevo usuario")
new_password = st.text_input("Contraseña", type="password")

if st.button("Agregar Usuario"):
    if new_username and new_password:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (new_username, new_password))
            conn.commit()
            st.success(f"Usuario {new_username} agregado correctamente")
        except sqlite3.IntegrityError:
            st.error("Ese usuario ya existe")
        conn.close()
    else:
        st.warning("Debe ingresar usuario y contraseña")

st.subheader("Eliminar usuario")
if not df_users.empty:
    user_to_delete = st.selectbox("Selecciona usuario para eliminar", df_users['username'].tolist())
    if st.button("Eliminar Usuario"):
        if user_to_delete == "admin":
            st.error("No se puede eliminar el usuario administrador")
        else:
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE username=?", (user_to_delete,))
            conn.commit()
            conn.close()
            st.success(f"Usuario {user_to_delete} eliminado correctamente")
else:
    st.warning("No hay usuarios para eliminar")

