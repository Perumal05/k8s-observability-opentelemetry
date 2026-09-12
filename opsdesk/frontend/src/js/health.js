/**
 * System Health View Controller
 */
class HealthController {
  static async load() {
    try {
      const [health, ready, info] = await Promise.all([
        ApiService.getHealth().catch(e => ({ status: 'DOWN', error: e.message })),
        ApiService.getReady().catch(e => ({ status: 'DOWN', database: 'DOWN', error: e.message })),
        ApiService.getSystemInfo().catch(e => ({ status: 'DOWN', error: e.message })),
      ]);

      this.renderHealth(health, ready, info);
    } catch (error) {
      App.showToast(`Error fetching health status: ${error.message}`, 'error');
    }
  }

  static renderHealth(health, ready, info) {
    // API Status
    const apiIndicator = document.getElementById('health-api-indicator');
    const apiText = document.getElementById('health-api-text');
    if (health.status === 'UP') {
      apiIndicator.className = 'health-indicator';
      apiText.textContent = 'API is Operational (200 OK)';
    } else {
      apiIndicator.className = 'health-indicator down';
      apiText.textContent = 'API Unhealthy';
    }

    // Database Status
    const dbIndicator = document.getElementById('health-db-indicator');
    const dbText = document.getElementById('health-db-text');
    if (ready.database === 'UP') {
      dbIndicator.className = 'health-indicator';
      dbText.textContent = 'Database Connected (PostgreSQL)';
    } else {
      dbIndicator.className = 'health-indicator down';
      dbText.textContent = 'Database Connection Failed';
    }

    // Metadata
    document.getElementById('sys-version').textContent = info.version || '1.0.0';
    document.getElementById('sys-env').textContent = (info.environment || 'development').toUpperCase();
    document.getElementById('sys-uptime').textContent = info.uptime_seconds ? `${info.uptime_seconds}s` : 'N/A';
  }
}

