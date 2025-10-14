from pydub import AudioSegment
import tempfile, os

def convert_to_wav(uploaded_file):
    """
    Converts MP3 to WAV and returns the path to WAV file.
    If file is already WAV, returns original temp path.
    """
    filename = uploaded_file.name
    ext = filename.split(".")[-1].lower()

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    if ext == "wav":
        return temp_path  # Already WAV, return path

    elif ext == "mp3":
        # Convert to WAV
        wav_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio = AudioSegment.from_mp3(temp_path)
        audio = audio.set_channels(1).set_frame_rate(16000)  # mono 16kHz
        audio.export(wav_temp.name, format="wav")
        os.remove(temp_path)  # Clean up original MP3 temp
        return wav_temp.name

    else:
        raise ValueError("Unsupported audio format. Please upload MP3 or WAV.")
