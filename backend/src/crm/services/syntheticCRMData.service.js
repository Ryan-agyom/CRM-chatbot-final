import { crmRepository } from "../repositories/crm.repository.js";

const firstNames = ["Ava", "Liam", "Noah", "Emma", "Mia", "Arjun", "Isha", "Sofia", "Ethan", "Zara"];
const lastNames = ["Sharma", "Patel", "Johnson", "Brown", "Martinez", "Singh", "Wilson", "Clark", "Taylor", "Gupta"];
const leadSources = ["chatbot", "website", "facebook-ads", "google-ads", "referral", "webinar"];
const industries = ["retail", "healthcare", "education", "real-estate", "finance", "ecommerce"];
const campaignSegments = ["new-users", "inactive-users", "high-value", "repeat-buyers", "trial-users"];
const campaignTriggers = ["manual", "signup", "abandoned-cart", "festival-offer", "win-back"];
const ticketIssues = ["refund request", "order delayed", "payment failed", "account access", "technical bug", "pricing question"];
const departments = ["support", "billing", "sales", "technical"];
const languages = ["en", "hi", "es"];

function pick(list, index) {
  return list[index % list.length];
}

function buildLead(index) {
  const firstName = pick(firstNames, index);
  const lastName = pick(lastNames, index + 3);
  const company = `${pick(industries, index)}-group-${index + 1}`;

  return {
    name: `${firstName} ${lastName}`,
    email: `${firstName}.${lastName}.${index + 1}@examplecrm.test`.toLowerCase(),
    phone: `+1-555-01${String(index + 10).padStart(2, "0")}`,
    requirements: `Interested in ${company} onboarding for chatbot automation and CRM workflow setup.`,
    source: pick(leadSources, index),
    company,
    budget: 1000 + index * 750,
    interestLevel: ["low", "medium", "high"][index % 3]
  };
}

function buildCampaign(index) {
  return {
    name: `Campaign ${index + 1}`,
    segment: pick(campaignSegments, index),
    message: `Hello from campaign ${index + 1}. We have an offer tailored for ${pick(campaignSegments, index)} customers.`,
    trigger: pick(campaignTriggers, index)
  };
}

function buildTicket(index) {
  const firstName = pick(firstNames, index + 2);
  const lastName = pick(lastNames, index + 5);
  const issue = pick(ticketIssues, index);

  return {
    customerName: `${firstName} ${lastName}`,
    issue,
    department: pick(departments, index),
    language: pick(languages, index),
    conversationHistory: [
      { role: "user", content: `I need help with ${issue}.` },
      { role: "assistant", content: "I can help with that. Let me collect a few details first." }
    ]
  };
}

function createSyntheticDataset({ leads = 25, campaigns = 10, tickets = 15 } = {}) {
  return {
    leads: Array.from({ length: leads }, (_unused, index) => buildLead(index)),
    campaigns: Array.from({ length: campaigns }, (_unused, index) => buildCampaign(index)),
    tickets: Array.from({ length: tickets }, (_unused, index) => buildTicket(index))
  };
}

export const syntheticCRMDataService = {
  preview(counts) {
    return createSyntheticDataset(counts);
  },
  seed(counts = {}) {
    const dataset = createSyntheticDataset(counts);

    const seededLeads = crmRepository.replace("leads", dataset.leads);
    const seededCampaigns = crmRepository.replace("campaigns", dataset.campaigns);
    const seededTickets = crmRepository.replace("tickets", dataset.tickets);

    return {
      counts: {
        leads: seededLeads.length,
        campaigns: seededCampaigns.length,
        tickets: seededTickets.length
      },
      sample: {
        lead: seededLeads[0] || null,
        campaign: seededCampaigns[0] || null,
        ticket: seededTickets[0] || null
      }
    };
  }
};
