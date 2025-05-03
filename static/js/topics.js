let topics = [];

// Loader button utility
function setButtonState(button, state) {
  button.classList.remove("charging", "loading", "done");
  if (state) {
    button.classList.add(state);
  }
}

// Render topic list to the sidebar
function renderTopics() {
  const list = document.querySelector(".topic-list");
  if (!list) return;

  list.innerHTML = "";

  topics.forEach((item, index) => {
    const container = document.createElement("div");
    container.className = "list-item";
    container.textContent = item.topic;

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "small-btn";
    deleteBtn.textContent = "❌";
    deleteBtn.onclick = () => removeTopic(index);

    container.appendChild(deleteBtn);
    list.appendChild(container);
  });
}

// Remove topic and refresh UI + send API delete
async function removeTopic(index) {
  const topicToDelete = topics[index];
  if (!topicToDelete) return;

  try {
    const response = await fetch(`/api/topics/${encodeURIComponent(topicToDelete.topic)}`, {
      method: "DELETE"
    });

    const result = await response.json();

    if (result.success) {
      topics.splice(index, 1);
      renderTopics();
      loadTopicsDropdown();
    } else {
      alert("Failed to delete topic from server.");
    }
  } catch (err) {
    console.error("Failed to delete topic:", err);
    alert("Error deleting topic.");
  }
}

// Load topics into <select id="topic-select">
function loadTopicsDropdown() {
  const select = document.getElementById("topic-select");
  if (!select) return;

  select.innerHTML = "";
  topics.forEach(item => {
    const option = document.createElement("option");
    option.value = item.topic;
    option.textContent = item.topic;
    select.appendChild(option);
  });
}

// Add topic using API and support loader animation
async function addTopic() {
  const input = document.getElementById("topic-input");
  const addBtn = document.getElementById("add-topic-btn");
  const topicText = input.value.trim();

  if (!topicText) {
    alert("Please enter a topic!");
    return;
  }

  try {
    setButtonState(addBtn, "charging");
    setTimeout(() => setButtonState(addBtn, "loading"), 400);

    const response = await fetch("/api/chatgpt/generate-overview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic: topicText })
    });

    const data = await response.json();

    if (data.error || !data.overview) {
      alert("Failed to generate overview.");
      setButtonState(addBtn, null);
      return;
    }

    topics.push({ topic: topicText, overview: data.overview });
    renderTopics();
    loadTopicsDropdown();

    input.value = "";
    setButtonState(addBtn, "done");
  } catch (err) {
    console.error("Error adding topic:", err);
    alert("Something went wrong.");
    setButtonState(addBtn, null);
  }
}

// Load topics from backend JSON on page load
document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/topics")
    .then(res => res.json())
    .then(data => {
      topics = data;
      renderTopics();
      loadTopicsDropdown();
    })
    .catch(err => {
      console.error("Failed to load topics:", err);
      topics = [];
    });
});