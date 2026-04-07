import streamlit as st
from docx import Document
import PyPDF2
import re
import pandas as pd
from collections import Counter

# --- CONFIG ---
st.set_page_config(page_title="ATS Expert Ultimate+", layout="centered")
st.title("🧠 ATS Expert Ultimate+ (Con Auditoría Profesional)")
st.markdown("---")

uploaded_files = st.file_uploader(
    "Sube múltiples CVs",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# --- DATA ---
SKILLS_CLAVE = [
    "python","sql","java","c++","javascript","typescript",
    "excel","power bi","tableau",
    "aws","azure","gcp","docker","kubernetes",
    "git","linux","api","rest",
    "machine learning","data analysis","etl","spark"
]

STOPWORDS = {"el","la","de","y","en","a","los","del","se","las","por","un","para"}

PALABRAS_DEBILES = ["responsable","apoyo","ayuda","encargado","participé"]

# --- FUNCIONES BASE ---
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

def limpiar_texto(texto):
    texto = re.sub(r'[^a-zA-Z0-9\s]', ' ', texto.lower())
    return re.sub(r'\s+', ' ', texto)

# --- AUDITORIA ---
def auditoria_cv(texto, vacante):
    observaciones = []

    palabras = texto.split()
    conteo = Counter(palabras)

    # --- REPETICION ---
    repetidas = [p for p, c in conteo.items() if c > 10 and len(p) > 4]
    if repetidas:
        observaciones.append(f"⚠️ Uso excesivo de palabras: {repetidas[:5]}")

    # --- PALABRAS DEBILES ---
    debiles = [p for p in palabras if p in PALABRAS_DEBILES]
    if debiles:
        observaciones.append("⚠️ Uso de lenguaje poco impactante (ej: responsable, apoyo)")

    # --- FALTA DE METRICAS ---
    if not re.search(r'\d+%', texto) and not re.search(r'\$', texto):
        observaciones.append("📉 No se detectan logros cuantificables (% , $ , números)")

    # --- ERRORES BASICOS ---
    if "  " in texto:
        observaciones.append("✍️ Posibles errores de formato (dobles espacios)")

    # --- FECHAS ---
    años = re.findall(r'(20\d{2})', texto)
    if len(años) > 1:
        años_int = sorted([int(a) for a in años])
        gaps = [años_int[i+1] - años_int[i] for i in range(len(años_int)-1)]
        if any(g > 3 for g in gaps):
            observaciones.append("📅 Posibles gaps laborales mayores a 3 años")

    # --- KEYWORDS ---
    kw_cv = set(limpiar_texto(texto).split())
    kw_vac = set(limpiar_texto(vacante).split())
    faltantes = kw_vac - kw_cv

    if len(faltantes) > 20:
        observaciones.append("🎯 Baja alineación con la vacante (faltan muchas keywords)")

    # --- SKILLS ---
    skills_faltantes = [s for s in SKILLS_CLAVE if s in vacante and s not in texto]
    if skills_faltantes:
        observaciones.append(f"🧠 Faltan skills clave: {skills_faltantes[:5]}")

    return observaciones

# --- ANALISIS PRINCIPAL ---
def analizar(cv, vacante):
    cv_clean = limpiar_texto(cv)
    vac_clean = limpiar_texto(vacante)

    kw_cv = set(cv_clean.split())
    kw_vac = set(vac_clean.split())

    score = int((len(kw_cv & kw_vac) / max(len(kw_vac),1)) * 100)

    return score

# --- UI ---
if uploaded_files:
    vacante = st.text_area("Pega la descripción del puesto")

    if st.button("🚀 Analizar candidatos"):
        resultados = []

        for file in uploaded_files:
            texto = extraer_texto(file)

            if texto.strip():
                score = analizar(texto, vacante)
                obs = auditoria_cv(texto, vacante)

                resultados.append({
                    "Archivo": file.name,
                    "Score": score,
                    "Observaciones": " | ".join(obs)
                })

        df = pd.DataFrame(resultados).sort_values(by="Score", ascending=False)

        st.subheader("🏆 Ranking")
        st.dataframe(df)

        # --- DETALLE ---
        st.markdown("### 🔍 Auditoría por candidato")

        for r in resultados:
            with st.expander(f"{r['Archivo']} ({r['Score']}%)"):
                if r["Observaciones"]:
                    for o in r["Observaciones"].split("|"):
                        st.write(o)
                else:
                    st.write("✅ CV bien optimizado")

        # --- DESCARGA ---
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📄 Descargar reporte", csv, "reporte_cv.csv")

else:
    st.info("Sube CVs para comenzar")

st.markdown("---")
st.caption("ATS Expert Ultimate+ con Auditoría Inteligente")