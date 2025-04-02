import streamlit as st
import openai
import tempfile
import os
import requests
from pydub import AudioSegment

# Crear cliente de OpenAI con clave desde secretos
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Imagen de Valentina
st.image("avatar.png", width=300)
st.title("🎙️ Tu asistente Valentina en la nube")

# Subida de archivo de audio
st.write("Subí tu pregunta en audio y Valentina te responde con voz.")
audio_file = st.file_uploader("Subí un audio (WAV o MP3)", type=["wav", "mp3"])

if audio_file is not None:
    # Convertir MP3 a WAV si hace falta
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        if audio_file.type == "audio/mp3":
            audio = AudioSegment.from_file(audio_file, format="mp3")
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

        # Generación de respuesta con ChatGPT
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sos Valentina, la asistente amable y cercana de Rolo."},
                {"role": "user", "content": user_text}
            ]
        )

        valentina_text = chat_response.choices[0].message.content
        st.markdown(f"**Valentina dice:** {valentina_text}")

        # Conversión a voz con ElevenLabs
        def elevenlabs_tts(text, voice="Rachel"):
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
            headers = {
                "xi-api-key": st.secrets["ELEVENLABS_API_KEY"],
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

        audio_output = elevenlabs_tts(valentina_text)
        st.audio(audio_output, format="audio/mp3")
