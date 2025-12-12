import streamlit as st
import pandas as pd
import logica #Archivo con la lógica de EvalIA
import ast
from datetime import datetime

# Import database functions
import database as db

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="EvalIA - App", layout="wide")

col1, col2, col3 = st.columns([1, 1, 0.5])

with col2:
    st.image("ev3.png", width=200)

# --- CSS ---
st.markdown("""
<style>
    .stTextArea textarea { font-size: 16px; }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# Note: All database functions are now in database.py
# This keeps the code clean and modular

# --- FUNCIONES DE AUTENTICACIÓN ---
def register_page():
    """Página de registro para nuevos estudiantes"""
    st.markdown("<h1 style='text-align: center;'>📝 Registro de Nuevo Estudiante</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Crear Cuenta")
        
        new_username = st.text_input("Usuario (único)", placeholder="ej: student4")
        new_name = st.text_input("Nombre Completo", placeholder="ej: Ana Martínez")
        new_password = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
        confirm_password = st.text_input("Confirmar Contraseña", type="password")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Registrarse", use_container_width=True):
                if not new_username or not new_name or not new_password:
                    st.error("Todos los campos son obligatorios")
                elif len(new_password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                elif new_password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                else:
                    success, message = db.register_user(new_username, new_password, new_name)
                    if success:
                        st.success(f"✅ {message}. Ahora puedes iniciar sesión")
                        st.balloons()
                        if st.button("Ir al Login"):
                            st.session_state['show_register'] = False
                            st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        with col_btn2:
            if st.button("Volver al Login", use_container_width=True):
                st.session_state['show_register'] = False
                st.rerun()

def login_page():
    st.markdown("<h1 style='text-align: center;'>🎓 Sistema de Evaluación Continua</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Inicia sesión para continuar</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("🔐 Login")
        
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("Iniciar Sesión", use_container_width=True):
                user = db.authenticate_user(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user['username']
                    st.session_state['role'] = user['role']
                    st.session_state['name'] = user['name']
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        
        with col_btn2:
            if st.button("Registrarse", use_container_width=True):
                st.session_state['show_register'] = True
                st.rerun()
        
        with col_btn3:
            if st.button("Limpiar", use_container_width=True):
                st.rerun()
        
        st.divider()
        st.info("**Usuarios de prueba:**\n\n**Docente:** teacher / teacher123\n\n**Estudiantes:**\n- student1 / student123 (Juan)\n- student2 / student456 (María)\n- student3 / student789 (Carlos)\n\n**¿Eres nuevo?** Haz clic en 'Registrarse'")

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- INICIALIZAR ESTADO ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'show_register' not in st.session_state:
    st.session_state['show_register'] = False

if not st.session_state['logged_in']:
    if st.session_state['show_register']:
        register_page()
    else:
        login_page()
    st.stop()

# Usuario autenticado - inicializar resto de estados
if 'current_qid' not in st.session_state:
    st.session_state['current_qid'] = None
if 'df_preguntas' not in st.session_state:
    st.session_state['df_preguntas'] = logica.cargar_dataset()

# --- HEADER ---
col_header1, col_header2 = st.columns([4, 1])

with col_header1:
    st.markdown("<h1 style='text-align: center;'>🎓 EvalIA: Sistema de Evaluación Continua</h1>", unsafe_allow_html=True)
    role_emoji = "👨‍🏫" if st.session_state['role'] == "teacher" else "👨‍🎓"
    st.markdown(f"<p style='text-align: center;'>{role_emoji} Bienvenido, <strong>{st.session_state['name']}</strong> | Capstone Project - Evaluación automática de respuestas.</p>", unsafe_allow_html=True)

with col_header2:
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        logout()

st.divider()

# --- PERFILES DIFERENCIADOS ---
if st.session_state['role'] == "teacher":
    # ========== PERFIL DOCENTE ==========
    st.markdown("## 👨‍🏫 Centro de Inteligencia Pedagógica")
    
    tab1, tab2, tab3 = st.tabs(["📝 Evaluar Preguntas", "📊 Estadísticas", "⚙️ Gestión"])
    
    
    with tab1:
        # Sección de selección de preguntas
        if 'df_preguntas' in st.session_state and not st.session_state['df_preguntas'].empty:
            df = st.session_state['df_preguntas']
            preguntas_disponibles = df['QUESTION'].tolist()
            
            st.subheader("Elije r")

            pregunta_elegida_texto = st.selectbox(
                "Seleccione una pregunta para evaluar:",
                preguntas_disponibles,
                index=preguntas_disponibles.index(st.session_state.get('current_question_text', preguntas_disponibles[0]))
                if 'current_question_text' in st.session_state and st.session_state['current_question_text'] in preguntas_disponibles
                else 0
            )

            if pregunta_elegida_texto:
                selected_row = df[df['QUESTION'] == pregunta_elegida_texto].iloc[0]
                selected_qid = selected_row['QUESTION_ID']
                
                st.session_state['current_question_text'] = pregunta_elegida_texto
                
                if st.session_state.get('current_qid') != selected_qid:
                    st.session_state['current_qid'] = selected_qid
                    if 'last_result' in st.session_state: del st.session_state['last_result']
                    st.rerun()
                    
        else:
            st.error("Error: El DataFrame de preguntas ('df_preguntas') no está cargado o está vacío.")

        st.divider()
        st.info("🎯 Como docente, puedes probar el sistema evaluando respuestas y viendo métricas detalladas.")

        # CUERPO PRINCIPAL - Docente
        if st.session_state['current_qid']:
            df = st.session_state['df_preguntas']
            fila = df[df['QUESTION_ID'] == st.session_state['current_qid']].iloc[0]
            
            st.subheader(f"Pregunta {fila['QUESTION_ID']}")
            st.markdown(f"### {fila['QUESTION']}")
            
            with st.form("eval_form_teacher"):
                respuesta_usuario = st.text_area("Prueba una respuesta:", height=150, placeholder="Escribe aquí para probar el sistema...")
                submitted = st.form_submit_button("📊 Evaluar Respuesta")
                
            if submitted:
                if not respuesta_usuario.strip():
                    st.warning("Por favor, escribe algo antes de evaluar.")
                else:
                    with st.spinner("Analizando semántica y generando feedback..."):
                        resultado_metricas = logica.get_semantic_similarity(
                            model_correct=fila["ANSWER_CORRECT"],
                            model_wrong=fila["WRONG_EXAMPLES"],
                            student_answer=respuesta_usuario,
                            keywords=logica.parse_list(fila.get("KEYWORDS", []))
                        )
                        
                        score = logica.scorer_logreg_kw(resultado_metricas)
                        interpretacion = logica.interpretar_3clases(score)
                        
                        feedback_ia, modelo = logica.generar_feedback_genai(
                            pregunta=fila["QUESTION"],
                            student_answer=respuesta_usuario,
                            interpretacion=interpretacion,
                            referencia=fila["ANSWER_CORRECT"],
                            hint=fila["HINT"]
                        )
                        
                        st.session_state['last_result'] = {
                            "interpretacion": interpretacion,
                            "feedback": feedback_ia,
                            "score": score,
                            "metrics": resultado_metricas,
                            "referencia": fila["ANSWER_CORRECT"],
                            "hint": fila["HINT"]
                        }
                        st.rerun()

        if 'last_result' in st.session_state:
            res = st.session_state['last_result']
            
            st.divider()
            
            if res['interpretacion'] == 'Correcta':
                st.success(f"✅ Resultado: **CORRECTA** (Confianza: {res['score']:.2f})")
            elif res['interpretacion'] == 'Incorrecta':
                st.error(f"❌ Resultado: **INCORRECTA** (Confianza: {res['score']:.2f})")
            else:
                st.warning(f"🤔 Resultado: **REVISIÓN NECESARIA** (Confianza: {res['score']:.2f})")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 🤖 Guía Personalizada de Aprendizaje")
                st.info(res['feedback'])
                
                with st.expander("Ver respuesta de referencia (Docente)"):
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
    
    with tab2:
        st.subheader("📊 Estadísticas de Estudiantes")
        
        all_submissions = db.get_all_submissions()
        
        if all_submissions:
            st.metric("Total de respuestas evaluadas", len(all_submissions))
            
            # Crear DataFrame con todas las respuestas
            df_submissions = pd.DataFrame(all_submissions)
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                estudiantes = list(set([s['student_name'] for s in all_submissions]))
                filtro_estudiante = st.selectbox("Filtrar por estudiante:", ["Todos"] + estudiantes)
            
            with col2:
                filtro_resultado = st.selectbox("Filtrar por resultado:", ["Todos", "Correcta", "Incorrecta", "Revisar"])
            
            # Aplicar filtros
            df_filtered = df_submissions.copy()
            if filtro_estudiante != "Todos":
                df_filtered = df_filtered[df_filtered['student_name'] == filtro_estudiante]
            if filtro_resultado != "Todos":
                df_filtered = df_filtered[df_filtered['resultado'] == filtro_resultado]
            
            # Mostrar tabla
            st.dataframe(
                df_filtered[['timestamp', 'student_name', 'pregunta', 'respuesta', 'resultado', 'score']],
                use_container_width=True,
                column_config={
                    "timestamp": "Fecha",
                    "student_name": "Estudiante",
                    "pregunta": "Pregunta",
                    "respuesta": "Respuesta",
                    "resultado": "Resultado",
                    "score": st.column_config.NumberColumn("Puntaje", format="%.2f")
                }
            )
            
            # Estadísticas generales
            st.divider()
            st.subheader("Resumen por Estudiante")
            
            for estudiante in estudiantes:
                student_data = [s for s in all_submissions if s['student_name'] == estudiante]
                total = len(student_data)
                correctas = len([s for s in student_data if s['resultado'] == 'Correcta'])
                incorrectas = len([s for s in student_data if s['resultado'] == 'Incorrecta'])
                revisar = len([s for s in student_data if s['resultado'] == 'Revisar'])
                
                with st.expander(f"📚 {estudiante} - {total} respuestas"):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total", total)
                    col2.metric("Correctas", correctas, delta=f"{(correctas/total*100):.0f}%")
                    col3.metric("Incorrectas", incorrectas)
                    col4.metric("Revisar", revisar)
        else:
            st.info("No hay respuestas de estudiantes aún.")
    
    with tab3:
        st.subheader("⚙️ Gestión de Preguntas")
        if 'df_preguntas' in st.session_state and not st.session_state['df_preguntas'].empty:
            st.dataframe(st.session_state['df_preguntas'])
            st.download_button(
                label="📥 Descargar Dataset",
                data=st.session_state['df_preguntas'].to_csv(index=False).encode('utf-8'),
                file_name='preguntas.csv',
                mime='text/csv',
            )
        else:
            st.warning("No hay preguntas cargadas.")

else:
    # ========== PERFIL ESTUDIANTE ==========
    st.markdown("## 👨‍🎓 Panel del Estudiante")
    
    tab1, tab2 = st.tabs(["📝 Responder Preguntas", "📊 Mi Historial"])
    
    with tab1:
        st.info("💡 Responde las preguntas para recibir feedback automático de la IA.")
        
        if 'df_preguntas' in st.session_state and not st.session_state['df_preguntas'].empty:
            df = st.session_state['df_preguntas']
            preguntas_disponibles = df['QUESTION'].tolist()
            
            pregunta_elegida_texto = st.selectbox(
                "Selecciona una pregunta:",
                preguntas_disponibles,
                index=preguntas_disponibles.index(st.session_state.get('current_question_text', preguntas_disponibles[0]))
                if 'current_question_text' in st.session_state and st.session_state['current_question_text'] in preguntas_disponibles
                else 0
            )

            if pregunta_elegida_texto:
                selected_row = df[df['QUESTION'] == pregunta_elegida_texto].iloc[0]
                selected_qid = selected_row['QUESTION_ID']
                
                st.session_state['current_question_text'] = pregunta_elegida_texto
                
                if st.session_state.get('current_qid') != selected_qid:
                    st.session_state['current_qid'] = selected_qid
                    if 'last_result' in st.session_state: del st.session_state['last_result']
                    st.rerun()
        
        st.divider()
        
        if st.session_state['current_qid']:
            df = st.session_state['df_preguntas']
            fila = df[df['QUESTION_ID'] == st.session_state['current_qid']].iloc[0]
            
            st.subheader(f"Pregunta {fila['QUESTION_ID']}")
            st.markdown(f"### {fila['QUESTION']}")
            
            with st.form("eval_form_student"):
                respuesta_usuario = st.text_area("Validación del pensamiento crítico:", height=150, placeholder="Escribe aquí tu explicación...")
                submitted = st.form_submit_button("📤 Enviar Respuesta")
                
            if submitted:
                if not respuesta_usuario.strip():
                    st.warning("Por favor, escribe algo antes de enviar.")
                else:
                    with st.spinner("Evaluando tu respuesta..."):
                        resultado_metricas = logica.get_semantic_similarity(
                            model_correct=fila["ANSWER_CORRECT"],
                            model_wrong=fila["WRONG_EXAMPLES"],
                            student_answer=respuesta_usuario,
                            keywords=logica.parse_list(fila.get("KEYWORDS", []))
                        )
                        
                        score = logica.scorer_logreg_kw(resultado_metricas)
                        interpretacion = logica.interpretar_3clases(score)
                        
                        feedback_ia, modelo = logica.generar_feedback_genai(
                            pregunta=fila["QUESTION"],
                            student_answer=respuesta_usuario,
                            interpretacion=interpretacion,
                            referencia=fila["ANSWER_CORRECT"],
                            hint=fila["HINT"]
                        )
                        
                        st.session_state['last_result'] = {
                            "interpretacion": interpretacion,
                            "feedback": feedback_ia,
                            "score": score,
                            "metrics": resultado_metricas,
                            "referencia": fila["ANSWER_CORRECT"],
                            "hint": fila["HINT"],
                            "pregunta": fila["QUESTION"],
                            "respuesta": respuesta_usuario
                        }
                        
                        # Guardar en archivo persistente
                        submission = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "username": st.session_state['username'],
                            "student_name": st.session_state['name'],
                            "pregunta_id": fila["QUESTION_ID"],
                            "pregunta": fila["QUESTION"][:100] + "..." if len(fila["QUESTION"]) > 100 else fila["QUESTION"],
                            "respuesta": respuesta_usuario[:200] + "..." if len(respuesta_usuario) > 200 else respuesta_usuario,
                            "resultado": interpretacion,
                            "score": float(score),
                            "feedback": feedback_ia[:200] + "..." if len(feedback_ia) > 200 else feedback_ia
                        }
                        db.save_submission(submission)
                        
                        st.rerun()

        if 'last_result' in st.session_state:
            res = st.session_state['last_result']
            
            st.divider()
            
            if res['interpretacion'] == 'Correcta':
                st.success(f"✅ ¡Excelente! Tu respuesta es **CORRECTA**")
            elif res['interpretacion'] == 'Incorrecta':
                st.error(f"❌ Tu respuesta necesita mejoras")
            else:
                st.warning(f"🤔 Tu respuesta será **REVISADA** por el docente")
            
            st.markdown("### 🤖 Feedback")
            st.info(res['feedback'])
            
            # Los estudiantes NO ven las métricas técnicas ni la respuesta de referencia
            with st.expander("💡 Ver pista"):
                st.write(res['hint'])
    
    with tab2:
        st.subheader("📊 Tu Historial de Respuestas")
        
        my_submissions = db.get_student_submissions(st.session_state['username'])
        
        if my_submissions:
            df_history = pd.DataFrame(my_submissions)
            
            # Estadísticas del estudiante
            col1, col2, col3 = st.columns(3)
            total = len(my_submissions)
            correctas = len([s for s in my_submissions if s['resultado'] == 'Correcta'])
            incorrectas = len([s for s in my_submissions if s['resultado'] == 'Incorrecta'])
            
            col1.metric("Total de respuestas", total)
            col2.metric("Correctas", correctas, delta=f"{(correctas/total*100):.0f}%" if total > 0 else "0%")
            col3.metric("Incorrectas", incorrectas)
            
            st.divider()
            
            # Mostrar historial
            st.dataframe(
                df_history[['timestamp', 'pregunta', 'respuesta', 'resultado', 'score']],
                use_container_width=True,
                column_config={
                    "timestamp": "Fecha",
                    "pregunta": "Pregunta",
                    "respuesta": "Tu Respuesta",
                    "resultado": "Resultado",
                    "score": st.column_config.NumberColumn("Puntaje", format="%.2f")
                }
            )
        else:
            st.info("Aún no has respondido ninguna pregunta. ¡Comienza ahora!")
