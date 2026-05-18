import { randomUUID } from "node:crypto";
import { inMemoryStore } from "../../shared/database/inMemoryStore.js";

const collections = inMemoryStore.crm;

export const crmRepository = {
  create(collectionName, payload) {
    const record = {
      id: randomUUID(),
      ...payload,
      createdAt: new Date().toISOString()
    };

    collections[collectionName].push(record);
    return record;
  },
  list(collectionName) {
    return collections[collectionName];
  },
  bulkCreate(collectionName, payloads) {
    return payloads.map((payload) => this.create(collectionName, payload));
  },
  clear(collectionName) {
    collections[collectionName] = [];
    return collections[collectionName];
  },
  replace(collectionName, payloads) {
    this.clear(collectionName);
    return this.bulkCreate(collectionName, payloads);
  },
  snapshot() {
    return {
      leads: collections.leads,
      campaigns: collections.campaigns,
      tickets: collections.tickets
    };
  }
};
