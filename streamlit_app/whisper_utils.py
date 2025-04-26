import openai
import os
import streamlit as st

# Configurer la clé API OpenAI depuis les secrets Streamlit
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=openai.api_key)

def transcribe_audio(file_path):
    """
    Transcrit un fichier audio en texte à l'aide de Whisper (modèle whisper-1).
    
    Paramètre :
        file_path (str) : Chemin local vers le fichier audio.
    
    Retourne :
        str : Transcription texte.
    """
    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        st.error(f"Erreur lors de la transcription : {e}")
        return ""

def classify_transcription(text):
    """
    Classifie un texte transcrit en fonction du profil DISC dominant avec GPT-4.
    
    Paramètre :
        text (str) : Texte à analyser.
    
    Retourne :
        str : Résultat de l’analyse DISC.
    """
    prompt = f"""Tu es un coach expert DISC 4Colors. Analyse le texte suivant et donne-moi le profil DISC dominant (rouge, jaune, vert ou bleu). Justifie brièvement.

Texte : {text}"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Erreur lors de la classification DISC : {e}")
        return "Erreur d’analyse DISC"
