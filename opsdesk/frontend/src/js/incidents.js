/**
 * Incidents List View Controller
 */
class IncidentsController {
  static currentPage = 1;
  static limit = 10;
  static totalPages = 1;

  static async load(page = 1) {
    this.currentPage = page;
    const status = document.getElementById('filter-status').value || undefined;
    const priority = document.getElementById('filter-priority').value || undefined;
    const category = document.getElementById('filter-category').value || undefined;
    const search = document.getElementById('search-incidents').value.trim() || undefined;

    const tbody = document.getElementById('incidents-table-body');
    tbody.innerHTML = `<tr><td colspan="7" class="empty-state"><div class="loading-spinner"></div> Loading incidents...</td></tr>`;

    try {
      const response = await ApiService.getIncidents({
        page: this.currentPage,
        limit: this.limit,
        status,
        priority,
        category,
        search,
      });

      this.totalPages = response.pages || 1;
      this.renderTable(response.items || []);
      this.renderPagination(response);
    } catch (error) {
      tbody.innerHTML = `<tr><td colspan="7" class="empty-state" style="color: var(--priority-critical);">Error loading incidents: ${error.message}</td></tr>`;
      App.showToast(error.message, 'error');
    }
  }

  static renderTable(items) {
    const tbody = document.getElementById('incidents-table-body');
    if (!items.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="empty-state">No incidents match the selected criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = items.map(inc => {
      const assigneeName = inc.assignee ? inc.assignee.name : '<span style="color: var(--text-muted);">Unassigned</span>';
      return `
        <tr class="clickable-row" onclick="App.navigateToDetail(${inc.id})">
          <td><strong style="color: var(--primary);">${inc.incident_number}</strong></td>
          <td>
            <div style="font-weight: 500;">${App.escapeHtml(inc.title)}</div>
            <div style="font-size: 11px; color: var(--text-muted);">${inc.category}</div>
          </td>
          <td><span class="badge badge-${inc.priority.toLowerCase()}"><span class="badge-dot"></span>${inc.priority}</span></td>
          <td><span class="badge badge-${inc.status.toLowerCase()}">${inc.status.replace('_', ' ')}</span></td>
          <td>${assigneeName}</td>
          <td style="color: var(--text-muted); font-size: 12px;">${App.formatDate(inc.created_at)}</td>
          <td style="color: var(--text-muted); font-size: 12px;">${App.formatDate(inc.updated_at)}</td>
        </tr>
      `;
    }).join('');
  }

  static renderPagination(response) {
    const pageInfo = document.getElementById('pagination-info');
    if (pageInfo) {
      const start = (response.page - 1) * response.limit + 1;
      const end = Math.min(response.page * response.limit, response.total);
      pageInfo.textContent = response.total > 0
        ? `Showing ${start} to ${end} of ${response.total} incidents`
        : `0 incidents`;
    }

    const prevBtn = document.getElementById('btn-prev-page');
    if (prevBtn) prevBtn.disabled = response.page <= 1;

    const nextBtn = document.getElementById('btn-next-page');
    if (nextBtn) nextBtn.disabled = response.page >= response.pages;
  }

  static prevPage() {
    if (this.currentPage > 1) {
      this.load(this.currentPage - 1);
    }
  }

  static nextPage() {
    if (this.currentPage < this.totalPages) {
      this.load(this.currentPage + 1);
    }
  }

  static applyFilters() {
    this.load(1);
  }

  static resetFilters() {
    const st = document.getElementById('filter-status');
    if (st) st.value = '';
    const pr = document.getElementById('filter-priority');
    if (pr) pr.value = '';
    const cat = document.getElementById('filter-category');
    if (cat) cat.value = '';
    const srch = document.getElementById('search-incidents');
    if (srch) srch.value = '';
    this.load(1);
  }
}
