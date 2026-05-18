import { syntheticCRMDataService } from "../src/crm/services/syntheticCRMData.service.js";

const leads = Number(process.argv[2] || 25);
const campaigns = Number(process.argv[3] || 10);
const tickets = Number(process.argv[4] || 15);

const result = syntheticCRMDataService.seed({ leads, campaigns, tickets });
console.log(JSON.stringify(result, null, 2));
