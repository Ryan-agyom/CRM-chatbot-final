import { config } from "../../config/index.js";

function buildConversationInput(prompt) {
  const recentHistory = prompt.history.slice(-10).map((message) => ({
    role: message.role === "assistant" ? "assistant" : "user",
    content: message.content
  }));

  return [
    ...recentHistory,
    {
      role: "user",
      content: prompt.userMessage
    }
  ];
}

function extractOutputText(payload) {
  if (typeof payload.output_text === "string" && payload.output_text.trim()) {
    return payload.output_text.trim();
  }

  if (!Array.isArray(payload.output)) {
    return "";
  }

  for (const item of payload.output) {
    if (!Array.isArray(item.content)) {
      continue;
    }

    for (const contentItem of item.content) {
      if (typeof contentItem.text === "string" && contentItem.text.trim()) {
        return contentItem.text.trim();
      }
    }
  }

  return "";
}

function buildGeminiContents(prompt) {
  const historyContents = prompt.history.slice(-10).map((message) => ({
    role: message.role === "assistant" ? "model" : "user",
    parts: [{ text: message.content }]
  }));

  return [
    ...historyContents,
    {
      role: "user",
      parts: [{ text: prompt.userMessage }]
    }
  ];
}

function extractGeminiText(payload) {
  const candidates = payload?.candidates;

  if (!Array.isArray(candidates)) {
    return "";
  }

  for (const candidate of candidates) {
    const parts = candidate?.content?.parts;

    if (!Array.isArray(parts)) {
      continue;
    }

    for (const part of parts) {
      if (typeof part?.text === "string" && part.text.trim()) {
        return part.text.trim();
      }
    }
  }

  return "";
}

async function generateOpenAIReply(prompt) {
  if (!config.openaiApiKey) {
    throw new Error("OPENAI_API_KEY is missing. Add it to the repo root .env file before starting the backend.");
  }

  const response = await fetch(`${config.openaiApiBaseUrl}/responses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${config.openaiApiKey}`
    },
    body: JSON.stringify({
      model: config.openaiModel,
      instructions: prompt.systemMessage,
      input: buildConversationInput(prompt)
    })
  });

  const payload = await response.json();

  if (!response.ok) {
    const message = payload?.error?.message || "OpenAI request failed.";
    throw new Error(message);
  }

  const reply = extractOutputText(payload);

  if (!reply) {
    throw new Error("OpenAI returned an empty reply.");
  }

  return reply;
}

async function generateGeminiReply(prompt) {
  if (!config.geminiApiKey) {
    throw new Error("GEMINI_API_KEY is missing. Add it to the repo root .env file before starting the backend.");
  }

  const response = await fetch(
    `${config.geminiApiBaseUrl}/models/${config.geminiModel}:generateContent`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-goog-api-key": config.geminiApiKey
      },
      body: JSON.stringify({
        systemInstruction: {
          parts: [{ text: prompt.systemMessage }]
        },
        contents: buildGeminiContents(prompt)
      })
    }
  );

  const payload = await response.json();

  if (!response.ok) {
    const message = payload?.error?.message || "Gemini request failed.";
    throw new Error(message);
  }

  const reply = extractGeminiText(payload);

  if (!reply) {
    throw new Error("Gemini returned an empty reply.");
  }

  return reply;
}

export const aiProvider = {
  async generateReply(prompt) {
    if (config.aiProvider === "gemini") {
      return generateGeminiReply(prompt);
    }
    return generateOpenAIReply(prompt);
  }
};
