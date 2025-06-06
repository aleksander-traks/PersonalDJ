const hosts = []; // 🛡️ GLOBAL array to store loaded hosts

// 🔁 Set button state for loaders
function setButtonState(button, state) {
  button.classList.remove("charging", "loading", "done");
  if (state) {
    button.classList.add(state);
  }
}

// Load hosts into memory and update both the host list and dropdown
async function loadHosts() {
  const response = await fetch("/api/hosts");
  const loadedHosts = await response.json();

  hosts.length = 0;
  hosts.push(...loadedHosts);

  const hostList = document.querySelector(".host-list");
  hostList.innerHTML = "";

  loadedHosts.forEach(host => {
    const item = document.createElement("div");
    item.className = "list-item";
    item.innerHTML = `
      ${host.name}
      <button class="small-btn" onclick="deleteHost('${host.voice_id}')">❌</button>
    `;
    hostList.appendChild(item);
  });

  const select = document.getElementById("host-select");
  select.innerHTML = "";

  loadedHosts.forEach(host => {
    const option = document.createElement("option");
    option.value = host.voice_id;
    option.textContent = host.name;
    select.appendChild(option);
  });
}

// Add a new host
async function addHost() {
  const input = document.querySelector("#new-host-name");
  const description = document.querySelector("#new-host-description");
  const addBtn = document.querySelector("button[onclick='addHost()']");

  if (!input.value.trim() || !description.value.trim()) {
    alert("Please enter both a host name and description.");
    return;
  }

  try {
    setButtonState(addBtn, "charging");
    setTimeout(() => setButtonState(addBtn, "loading"), 500);

    const response = await fetch("/api/hosts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: input.value.trim(),
        description: description.value.trim()
      })
    });

    if (response.ok) {
      alert("Host created!");
      input.value = "";
      description.value = "";
      setButtonState(addBtn, "done");
      await loadHosts();
    } else {
      alert("Failed to create host.");
      setButtonState(addBtn, null);
    }
  } catch (err) {
    console.error("Error adding host:", err);
    alert("Something went wrong.");
    setButtonState(addBtn, null);
  }
}

// Delete an existing host
async function deleteHost(voiceId) {
  if (!confirm("Are you sure you want to delete this voice?")) return;

  const response = await fetch(`/api/hosts/${voiceId}`, {
    method: "DELETE"
  });

  if (response.ok) {
    alert("Voice deleted successfully!");
    await loadHosts();
  } else {
    alert("Failed to delete voice.");
  }
}

// When the DOM is ready, load hosts immediately
document.addEventListener('DOMContentLoaded', function() {
  loadHosts();
});