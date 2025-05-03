
// 🔁 Set button state: charging → loading → done
function setButtonState(button, state) {
  button.classList.remove("charging", "loading", "done");
  if (state) {
    button.classList.add(state);
  }
}

// 🛡️ Generate Line using ChatGPT
async function generateRadioLine() {
  const hostSelect = document.getElementById("host-select");
  const topicSelect = document.getElementById("topic-select");
  const outputTextarea = document.getElementById("generated-line");
  const generateBtn = document.getElementById("generate-line-btn");

  const selectedHostName = hostSelect.options[hostSelect.selectedIndex].text;
  const selectedTopic = topicSelect.value;

  if (!selectedHostName || !selectedTopic) {
    alert("Please select both a Radio Host and a Topic!");
    return;
  }

  const host = hosts.find(h => h.name === selectedHostName);

  if (!host) {
    alert(`Selected host '${selectedHostName}' not found!`);
    return;
  }

  if (!host.description) {
    alert(`Host '${selectedHostName}' has no description set!`);
    return;
  }

  try {
    setButtonState(generateBtn, "charging");
    setTimeout(() => setButtonState(generateBtn, "loading"), 500);

    const response = await fetch("/api/chatgpt/generate-line", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic: selectedTopic,
        host_description: host.description
      })
    });

    const data = await response.json();

    if (data.error) {
      outputTextarea.value = "Error generating line.";
      setButtonState(generateBtn, null);
    } else {
      outputTextarea.value = data.line;
      setButtonState(generateBtn, "done");
    }
  } catch (error) {
    console.error("Error generating line:", error);
    outputTextarea.value = "Failed to generate.";
    setButtonState(generateBtn, null);
  }
}

// 🛡️ Voice Over Line using ElevenLabs
async function generateVoiceLine() {
  const hostSelect = document.getElementById("host-select");
  const topicSelect = document.getElementById("topic-select");
  const outputTextarea = document.getElementById("generated-line");
  const introSelect = document.getElementById("intro-select");
  const voiceBtn = document.getElementById("generate-voice-btn");

  const selectedHostId = hostSelect.value;
  const selectedTopic = topicSelect.value;
  const selectedIntro = introSelect ? introSelect.value : null;
  const selectedHost = hosts.find(h => h.voice_id === selectedHostId);

  if (!selectedHostId || !selectedTopic || !selectedHost) {
    alert("Please select both a host and a topic.");
    return;
  }

  const generatedLine = outputTextarea.value.trim();

  if (!generatedLine) {
    alert("Generated line is empty! Please generate or edit a line first.");
    return;
  }

  console.log("▶️ Sending audio generation request with:", {
    voice_id: selectedHostId,
    host_name: selectedHost.name,
    topic_name: selectedTopic,
    text: generatedLine,
    music_intro: selectedIntro
  });

  try {
    setButtonState(voiceBtn, "charging");
    setTimeout(() => setButtonState(voiceBtn, "loading"), 500);

    const ttsResponse = await fetch("/api/elevenlabs/generate-audio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        voice_id: selectedHostId,
        host_name: selectedHost.name,
        topic_name: selectedTopic,
        text: generatedLine,
        music_intro: selectedIntro
      })
    });

    const ttsData = await ttsResponse.json();

    if (ttsData.error) {
      alert("Failed to generate audio.");
      setButtonState(voiceBtn, null);
    } else {
      console.log("Audio URL:", ttsData.audio_url);

      const audioPlayer = document.getElementById("main-audio-player");
      if (audioPlayer) {
        audioPlayer.src = ttsData.audio_url;
        audioPlayer.play();
      }

      const downloadLink = document.getElementById("download-link");
      if (downloadLink) {
        downloadLink.href = ttsData.audio_url;
        downloadLink.download = ttsData.audio_url.split("/").pop();
        downloadLink.style.display = "inline-block";
      }

      // ✅ Real-time DOM update
      const filename = ttsData.audio_url.split("/").pop();
      if (typeof addGeneratedLine === "function") {
        addGeneratedLine(selectedHost.name, selectedTopic, ttsData.audio_url, filename);
      }

      setButtonState(voiceBtn, "done");
    }
  } catch (error) {
    console.error("Error generating voice line:", error);
    alert("Failed to generate voice line due to an error.");
    setButtonState(voiceBtn, null);
  }
}

// ✅ NEW: Load intro music options on page load
document.addEventListener("DOMContentLoaded", () => {
  const introSelect = document.getElementById("intro-select");
  if (!introSelect) return;

  fetch("/api/music-intros")
    .then(res => res.json())
    .then(data => {
      data.intros.forEach(intro => {
        const opt = document.createElement("option");
        opt.value = intro;
        opt.textContent = intro;
        introSelect.appendChild(opt);
      });
    })
    .catch(err => console.error("Failed to load intros:", err));
});
