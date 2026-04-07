import streamlit as st
from docx import Document
import PyPDF2
from google import genai

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ATS Expert Pro", layout="centered", page_icon="🛡️")

# --- CONFIGURACIÓN DE IA ---
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ No se encontró la API Key en los secretos de Streamlit.")
    st.stop()

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
        # --- PDF ---
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    texto_extraido += text

        # --- DOCX ---
        else:
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                texto_extraido += para.text + "\n"

        # --- VALIDACIÓN ---
        if texto_extraido.strip():
            st.success("✅ ¡Éxito! El ATS pudo leer el texto de tu archivo.")

            with st.expander("Haz clic aquí para ver el texto detectado"):
                st.text(texto_extraido)

            # --- PASO 2: IA ---
            st.markdown("---")
            st.subheader("Paso 2: Análisis de Compatibilidad con IA")

            vacante = st.text_area(
                "Pega aquí la descripción del puesto o los requisitos:",
                placeholder="Ejemplo: Se busca Ingeniero de Software con experiencia en Python, SQL y APIs REST...",
                height=200
            )

            if st.button("🚀 Iniciar Análisis de IA"):
                if not vacante.strip():
                    st.warning("Por favor, pega la descripción de la vacante.")
                else:
                    with st.spinner("La IA está evaluando tu perfil..."):
                        try:
                            prompt = f"""
Actúa como un experto en Reclutamiento Técnico y Sistemas ATS.

Analiza el siguiente CV comparándolo con la vacante.

CV:
{texto_extraido}

VACANTE:
{vacante}

Entrega un reporte en formato Markdown con:

1. Porcentaje de compatibilidad (0-100%)
2. Análisis de keywords (cuáles faltan)
3. Fortalezas del candidato
4. Recomendaciones específicas para mejorar el CV
"""

                            response = client.models.generate_content(
                                model="gemini-2.0-flash",
                                contents=prompt
                            )

                            st.markdown("---")
                            st.markdown("### 📊 Resultado del Análisis")
                            st.markdown(response.text)

                        except Exception as e:
                            st.error(f"Error al conectar con la IA: {e}")

        else:
            st.warning("⚠️ El archivo parece vacío o es una imagen escaneada.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")

else:
    st.write("Por favor, sube un archivo para comenzar.")

# --- FOOTER ---
st.markdown("---")
st.caption("ATS Expert Pro - Desarrollado por David Pérez Reyes")