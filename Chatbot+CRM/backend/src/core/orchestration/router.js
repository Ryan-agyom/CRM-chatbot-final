export function routeConversation(message) {
  if (message.toLowerCase().includes("crm")) {
    return "crm";
  }

  return "general-chatbot";
}
