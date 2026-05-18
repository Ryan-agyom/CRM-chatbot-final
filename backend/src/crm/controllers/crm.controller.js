import { salesCRMService } from "../services/salesCRM.service.js";
import { marketingCRMService } from "../services/marketingCRM.service.js";
import { supportCRMService } from "../services/supportCRM.service.js";
import { analyticsCRMService } from "../services/analyticsCRM.service.js";
import { syntheticCRMDataService } from "../services/syntheticCRMData.service.js";
import { crmRepository } from "../repositories/crm.repository.js";

export function getCRMOverview(_request, response) {
  response.json({
    module: "crm",
    sections: ["sales", "marketing", "support", "analytics"],
    independence: "The CRM module is isolated from the core chatbot module."
  });
}

export function createLead(request, response) {
  const lead = salesCRMService.captureLead(request.body);
  response.status(201).json(lead);
}

export function qualifyLead(request, response) {
  const result = salesCRMService.qualifyLead(request.body);
  response.json(result);
}

export function scheduleAppointment(request, response) {
  const appointment = salesCRMService.scheduleAppointment(request.body);
  response.status(201).json(appointment);
}

export function createCampaign(request, response) {
  const campaign = marketingCRMService.createCampaign(request.body);
  response.status(201).json(campaign);
}

export function createSupportTicket(request, response) {
  const ticket = supportCRMService.createTicket(request.body);
  response.status(201).json(ticket);
}

export function getInsights(_request, response) {
  response.json(analyticsCRMService.getInsights());
}

export function listLeads(_request, response) {
  response.json(crmRepository.list("leads"));
}

export function listCampaigns(_request, response) {
  response.json(crmRepository.list("campaigns"));
}

export function listSupportTickets(_request, response) {
  response.json(crmRepository.list("tickets"));
}

export function seedSyntheticCRMData(request, response) {
  const leads = Number(request.body?.leads ?? 25);
  const campaigns = Number(request.body?.campaigns ?? 10);
  const tickets = Number(request.body?.tickets ?? 15);

  const result = syntheticCRMDataService.seed({ leads, campaigns, tickets });
  response.status(201).json(result);
}
