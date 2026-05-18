import express from "express";
import cors from "cors";
import { chatbotRouter } from "./core/chatbot/chatbot.routes.js";
import { crmRouter } from "./crm/routes/crm.routes.js";
import { requestLogger } from "./shared/middleware/requestLogger.js";
import { config } from "./config/index.js";

const app = express();

app.use(cors({ origin: config.frontendUrl }));
app.use(express.json());
app.use(requestLogger);

app.get("/api/health", (_request, response) => {
  response.json({
    status: "ok",
    modules: ["general-chatbot", "crm"]
  });
});

app.use("/api/chat", chatbotRouter);
app.use("/api/crm", crmRouter);

app.listen(config.port, () => {
  console.log(`Backend listening on http://localhost:${config.port}`);
});
