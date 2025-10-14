document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "http://127.0.0.1:8000/upload";

    // Get all DOM elements
    const uploadBtn = document.getElementById("uploadBtn");
    const audioFileInput = document.getElementById("audioFile");
    const numSpeakersInput = document.getElementById("numSpeakers");
    const statusEl = document.getElementById("status");
    const loader = document.getElementById("loader");
    const resultsDiv = document.getElementById("results");

    // Add event listener for the upload button
    uploadBtn.addEventListener("click", async () => {
        const file = audioFileInput.files[0];
        const numSpeakers = parseInt(numSpeakersInput.value);

        if (!file) {
            alert("Please select an audio file first.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("num_speakers", numSpeakers);

        // Show loader and disable button
        loader.classList.remove("hidden");
        uploadBtn.disabled = true;
        statusEl.textContent = "";
        resultsDiv.classList.add("hidden");

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "An error occurred while processing the audio.");
            }

            const data = await response.json();
            populateResults(data);
            resultsDiv.classList.remove("hidden");
            statusEl.textContent = "Processing complete! ✅";

        } catch (error) {
            statusEl.textContent = "";
            alert(`Error: ${error.message}`);
        } finally {
            // Hide loader and re-enable button
            loader.classList.add("hidden");
            uploadBtn.disabled = false;
        }
    });

    function populateResults(data) {
        // Update Meeting Info
        document.getElementById("date").textContent = `Date: ${data.meeting_date}`;
        document.getElementById("start").textContent = `Start Time: ${data.start_time}`;
        document.getElementById("end").textContent = `End Time: ${data.end_time}`;

        // Update Textareas
        const summaryText = data.summary;
        const keyPointsText = data.key_points.join("\n- ");
        const actionPointsText = data.action_points.join("\n- ");
        const transcriptText = data.transcript;

        document.getElementById("summary").value = summaryText;
        document.getElementById("keyPoints").value = `- ${keyPointsText}`;
        document.getElementById("actionPoints").value = `- ${actionPointsText}`;
        document.getElementById("transcript").value = transcriptText;

        // Setup Download Buttons
        setupDownload("downloadSummary", "meeting_summary.txt", summaryText);
        setupDownload("downloadKeyPoints", "key_points.txt", `- ${keyPointsText}`);
        setupDownload("downloadActionPoints", "action_points.txt", `- ${actionPointsText}`);
        setupDownload("downloadTranscript", "meeting_transcript.txt", transcriptText);
    }

    function setupDownload(buttonId, fileName, content) {
        const button = document.getElementById(buttonId);
        button.onclick = () => {
            const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = fileName;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        };
    }
});