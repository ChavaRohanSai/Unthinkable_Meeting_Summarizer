import sys
import os

# Add the backend folder to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))


import streamlit as st
import os
import tempfile
from pydub import AudioSegment
from asr.transcriber import transcribe_audio
from summarizer.summarizer import summarize_meeting

st.set_page_config(page_title="AI Meeting Summarizer", layout="wide")
st.title("🎙️ AI Meeting Summarizer")

# --- Google Credentials ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Project_Unthinkable/googlecreds/service_account.json"

# --- Audio Upload ---
uploaded_file = st.file_uploader("Upload meeting audio (WAV or MP3)", type=["wav", "mp3"])

def convert_to_wav(file):
    """Convert MP3 to WAV, or return WAV as-is."""
    filename = file.name
    ext = filename.split(".")[-1].lower()

    if ext == "wav":
        return file
    elif ext == "mp3":
        wav_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio = AudioSegment.from_mp3(file)
        audio = audio.set_channels(1).set_frame_rate(16000)  # mono 16kHz
        audio.export(wav_temp.name, format="wav")
        return open(wav_temp.name, "rb")
    else:
        raise ValueError("Unsupported audio format. Please upload WAV or MP3.")

if uploaded_file:
    try:
        wav_file = convert_to_wav(uploaded_file)

        # Save to temp file for transcription
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(wav_file.read())
            temp_audio_path = temp_audio.name

        st.info("Transcribing audio... ⏳")
        transcript = transcribe_audio(temp_audio_path, num_speakers=2)
        st.success("Transcription complete ✅")

        st.info("Generating summary & extracting key points 🧠")
        summary_data = summarize_meeting(transcript)
        st.success("Summary complete ✅")

        # --- Structured Output Columns ---
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Meeting Summary")
            st.text_area("", summary_data.get("summary",""), height=250)
            st.download_button("Download Summary", summary_data.get("summary",""), file_name="meeting_summary.txt")

        with col2:
            st.subheader("Key Points Discussed")
            st.text_area("", "\n".join(summary_data.get("key_points", [])), height=250)
            st.download_button("Download Key Points", "\n".join(summary_data.get("key_points", [])), file_name="key_points.txt")

        with col3:
            st.subheader("Action Points Discussed")
            st.text_area("", "\n".join(summary_data.get("action_points", [])), height=250)
            st.download_button("Download Action Points", "\n".join(summary_data.get("action_points", [])), file_name="action_points.txt")

        # --- Full Transcript (optional, below columns) ---
        st.subheader("Full Transcript")
        st.text_area("", transcript, height=300)
        st.download_button("Download Transcript", transcript, file_name="meeting_transcript.txt")

    except ValueError as e:
        st.error(str(e))
    finally:
        # Cleanup temporary files
        try:
            wav_file.close()
            if "temp_audio_path" in locals():
                os.remove(temp_audio_path)
            if uploaded_file.name.lower().endswith("mp3"):
                os.remove(wav_file.name)
        except:
            pass
