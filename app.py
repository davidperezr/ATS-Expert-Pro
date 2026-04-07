import streamlit as st
from docx import Document
import PyPDF2

st.set_page_config(page_title="ATS Expert Pro", layout="centered")

st.title("🛡️ ATS Expert Pro")
st.markdown("---")
st.subheader("Paso 1: Validación de Formato")

uploaded_file = st.file_uploader("Sube tu CV (PDF o DOCX)", type=["pdf", "docx"])

if uploaded_file:
    st.info("Analizando estructura...")
    # Aquí procesaremos el archivo en el siguiente paso