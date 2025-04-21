import streamlit as st
import tempfile
import os
from supabase_client import supabase
from whisper_utils import transcribe_audio

st.set_page_config(page_title="Pitch Uploader - GENUP2050", layout="centered")
st.title("Pitch Uploader - GENUP2050")

video_file = st.file_uploader("Téléverse ta vidéo de pitch", type=["mp4", "mov", "m4a", "mp3"])

if video_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=video_file.name) as temp_file:
        temp_file.write(video_file.read())
        temp_file_path = temp_file.name

    st.success("Vidéo reçue. Transcription en cours...")

    transcription = transcribe_audio(temp_file_path)
    st.text_area("Transcription :", transcription, height=200)

    bucket_name = "pitch-videos"
    supabase.storage.from_(bucket_name).upload(f"{video_file.name}", temp_file_path)
    video_url = supabase.storage.from_(bucket_name).get_public_url(video_file.name)

    user_name = st.text_input("Ton prénom / pseudo")
    if st.button("Enregistrer le pitch"):
        data = {
            "user_name": user_name,
            "video_url": video_url,
            "transcription": transcription
        }
        supabase.table("pitchs").insert(data).execute()
        st.success("Pitch sauvegardé avec succès !")
