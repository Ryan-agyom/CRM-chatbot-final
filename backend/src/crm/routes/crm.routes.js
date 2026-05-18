import { Router } from "express";
import {
  getCRMOverview,
  createLead,
  qualifyLead,
  scheduleAppointment,
  createCampaign,
  createSupportTicket,
  getInsights,
  listLeads,
  listCampaigns,
  listSupportTickets,
  seedSyntheticCRMData
} from "../controllers/crm.controller.js";

const router = Router();

router.get("/overview", getCRMOverview);
router.get("/leads", listLeads);
router.post("/leads", createLead);
router.post("/leads/qualify", qualifyLead);
router.post("/appointments", scheduleAppointment);
router.get("/campaigns", listCampaigns);
router.post("/campaigns", createCampaign);
router.get("/support/tickets", listSupportTickets);
router.post("/support/tickets", createSupportTicket);
router.get("/analytics/insights", getInsights);
router.post("/dev/seed", seedSyntheticCRMData);

export { router as crmRouter };
