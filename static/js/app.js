import { Api } from './api.js';
import { RuleCatalog } from './components/RuleCatalog.js';
import { PayloadEditor } from './components/PayloadEditor.js';
import { EvaluationResultView } from './components/EvaluationResultView.js';

class RuleEngineApp {
  constructor() {
    this.ruleCatalog = new RuleCatalog('ruleCatalogList');
    this.payloadEditor = new PayloadEditor('payloadInput', 'presetSelect');
    this.resultView = new EvaluationResultView('evalResultsStream', 'evalMetricsHeader');
  }

  async init() {
    this.payloadEditor.init();
    await this.loadRules();
    this.bindEvents();
    // Run initial evaluation
    await this.runEvaluation();
  }

  async loadRules() {
    const rules = await Api.getRules();
    this.ruleCatalog.update(rules);
  }

  bindEvents() {
    const runBtn = document.getElementById('btnEvaluate');
    if (runBtn) {
      runBtn.addEventListener('click', () => this.runEvaluation());
    }
  }

  async runEvaluation() {
    const payload = this.payloadEditor.getPayload();
    if (!payload) return;

    const btn = document.getElementById('btnEvaluate');
    btn.disabled = true;
    btn.textContent = "Evaluating...";

    try {
      const response = await Api.evaluatePayload(payload);
      this.resultView.update(response);
    } catch (err) {
      console.error("Evaluation failed:", err);
    } finally {
      btn.disabled = false;
      btn.innerHTML = "⚡ Evaluate Payload Against Rules";
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const app = new RuleEngineApp();
  app.init();
});
