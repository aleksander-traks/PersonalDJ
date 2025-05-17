let lastSeenTime = "";
let songCounter = 0;

console.log("🎧 content.js loaded");

// Helper: Pause/resume Spotify
function pauseSpotify() {
  const pauseBtn = document.querySelector('button[aria-label="Pause"]');
  if (pauseBtn) {
    pauseBtn.click();
    console.log("⏸️ Paused Spotify");
  } else {
    console.warn("⚠️ Pause button not found");
  }
}

function resumeSpotify() {
  const playBtn = document.querySelector('button[aria-label="Play"]');
  if (playBtn) {
    playBtn.click();
    console.log("▶️ Resumed Spotify");
  } else {
    console.warn("⚠️ Play button not found");
  }
}

// Core logic: Check and inject if threshold met
function checkAndInject() {
  chrome.storage.sync.get(['selectedFile', 'songThreshold'], (data) => {
    const threshold = parseInt(data.songThreshold) || 3;
    const selectedFile = data.selectedFile;

    console.log("🧠 Threshold:", threshold, "| File:", selectedFile);

    if (!selectedFile) {
      console.warn("⚠️ No audio file selected.");
      return;
    }

    if (songCounter >= threshold) {
      console.log("🚨 Threshold reached. Injecting audio...");
      songCounter = 0;
      injectAudioFromBackend(selectedFile);
    }
  });
}

// Inject and play audio using signed Supabase URL
async function injectAudioFromBackend(filename) {
  try {
    pauseSpotify();
    await new Promise(resolve => setTimeout(resolve, 300));

    const res = await fetch(`https://personaldj.onrender.com/api/voice-lines/${encodeURIComponent(filename)}/url`);
    const { url } = await res.json();
    console.log("🔗 Audio URL fetched:", url);

    const audio = new Audio(url);
    audio.play();
    console.log("▶️ Audio playing");

    audio.onended = () => {
      console.log("✅ Audio finished");
      resumeSpotify();
    };

    audio.onerror = (e) => {
      console.error("❌ Audio error:", e);
      resumeSpotify();
    };
  } catch (err) {
    console.error("❌ Failed to fetch/play audio:", err);
    resumeSpotify();
  }
}

(function watchNowPlayingContainer() {
  const container = document.querySelector('[data-testid="now-playing-widget"]');

  if (!container) {
    console.warn("⚠️ Now playing widget not found. Retrying...");
    setTimeout(watchNowPlayingContainer, 1000);
    return;
  }

  const getTitle = () => {
    const titleEl = container.querySelector('[data-testid="context-item-info-title"]');
    return titleEl?.textContent?.trim() || null;
  };

  window._lastTrackTitle = getTitle();

  const observer = new MutationObserver(() => {
    const newTitle = getTitle();
    if (newTitle && newTitle !== window._lastTrackTitle) {
      console.log("🎵 Song changed to:", newTitle);
      window._lastTrackTitle = newTitle;

      songCounter++;
      checkAndInject();
    }
  });

  observer.observe(container, { childList: true, subtree: true });
  console.log("👁️ Now watching container for song changes:", window._lastTrackTitle);
})();