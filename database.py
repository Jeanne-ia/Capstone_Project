"""
Database operations using Supabase
Handles user authentication and student submissions
"""

from supabase import create_client, Client
import streamlit as st
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# Initialize Supabase client
@st.cache_resource
def init_supabase() -> Client:
    """Initialize and cache Supabase client"""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        
        # Create client with minimal options to avoid compatibility issues
        options = {
            "schema": "public",
            "auto_refresh_token": True,
            "persist_session": True,
        }
        
        return create_client(supabase_url=url, supabase_key=key)
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        return None

# Get Supabase client
supabase: Client = init_supabase()

# ==================== USER MANAGEMENT ====================

def register_user(username: str, password: str, name: str) -> Tuple[bool, str]:
    """
    Register a new student user
    Returns: (success: bool, message: str)
    """
    try:
        # Check if username already exists
        response = supabase.table('users').select('username').eq('username', username).execute()
        
        if response.data and len(response.data) > 0:
            return False, "El usuario ya existe"
        
        # Insert new user
        data = {
            "username": username,
            "password": password,  # In production, hash this!
            "name": name,
            "role": "student",
            "created_at": datetime.now().isoformat()
        }
        
        supabase.table('users').insert(data).execute()
        return True, "Registro exitoso"
    
    except Exception as e:
        return False, f"Error al registrar: {str(e)}"

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user and return user data
    Returns: user dict if successful, None otherwise
    """
    try:
        response = supabase.table('users').select('*').eq('username', username).eq('password', password).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    except Exception as e:
        st.error(f"Error al autenticar: {e}")
        return None

def get_all_users() -> List[Dict]:
    """Get all users (for admin purposes)"""
    try:
        response = supabase.table('users').select('*').execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error al obtener usuarios: {e}")
        return []

# ==================== SUBMISSIONS MANAGEMENT ====================

def save_submission(submission: Dict) -> bool:
    """
    Save a student submission to database
    Returns: True if successful, False otherwise
    """
    try:
        # Add created_at timestamp if not present
        if 'created_at' not in submission:
            submission['created_at'] = datetime.now().isoformat()
        
        result = supabase.table('submissions').insert(submission).execute()
        print(f"✅ Submission saved successfully: {result}")
        return True
    
    except Exception as e:
        print(f"❌ Error saving submission: {e}")
        st.error(f"Error al guardar respuesta: {e}")
        return False

def get_student_submissions(username: str) -> List[Dict]:
    """
    Get all submissions for a specific student
    Returns: List of submission dictionaries
    """
    try:
        response = supabase.table('submissions').select('*').eq('username', username).order('id', desc=True).execute()
        print(f"📊 Retrieved {len(response.data) if response.data else 0} submissions for {username}")
        return response.data if response.data else []
    
    except Exception as e:
        print(f"❌ Error getting submissions: {e}")
        st.error(f"Error al obtener respuestas: {e}")
        return []

def get_all_submissions() -> List[Dict]:
    """
    Get all submissions from all students (for teacher)
    Returns: List of submission dictionaries
    """
    try:
        response = supabase.table('submissions').select('*').order('id', desc=True).execute()
        print(f"📊 Retrieved {len(response.data) if response.data else 0} total submissions")
        return response.data if response.data else []
    
    except Exception as e:
        print(f"❌ Error getting all submissions: {e}")
        st.error(f"Error al obtener todas las respuestas: {e}")
        return []

def get_submissions_by_student_name(student_name: str) -> List[Dict]:
    """Get all submissions for a student by their name"""
    try:
        response = supabase.table('submissions').select('*').eq('student_name', student_name).order('id', desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error al filtrar por estudiante: {e}")
        return []

def get_submissions_by_result(resultado: str) -> List[Dict]:
    """Get all submissions filtered by result (Correcta/Incorrecta/Revisar)"""
    try:
        response = supabase.table('submissions').select('*').eq('resultado', resultado).order('id', desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error al filtrar por resultado: {e}")
        return []

def get_submission_stats() -> Dict:
    """Get aggregated statistics for all submissions"""
    try:
        all_subs = get_all_submissions()
        
        stats = {
            "total": len(all_subs),
            "correctas": len([s for s in all_subs if s.get('resultado') == 'Correcta']),
            "incorrectas": len([s for s in all_subs if s.get('resultado') == 'Incorrecta']),
            "revisar": len([s for s in all_subs if s.get('resultado') == 'Revisar']),
            "students": len(set([s.get('student_name') for s in all_subs]))
        }
        
        return stats
    
    except Exception as e:
        st.error(f"Error al calcular estadísticas: {e}")
        return {"total": 0, "correctas": 0, "incorrectas": 0, "revisar": 0, "students": 0}

# ==================== INITIALIZATION ====================

def initialize_default_users():
    """
    Initialize default users if they don't exist
    Call this once during setup
    """
    default_users = [
        {"username": "teacher", "password": "teacher123", "name": "Profesor", "role": "teacher"},
        {"username": "student1", "password": "student123", "name": "Juan Pérez", "role": "student"},
        {"username": "student2", "password": "student456", "name": "María García", "role": "student"},
        {"username": "student3", "password": "student789", "name": "Carlos López", "role": "student"}
    ]
    
    try:
        for user in default_users:
            # Check if user exists
            response = supabase.table('users').select('username').eq('username', user['username']).execute()
            
            if not response.data or len(response.data) == 0:
                # User doesn't exist, create it
                user['created_at'] = datetime.now().isoformat()
                supabase.table('users').insert(user).execute()
                print(f"Created user: {user['username']}")
        
        return True
    except Exception as e:
        print(f"Error initializing users: {e}")
        return False
