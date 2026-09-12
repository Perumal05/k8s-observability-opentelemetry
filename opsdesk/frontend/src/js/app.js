/**
 * Main OpsDesk Application Coordinator
 */
class App {
  static currentView = 'dashboard';
  static cachedUsers = null;

  static async init() {
    this.setupNavigation();
    this.setupEventListeners();
    await this.switchView('dashboard');
  }

  static setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const view = btn.getAttribute('data-view');
        if (view) {
          this.switchView(view);
        }
      });
    });
  }

  static setupEventListeners() {
    // Search input enter key
    const searchInput = document.getElementById('search-incidents');
    if (searchInput) {
      searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          IncidentsController.applyFilters();
        }
      });
    }

    // Create incident form
    const createForm = document.getElementById('create-incident-form');
    if (createForm) {
      createForm.addEventListener('submit', (e) => CreateIncidentController.submit(e));
    }
  }

  static async switchView(viewName) {
    this.currentView = viewName;

    // Update active navigation item
    document.querySelectorAll('.nav-item').forEach(el => {
      el.classList.toggle('active', el.getAttribute('data-view') === viewName);
    });

    // Hide all view sections
    document.querySelectorAll('.view-section').forEach(sec => {
      sec.classList.remove('active');
    });

    // Show target view section
    const targetSection = document.getElementById(`view-${viewName}`);
    if (targetSection) {
      targetSection.classList.add('active');
    }

    // Update header title
    const titles = {
      dashboard: 'Operations Dashboard',
      incidents: 'Incident Management',
      create: 'Create New Incident',
      detail: 'Incident Details',
      health: 'System Status & Diagnostics',
    };
    document.getElementById('header-title').textContent = titles[viewName] || 'OpsDesk';

    // Dispatch load actions for active view
    switch (viewName) {
      case 'dashboard':
        await DashboardController.load();
        break;
      case 'incidents':
        await IncidentsController.load(1);
        break;
      case 'create':
        await CreateIncidentController.init();
        break;
      case 'health':
        await HealthController.load();
        break;
    }
  }

  static async navigateToDetail(incidentId) {
    this.switchView('detail');
    await IncidentDetailController.load(incidentId);
  }

  static async getUsers() {
    if (!this.cachedUsers) {
      this.cachedUsers = await ApiService.getUsers();
    }
    return this.cachedUsers;
  }

  static showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div>${this.escapeHtml(message)}</div>
      <button style="background:transparent;border:none;color:var(--text-muted);cursor:pointer;font-size:14px;" onclick="this.parentElement.remove()">✕</button>
    `;
    container.appendChild(toast);

    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 4500);
  }

  static formatDate(isoString) {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  }

  static escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
}

// Bootstrap application on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
