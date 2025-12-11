import streamlit as st
import pandas as pd
import logica #Archivo con la lógica de EvalIA
import ast

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="EvalIA - App", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stTextArea textarea { font-size: 16px; }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAR ESTADO ---
# Necesario para recordar la pregunta actual aunque recargues
if 'current_qid' not in st.session_state:
    st.session_state['current_qid'] = None
if 'df_preguntas' not in st.session_state:
    st.session_state['df_preguntas'] = logica.cargar_dataset()

# --- HEADER ---
st.title("🎓 EvalIA: Sistema de Evaluación Continua")
st.markdown("Capstone Project | Evaluación automática de respuestas abiertas con **SBERT + Regresión Logística + GenAI**.")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("Control")
    if st.button("🔄 Cargar Nueva Pregunta"):
        if not st.session_state['df_preguntas'].empty:
            sample = st.session_state['df_preguntas'].sample(1).iloc[0]
            st.session_state['current_qid'] = sample['QUESTION_ID']
            # Limpiamos resultados anteriores
            if 'last_result' in st.session_state: del st.session_state['last_result']
            st.rerun()
        else:
            st.error("Error: Dataset no cargado.")
    
    st.divider()
    st.info("Este sistema asiste al profesor filtrando respuestas claras y marcando dudosas.")

# --- CUERPO PRINCIPAL ---

# 1. Mostrar Pregunta
if st.session_state['current_qid']:
    # Buscar datos de la pregunta actual
    df = st.session_state['df_preguntas']
    fila = df[df['QUESTION_ID'] == st.session_state['current_qid']].iloc[0]
    
    st.subheader(f"Pregunta {fila['QUESTION_ID']}")
    st.markdown(f"### {fila['QUESTION']}")
    
    # 2. Formulario de Respuesta
    with st.form("eval_form"):
        respuesta_usuario = st.text_area("Tu respuesta:", height=150, placeholder="Escribe aquí tu explicación técnica...")
        submitted = st.form_submit_button("📊 Evaluar Respuesta")
        
    if submitted:
        if not respuesta_usuario.strip():
            st.warning("Por favor, escribe algo antes de evaluar.")
        else:
            with st.spinner("Analizando semántica y generando feedback..."):
                # --- LLAMADA A LA LÓGICA ---
                
                # A) Cálculos Semánticos
                resultado_metricas = logica.get_semantic_similarity(
                    model_correct=fila["ANSWER_CORRECT"],
                    model_wrong=fila["WRONG_EXAMPLES"],
                    student_answer=respuesta_usuario,
                    keywords=logica.parse_list(fila.get("KEYWORDS", []))
                )
                
                # B) Clasificación (Regresión Logística)
                score = logica.scorer_logreg_kw(resultado_metricas)
                interpretacion = logica.interpretar_3clases(score)
                
                # C) Feedback Generativo (Gemini)
                feedback_ia, modelo = logica.generar_feedback_genai(
                    pregunta=fila["QUESTION"],
                    student_answer=respuesta_usuario,
                    interpretacion=interpretacion,
                    referencia=fila["ANSWER_CORRECT"],
                    hint=fila["HINT"]
                )
                
                # Guardamos resultados en sesión para que no desaparezcan
                st.session_state['last_result'] = {
                    "interpretacion": interpretacion,
                    "feedback": feedback_ia,
                    "score": score,
                    "metrics": resultado_metricas,
                    "referencia": fila["ANSWER_CORRECT"],
                    "hint": fila["HINT"]
                }
                st.rerun()

# 3. Mostrar Resultados
if 'last_result' in st.session_state:
    res = st.session_state['last_result']
    
    st.divider()
    
    # Encabezado de resultado con color
    if res['interpretacion'] == 'Correcta':
        st.success(f"✅ Resultado: **CORRECTA** (Confianza: {res['score']:.2f})")
    elif res['interpretacion'] == 'Incorrecta':
        st.error(f"❌ Resultado: **INCORRECTA** (Confianza: {res['score']:.2f})")
    else:
        st.warning(f"🤔 Resultado: **REVISIÓN NECESARIA** (Confianza: {res['score']:.2f})")
    
    # Columnas para Feedback y Métricas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🤖 Feedback IA")
        st.info(res['feedback'])
        
        with st.expander("Ver respuesta de referencia (Profesor)"):
            try:
                refs = ast.literal_eval(res['referencia']) if isinstance(res['referencia'], str) else res['referencia']
                st.write(refs[0] if isinstance(refs, list) and len(refs)>0 else str(refs))
            except:
                st.write(res['referencia'])
                
    with col2:
        st.markdown("### 📈 Métricas Técnicas")
        st.metric("Similitud con respuestas CORRECTAS", f"{res['metrics']['max_correct']:.2f}")
        st.metric("Similitud con respuestas INCORRECTAS", f"{res['metrics']['max_wrong']:.2f}")
        st.metric("Uso de Keywords (F1)", f"{res['metrics']['kw_f1']:.2f}")

else:
    if not st.session_state['current_qid']:
        st.info("👈 Pulsa 'Cargar Nueva Pregunta' en la barra lateral para comenzar.")

        
