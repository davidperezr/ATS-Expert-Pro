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
    
    texto_extraido = ""
    
    try:
        # Lógica para leer PDF
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                texto_extraido += page.extract_text()
        
        # Lógica para leer DOCX
        else:
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                texto_extraido += para.text + "\n"

        if texto_extraido.strip():
            st.success("✅ ¡Éxito! El ATS pudo leer el texto de tu archivo.")
            with st.expander("Haz clic aquí para ver el texto detectado"):
                st.text(texto_extraido)
        else:
            st.warning("⚠️ El archivo se subió, pero parece estar vacío o ser una imagen (scaneado).")
            
    except Exception as e:
        st.error(f"Hubo un error al procesar el archivo: {e}")