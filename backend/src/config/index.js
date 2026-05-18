import dotenv from "dotenv";

dotenv.config({ path: new URL("../../../.env", import.meta.url) });
dotenv.config({ path: new URL("../../.env", import.meta.url), override: true });

export const config = {
  port: process.env.PORT || 5000,
  frontendUrl: process.env.FRONTEND_URL || "http://localhost:5173",
  aiProvider: process.env.AI_PROVIDER || "openai",
  openaiApiKey: process.env.OPENAI_API_KEY || "",
  openaiModel: process.env.OPENAI_MODEL || "gpt-5.4-mini",
  openaiApiBaseUrl: process.env.OPENAI_API_BASE_URL || "https://api.openai.com/v1",
  geminiApiKey: process.env.GEMINI_API_KEY || "",
  geminiModel: process.env.GEMINI_MODEL || "gemini-2.5-flash",
  geminiApiBaseUrl: process.env.GEMINI_API_BASE_URL || "https://generativelanguage.googleapis.com/v1beta"
};
