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
st.markdown("<h1 style='text-align: center;'>🎓 EvalIA: Sistema de Evaluación Continua</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Capstone Project | Evaluación automática de respuestas abiertas con <strong>SBERT + Regresión Logística + GenAI</strong>.</p>", unsafe_allow_html=True)

# --- BARRA LATERAL (SIDEBAR) ---
# with st.sidebar:
if 'df_preguntas' in st.session_state and not st.session_state['df_preguntas'].empty:
    df = st.session_state['df_preguntas']
    
    # 2. Obtener la lista de preguntas (asumiendo que la columna se llama 'QUESTION_TEXT')
    # Si tu columna se llama diferente (ej: 'pregunta'), cámbialo aquí.
    print(df.columns)
    print(df.head())
    preguntas_disponibles = df['QUESTION'].tolist()
    
    st.header("Control de Pregunta")

    # 3. Crear el Selectbox con los textos de las preguntas
    pregunta_elegida_texto = st.selectbox(
        "Seleccione una pregunta para evaluar:",
        preguntas_disponibles,
        # Establece la pregunta actualmente cargada como valor por defecto si existe
        index=preguntas_disponibles.index(st.session_state.get('current_question_text', preguntas_disponibles[0]))
        if 'current_question_text' in st.session_state and st.session_state['current_question_text'] in preguntas_disponibles
        else 0
    )

    # 4. Lógica para actualizar el ID de la pregunta seleccionada
    # Usamos el texto seleccionado para encontrar su QUESTION_ID correspondiente en el DataFrame
    if pregunta_elegida_texto:
        # Encuentra el QUESTION_ID asociado al texto elegido
        selected_row = df[df['QUESTION'] == pregunta_elegida_texto].iloc[0]
        selected_qid = selected_row['QUESTION_ID']
        
        # Guardamos el texto también para mantener el selectbox seleccionado
        st.session_state['current_question_text'] = pregunta_elegida_texto
        
        # Solo actualizamos el estado si el ID ha cambiado
        if st.session_state.get('current_qid') != selected_qid:
            st.session_state['current_qid'] = selected_qid
            # Limpiamos resultados anteriores
            if 'last_result' in st.session_state: del st.session_state['last_result']
            st.rerun()
            
else:
    st.error("Error: El DataFrame de preguntas ('df_preguntas') no está cargado o está vacío.")

st.divider()
st.info("Este sistema asiste al profesor filtrando respuestas claras y marcando dudosas.")
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

        
