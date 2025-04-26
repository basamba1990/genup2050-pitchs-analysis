import streamlit as st
import tempfile
from supabase_client import supabase
from whisper_utils import transcribe_audio, classify_transcription

st.set_page_config(page_title="Pitch Uploader - GENUP2050", layout="centered")
st.title("Pitch Uploader - GENUP2050")

video_file = st.file_uploader("Téléverse ta vidéo de pitch", type=["mp4", "mov", "m4a", "mp3"])

if video_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=video_file.name) as temp_file:
        temp_file.write(video_file.read())
        temp_file_path = temp_file.name

    st.success("Vidéo reçue. Transcription en cours...")

    try:
        # Étape 1 : Transcription
        transcription = transcribe_audio(temp_file_path)
        st.text_area("Transcription :", transcription, height=200)

        # Étape 2 : Classification DISC
        st.info("Analyse du profil DISC en cours...")
        disc_profile = classify_transcription(transcription)
        st.text_area("Profil DISC détecté :", disc_profile, height=100)

        # Étape 3 : Upload de la vidéo
        bucket_name = "pitch-videos"
        supabase.storage.from_(bucket_name).upload(video_file.name, temp_file_path)
        video_url = supabase.storage.from_(bucket_name).get_public_url(video_file.name)

        # Étape 4 : Sauvegarde Supabase
        user_name = st.text_input("Ton prénom / pseudo")
        if st.button("Enregistrer le pitch") and user_name:
            data = {
                "user_name": user_name,
                "video_url": video_url,
                "transcription": transcription,
                "disc_profile": disc_profile  # Nouvelle colonne
            }
            supabase.table("pitchs").insert(data).execute()
            st.success("Pitch sauvegardé avec succès !")
        elif st.button("Enregistrer le pitch") and not user_name:
            st.warning("Merci d’ajouter un prénom ou pseudo.")

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
