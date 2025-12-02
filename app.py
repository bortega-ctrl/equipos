
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

        ubicaciones = aulas + laboratorios
        if not ubicaciones:
            st.warning("No hay aulas ni laboratorios registrados.")
        else:
            ubicacion = st.selectbox("Selecciona ubicación", ubicaciones)
            tipo = st.selectbox("Tipo", ["PC", "Pantalla"])
            mac = st.text_input("MAC Address")
            serie = st.text_input("Número de serie")
            control = st.text_input("Número de control")
            if st.button("Guardar Equipo", key="guardar_equipo", help="Registra el equipo"):
                conn = sqlite3.connect("data.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO equipos (tipo, ubicacion, mac, serie, control) VALUES (?, ?, ?, ?, ?)",
                               (tipo, ubicacion, mac, serie, control))
                conn.commit()
                conn.close()
                st.success(f"Equipo registrado en {ubicacion}")

    # --- Tab 3: Reporte y Edición ---
    with tab3:
        st.markdown("<h4 style='color:#9C27B0;'>Reporte y Edición de Equipos</h4>", unsafe_allow_html=True)
        conn = sqlite3.connect("data.db")
        df = pd.read_sql_query("SELECT * FROM equipos", conn)
        conn.close()

        bloque_filter = st.selectbox("Filtrar por bloque", ["Todos"] + sorted(df['ubicacion'].str[0].unique()))
        estado_filter = st.selectbox("Filtrar por estado", ["Todos", "OK", "Falla", "Garantía"])

        filtered_df = df.copy()
        if bloque_filter != "Todos":
            filtered_df = filtered_df[filtered_df['ubicacion'].str.startswith(bloque_filter)]
        if estado_filter != "Todos":
            filtered_df = filtered_df[filtered_df['estado'] == estado_filter]

        st.write("Editar equipos directamente en la tabla:")
        edited_df = st.data_editor(
            filtered_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True)
            }
        )

        if st.button("Guardar cambios en la base de datos", key="guardar_cambios"):
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            for _, row in edited_df.iterrows():
                cursor.execute("""
                    UPDATE equipos SET tipo=?, ubicacion=?, mac=?, serie=?, control=?, estado=?, motivo=? WHERE id=?
                """, (
                    row['tipo'],
                    row['ubicacion'],
                    row['mac'],
                    row['serie'],
                    row['control'],
                    row['estado'],
                    row['motivo'],
                    row['id']
                ))
            conn.commit()
            conn.close()
            st.success("Todos los cambios se han guardado correctamente")

        if st.button("Exportar a PDF", key="export_pdf"):
            pdf_file = "reporte_filtrado.pdf"
            c = canvas.Canvas(pdf_file, pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(30, 750, "Reporte de Equipos Filtrado")
            y = 700
            for index, row in filtered_df.iterrows():
                text = f"ID:{row['id']} | {row['tipo']} | {row['ubicacion']} | Estado:{row['estado']} | Motivo:{row['motivo']}"
                c.drawString(30, y, text)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 750
            c.save()
            st.success(f"PDF generado: {pdf_file}")

    # --- Tab 4: Eliminar ---
    with tab4:
        st.markdown("<h4 style='color:#F44336;'>Eliminar Aula/Laboratorio o Equipo</h4>", unsafe_allow_html=True)
        delete_type = st.radio("¿Qué deseas eliminar?", ["Aula/Laboratorio", "Equipo"])
        if delete_type == "Aula/Laboratorio":
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT bloque, numero FROM aulas")
            aulas = [f"Aula {row[0]}{row[1]}" for row in cursor.fetchall()]
            cursor.execute("SELECT bloque FROM laboratorios")
            laboratorios = [f"Lab-{row[0]}" for row in cursor.fetchall()]
            conn.close()
            opciones = aulas + laboratorios
            if opciones:
                seleccion = st.selectbox("Selecciona para eliminar", opciones)
                if st.button("Eliminar Aula/Lab", key="eliminar_aula"):
                    conn = sqlite3.connect("data.db")
                    cursor = conn.cursor()
                    if "Aula" in seleccion:
                        bloque = seleccion.split()[1][0]
                        numero = seleccion.split()[1][1:]
                        cursor.execute("DELETE FROM aulas WHERE bloque=? AND numero=?", (bloque, numero))
                    else:
                        bloque = seleccion.split("-")[1]
                        cursor.execute("DELETE FROM laboratorios WHERE bloque=?", (bloque,))
                    conn.commit()
                    conn.close()
                    st.success(f"{seleccion} eliminada correctamente")
            else:
                st.warning("No hay aulas ni laboratorios registrados.")
        else:
            conn = sqlite3.connect("data.db")
            df_equipos = pd.read_sql_query("SELECT * FROM equipos", conn)
            conn.close()
            if not df_equipos.empty:
                equipo_id = st.selectbox("Selecciona ID del equipo", df_equipos['id'].tolist())
                if st.button("Eliminar Equipo", key="eliminar_equipo"):
                    conn = sqlite3.connect("data.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM equipos WHERE id=?", (equipo_id,))
                    conn.commit()
                    conn.close()
                    st.success(f"Equipo con ID {equipo_id} eliminado correctamente")
            else:
                st.warning("No hay equipos registrados.")

    # --- Tab 5: Gestionar Usuarios ---
    with tab5:
        st.markdown("<h4 style='color:#607D8B;'>Gestión de Usuarios</h4>", unsafe_allow_html=True)

        conn = sqlite3.connect("data.db")
        df_users = pd.read_sql_query("SELECT id, username FROM usuarios", conn)
        conn.close()

        st.write("Usuarios actuales:")
        st.dataframe(df_users)

        st.subheader("Agregar nuevo usuario")
        new_username = st.text_input("Nuevo usuario")
        new_password = st.text_input("Contraseña", type="password")
        if st.button("Agregar Usuario", key="agregar_usuario"):
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
            if st.button("Eliminar Usuario", key="eliminar_usuario"):
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
            st.warning("No hay usuarios registrados")
