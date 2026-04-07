import streamlit as st
from docx import Document
import PyPDF2
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ATS Expert Pro", layout="centered", page_icon="🛡️")

# --- CONFIGURACIÓN DE IA ---
if "GEMINI_API_KEY" in st.secrets:
    # 1. Configuramos la API Key sin parámetros extraños
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 2. Usamos el nombre del modelo con el prefijo 'models/' 
    # Esto fuerza a la librería a encontrarlo en cualquier versión de API
    model = genai.GenerativeModel('models/gemini-1.5-flash')
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
            with st.expander("Haz clic aquí para ver el texto detectado"):
                st.text(texto_extraido)
            
            st.markdown("---")
            st.subheader("Paso 2: Análisis de Compatibilidad con IA")
            
            vacante = st.text_area(
                "Pega aquí la descripción del puesto o los requisitos:",
                placeholder="Ejemplo: Se busca Ingeniero de Software...",
                height=200
            )
            
            if st.button("🚀 Iniciar Análisis de IA"):
                if not vacante.strip():
                    st.warning("Por favor, pega la descripción de la vacante.")
                else:
                    with st.spinner("La IA está evaluando tu perfil..."):
                        try:
                            prompt = f"""
                            Actúa como un experto en Reclutamiento Técnico.
                            Analiza el CV contra la VACANTE.
                            CV: {texto_extraido}
                            VACANTE: {vacante}
                            Devuelve: Compatibilidad %, Keywords faltantes, Fortalezas y Recomendaciones.
                            """
                            # Aquí es donde ocurría el error 404
                            response = model.generate_content(prompt)
                            
                            st.markdown("---")
                            st.markdown("### 📊 Resultado del Análisis")
                            st.markdown(response.text)
                            
                        except Exception as e:
                            st.error(f"Error de conexión con Gemini: {e}")
                            st.info("Revisa que tu API Key en Secrets sea válida y no tenga espacios.")
                            
        else:
            st.warning("⚠️ No se pudo extraer texto del archivo.")
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.write("Sube un archivo para comenzar.")

st.markdown("---")
st.caption("ATS Expert Pro - Desarrollado con Streamlit y Google Gemini AI")