import streamlit as st
from docx import Document
import PyPDF2
import google.generativeai as genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ATS Expert Pro", layout="centered")

# --- CONFIGURACIÓN DE IA ---
# Recuerda tener tu archivo .streamlit/secrets.toml con:
# GEMINI_API_KEY = "AIzaSyDfPDiD7M1rY1tK7p25m488R7doOoHm95s"
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ No se encontró la API Key en los secretos de Streamlit.")

# --- INTERFAZ PRINCIPAL ---
st.title("🛡️ ATS Expert Pro")
st.markdown("---")

# --- PASO 1: CARGA Y VALIDACIÓN ---
st.subheader("Paso 1: Validación de Formato")
uploaded_file = st.file_uploader("Sube tu CV (PDF o DOCX)", type=["pdf", "docx"])

texto_extraido = "" # Inicializamos la variable

if uploaded_file:
    st.info("Analizando estructura...")
    
    try:
        # Lógica para leer PDF
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                texto_extraido += page.extract_text()
        
        # Lógica para leer DOCX (Word)
        else:
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                texto_extraido += para.text + "\n"

        if texto_extraido.strip():
            st.success("✅ ¡Éxito! El ATS pudo leer el texto de tu archivo.")
            with st.expander("Haz clic aquí para ver el texto detectado"):
                st.text(texto_extraido)
            
            # --- PASO 2: INTEGRACIÓN DE IA ---
            st.markdown("---")
            st.subheader("Paso 2: Análisis de Compatibilidad con IA")
            
            vacante = st.text_area(
                "Pega aquí la descripción del puesto o los requisitos:",
                placeholder="Ejemplo: Se busca Ingeniero de Software con experiencia en Python, SQL y APIs REST...",
                height=200
            )
            
            if st.button("🚀 Iniciar Análisis de IA"):
                if not vacante.strip():
                    st.warning("Por favor, pega la descripción de la vacante para poder comparar.")
                else:
                    with st.spinner("La IA está evaluando tu perfil contra la vacante..."):
                        try:
                            # El Prompt Maestro para el ATS
                            prompt = f"""
                            Actúa como un experto en Reclutamiento Técnico y Sistemas ATS.
                            Analiza el siguiente CV basándote en la descripción de la vacante.
                            
                            DOCUMENTO CV:
                            {texto_extraido}
                            
                            DESCRIPCIÓN DE LA VACANTE:
                            {vacante}
                            
                            Proporciona un informe estructurado con:
                            1. Porcentaje de compatibilidad (0-100%).
                            2. Análisis de Keywords (¿Cuáles faltan?).
                            3. Fortalezas detectadas.
                            4. Recomendaciones críticas para mejorar el CV para esta posición.
                            """
                            
                            response = model.generate_content(prompt)
                            
                            st.markdown("### 📊 Resultado del Análisis")
                            st.markdown(response.text)
                            
                        except Exception as e:
                            st.error(f"Error al conectar con la IA: {e}")
                            
        else:
            st.warning("⚠️ El archivo se subió, pero parece estar vacío o ser una imagen escaneada.")
            
    except Exception as e:
        st.error(f"Hubo un error al procesar el archivo: {e}")

else:
    st.write("Por favor, sube un archivo para comenzar.")