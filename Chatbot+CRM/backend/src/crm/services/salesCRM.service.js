import { crmRepository } from "../repositories/crm.repository.js";
import { scoreLead } from "../utils/leadScoring.js";
import { followUpAutomation } from "../automations/followUpAutomation.js";
import { calendarIntegration } from "../integrations/calendar.integration.js";

export const salesCRMService = {
  captureLead(payload) {
    const lead = crmRepository.create("leads", {
      name: payload.name,
      email: payload.email,
      phone: payload.phone,
      requirements: payload.requirements,
      source: payload.source || "chatbot"
    });

    followUpAutomation.queueLeadFollowUp(lead);
    return lead;
  },
  qualifyLead(payload) {
    const score = scoreLead(payload);

    return {
      score,
      category: score >= 80 ? "hot" : score >= 50 ? "warm" : "cold",
      criteria: {
        budget: payload.budget,
        interestLevel: payload.interestLevel,
        companySize: payload.companySize,
        purchaseTimeline: payload.purchaseTimeline
      }
    };
  },
  scheduleAppointment(payload) {
    return calendarIntegration.bookAppointment(payload);
  }
};
