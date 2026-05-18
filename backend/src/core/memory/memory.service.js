const memoryStore = new Map();

export const memoryService = {
  remember(sessionId, payload) {
    memoryStore.set(sessionId, {
      ...(memoryStore.get(sessionId) || {}),
      ...payload
    });
  },
  recall(sessionId) {
    return memoryStore.get(sessionId) || {};
  }
};
