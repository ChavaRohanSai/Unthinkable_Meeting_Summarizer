AI Meeting Summarizer
## 🙏 Acknowledgements

This project utilizes the following key technologies and models:

* **Summarization Model:** The text summarization capability is powered by the [BART (large-cnn) model](https://huggingface.co/facebook/bart-large-cnn) developed by Facebook AI (now Meta AI). We access it through the Hugging Face Transformers library.
    * **Original Paper:** Lewis, M., Liu, Y., Goyal, N., Ghazvininejad, M., Mohamed, A., Levy, O., Stoyanov, V., & Zettlemoyer, L. (2019). *BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension*. [arXiv:1910.13461](https://arxiv.org/abs/1910.13461).

* **Speech-to-Text:** Transcription is handled by the [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text).

* **Backend Framework:** The application's API is built with [FastAPI](https://fastapi.tiangolo.com/).



AI Meeting Summarizer is a web-based application that allows users to upload meeting audio (MP3/WAV), transcribe it, summarize key points, and extract action items using Google Speech-to-Text and Hugging Face Transformers.

Features:
- Upload audio files (.mp3 or .wav)
- Transcription with speaker diarization (detects multiple speakers)
- Summarization of the meeting transcript
- Extraction of Key Points and Action Items
- Downloadable summaries, key points, action items, and full transcript
- Responsive HTML/CSS frontend

Tech Stack:
- Backend: FastAPI, Python, MySQL
- Frontend: HTML, CSS, JavaScript
- Speech-to-Text: Google Cloud Speech API
- Summarization: Hugging Face Transformers (facebook/bart-large-cnn)
- Audio Processing: Pydub

Installation:

1. Clone the repository
   git clone <your-repo-url>
   cd Project_Unthinkable

2. Create and activate a virtual environment
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt

4. Set Google credentials
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account.json"
   # Windows PowerShell
   $env:GOOGLE_APPLICATION_CREDENTIALS="D:/Project_Unthinkable/googlecreds/service_account.json"

5. Set up MySQL database
   CREATE DATABASE meeting_app;
   USE meeting_app;

   CREATE TABLE meetings (
       id VARCHAR(255) PRIMARY KEY,
       filename VARCHAR(255),
       transcript LONGTEXT,
       summary LONGTEXT,
       key_points LONGTEXT,
       action_points LONGTEXT,
       meeting_date DATE,
       start_time TIME,
       end_time TIME
   );

6. Configure database credentials in backend/database.py:
   DB_CONFIG = {
       "host": "localhost",
       "user": "your_mysql_username",
       "password": "your_mysql_password",
       "database": "meeting_app"
   }

Running the Application:

1. Start the FastAPI backend
   uvicorn backend.api_server:app --reload

2. Open the frontend
   - Open index.html in your browser
   - Upload an audio file and enter the number of speakers
   - Click Upload & Process to generate transcription and summary

Notes:
- Make sure your Google Cloud service account has Speech-to-Text API enabled
- Hugging Face summarization may take some time for long transcripts
- Default number of speakers is 2 if not specified
- If Key Points or Action Items are not found, the application will display:
  "No more points mentioned."

License:
MIT License © 2025
