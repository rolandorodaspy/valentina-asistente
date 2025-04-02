import streamlit as st
import openai
import requests
import tempfile
from pydub import AudioSegment

# Cargar claves desde los secretos
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]

# Mostrar imagen del avatar
st.image("avatar.png", width=300)
st.title("🎙️ Tu asistente Valentina")

# Subir archivo de audio
st.write("Subí un audio en formato WAV o MP3 para que Valentina te responda con voz.")
audio_file = st.file_uploader("Subí un audio (WAV/MP3)", type=["wav", "mp3"])

if audio_file is not None:
    # Convertir MP3 a WAV si es necesario
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

        # Respuesta con ChatGPT
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sos Valentina, la asistente cálida y cercana de Rolo."},
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

        audio_bytes = elevenlabs_tts(valentina_text)
        st.audio(audio_bytes, format="audio/mp3")
