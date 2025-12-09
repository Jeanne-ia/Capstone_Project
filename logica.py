import pandas as pd
import numpy as np
import re
import ast
import json
import joblib
import nltk
from nltk.corpus import stopwords
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
    # Asumimos que los archivos están en la misma carpeta que este script
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
    t_low = params.get("t_low", 0.3)
    t_high = params.get("t_high", 0.7)
    features = params.get("feature_cols", [])
else:
    # Valores por defecto por si falla la carga
    t_low, t_high, features = 0.3, 0.7, []

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
    if model_kw is None: return 0.5 # Fallback si no hay modelo
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
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        return "⚠️ Error: No se encontró la GEMINI_API_KEY en los secretos.", "Error"

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Actúa como profesor de Deep Learning.
    Pregunta: {pregunta}
    Respuesta alumno: {student_answer}
    Clasificación modelo: {interpretacion}
    Referencia: {referencia}
    Pista: {hint}
    
    Dame un feedback breve (max 3 líneas), en segunda persona, constructivo. 
    Si es correcta, felicita y matiza. Si es incorrecta, explica el error sin juzgar.
    """
    
    try:
        resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return resp.text.strip(), "gemini-2.0-flash"
    except Exception as e:
        return f"No se pudo generar feedback IA. Error: {str(e)}", "Error"
