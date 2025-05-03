const generatedLines = []; // Store voice lines

// 🛡️ Load existing voice lines from server
async function loadGeneratedVoiceLines() {
  try {
    const response = await fetch("/api/voice-lines");
    const data = await response.json();

    if (!Array.isArray(data)) {
      console.error("Voice lines response is not an array:", data);
      return;
    }

    data.forEach((filename) => {
      const parts = filename.split("+");
      const hostName = parts[0] || "Unknown Host";
      const topicName = parts[1] || "Unknown Topic";

      const audioUrl = `/static/audio/${filename}`; // fallback path
      addGeneratedLine(hostName, topicName, audioUrl, filename);
    });
  } catch (err) {
    console.error("Failed to load voice lines:", err);
  }
}

// 🛡️ Add a new voice line visually
function addGeneratedLine(hostName, topicName, audioUrl, filename) {
  const container = document.getElementById("generated-lines");

  const index = generatedLines.length;
  const title = `${hostName} + ${topicName}`;

  const lineElement = document.createElement("div");
  lineElement.className = "generated-line";
  lineElement.id = `generated-line-${index}`;

  lineElement.innerHTML = `
    <span>${title}</span>
    <div class="button-group">
      <button onclick="playGeneratedLine('${audioUrl}', '${title}')">▶️</button>
      <a href="${audioUrl}" download class="download-btn">⬇️</a>
      <button onclick="deleteGeneratedLine('${filename}', ${index})" class="delete-btn">🗑️</button>
    </div>
  `;

  container.appendChild(lineElement);

  generatedLines.push({
    title: title,
    url: audioUrl,
    filename: filename,
    elementId: `generated-line-${index}`
  });
}

// 🛡️ Play a voice line
function playGeneratedLine(audioUrl, title) {
  const audioPlayer = document.getElementById("main-audio-player");
  const nowPlayingText = document.getElementById("now-playing-text");

  if (audioPlayer) {
    audioPlayer.src = audioUrl;
    audioPlayer.play();
  }
  if (nowPlayingText) {
    nowPlayingText.innerText = `🎵 Now Playing: ${title}`;
  }
}

// 🛡️ Delete a voice line visually (and later server)
function deleteGeneratedLine(filename, index) {
  const confirmDelete = confirm(`Are you sure you want to delete ${filename}?`);
  if (!confirmDelete) return;

  // 1. Remove from DOM
  const lineInfo = generatedLines[index];
  if (lineInfo) {
    const lineElement = document.getElementById(lineInfo.elementId);
    if (lineElement) {
      lineElement.remove();
    }
    generatedLines[index] = null;
  }

  // 2. Future: Actually send DELETE request to Flask
  // fetch(`/api/voice-lines/${filename}`, { method: 'DELETE' });
}

// 🛡️ When page loads, load all saved voice lines
document.addEventListener('DOMContentLoaded', function () {
  loadGeneratedVoiceLines();
});