import streamlit as st
from docx import Document
import PyPDF2
import re
import pandas as pd
from collections import Counter
import language_tool_python

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# --- CONFIG ---
st.set_page_config(page_title="ATS Expert Ultimate PRO", layout="centered")
st.title("🧠 ATS Expert Ultimate PRO (Nivel Consultora)")
st.markdown("---")

tool = language_tool_python.LanguageTool('es')

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

# --- ORTOGRAFIA ---
def analizar_ortografia(texto):
    matches = tool.check(texto)
    errores = []
    for m in matches[:15]:
        errores.append(f"❌ {m.message}")
    return errores

# --- LOGROS VS RESPONSABILIDADES ---
def analizar_logros(texto):
    lineas = texto.split("\n")
    logros = 0
    responsabilidades = 0

    for l in lineas:
        if re.search(r'\d+%|\$|\d+', l):
            logros += 1
        elif any(p in l for p in PALABRAS_DEBILES):
            responsabilidades += 1

    return logros, responsabilidades

# --- BULLETS ---
def detectar_bullets(texto):
    return len(re.findall(r'[-•●]', texto))

# --- ANALISIS BASE ATS ---
def analizar(texto, vacante):
    cv_clean = limpiar_texto(texto)
    vac_clean = limpiar_texto(vacante)

    kw_cv = set(cv_clean.split())
    kw_vac = set(vac_clean.split())

    return int((len(kw_cv & kw_vac) / max(len(kw_vac),1)) * 100)

# --- SCORE AVANZADO ---
def score_avanzado(texto, vacante):
    score_kw = analizar(texto, vacante)

    errores = len(analizar_ortografia(texto))
    logros, resp = analizar_logros(texto)

    score = (
        score_kw * 0.4 +
        max(0, 100 - errores*5) * 0.2 +
        min(logros*10, 100) * 0.2 +
        (100 if logros > resp else 50) * 0.2
    )

    return int(score)

# --- AUDITORIA COMPLETA ---
def auditoria_cv(texto, vacante):
    observaciones = []

    palabras = texto.split()
    conteo = Counter(palabras)

    repetidas = [p for p, c in conteo.items() if c > 10 and len(p) > 4]
    if repetidas:
        observaciones.append(f"⚠️ Palabras repetidas: {repetidas[:5]}")

    if any(p in palabras for p in PALABRAS_DEBILES):
        observaciones.append("⚠️ Lenguaje débil detectado")

    if not re.search(r'\d+%|\$', texto):
        observaciones.append("📉 Falta de métricas cuantificables")

    if "  " in texto:
        observaciones.append("✍️ Problemas de formato")

    años = re.findall(r'(20\d{2})', texto)
    if len(años) > 1:
        años_int = sorted([int(a) for a in años])
        gaps = [años_int[i+1] - años_int[i] for i in range(len(años_int)-1)]
        if any(g > 3 for g in gaps):
            observaciones.append("📅 Posibles gaps laborales")

    kw_cv = set(limpiar_texto(texto).split())
    kw_vac = set(limpiar_texto(vacante).split())

    faltantes = kw_vac - kw_cv
    if len(faltantes) > 20:
        observaciones.append("🎯 Baja coincidencia ATS")

    skills_faltantes = [s for s in SKILLS_CLAVE if s in vacante and s not in texto]
    if skills_faltantes:
        observaciones.append(f"🧠 Skills faltantes: {skills_faltantes[:5]}")

    return observaciones

# --- REESCRITURA ---
def reescribir_cv(texto):
    mejoras = []
    for linea in texto.split("\n"):
        if any(p in linea for p in PALABRAS_DEBILES):
            nueva = re.sub(r"responsable de", "Lideré", linea)
            nueva = re.sub(r"apoyo en", "Contribuí a", nueva)
            mejoras.append("💡 " + nueva)
        else:
            mejoras.append(linea)
    return "\n".join(mejoras)

# --- PDF ---
def generar_pdf(nombre, score, observaciones, mejoras):
    doc = SimpleDocTemplate(f"{nombre}_reporte.pdf")
    styles = getSampleStyleSheet()

    contenido = []
    contenido.append(Paragraph(f"Reporte ATS - {nombre}", styles['Title']))
    contenido.append(Spacer(1, 10))
    contenido.append(Paragraph(f"Score: {score}", styles['Heading2']))

    contenido.append(Paragraph("Observaciones:", styles['Heading3']))
    for o in observaciones:
        contenido.append(Paragraph(o, styles['Normal']))

    contenido.append(Spacer(1, 10))
    contenido.append(Paragraph("CV Mejorado:", styles['Heading3']))

    for m in mejoras.split("\n")[:50]:
        contenido.append(Paragraph(m, styles['Normal']))

    doc.build(contenido)

# --- DOCX ---
def generar_docx(nombre, texto_mejorado):
    doc = Document()
    doc.add_heading('CV Optimizado', 0)

    for linea in texto_mejorado.split("\n"):
        doc.add_paragraph(linea)

    doc.save(f"{nombre}_mejorado.docx")

# --- UI PRINCIPAL ---
if uploaded_files:
    vacante = st.text_area("Pega la descripción del puesto")

    if st.button("🚀 Analizar candidatos"):
        resultados = []

        for file in uploaded_files:
            texto = extraer_texto(file)

            if texto.strip():
                score = score_avanzado(texto, vacante)
                obs = auditoria_cv(texto, vacante)
                errores = analizar_ortografia(texto)
                logros, resp = analizar_logros(texto)
                bullets = detectar_bullets(texto)

                texto_mejorado = reescribir_cv(texto)

                generar_pdf(file.name, score, obs + errores, texto_mejorado)
                generar_docx(file.name, texto_mejorado)

                resultados.append({
                    "Archivo": file.name,
                    "Score": score,
                    "Logros": logros,
                    "Responsabilidades": resp,
                    "Bullets": bullets,
                    "Errores": len(errores)
                })

        df = pd.DataFrame(resultados).sort_values(by="Score", ascending=False)

        st.subheader("🏆 Ranking")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📄 Descargar CSV", csv, "reporte_cv.csv")

else:
    st.info("Sube CVs para comenzar")

st.markdown("---")
st.caption("ATS Expert Ultimate PRO - Sistema Inteligente de Optimización de CV")