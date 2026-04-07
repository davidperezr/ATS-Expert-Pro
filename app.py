import streamlit as st
from docx import Document
import PyPDF2
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ATS Expert Pro", layout="centered", page_icon="🛡️")

# --- CONFIGURACIÓN DE IA ---
if "GEMINI_API_KEY" in st.secrets:
    # Configuración directa y limpia
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Usar el nombre del modelo sin prefijos extraños para evitar el 404
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ No se encontró la API Key en los secretos de Streamlit.")

# --- INTERFAZ PRINCIPAL ---
st.title("🛡️ ATS Expert Pro")
st.markdown("---")

# --- PASO 1: CARGA Y VALIDACIÓN ---
st.subheader("Paso 1: Validación de Formato")
uploaded_file = st.file_uploader("Sube tu CV (PDF o DOCX)", type=["pdf", "docx"])

texto_extraido = "" 

if uploaded_file:
    st.info("Analizando estructura...")
    try:
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    texto_extraido += text
        else:
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                texto_extraido += para.text + "\n"

        if texto_extraido.strip():
            st.success("✅ ¡Éxito! El ATS pudo leer el texto de tu archivo.")
            with st.expander("Ver texto detectado"):
                st.text(texto_extraido)
            
            st.markdown("---")
            st.subheader("Paso 2: Análisis de Compatibilidad")
            
            vacante = st.text_area(
                "Pega aquí la descripción de la vacante:",
                placeholder="Ejemplo: Se busca Ingeniero con experiencia en Python...",
                height=200
            )
            
            if st.button("🚀 Iniciar Análisis"):
                if not vacante.strip():
                    st.warning("Por favor, pega los requisitos de la vacante.")
                else:
                    with st.spinner("La IA está evaluando tu perfil..."):
                        try:
                            prompt = f"""
                            Actúa como un experto en Reclutamiento.
                            Compara este CV con la VACANTE proporcionada.
                            CV: {texto_extraido}
                            VACANTE: {vacante}
                            
                            Devuelve un informe en Markdown con:
                            - % de compatibilidad.
                            - Keywords faltantes.
                            - Fortalezas.
                            - 3 consejos para mejorar el CV.
                            """
                            # Generación de contenido
                            response = model.generate_content(prompt)
                            st.markdown("### 📊 Resultado")
                            st.markdown(response.text)
                            
                        except Exception as e:
                            st.error(f"Error de conexión: {e}")
                            st.info("Verifica que tu API Key sea válida en los Secrets.")
        else:
            st.warning("⚠️ No se detectó texto en el archivo.")
    except Exception as e:
        st.error(f"Error al procesar archivo: {e}")
else:
    st.write("Sube un archivo para comenzar.")

st.markdown("---")
st.caption("ATS Expert Pro - Desarrollado por David Pérez Reyes")