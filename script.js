const chatArea = document.getElementById("chat-area");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");

function addMessage(from, text) {
  const msgDiv = document.createElement("div");
  msgDiv.textContent = text;
  msgDiv.classList.add("message");
  msgDiv.classList.add(from === "user" ? "user-message" : "bot-message");
  chatArea.appendChild(msgDiv);
  chatArea.scrollTop = chatArea.scrollHeight;
}

// Initial greeting from bot
addMessage("bot", "Hello! How can I assist you with H2flow Controls today?");

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;
  addMessage("user", text);
  userInput.value = "";

  try {
    const response = await fetch("https://your-render-backend-url/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    if (!response.ok) {
      addMessage("bot", "Sorry, something went wrong. Please try again.");
      return;
    }
    const data = await response.json();
    addMessage("bot", data.reply);
  } catch (err) {
    addMessage("bot", "Network error. Please check your connection.");
  }
}

sendButton.addEventListener("click", sendMessage);
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
