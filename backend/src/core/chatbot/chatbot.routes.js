import { Router } from "express";
import { sendMessage } from "./chatbot.controller.js";

const router = Router();

router.post("/", sendMessage);

export { router as chatbotRouter };
