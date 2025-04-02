import streamlit as st
import openai
import requests
import tempfile
from pydub import AudioSegment

# Inicializar cliente OpenAI con API Key desde secretos
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]

# Mostrar imagen del avatar
st.image("avatar.png", width=300)
st.title("🎙️ Tu asistente Valentina")

# Subir archivo de audio
st.write("Subí un audio en formato WAV o MP3 para que Valentina te responda con voz.")
audio_file = st.file_uploader("Subí un audio (WAV/MP3)", type=["wav", "mp3"])

if audio_file is not None:
    # Convertir MP3 a WAV si hace falta
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        if audio_file.type == "audio/mp3":
            audio = AudioSegment.from_mp3(audio_file)
            audio.export(tmp_audio.name, format="wav")
        else:
            tmp_audio.write(audio_file.read())

        st.audio(tmp_audio.name)

        # Transcripción con Whisper
        with open(tmp_audio.name, "rb") as audio_input:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_input
            )
        user_text = transcript.text
        st.markdown(f"**Transcripción:** {user_text}")

        # Respuesta de Valentina con GPT
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sos Valentina, una asistente cálida, amable y cercana. Respondés con empatía y claridad."},
                {"role": "user", "content": user_text}
            ]
        )
        valentina_text = chat_response.choices[0].message.content
        st.markdown(f"**Valentina dice:** {valentina_text}")

        # Texto a voz con ElevenLabs
        def elevenlabs_tts(text, voice="Rachel"):
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            }
            data = {
                "text": text,
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.75
                }
            }
            response = requests.post(url, headers=headers, json=data)
            return response.content

        # Reproducir audio si es válido
        try:
            audio_bytes = elevenlabs_tts(valentina_text)

            if audio_bytes and len(audio_bytes) > 1000:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                    tmpfile.write(audio_bytes)
                    st.audio(tmpfile.name, format="audio/mp3")
            else:
                st.error("⚠️ No se pudo reproducir el audio. El archivo está vacío o corrupto.")
        except Exception as e:
            st.error(f"Error al generar audio con ElevenLabs: {e}")
