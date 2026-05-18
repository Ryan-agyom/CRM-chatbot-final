import { crmRepository } from "../repositories/crm.repository.js";
import { campaignAutomation } from "../automations/campaignAutomation.js";

export const marketingCRMService = {
  createCampaign(payload) {
    const campaign = crmRepository.create("campaigns", {
      name: payload.name,
      segment: payload.segment,
      message: payload.message,
      trigger: payload.trigger || "manual"
    });

    campaignAutomation.schedule(campaign);
    return campaign;
  },
  segmentCustomers(customers) {
    return {
      newCustomers: customers.filter((customer) => customer.orders === 0),
      returningCustomers: customers.filter((customer) => customer.orders > 0),
      highSpenders: customers.filter((customer) => customer.totalSpend >= 100000),
      inactiveUsers: customers.filter((customer) => customer.lastSeenDays >= 30)
    };
  }
};
