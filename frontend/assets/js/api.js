/**
 * API client module for JSON Rule Engine.
 */
export const Api = {
  async getRules() {
    try {
      const res = await fetch('/api/rules');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn("Failed to fetch rule catalog:", err);
      return [];
    }
  },

  async evaluatePayload(payload) {
    const res = await fetch('/api/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return await res.json();
  }
};
