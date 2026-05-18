const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";
const SESSION_STORAGE_KEY = "chatbot-session-id";

function getSessionId() {
  const existingSessionId = window.localStorage.getItem(SESSION_STORAGE_KEY);

  if (existingSessionId) {
    return existingSessionId;
  }

  const nextSessionId = window.crypto.randomUUID();
  window.localStorage.setItem(SESSION_STORAGE_KEY, nextSessionId);
  return nextSessionId;
}

export async function sendChatMessage(message) {
  if (!message.trim()) {
    return { reply: "Please enter a message first." };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        sessionId: getSessionId()
      })
    });

    if (!response.ok) {
      const payload = await response.json();
      throw new Error(payload.error || "The chatbot request failed.");
    }

    return response.json();
  } catch (error) {
    return {
      reply: error.message || "The backend is not reachable right now."
    };
  }
}
