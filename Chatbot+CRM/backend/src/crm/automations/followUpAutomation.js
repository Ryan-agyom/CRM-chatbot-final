export const followUpAutomation = {
  queueLeadFollowUp(lead) {
    return {
      leadId: lead.id,
      actions: [
        "Send reminder message",
        "Ask if the customer is still interested",
        "Share product offers and details"
      ]
    };
  }
};
