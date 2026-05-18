import React, { useState } from "react";
import { sendChatMessage } from "../services/chatService.js";

export default function ChatWidget() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("Ask the assistant something to test the general chatbot flow.");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setIsLoading(true);

    try {
      const response = await sendChatMessage(message);
      setReply(response.reply);
      setMessage("");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="card chatbot-panel">
      <h2>General Chatbot</h2>
      <p>This section is intentionally separate from CRM logic.</p>
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Type a message"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>
      <div className="response-box">{reply}</div>
    </section>
  );
}
