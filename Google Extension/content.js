let lastSong = "";
let songCounter = 0;
let songThreshold = 3;
let selectedFile = "";

// Load initial values from Chrome storage
chrome.storage.sync.get(['songThreshold', 'selectedFile'], (data) => {
  songThreshold = data.songThreshold || 3;
  selectedFile = data.selectedFile || "";
});

// Listen for updates from the popup
chrome.storage.onChanged.addListener((changes) => {
  if (changes.songThreshold?.newValue) {
    songThreshold = changes.songThreshold.newValue;
    console.log(`Updated song threshold to ${songThreshold}`);
  }
  if (changes.selectedFile?.newValue) {
    selectedFile = changes.selectedFile.newValue;
    console.log(`Updated selected file to ${selectedFile}`);
  }
});

// Monitor currently playing song
function trackSong() {
  const songNameEl = document.querySelector('[data-testid="nowplaying-track-link"]');
  const currentSong = songNameEl?.textContent;

  if (currentSong && currentSong !== lastSong) {
    lastSong = currentSong;
    songCounter++;
    console.log(`Now playing: ${currentSong} (${songCounter}/${songThreshold})`);

    if (songCounter >= songThreshold) {
      songCounter = 0;
      injectAudioFromBackend();
    }
  }
}

setInterval(trackSong, 2000);

// Fetch signed URL and inject audio
async function injectAudioFromBackend() {
  if (!selectedFile) {
    console.warn("No audio file selected.");
    return;
  }

  try {
    const res = await fetch(`https://personaldj.onrender.com/api/voice-lines/${selectedFile}/url`);
    const json = await res.json();
    const audioUrl = json.url;

    const audio = new Audio(audioUrl);
    audio.volume = 1;
    audio.play();

    // Pause Spotify
    document.querySelector('[data-testid="control-button-pause"]')?.click();

    audio.onended = () => {
      // Resume Spotify
      document.querySelector('[data-testid="control-button-play"]')?.click();
    };
  } catch (err) {
    console.error("Error injecting audio:", err);
  }
}