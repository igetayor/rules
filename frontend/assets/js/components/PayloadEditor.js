/**
 * Component: PayloadEditor manages preset selection and input JSON validation.
 */
export const PRESETS = {
  fraud: {
    "transaction": { "amount": 14500, "currency": "EUR", "ip": "185.220.101.4" },
    "user": { "risk_score": 88, "tier": "STANDARD", "email": "trader@cryptomixer.io" },
    "network": { "is_vpn": true }
  },
  vip: {
    "transaction": { "amount": 75000, "currency": "USD" },
    "user": { "tier": "VIP", "kyc_status": "VERIFIED", "credit_score": 790, "email": "fund_manager@blackrock.com" },
    "network": { "is_vpn": false }
  },
  disposable: {
    "user": { "email": "testuser99@tempmail.com", "tier": "FREE", "risk_score": 30 },
    "network": { "is_vpn": true }
  }
};

export class PayloadEditor {
  constructor(editorId, presetSelectId) {
    this.editor = document.getElementById(editorId);
    this.presetSelect = document.getElementById(presetSelectId);
  }

  init() {
    if (this.presetSelect) {
      this.presetSelect.addEventListener('change', (e) => {
        const val = e.target.value;
        if (PRESETS[val]) {
          this.editor.value = JSON.stringify(PRESETS[val], null, 2);
        }
      });
      // Default to fraud
      this.editor.value = JSON.stringify(PRESETS.fraud, null, 2);
    }
  }

  getPayload() {
    try {
      return JSON.parse(this.editor.value);
    } catch (e) {
      alert("Invalid JSON format in payload editor: " + e.message);
      return null;
    }
  }
}
