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
