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
    
    text = ""
    # Lógica para leer PDF
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text()
    
    # Lógica para leer DOCX
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"

    if text:
        st.success("✅ Texto extraído correctamente")
        with st.expander("Ver texto extraído"):
            st.write(text)
    else:
        st.error("No se pudo extraer texto. Revisa si tu archivo es una imagen o está protegido.")