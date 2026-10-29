/**
 * Component: EvaluationResultView renders the evaluation audit tree and sub-millisecond benchmark header.
 */
export class EvaluationResultView {
  constructor(containerId, headerId) {
    this.container = document.getElementById(containerId);
    this.header = document.getElementById(headerId);
  }

  update(response) {
    if (!this.container || !response) return;

    if (this.header) {
      this.header.innerHTML = `
        <span style="color: #a5b4fc; font-weight: 700;">⏱️ ${response.evaluation_time_us}&mu;s</span>
        <span style="margin: 0 0.5rem; color: var(--border-subtle);">|</span>
        <span style="color: #34d399; font-weight: 700;">${response.rules_triggered_count} / ${response.rules_evaluated_count} Triggered</span>
      `;
    }

    const results = response.results || [];
    this.container.innerHTML = results.map(r => {
      const isMatched = r.matched;
      const statusPill = isMatched 
        ? '<span class="eval-status-pill pass">TRIGGERED</span>'
        : '<span class="eval-status-pill fail">NOT MET</span>';

      const conditionChecks = (r.condition_evaluations || []).map(c => `
        <div class="check-item ${c.passed ? 'passed' : 'failed'}">
          <span>${c.passed ? '✔' : '✖'}</span>
          <span><strong>${c.field}</strong> [${c.operator} ${JSON.stringify(c.target_value)}] -> Actual: ${JSON.stringify(c.actual_value)}</span>
        </div>
      `).join('');

      return `
        <div class="eval-card ${isMatched ? 'matched' : 'unmatched'}">
          <div class="eval-card-top">
            <span style="font-family: var(--font-mono); font-weight: 700; color: ${isMatched ? '#34d399' : 'var(--text-muted)'};">
              ${r.rule_id}
            </span>
            ${statusPill}
          </div>
          <div style="font-size: 0.85rem; color: var(--text-main); font-weight: 600;">
            ${r.explanation}
          </div>
          <div class="condition-check-list">
            ${conditionChecks}
          </div>
        </div>
      `;
    }).join('');
  }
}
