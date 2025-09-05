const chatArea = document.getElementById("chat-area");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

// Create and open WebSocket connection
const ws = new WebSocket("wss://h2flow.onrender.com/ws/chat");

ws.onopen = () => {
  addMessage("bot", "Hello! How can I assist you with H2flow Controls today?");
};

ws.onmessage = (event) => {
  addMessage("bot", event.data);
};

ws.onerror = (error) => {
  addMessage("bot", "Network error. Please check your connection.");
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  addMessage("bot", "Connection closed.");
};

function addMessage(from, text) {
  const msgDiv = document.createElement("div");
  msgDiv.textContent = text;
  msgDiv.classList.add("message");
  msgDiv.classList.add(from === "user" ? "user-message" : "bot-message");
  chatArea.appendChild(msgDiv);
  chatArea.scrollTop = chatArea.scrollHeight;
}

sendButton.addEventListener("click", () => {
  const text = userInput.value.trim();
  if (!text) return;
  addMessage("user", text);
  ws.send(text);
  userInput.value = "";
});

userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendButton.click();
  }
});
