from transformers import pipeline
import json

def summarize_meeting(transcript: str):
    """
    Summarizes the meeting transcript into summary, key points, and action items.
    Returns a dict with keys: summary, key_points, action_points.
    """
    print(" Initializing summarization model...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    # Break large transcripts into chunks
    max_chunk_size = 2000
    chunks = [transcript[i:i + max_chunk_size] for i in range(0, len(transcript), max_chunk_size)]

    print(f" Summarizing transcript in {len(chunks)} chunks...")
    summaries = []
    for idx, chunk in enumerate(chunks, 1):
        print(f"Summarizing chunk {idx}/{len(chunks)}...")
        result = summarizer(
            chunk,
            max_length=200,
            min_length=50,
            do_sample=False
        )[0]['summary_text']
        summaries.append(result)

    combined_summary = " ".join(summaries)

    # Prompt-based extraction
    prompt_text = f"""
    Extract key points and action items from the following meeting summary.
    - If no key points are mentioned, return 'No key points mentioned'.
    - If no action items are mentioned, return 'No action points mentioned'.
    - Return JSON in this format:
    {{
        "summary": "...",
        "key_points": [...],
        "action_points": [...]
    }}
    Meeting summary: {combined_summary}
    """

    # Use summarizer again to generate structured output
    try:
        structured_text = summarizer(prompt_text, max_length=300)[0]['summary_text']

        # Attempt to parse as JSON
        structured_output = json.loads(structured_text)
    except Exception as e:
        print(f"Could not parse structured output: {e}")
        # Fallback
        structured_output = {
            "summary": combined_summary.strip(),
            "key_points": ["No key points mentioned"],
            "action_points": ["No action points mentioned"]
        }

    return structured_output
