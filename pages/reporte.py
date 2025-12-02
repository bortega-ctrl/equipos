import streamlit as st
import sqlite3
import pandas as pd
from utils.pdf_export import export_to_pdf

st.header("📊 Reporte y Edición de Equipos")

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

st.write("Equipos filtrados:")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("<h4 style='margin-top:20px;'>Resumen por estado</h4>", unsafe_allow_html=True)
estado_counts = filtered_df['estado'].value_counts()
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<h2 style='text-align:center;color:green;'>{estado_counts.get('OK',0)}</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>OK</p>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<h2 style='text-align:center;color:red;'>{estado_counts.get('Falla',0)}</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Falla</p>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<h2 style='text-align:center;color:orange;'>{estado_counts.get('Garantía',0)}</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Garantía</p>", unsafe_allow_html=True)

btn_col1, btn_col2 = st.columns(2)
with btn_col1:
    if st.button("📥 Exportar a Excel"):
        filtered_df.to_excel("reporte_filtrado.xlsx", index=False)
        st.success("Archivo Excel generado correctamente")
with btn_col2:
    if st.button("📄 Exportar a PDF"):
        export_to_pdf(filtered_df, filename="reporte_filtrado.pdf")
        st.success("PDF generado correctamente")