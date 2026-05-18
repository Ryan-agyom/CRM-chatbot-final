import { buildPrompt } from "../prompts/basePrompts.js";
import { aiProvider } from "../ai/provider.js";
import { sessionService } from "../sessions/session.service.js";
import { memoryService } from "../memory/memory.service.js";
import { routeConversation } from "../orchestration/router.js";
import { analyticsCRMService } from "../../crm/services/analyticsCRM.service.js";
import { crmRepository } from "../../crm/repositories/crm.repository.js";

function formatList(values) {
  return values.length ? values.join(", ") : "none";
}

function isCRMSummaryQuestion(message) {
  const normalizedMessage = message.toLowerCase();

  return [
    "summarize",
    "summary",
    "overview",
    "current crm",
    "how many leads",
    "how many campaigns",
    "how many support tickets",
    "obvious trends"
  ].some((term) => normalizedMessage.includes(term));
}

function buildCRMContext() {
  const leads = crmRepository.list("leads");
  const campaigns = crmRepository.list("campaigns");
  const tickets = crmRepository.list("tickets");

  return {
    counts: {
      leads: leads.length,
      campaigns: campaigns.length,
      tickets: tickets.length
    },
    insights: analyticsCRMService.getInsights(),
    samples: {
      leads: leads.slice(0, 3),
      campaigns: campaigns.slice(0, 3),
      tickets: tickets.slice(0, 3)
    }
  };
}

function buildCRMSummaryReply() {
  const leads = crmRepository.list("leads");
  const campaigns = crmRepository.list("campaigns");
  const tickets = crmRepository.list("tickets");
  const insights = analyticsCRMService.getInsights();

  const leadNames = leads.slice(0, 5).map((lead) => `${lead.name} (${lead.source})`);
  const campaignNames = campaigns.slice(0, 5).map((campaign) => `${campaign.name} [${campaign.segment}]`);
  const ticketSamples = tickets
    .slice(0, 5)
    .map((ticket) => `${ticket.customerName}: ${ticket.issue} (${ticket.department}, ${ticket.language})`);

  return [
    "CRM Summary",
    "",
    `Counts: ${leads.length} leads, ${campaigns.length} campaigns, ${tickets.length} support tickets.`,
    "",
    `Lead examples: ${formatList(leadNames)}.`,
    `Campaign examples: ${formatList(campaignNames)}.`,
    `Ticket examples: ${formatList(ticketSamples)}.`,
    "",
    "Insights:",
    `Common complaints: ${formatList(insights.customerInsights.commonComplaints.slice(0, 6))}.`,
    `Likely conversions: ${insights.predictiveAnalysis.likelyToConvert} leads currently look ready based on the seeded dataset.`,
    `Churn risk: ${insights.predictiveAnalysis.likelyToChurn}.`,
    `Trending products: ${formatList(insights.predictiveAnalysis.trendingProducts)}.`
  ].join("\n");
}

export const chatbotService = {
  async respond({ message, sessionId }) {
    const history = sessionService.getHistory(sessionId);
    const module = routeConversation(message);
    let reply;

    if (module === "crm" && isCRMSummaryQuestion(message)) {
      reply = buildCRMSummaryReply();
    } else {
      const prompt = buildPrompt({
        message,
        history,
        module,
        crmContext: module === "crm" ? buildCRMContext() : null
      });
      reply = await aiProvider.generateReply(prompt);
    }

    sessionService.appendMessage(sessionId, { role: "user", content: message });
    sessionService.appendMessage(sessionId, { role: "assistant", content: reply });
    memoryService.remember(sessionId, { lastIntent: module });

    return {
      sessionId,
      reply
    };
  }
};
