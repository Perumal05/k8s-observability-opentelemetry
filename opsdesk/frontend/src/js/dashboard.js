/**
 * Dashboard View Controller
 */
class DashboardController {
  static async load() {
    try {
      const [summary, stats] = await Promise.all([
        ApiService.getDashboardSummary(),
        ApiService.getDashboardStatistics(),
      ]);

      this.renderKPIs(summary);
      this.renderBreakdowns(stats);
      this.renderRecentIncidents(summary.recent_incidents || []);
    } catch (error) {
      App.showToast(`Failed to load dashboard data: ${error.message}`, 'error');
    }
  }

  static renderKPIs(summary) {
    document.getElementById('kpi-total').textContent = summary.total_incidents ?? 0;
    document.getElementById('kpi-open').textContent = summary.open_incidents ?? 0;
    document.getElementById('kpi-critical').textContent = summary.critical_incidents ?? 0;
    document.getElementById('kpi-resolved').textContent = summary.resolved_incidents ?? 0;
    document.getElementById('kpi-today').textContent = summary.created_today ?? 0;

    const mttr = summary.avg_resolution_time_minutes;
    document.getElementById('kpi-mttr').textContent = mttr ? `${mttr}m` : 'N/A';
  }

  static renderBreakdowns(stats) {
    // Priority Bars
    const priorityContainer = document.getElementById('priority-breakdown');
    const priorityCounts = stats.by_priority || {};
    const totalPriority = Object.values(priorityCounts).reduce((a, b) => a + b, 0) || 1;

    const priorityColors = {
      CRITICAL: 'var(--priority-critical)',
      HIGH: 'var(--priority-high)',
      MEDIUM: 'var(--priority-medium)',
      LOW: 'var(--priority-low)',
    };

    let priorityHtml = '';
    for (const [prio, count] of Object.entries(priorityCounts)) {
      const pct = Math.round((count / totalPriority) * 100);
      const color = priorityColors[prio] || 'var(--primary)';
      priorityHtml += `
        <div class="stat-bar-item">
          <div class="stat-bar-label">
            <span>${prio}</span>
            <span><strong>${count}</strong> (${pct}%)</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${pct}%; background-color: ${color};"></div>
          </div>
        </div>
      `;
    }
    priorityContainer.innerHTML = priorityHtml;

    // Status Bars
    const statusContainer = document.getElementById('status-breakdown');
    const statusCounts = stats.by_status || {};
    const totalStatus = Object.values(statusCounts).reduce((a, b) => a + b, 0) || 1;

    const statusColors = {
      OPEN: 'var(--status-open)',
      IN_PROGRESS: 'var(--status-in-progress)',
      PENDING: 'var(--status-pending)',
      RESOLVED: 'var(--status-resolved)',
      CLOSED: 'var(--status-closed)',
    };

    let statusHtml = '';
    for (const [st, count] of Object.entries(statusCounts)) {
      const pct = Math.round((count / totalStatus) * 100);
      const color = statusColors[st] || 'var(--text-secondary)';
      statusHtml += `
        <div class="stat-bar-item">
          <div class="stat-bar-label">
            <span>${st.replace('_', ' ')}</span>
            <span><strong>${count}</strong> (${pct}%)</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${pct}%; background-color: ${color};"></div>
          </div>
        </div>
      `;
    }
    statusContainer.innerHTML = statusHtml;
  }

  static renderRecentIncidents(incidents) {
    const tbody = document.getElementById('recent-incidents-body');
    if (!incidents.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No incidents recorded yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = incidents.map(inc => `
      <tr class="clickable-row" onclick="App.navigateToDetail(${inc.id})">
        <td><strong>${inc.incident_number}</strong></td>
        <td>${App.escapeHtml(inc.title)}</td>
        <td><span class="badge badge-${inc.priority.toLowerCase()}"><span class="badge-dot"></span>${inc.priority}</span></td>
        <td><span class="badge badge-${inc.status.toLowerCase()}">${inc.status.replace('_', ' ')}</span></td>
        <td style="color: var(--text-muted);">${App.formatDate(inc.created_at)}</td>
      </tr>
    `).join('');
  }
}
