import { chatbotService } from "./chatbot.service.js";

export async function sendMessage(request, response) {
  const { message, sessionId = "guest-session" } = request.body;

  if (!message || !message.trim()) {
    response.status(400).json({ error: "Message is required." });
    return;
  }

  try {
    const result = await chatbotService.respond({ message, sessionId });
    response.json(result);
  } catch (error) {
    response.status(500).json({
      error: error.message || "Failed to generate a chatbot response."
    });
  }
}
