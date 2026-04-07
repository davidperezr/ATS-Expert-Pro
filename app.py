import streamlit as st
from docx import Document
import PyPDF2
import re

# --- CONFIG ---
st.set_page_config(page_title="ATS Expert Pro", layout="centered")

# --- UI ---
st.title("🛡️ ATS Expert Pro (Modo Gratis)")
st.markdown("---")

uploaded_file = st.file_uploader("Sube tu CV (PDF o DOCX)", type=["pdf", "docx"])

texto_extraido = ""

# --- EXTRAER TEXTO ---
def extraer_texto(file):
    texto = ""

    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            texto += page.extract_text() or ""
    else:
        doc = Document(file)
        for p in doc.paragraphs:
            texto += p.text + "\n"

    return texto.lower()

# --- LIMPIAR TEXTO ---
def limpiar_texto(texto):
    return re.sub(r'[^a-zA-Z0-9\s]', '', texto)

# --- EXTRAER KEYWORDS ---
def obtener_keywords(texto):
    palabras = texto.split()
    palabras_unicas = list(set(palabras))
    return palabras_unicas

# --- ANALISIS ATS ---
def analizar(cv, vacante):
    cv = limpiar_texto(cv)
    vacante = limpiar_texto(vacante)

    kw_cv = set(obtener_keywords(cv))
    kw_vac = set(obtener_keywords(vacante))

    coincidencias = kw_cv.intersection(kw_vac)
    faltantes = kw_vac - kw_cv

    if len(kw_vac) == 0:
        score = 0
    else:
        score = int((len(coincidencias) / len(kw_vac)) * 100)

    return score, coincidencias, faltantes

# --- MAIN ---
if uploaded_file:
    texto_extraido = extraer_texto(uploaded_file)

    if texto_extraido.strip():
        st.success("✅ Texto extraído correctamente")

        with st.expander("Ver CV detectado"):
            st.text(texto_extraido[:2000])

        vacante = st.text_area("Pega la descripción del puesto")

        if st.button("🚀 Analizar CV"):
            if not vacante.strip():
                st.warning("Agrega la vacante")
            else:
                score, ok, faltantes = analizar(texto_extraido, vacante)

                st.markdown("---")
                st.subheader("📊 Resultado ATS")

                st.metric("Compatibilidad", f"{score}%")

                st.markdown("### ✅ Coincidencias")
                st.write(list(ok)[:20])

                st.markdown("### ❌ Keywords faltantes")
                st.write(list(faltantes)[:20])

                st.markdown("### 💡 Recomendaciones")
                st.write("Incluye más palabras clave relevantes de la vacante en tu CV.")

    else:
        st.warning("No se pudo leer el archivo")

else:
    st.info("Sube tu CV para comenzar")

st.markdown("---")
st.caption("Versión gratuita sin IA - ATS Expert Pro")