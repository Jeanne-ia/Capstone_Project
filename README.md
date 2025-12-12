                                                                                                                  
```                                                                                                                  
                              8888888888                  888 8888888        d8888 
                              888                         888   888         d88888 
                              888                         888   888        d88P888 
                              8888888   888  888  8888b.  888   888       d88P 888 
                              888       888  888     "88b 888   888      d88P  888 
                              888       Y88  88P .d888888 888   888     d88P   888 
                              888        Y8bd8P  888  888 888   888    d8888888888 
                              8888888888  Y88P   "Y888888 888 8888888 d88P     888 
```                                                     
                                                                                                     

[TOC]

# Introducción
Repositorio que aloja el código para el Capstone del Máster de Ciencia de Datos.

El proyecto EvalIA surge para abordar la brecha identificada en las soluciones comerciales. Nuestra principal contribución reside en el diseño de un sistema híbrido que equilibra la eficiencia tecnológica con la intención pedagógica:
Optimización Híbrida de Recursos: A diferencia de los sistemas puramente basados en LLMs, EvalIA emplea una solución de bajo coste y alta velocidad (SBERT + Regresión Logística) para la evaluación objetiva, mitigando los riesgos de alucinación y el coste computacional. El LLM (Gemini) se reserva exclusivamente para la tarea donde ofrece el mayor valor: la generación de feedback empático y formativo.
Foco en el Pensamiento Crítico y la Educación Superior: EvalIA está específicamente diseñado para evaluar la formulación de la respuesta, incentivando el pensamiento crítico en el estudiante de nivel superior. La herramienta no solo verifica la exactitud, sino que orienta al estudiante hacia la comprensión de los objetivos de aprendizaje del módulo, en este caso de Deep Learning, una funcionalidad no cubierta con esta especificidad y profundidad por las plataformas existentes.
Sistema de Mejora Continua: Al integrar el feedback personalizado con una aplicación web persistente (Streamlit), EvalIA se posiciona como una herramienta que apoya la mejora continua del estudiante y facilita al docente la monitorización del logro de destrezas, trascendiendo la simple automatización de la nota.


# 🔐 EvalIA - Sistema de Login

## ✨ Registro de Nuevos Estudiantes

**¡SÍ! Los nuevos estudiantes pueden crear su propia cuenta.**

En la pantalla de login, haz clic en el botón **"Registrarse"** y completa:
- Usuario único (ej: `student4`)
- Nombre completo (ej: `Ana Martínez`)
- Contraseña (mínimo 6 caracteres)
- Confirmar contraseña

Una vez registrado, podrás iniciar sesión inmediatamente con tus credenciales.

---

## Usuarios de Prueba

### Profesor
- **Usuario:** `teacher`
- **Contraseña:** `teacher123`
- **Permisos:** 
  - Ver todas las respuestas de todos los estudiantes
  - Filtrar por estudiante o resultado
  - Ver estadísticas completas
  - Descargar dataset de preguntas

### Estudiantes Pre-registrados

#### Estudiante 1 - Juan Pérez
- **Usuario:** `student1`
- **Contraseña:** `student123`

#### Estudiante 2 - María García
- **Usuario:** `student2`
- **Contraseña:** `student456`

#### Estudiante 3 - Carlos López
- **Usuario:** `student3`
- **Contraseña:** `student789`

**Permisos de estudiantes:**
- Responder preguntas
- Ver su propio historial
- Ver feedback de IA
- Ver pistas (NO respuestas de referencia)

## 💾 Almacenamiento de Datos

### Respuestas de Estudiantes
Las respuestas se guardan en `student_submissions.json` y son **persistentes**:

✅ Los datos se mantienen después de cerrar sesión
✅ El profesor puede ver todas las respuestas de todos los estudiantes
✅ Cada estudiante solo ve sus propias respuestas
✅ Los datos sobreviven al reinicio de la aplicación

### Cuentas de Usuario
Las cuentas se guardan en `users.json`:

✅ Nuevos estudiantes pueden auto-registrarse
✅ Las credenciales se guardan de forma persistente
✅ Solo los estudiantes pueden auto-registrarse (no profesores)

## 🚀 Cómo usar

1. Inicia la aplicación: `streamlit run app.py`
2. **Nuevo usuario:** Haz clic en "Registrarse" y crea tu cuenta
3. **Usuario existente:** Ingresa con tus credenciales
4. Los estudiantes pueden responder preguntas
5. El profesor puede ver todas las estadísticas en la pestaña "📊 Estadísticas"