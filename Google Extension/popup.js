document.addEventListener('DOMContentLoaded', async () => {
    console.log("📦 Popup loaded");
  
    const input = document.getElementById('songCount');
    const select = document.getElementById('audioSelect');
    const saveBtn = document.getElementById('save');
  
    // Load current settings
    chrome.storage.sync.get(['songThreshold', 'selectedFile'], (data) => {
      console.log("📥 Loaded settings from chrome.storage:", data);
      input.value = data.songThreshold || 3;
    });
  
    // Fetch audio file list from your Flask backend
    try {
      console.log("🌐 Fetching audio file list...");
      const response = await fetch("https://personaldj.onrender.com/api/voice-lines");
      const files = await response.json();
      console.log("📄 Files fetched:", files);
  
      // Populate dropdown
      for (const name of files) {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = decodeURIComponent(name.replace(/\+/g, " "));
        select.appendChild(option);
      }
  
      // Set selected file if saved previously
      chrome.storage.sync.get(['selectedFile'], (data) => {
        console.log("🎵 Selected file in storage:", data.selectedFile);
        if (data.selectedFile) {
          select.value = data.selectedFile;
        }
      });
  
    } catch (err) {
      console.error("❌ Failed to fetch audio file list:", err);
      const errorOption = document.createElement('option');
      errorOption.textContent = "Error loading files";
      errorOption.disabled = true;
      select.appendChild(errorOption);
    }
  
    // Save settings
    saveBtn.addEventListener('click', () => {
      const value = parseInt(input.value, 10);
      const selectedFile = select.value;
      console.log("💾 Saving settings:", { songThreshold: value, selectedFile });
  
      chrome.storage.sync.set({
        songThreshold: value,
        selectedFile: selectedFile
      }, () => {
        alert('Saved!');
        console.log("✅ Settings saved.");
      });
    });
  });