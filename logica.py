import pandas as pd
import numpy as np
import re
import ast
import json
import joblib
import nltk
from nltk.corpus import stopwords
from collections import Counter
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
import streamlit as st

# --- CONFIGURACIÓN INICIAL ---

# Descargar stopwords si no existen
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

spanish_stopwords = set(stopwords.words('spanish'))

# --- CARGA DE MODELOS (Con Caché para velocidad) ---

@st.cache_resource
def cargar_modelo_sbert():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

@st.cache_resource
def cargar_recursos_ml():
    # Archivos están en la misma carpeta
    try:
        model_kw = joblib.load("model_kw.joblib")
        with open("params_kw.json") as f:
            params = json.load(f)
        return model_kw, params
    except FileNotFoundError:
        return None, None

@st.cache_data
def cargar_dataset():
    try:
        # Intentamos cargar el CSV
        df = pd.read_csv("Dataset_preguntas_v1.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame() # Retorna vacío si falla

# Inicializamos modelos globales
model_sbert = cargar_modelo_sbert()
model_kw, params = cargar_recursos_ml()

# Extraer parámetros si cargaron bien
if params:
    t_low = params.get("t_low", 0.3509)
    t_high = params.get("t_high", 0.6018)
    features = params.get("feature_cols", ['avg_correct', 'max_correct', 'avg_wrong', 'max_wrong', 'kw_recall', 'kw_precision', 'kw_f1'])
else:
    # Valores por defecto por si falla la carga
    t_low, t_high, features = 0.3509, 0.6018, ['avg_correct', 'max_correct', 'avg_wrong', 'max_wrong', 'kw_recall', 'kw_precision', 'kw_f1']

# --- FUNCIONES DE LÓGICA ---

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_list(x):
    try:
        return ast.literal_eval(x) if isinstance(x, str) else x
    except Exception:
        return [x]
        
# Función para extraer palabras clave
def compute_all_keywords(df, top_k=10, threshold=0.2):
    # Keywords candidatos ordenadas por SBERT
    def keybert_like_keywords(ANSWER_LST, top_k=10):
        if not isinstance(ANSWER_LST, str):
            return []
        try:
            parsed = ast.literal_eval(ANSWER_LST)
            sentences = parsed if isinstance(parsed, list) else [parsed]
        except Exception:
            sentences = [ANSWER_LST]

        text = " ".join(sentences)
        clean = preprocess_text(text)

        words = [
            w for w in clean.split()
            if w not in spanish_stopwords and len(w) > 2
        ]
        if not words:
            return []

        candidates = sorted(set(words))

        doc_emb = model_sbert.encode([clean])
        cand_embs = model_sbert.encode(candidates)

        sims = cosine_similarity(doc_emb, cand_embs)[0]
        idx_sorted = sims.argsort()[::-1]
        top_idx = idx_sorted[:top_k]

        return [candidates[i] for i in top_idx]

    # Calcular KEYWORDS_SBERT para cada pregunta
    df["KEYWORDS_SBERT"] = df["ANSWER_CORRECT"].apply(
        lambda txt: keybert_like_keywords(txt, top_k=top_k)
    )

    # Calcular keywords globales
    df_counts = Counter()
    n_docs = len(df)

    for kws in df["KEYWORDS_SBERT"]:
        for w in set(kws):
            df_counts[w] += 1

    auto_global_stopwords = {
        w for w, c in df_counts.items() if c / n_docs > threshold
    }

    # Filtrar palabras globales
    def filter_stopwords(kws):
        return [w for w in kws if w not in auto_global_stopwords]

    df["KEYWORDS"] = df["KEYWORDS_SBERT"].apply(filter_stopwords)
    df.drop('KEYWORDS_SBERT', axis=1, inplace=True)
    return df

def get_keyword_coverage(student_answer, keywords):
    kw_set = set(keywords or [])
    if not isinstance(student_answer, str) or not student_answer.strip() or not kw_set:
        return {"kw_recall": 0.0, "kw_precision": 0.0, "kw_f1": 0.0}

    clean = preprocess_text(student_answer)
    words = clean.split()
    student_words = {w for w in words if w not in spanish_stopwords and len(w) > 2}

    if not student_words:
        return {"kw_recall": 0.0, "kw_precision": 0.0, "kw_f1": 0.0}

    overlap = student_words & kw_set
    hits = len(overlap)
    kw_recall = hits / len(kw_set) if kw_set else 0.0
    kw_precision = hits / len(student_words) if student_words else 0.0
    kw_f1 = (2 * kw_precision * kw_recall / (kw_precision + kw_recall)) if (kw_precision + kw_recall) > 0 else 0.0

    return {"kw_recall": kw_recall, "kw_precision": kw_precision, "kw_f1": kw_f1}

def get_semantic_similarity(model_correct, model_wrong, student_answer, keywords=None):
    correct_list = parse_list(model_correct)
    wrong_list = parse_list(model_wrong)
    
    clean_student = preprocess_text(student_answer)
    if not clean_student:
        return {'avg_correct': 0.0, 'avg_wrong': 0.0, 'max_correct': 0.0, 'max_wrong': 0.0}

    embedding_student = model_sbert.encode([clean_student])

    def sim_to_list(list_ref):
        sims = []
        for ref in list_ref:
            clean_ref = preprocess_text(str(ref))
            emb_ref = model_sbert.encode([clean_ref])
            sims.append(float(cosine_similarity(emb_ref, embedding_student)[0][0]))
        return sims

    correct_scores = sim_to_list(correct_list)
    wrong_scores = sim_to_list(wrong_list)
    
    base = {
        'avg_correct': sum(correct_scores)/len(correct_scores) if correct_scores else 0.0,
        'avg_wrong': sum(wrong_scores)/len(wrong_scores) if wrong_scores else 0.0,
        'max_correct': max(correct_scores) if correct_scores else 0.0,
        'max_wrong': max(wrong_scores) if wrong_scores else 0.0
    }
    base.update(get_keyword_coverage(student_answer, keywords or []))
    return base

def scorer_logreg_kw(row):
    if model_kw is None: return 0.0 # Fallback si no hay modelo
    linear = model_kw.intercept_[0]
    for coef, feat in zip(model_kw.coef_[0], features):
        linear += coef * row.get(feat, 0)
    return 1 / (1 + np.exp(-linear))

def interpretar_3clases(score):
    if score >= t_high: return 'Correcta'
    elif score <= t_low: return 'Incorrecta'
    else: return 'Revisar'

def generar_feedback_genai(pregunta, student_answer, interpretacion, referencia, hint):
    # Intentamos obtener la API KEY de los secretos de Streamlit
    
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
            Eres profesor de un máster en Deep Learning y corriges preguntas abiertas de teoría.
            
            Tu tarea:
            Escribe un feedback breve y personalizado (máximo 3 líneas) sobre la respuesta del estudiante, en español.
            
            Contexto:
            - Pregunta del examen:
            {pregunta}
            
            - Respuesta del estudiante:
            {student_answer}
            
            - Clasificación automática de la respuesta (CORRECTA, INCORRECTA, REVISAR_PROFESOR):
            {interpretacion}
            
            - Respuestas de referencia del profesor:
            {referencia}
            
            - Pista o hint para el alumno:
            {hint}
            
            Instrucciones generales:
            - Habla siempre en segunda persona (por ejemplo: "tu respuesta...").
            - No repitas la pregunta ni copies literalmente la respuesta de referencia.
            - No menciones que eres un modelo de lenguaje ni al sistema automático.
            - Mantén un tono claro, cercano y motivador.
            
            Reglas según la clasificación:
            - Si la clasificación es CORRECTA:
              - Comienza con una breve felicitación.
              - Señala un punto fuerte concreto de la respuesta.
              - Sugiere una idea para profundizar o matizar.
            
            - Si la clasificación es INCORRECTA:
              - Usa un tono constructivo, sin juicios duros.
              - Explica qué concepto importante falta, está confuso o es erróneo.
              - Sugiere 1–2 acciones claras para mejorar (qué revisar o cómo reformular).
            
            - Si la clasificación es REVISAR:
              - Indica que la respuesta debe ser revisada por un profesor humano.
              - Menciona brevemente un aspecto que parece bien encaminado y otro que genera duda o ambigüedad.
              - Invita al estudiante a revisar los conceptos clave relacionados con la pregunta.
            
            Formato de salida:
            Devuelve solo el texto del feedback, en un único párrafo de máximo 3–4 líneas, sin listas, encabezados ni emojis.
            """

    MODELOS = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]
    for modelo in MODELOS:
        try:
            resp = client.models.generate_content(model=modelo,contents=prompt,)
            feedback = resp.text.strip()
            return feedback, modelo
        except Exception as e:
            msg = str(e).lower()
            # Por si hay error de rate limit
            if ("rate" in msg and "limit" in msg) or "429" in msg or "resourceexhausted" in msg:
                ultimo_error = e
                continue  # intenta con el siguiente modelo
            ultimo_error = e
            break
    # Feedback "humano" neutro en lugar del traceback de ERROR
    feedback_fallback = (
        "Por ahora no pude generar feedback automático. "
        "Revisa tu respuesta comparando los conceptos clave vistos en clase "
        "y las pistas proporcionadas."
    )

    return feedback_fallback, "ERROR"
