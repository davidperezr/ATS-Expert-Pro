import streamlit as st
from docx import Document
import PyPDF2
import re

# --- CONFIG ---
st.set_page_config(page_title="ATS Expert Pro", layout="centered")

st.title("🛡️ ATS Expert Pro (Nivel Profesional - Sin IA)")
st.markdown("---")

uploaded_file = st.file_uploader("Sube tu CV (PDF o DOCX)", type=["pdf", "docx"])

# --- SKILLS AVANZADAS ---
SKILLS_CLAVE = [
    "python","sql","java","c++","javascript","typescript",
    "excel","power bi","tableau",
    "aws","azure","gcp","docker","kubernetes",
    "git","linux","api","rest",
    "machine learning","data analysis","etl","spark"
]

STOPWORDS = {
    "el","la","de","y","en","a","los","del","se","las","por","un","para","con",
    "una","su","al","lo","como","más","pero","sus","le","ya","o","este","sí"
}

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

def obtener_keywords(texto):
    palabras = texto.split()
    return set([p for p in palabras if len(p) > 3 and p not in STOPWORDS])

def detectar_skills(texto):
    return set([s for s in SKILLS_CLAVE if s in texto])

# --- ANALISIS AVANZADO ---
def analizar_avanzado(cv, vacante):
    cv = limpiar_texto(cv)
    vacante = limpiar_texto(vacante)

    kw_cv = obtener_keywords(cv)
    kw_vac = obtener_keywords(vacante)

    skills_cv = detectar_skills(cv)
    skills_vac = detectar_skills(vacante)

    # --- METRICAS ---
    kw_match = len(kw_cv & kw_vac)
    kw_total = len(kw_vac)

    skills_match = len(skills_cv & skills_vac)
    skills_total = len(skills_vac)

    densidad = kw_match / max(len(kw_cv), 1)

    # --- SCORES ---
    score_kw = (kw_match / kw_total) if kw_total else 0
    score_skills = (skills_match / skills_total) if skills_total else 0
    score_densidad = densidad

    score_final = int((score_kw*0.5 + score_skills*0.3 + score_densidad*0.2)*100)

    return {
        "score": score_final,
        "score_kw": int(score_kw*100),
        "score_skills": int(score_skills*100),
        "score_densidad": int(score_densidad*100),
        "kw_ok": kw_cv & kw_vac,
        "kw_missing": kw_vac - kw_cv,
        "skills_ok": skills_cv & skills_vac,
        "skills_missing": skills_vac - skills_cv
    }

# --- CLASIFICACION ---
def clasificar(score):
    if score >= 75:
        return "🟢 Alto"
    elif score >= 50:
        return "🟡 Medio"
    else:
        return "🔴 Bajo"

# --- UI ---
if uploaded_file:
    texto_cv = extraer_texto(uploaded_file)

    if texto_cv.strip():
        st.success("✅ CV procesado correctamente")

        with st.expander("Vista previa CV"):
            st.text(texto_cv[:2000])

        vacante = st.text_area("Pega la descripción del puesto")

        if st.button("🚀 Analizar CV"):
            if not vacante.strip():
                st.warning("Agrega la vacante")
            else:
                resultado = analizar_avanzado(texto_cv, vacante)

                st.markdown("---")
                st.subheader("📊 Score Global")
                st.metric("Compatibilidad", f"{resultado['score']}%")
                st.write("Nivel:", clasificar(resultado["score"]))

                # --- BARRAS ---
                st.markdown("### 📈 Desglose del Score")
                st.progress(resultado["score_kw"]/100)
                st.write(f"Keywords: {resultado['score_kw']}%")

                st.progress(resultado["score_skills"]/100)
                st.write(f"Skills: {resultado['score_skills']}%")

                st.progress(resultado["score_densidad"]/100)
                st.write(f"Densidad: {resultado['score_densidad']}%")

                # --- SKILLS ---
                st.markdown("### 🧠 Skills detectadas")
                st.write(list(resultado["skills_ok"]))

                st.markdown("### ❌ Skills faltantes")
                st.write(list(resultado["skills_missing"]))

                # --- KEYWORDS ---
                st.markdown("### ✅ Keywords relevantes")
                st.write(list(resultado["kw_ok"])[:20])

                st.markdown("### ❌ Keywords faltantes")
                st.write(list(resultado["kw_missing"])[:20])

                # --- RESUMEN ---
                st.markdown("### 🧾 Resumen Ejecutivo")

                if resultado["score"] < 50:
                    st.error("Perfil con baja alineación. Requiere ajustes importantes.")
                elif resultado["score"] < 75:
                    st.warning("Buen perfil, pero puede optimizarse.")
                else:
                    st.success("Perfil altamente alineado con la vacante.")

                # --- RECOMENDACIONES ---
                st.markdown("### 💡 Recomendaciones")

                if resultado["skills_missing"]:
                    st.write("👉 Agrega estas skills:", list(resultado["skills_missing"])[:10])

                if resultado["kw_missing"]:
                    st.write("👉 Incorpora keywords clave en tu CV.")

    else:
        st.warning("No se pudo leer el archivo")

else:
    st.info("Sube tu CV para comenzar")

st.markdown("---")
st.caption("ATS Expert Pro - Nivel Profesional sin IA")