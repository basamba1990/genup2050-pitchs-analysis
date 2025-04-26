import streamlit as st
from supabase import create_client, Client

# Charger les clés depuis les secrets Streamlit
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Créer le client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fonction pour récupérer l'ID de l'utilisateur connecté (si tu actives l'auth plus tard)
def get_current_user_id():
    try:
        user = supabase.auth.get_user()
        if user and user.user and user.user.id:
            return user.user.id
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur : {e}")
        return None
