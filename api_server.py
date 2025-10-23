from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.asr.transcriber import transcribe_audio
from backend.summarizer.summarizer import summarize_meeting
from backend.database import save_meeting, get_all_meetings, get_meeting_by_id
from pydub import AudioSegment
import tempfile, os
from datetime import datetime, timedelta

app = FastAPI(title="AI Meeting Summarizer API")

# --- CORS for frontend ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Google credentials for transcription ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Project_Unthinkable/backend/googlecreds/service_account.json"

# ----------------- Endpoints -----------------

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...), num_speakers: int = 2):
    """
    Upload WAV or MP3, transcribe, summarize, extract key/action points, save to MySQL.
    Optional: num_speakers (default 2)
    """
    
    # --- Save uploaded file temporarily ---
    suffix = os.path.splitext(file.filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    # --- Convert MP3 to WAV if needed ---
    if suffix == ".mp3":
        wav_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio = AudioSegment.from_mp3(temp_path)
        audio = audio.set_channels(1).set_frame_rate(16000)  # mono 16kHz
        audio.export(wav_temp.name, format="wav")
        temp_path = wav_temp.name

    # --- Transcription ---
    transcript = transcribe_audio(temp_path, num_speakers=num_speakers)

    # --- Summarization & extract key/action points ---
    summary_data = summarize_meeting(transcript)
    # Support older summarizer returning string
    if isinstance(summary_data, str):
        summary_data = {
            "summary": summary_data,
            "key_points": [],
            "action_points": []
        }
    summary = summary_data.get("summary", "")
    key_points = summary_data.get("key_points", [])
    action_points = summary_data.get("action_points", [])

    # --- Timestamps ---
    meeting_date = datetime.now().date()
    start_time = datetime.now().time().strftime("%H:%M:%S")
    audio_duration_sec = AudioSegment.from_wav(temp_path).duration_seconds
    end_time = (datetime.now() + timedelta(seconds=audio_duration_sec)).time().strftime("%H:%M:%S")

    # --- Save to MySQL ---
    meeting_id = save_meeting(
        filename=file.filename,
        transcript=transcript,
        summary=summary,
        key_points=key_points,
        action_points=action_points,
        meeting_date=meeting_date,
        start_time=start_time,
        end_time=end_time
    )

    # --- Cleanup temp files ---
    os.remove(temp_path)
    if suffix == ".mp3":
        os.remove(wav_temp.name)

    # --- Response ---
    return {
        "meeting_id": meeting_id,
        "transcript": transcript,
        "summary": summary,
        "key_points": key_points if key_points else ["No key points mentioned."],
        "action_points": action_points if action_points else ["No action points mentioned."],
        "meeting_date": str(meeting_date),
        "start_time": start_time,
        "end_time": end_time
    }


@app.get("/meetings")
def list_meetings():
    """List all meetings with summary, key points, action points, and timestamps."""
    return get_all_meetings()


@app.get("/meetings/{meeting_id}")
def get_meeting(meeting_id: str):
    """Get one meeting by ID, including transcript, summary, key points, action points, timestamps."""
    meeting = get_meeting_by_id(meeting_id)
    if not meeting:
        return {"error": "Meeting not found"}
    # Ensure empty lists are replaced with default messages
    if not meeting["key_points"]:
        meeting["key_points"] = ["No key points mentioned."]
    if not meeting["action_points"]:
        meeting["action_points"] = ["No action points mentioned."]
    return meeting
