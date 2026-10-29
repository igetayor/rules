/**
 * Component: RuleCatalog renders the active ruleset and conditions summary.
 */
export class RuleCatalog {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
  }

  update(rules = []) {
    if (!this.container) return;

    this.container.innerHTML = rules.map(r => {
      const conditionBadges = (r.conditions || []).map(c => 
        `<span class="cond-tag">${c.field} <strong>${c.operator}</strong> ${JSON.stringify(c.value)}</span>`
      ).join('');

      return `
        <div class="rule-card">
          <div class="rule-card-header">
            <span class="rule-id">${r.id}</span>
            <span class="rule-action-badge">ACTION: ${r.action}</span>
          </div>
          <div class="rule-desc">${r.description}</div>
          <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 0.25rem;">
            Logic: <strong style="color: #a5b4fc;">${r.match_all ? 'ALL must match (AND)' : 'ANY can match (OR)'}</strong>
          </div>
          <div class="conditions-tag-group">
            ${conditionBadges}
          </div>
        </div>
      `;
    }).join('');
  }
}
