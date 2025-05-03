// In-memory array to store generated topics
const topics = [];

// Add a new topic
async function addTopic() {
  const topicInputField = document.getElementById("topic-input");
  const topicInput = topicInputField.value.trim();

  if (!topicInput) {
    alert("Please enter a topic!");
    return;
  }

  try {
    const response = await fetch("/api/chatgpt/generate-overview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic: topicInput })
    });

    const data = await response.json();

    if (data.error) {
      alert("Failed to generate overview: " + data.error);
      return;
    }

    const overview = data.overview;
    const newTopic = { topic: topicInput, overview };

    topics.push(newTopic);

    renderTopics();
    loadTopicsDropdown();

    topicInputField.value = ""; // Clear input field

  } catch (error) {
    console.error("Error generating overview:", error);
    alert("Something went wrong while adding the topic!");
  }
}

// Render the list of topics on the page
function renderTopics() {
  const topicList = document.querySelector(".topic-list");
  topicList.innerHTML = "";

  if (topics.length === 0) {
    const emptyMessage = document.createElement("div");
    emptyMessage.className = "list-item";
    emptyMessage.textContent = "No topics available.";
    topicList.appendChild(emptyMessage);
    return;
  }

  topics.forEach((t, index) => {
    const item = document.createElement("div");
    item.className = "list-item";
    item.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span><strong>${t.topic}</strong></span>
        <button class="small-btn" onclick="deleteTopic(${index})">❌</button>
      </div>
    `;
    topicList.appendChild(item);
  });
}

// Delete a topic
async function deleteTopic(index) {
  const topicToDelete = topics[index];

  if (!confirm(`Are you sure you want to delete "${topicToDelete.topic}"?`)) {
    return;
  }

  try {
    const response = await fetch(`/api/topics/${encodeURIComponent(topicToDelete.topic)}`, {
      method: "DELETE"
    });

    if (response.ok) {
      topics.splice(index, 1); // Remove from local array
      renderTopics();
      loadTopicsDropdown();
    } else {
      alert("Failed to delete topic from server.");
    }
  } catch (error) {
    console.error("Error deleting topic:", error);
    alert("Something went wrong while deleting!");
  }
}

// Load topics from the backend into frontend memory
async function loadTopics() {
  try {
    const response = await fetch("/api/topics");
    const savedTopics = await response.json();

    topics.length = 0; // Clear
    topics.push(...savedTopics); // Load

    renderTopics();
  } catch (error) {
    console.error("Failed to load topics:", error);
  }
}

// Load topics into the select dropdown
async function loadTopicsDropdown() {
  const select = document.getElementById("topic-select");

  try {
    const response = await fetch("/api/topics");
    const savedTopics = await response.json();

    select.innerHTML = ""; // Clear previous

    if (savedTopics.length === 0) {
      const emptyOption = document.createElement("option");
      emptyOption.textContent = "No topics available yet.";
      select.appendChild(emptyOption);
      return;
    }

    savedTopics.forEach(t => {
      const option = document.createElement("option");
      option.value = t.topic;
      option.textContent = t.topic;
      select.appendChild(option);
    });

  } catch (error) {
    console.error("Failed to load topics dropdown:", error);
    select.innerHTML = "<option>Error loading topics</option>";
  }
}

// On page load, fetch everything
window.addEventListener("DOMContentLoaded", () => {
  loadTopics();
  loadTopicsDropdown();
});

