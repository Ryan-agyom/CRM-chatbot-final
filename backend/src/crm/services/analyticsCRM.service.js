import { crmAnalyticsEngine } from "../analytics/crmAnalyticsEngine.js";
import { crmRepository } from "../repositories/crm.repository.js";

export const analyticsCRMService = {
  getInsights() {
    return crmAnalyticsEngine.generate({
      leads: crmRepository.list("leads"),
      campaigns: crmRepository.list("campaigns"),
      tickets: crmRepository.list("tickets")
    });
  }
};
