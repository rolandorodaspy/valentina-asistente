import streamlit as st
import openai
from gtts import gTTS
import tempfile
import base64
from audiorecorder import audiorecorder
from pydub import AudioSegment

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.image("avatar.png", width=300)
st.title("🎙️ Tu asistente Valentina")

# Grabar audio desde el navegador
st.subheader("🎤 Hablale a Valentina")
audio = audiorecorder("🔴 Grabar", "⚪️ Detener")

if len(audio) > 0:
    # Guardar audio como WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        tmp_audio.write(audio.tobytes())

    st.audio(tmp_audio.name)

    # Transcribir con Whisper
    with open(tmp_audio.name, "rb") as audio_input:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_input
        )
    user_text = transcript.text
    st.markdown(f"**Transcripción:** {user_text}")

    # Generar respuesta con GPT
    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sos Valentina, una asistente cálida, cercana y clara."},
            {"role": "user", "content": user_text}
        ]
    )
    valentina_text = chat_response.choices[0].message.content
    st.markdown(f"**Valentina dice:** {valentina_text}")

    # Convertir texto a voz con gTTS
    tts = gTTS(text=valentina_text, lang='es')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tts_audio:
        tts.save(tts_audio.name)

        # Reproducir automáticamente usando JavaScript
        audio_base64 = base64.b64encode(open(tts_audio.name, 'rb').read()).decode()
        audio_html = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
