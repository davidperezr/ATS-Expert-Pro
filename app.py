import streamlit as st
from docx import Document
import PyPDF2
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="ATS Expert Pro", layout="centered", page_icon="🛡️")

# --- VALIDAR API KEY ---
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("⚠️ No se encontró la API Key de OpenRouter en secrets.toml")
    st.stop()

# --- FUNCIÓN IA ---
def analizar_con_ia(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openchat/openchat-7b:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()["choices"][0]["message"]["content"]


# --- INTERFAZ ---
st.title("🛡️ ATS Expert Pro")
st.markdown("---")

# --- SUBIDA DE ARCHIVO ---
st.subheader("Paso 1: Validación de Formato")
uploaded_file = st.file_uploader("Sube tu CV (PDF o DOCX)", type=["pdf", "docx"])

texto_extraido = ""

def recortar_texto(texto, max_chars=6000):
    return texto[:max_chars]

if uploaded_file:
    st.info("Analizando estructura...")

    try:
        # PDF
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    texto_extraido += text

        # DOCX
        else:
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                texto_extraido += para.text + "\n"

        if texto_extraido.strip():
            st.success("✅ ¡Éxito! El ATS pudo leer el texto de tu archivo.")

            with st.expander("Ver texto detectado"):
                st.text(texto_extraido)

            # --- IA ---
            st.markdown("---")
            st.subheader("Paso 2: Análisis con IA")

            vacante = st.text_area(
                "Pega la descripción del puesto:",
                height=200
            )

            if st.button("🚀 Analizar CV"):
                if not vacante.strip():
                    st.warning("Agrega la descripción de la vacante.")
                else:
                    with st.spinner("Analizando con IA..."):
                        try:
                            # Reducir tamaño para evitar errores
                            cv_corto = recortar_texto(texto_extraido)
                            vacante_corta = recortar_texto(vacante)

                            prompt = f"""
Actúa como experto en reclutamiento ATS.

Analiza este CV contra la vacante.

CV:
{cv_corto}

VACANTE:
{vacante_corta}

Entrega:

1. Porcentaje de compatibilidad (0-100%)
2. Keywords faltantes
3. Fortalezas
4. Recomendaciones específicas
"""

                            resultado = analizar_con_ia(prompt)

                            st.markdown("---")
                            st.markdown("### 📊 Resultado")
                            st.markdown(resultado)

                        except Exception as e:
                            st.error(f"Error con IA: {e}")

        else:
            st.warning("⚠️ El archivo parece vacío o escaneado.")

    except Exception as e:
        st.error(f"Error procesando archivo: {e}")

else:
    st.write("Sube un CV para comenzar.")

# --- FOOTER ---
st.markdown("---")
st.caption("ATS Expert Pro - David Pérez Reyes")