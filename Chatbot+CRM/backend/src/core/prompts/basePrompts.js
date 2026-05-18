export function buildPrompt({ message, history, module = "general-chatbot", crmContext = null }) {
  if (module === "crm" && crmContext) {
    return {
      systemMessage: [
        "You are a CRM assistant connected to live in-memory CRM data from this application.",
        "Answer using only the CRM context provided below.",
        "If the answer is not present in the CRM context, say that the current CRM dataset does not contain it.",
        "Be concise and concrete. Mention counts and trends when relevant.",
        `CRM context: ${JSON.stringify(crmContext)}`
      ].join(" "),
      userMessage: message,
      history
    };
  }

  return {
    systemMessage: "You are a general-purpose chatbot assistant.",
    userMessage: message,
    history
  };
}
