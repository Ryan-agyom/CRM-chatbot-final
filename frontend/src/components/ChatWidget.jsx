import React, { useState } from "react";
import { sendChatMessage } from "../services/chatService.js";

export default function ChatWidget() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("Ask the assistant something to test the general chatbot flow.");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!message.trim()) {
      return;
    }

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
    <section className="card chatbot-panel" id="chat-widget">
      <div className="panel-header">
        <div>
          <h2>Live Chat Assistant</h2>
          <p>Ask anything and get instant responses from the chatbot demo.</p>
        </div>
        <span className="status-badge">Live Demo</span>
      </div>

      <form onSubmit={handleSubmit} className="chat-form">
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask a question or describe a task"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !message.trim()}>
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>

      <div className="response-box" aria-live="polite">{reply}</div>
      <p className="hint">Try: “Suggest a follow-up email for a new lead.”</p>
    </section>
  );
}
