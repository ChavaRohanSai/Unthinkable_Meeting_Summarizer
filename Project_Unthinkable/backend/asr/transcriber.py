from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment
import io
import os
import shutil
import logging

# ✅ Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def convert_audio(file_path, output_path="converted.wav"):
    """
    Converts audio to mono and 16 kHz WAV format for Google Speech-to-Text.
    """
    try:
        logging.info("Converting audio to mono 16kHz WAV...")
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(output_path, format="wav")
        return output_path
    except Exception as e:
        raise RuntimeError(f"Audio conversion failed: {e}")

def split_audio(file_path, chunk_length_ms=30000):
    """
    Splits audio into chunks of given length (default = 30 s).
    """
    try:
        logging.info("Splitting audio into chunks...")
        audio = AudioSegment.from_wav(file_path)
        return [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    except Exception as e:
        raise RuntimeError(f"Audio splitting failed: {e}")

def export_chunks(chunks, output_dir="temp_chunks"):
    """
    Saves AudioSegment chunks to WAV files and returns list of file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_paths = []
    for i, chunk in enumerate(chunks):
        path = os.path.join(output_dir, f"chunk_{i}.wav")
        chunk.export(path, format="wav")
        file_paths.append(path)
    logging.info(f"Exported {len(file_paths)} chunks to {output_dir}")
    return file_paths

def transcribe_chunk(file_path, num_speakers=2):
    """
    Transcribes one chunk via Google Speech-to-Text with speaker diarization.
    """
    client = speech.SpeechClient()
    with io.open(file_path, "rb") as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_speaker_diarization=True,
        diarization_speaker_count=num_speakers,
        enable_automatic_punctuation=True,
        model="latest_long"  # ✅ Better for long-form audio
    )

    logging.info(f"🎧 Transcribing {os.path.basename(file_path)} ...")
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=600)

    if not response.results:
        logging.warning(f"No transcription results for {file_path}")
        return ""

    words_info = response.results[-1].alternatives[0].words
    transcript_lines, current_line, current_speaker = [], [], None

    for word_info in words_info:
        speaker_tag = f"Speaker {word_info.speaker_tag}"
        if current_speaker is None:
            current_speaker = speaker_tag
        elif speaker_tag != current_speaker:
            transcript_lines.append(f"{current_speaker}: {' '.join(current_line)}")
            current_speaker, current_line = speaker_tag, []
        current_line.append(word_info.word)

    if current_line:
        transcript_lines.append(f"{current_speaker}: {' '.join(current_line)}")

    return "\n".join(transcript_lines)

def transcribe_audio(file_path, num_speakers=2):
    """
    Full pipeline: convert → split → transcribe → merge.
    Returns the complete speaker-labeled transcript.
    """
    logging.info("Starting full transcription pipeline...")
    converted = convert_audio(file_path)

    chunks = split_audio(converted)
    chunk_files = export_chunks(chunks)

    logging.info(f"🚀 Starting transcription for {len(chunk_files)} chunks...")
    full_transcript = ""
    try:
        for idx, chunk_file in enumerate(chunk_files, 1):
            logging.info(f"Processing chunk {idx}/{len(chunk_files)}")
            full_transcript += transcribe_chunk(chunk_file, num_speakers) + "\n"
    finally:
        # Clean up temp files even if something fails
        logging.info("🧹 Cleaning up temporary files...")
        shutil.rmtree("temp_chunks", ignore_errors=True)
        if os.path.exists(converted):
            os.remove(converted)

    logging.info("✅ Transcription complete.")
    return full_transcript.strip()

# ✅ Stand-alone test
if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Project_Unthinkable/googlecreds/service_account.json"

    transcript = transcribe_audio(
        "D:/Project_Unthinkable/sample_test_file/meeting_audio.wav",
        num_speakers=2
    )

    print("\n--- TRANSCRIPT ---\n")
    print(transcript)
