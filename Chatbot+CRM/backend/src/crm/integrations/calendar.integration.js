import { randomUUID } from "node:crypto";

export const calendarIntegration = {
  bookAppointment(payload) {
    return {
      id: randomUUID(),
      customerName: payload.customerName,
      type: payload.type || "demo",
      scheduledFor: payload.scheduledFor,
      reminderEnabled: payload.reminderEnabled !== false
    };
  }
};
