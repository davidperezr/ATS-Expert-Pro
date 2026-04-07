import streamlit as st
from docx import Document
import PyPDF2
import re
import pandas as pd

# --- CONFIG ---
st.set_page_config(page_title="ATS Expert Ultimate", layout="centered")
st.title("🧠 ATS Expert Ultimate (Nivel Reclutador Senior)")
st.markdown("---")

uploaded_files = st.file_uploader(
    "Sube múltiples CVs",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# --- DATA BASE ---
SKILLS_CLAVE = [
    "python","sql","java","c++","javascript","typescript",
    "excel","power bi","tableau",
    "aws","azure","gcp","docker","kubernetes",
    "git","linux","api","rest",
    "machine learning","data analysis","etl","spark"
]

IDIOMAS = ["english","spanish","french","german"]

EDUCACION = ["licenciatura","ingenieria","maestria","doctorado","bachelor","master"]

STOPWORDS = {
    "el","la","de","y","en","a","los","del","se","las","por","un","para","con",
    "una","su","al","lo","como","más","pero","sus","le","ya","o","este","sí"
}

# --- FUNCIONES ---
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

def obtener_keywords(texto):
    palabras = texto.split()
    return set([p for p in palabras if len(p) > 3 and p not in STOPWORDS])

def detectar_skills(texto):
    return set([s for s in SKILLS_CLAVE if s in texto])

def detectar_idiomas(texto):
    return [i for i in IDIOMAS if i in texto]

def detectar_educacion(texto):
    return [e for e in EDUCACION if e in texto]

def extraer_nombre(texto):
    lineas = texto.split("\n")
    if lineas:
        return lineas[0][:40]
    return "No detectado"

def estimar_experiencia(texto):
    matches = re.findall(r'(\d+)\s*(años|years)', texto)
    if matches:
        return max([int(m[0]) for m in matches])
    return 0

# --- ANALISIS ---
def analizar(cv, vacante):
    cv_clean = limpiar_texto(cv)
    vac_clean = limpiar_texto(vacante)

    kw_cv = obtener_keywords(cv_clean)
    kw_vac = obtener_keywords(vac_clean)

    skills_cv = detectar_skills(cv_clean)
    skills_vac = detectar_skills(vac_clean)

    idiomas = detectar_idiomas(cv_clean)
    educacion = detectar_educacion(cv_clean)
    experiencia = estimar_experiencia(cv_clean)

    # --- SCORES ---
    kw_score = len(kw_cv & kw_vac) / max(len(kw_vac),1)
    skills_score = len(skills_cv & skills_vac) / max(len(skills_vac),1)
    densidad = len(kw_cv & kw_vac) / max(len(kw_cv),1)

    # BONUS experiencia
    bonus_exp = min(experiencia / 10, 1)

    # PENALIZACION skills críticas
    faltantes = skills_vac - skills_cv
    penalizacion = len(faltantes) * 0.05

    score = (kw_score*0.4 + skills_score*0.3 + densidad*0.1 + bonus_exp*0.2) - penalizacion
    score = max(0, min(int(score * 100), 100))

    explicacion = f"""
    KW:{int(kw_score*100)}% | Skills:{int(skills_score*100)}% | Exp:{experiencia} años
    Penalización:{len(faltantes)} skills faltantes
    """

    return {
        "score": score,
        "skills_ok": skills_cv & skills_vac,
        "skills_missing": faltantes,
        "idiomas": idiomas,
        "educacion": educacion,
        "experiencia": experiencia,
        "explicacion": explicacion
    }

# --- UI ---
if uploaded_files:
    vacante = st.text_area("Pega la descripción del puesto")

    if st.button("🚀 Analizar candidatos"):
        if not vacante.strip():
            st.warning("Agrega la vacante")
        else:
            resultados = []

            for file in uploaded_files:
                texto = extraer_texto(file)

                if texto.strip():
                    nombre = extraer_nombre(texto)
                    analisis = analizar(texto, vacante)

                    resultados.append({
                        "Archivo": file.name,
                        "Nombre": nombre,
                        "Score": analisis["score"],
                        "Experiencia (años)": analisis["experiencia"],
                        "Educación": ", ".join(analisis["educacion"]),
                        "Idiomas": ", ".join(analisis["idiomas"]),
                        "Skills Match": ", ".join(analisis["skills_ok"]),
                        "Skills Faltantes": ", ".join(analisis["skills_missing"]),
                        "Explicación": analisis["explicacion"]
                    })

            df = pd.DataFrame(resultados).sort_values(by="Score", ascending=False)

            st.markdown("---")
            st.subheader("🏆 Ranking Inteligente")
            st.dataframe(df, use_container_width=True)

            # --- TOP ---
            st.markdown("### 🥇 Mejores candidatos")
            for i, row in df.head(3).iterrows():
                st.success(f"{row['Nombre']} — {row['Score']}% ({row['Experiencia (años)']} años)")

            # --- DESCARGA ---
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📄 Descargar CSV", csv, "ranking.csv")

else:
    st.info("Sube CVs para comenzar")

st.markdown("---")
st.caption("ATS Expert Ultimate - Nivel Reclutador Senior")