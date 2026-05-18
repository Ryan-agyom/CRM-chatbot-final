import { crmRepository } from "../repositories/crm.repository.js";

export const supportCRMService = {
  createTicket(payload) {
    return crmRepository.create("tickets", {
      customerName: payload.customerName,
      issue: payload.issue,
      department: payload.department || "support",
      language: payload.language || "en",
      conversationHistory: payload.conversationHistory || []
    });
  },
  suggestResolution(issueType) {
    const playbooks = {
      order_status: "Check shipment tracking and latest dispatch event.",
      refund: "Verify payment state and refund policy eligibility.",
      technical: "Run guided troubleshooting and send FAQ article."
    };

    return playbooks[issueType] || "Escalate to a live support agent.";
  }
};
