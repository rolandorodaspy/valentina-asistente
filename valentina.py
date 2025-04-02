import streamlit as st
import openai
import tempfile
from pydub import AudioSegment
from gtts import gTTS

# Inicializar cliente OpenAI
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Mostrar avatar
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

        # Generar respuesta con GPT
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sos Valentina, una asistente cálida, amable y cercana que responde con cariño y claridad."},
                {"role": "user", "content": user_text}
            ]
        )
        valentina_text = chat_response.choices[0].message.content
        st.markdown(f"**Valentina dice:** {valentina_text}")

        # Convertir texto a voz con gTTS
        try:
            tts = gTTS(text=valentina_text, lang='es')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tts_audio:
                tts.save(tts_audio.name)
                st.audio(tts_audio.name, format="audio/mp3")
        except Exception as e:
            st.error(f"Error al generar audio con gTTS: {e}")
