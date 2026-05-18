const sessionStore = new Map();

export const sessionService = {
  getHistory(sessionId) {
    return sessionStore.get(sessionId) || [];
  },
  appendMessage(sessionId, message) {
    const history = sessionStore.get(sessionId) || [];
    sessionStore.set(sessionId, [...history, message]);
  }
};
