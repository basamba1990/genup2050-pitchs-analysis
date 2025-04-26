import streamlit as st
import tempfile
from fpdf import FPDF
from supabase_client import supabase, get_current_user_id
from whisper_utils import transcribe_audio, classify_transcription

st.set_page_config(page_title="Pitch Uploader - GENUP2050", layout="centered")
st.title("Pitch Uploader - GENUP2050")

# Authentification
auth_token = st.query_params.get("token") or st.secrets.get("SUPABASE_USER_TOKEN")

if auth_token:
    supabase.auth.set_session(auth_token, None)
    user_id = get_current_user_id()
    if not user_id:
        st.error("Token invalide ou session expirée.")
        st.stop()
else:
    st.warning("Authentification requise. Ajoute ?token=TON_TOKEN à l’URL.")
    st.stop()

# Upload de fichier
video_file = st.file_uploader("Téléverse ta vidéo de pitch", type=["mp4", "mov", "m4a", "mp3"])

if video_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=video_file.name) as temp_file:
        temp_file.write(video_file.read())
        temp_file_path = temp_file.name

    st.success("Vidéo reçue. Transcription en cours...")

    try:
        transcription = transcribe_audio(temp_file_path)
        st.text_area("Transcription :", transcription, height=200)

        st.info("Analyse du profil DISC en cours...")
        disc_profile = classify_transcription(transcription)
        st.text_area("Profil DISC détecté :", disc_profile, height=100)

        bucket_name = "pitch-videos"
        supabase.storage.from_(bucket_name).upload(video_file.name, temp_file_path)
        video_url = supabase.storage.from_(bucket_name).get_public_url(video_file.name)

        user_name = st.text_input("Ton prénom / pseudo")
        if st.button("Enregistrer le pitch"):
            if not user_name:
                st.warning("Merci d’ajouter un prénom ou pseudo.")
            else:
                data = {
                    "user_name": user_name,
                    "video_url": video_url,
                    "transcription": transcription,
                    "disc_profile": disc_profile,
                    "user_id": user_id
                }
                response = supabase.table("pitchs").insert(data).execute()
                if response.error:
                    st.error(f"Erreur de sauvegarde : {response.error.message}")
                else:
                    st.success("Pitch sauvegardé avec succès !")

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")

# === Section : Affichage des pitchs de l'utilisateur ===
st.markdown("---")
st.subheader("Mes pitchs enregistrés")

try:
    response = supabase.table("pitchs").select("*").eq("user_id", user_id).execute()
    pitchs = response.data

    if pitchs:
        for pitch in pitchs:
            with st.expander(f"{pitch['user_name']}"):
                st.video(pitch["video_url"])
                st.markdown(f"**Profil DISC :** {pitch['disc_profile']}")
                st.text_area("Transcription complète :", pitch["transcription"], height=150)

                # Bouton PDF
                if st.button(f"📄 Télécharger PDF - {pitch['id']}"):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.multi_cell(0, 10, f"Nom : {pitch['user_name']}\n\nProfil DISC : {pitch['disc_profile']}\n\nTranscription :\n{pitch['transcription']}")
                    pdf_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    pdf.output(pdf_output.name)
                    with open(pdf_output.name, "rb") as file:
                        st.download_button("Télécharger la transcription PDF", data=file, file_name="transcription_pitch.pdf")

                # Bouton de suppression
                if st.button(f"🗑 Supprimer le pitch - {pitch['id']}"):
                    delete_response = supabase.table("pitchs").delete().eq("id", pitch["id"]).execute()
                    if delete_response.error:
                        st.error("Erreur lors de la suppression.")
                    else:
                        st.success("Pitch supprimé. Recharge la page pour voir la mise à jour.")
    else:
        st.info("Aucun pitch enregistré pour l’instant.")

except Exception as e:
    st.error(f"Erreur lors du chargement des pitchs : {e}")
