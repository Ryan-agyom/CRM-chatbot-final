export function createTicketModel(data) {
  return {
    id: data.id,
    customerName: data.customerName,
    issue: data.issue,
    department: data.department,
    language: data.language,
    conversationHistory: data.conversationHistory,
    createdAt: data.createdAt
  };
}
