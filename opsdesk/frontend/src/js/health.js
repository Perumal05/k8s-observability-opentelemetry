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
    const setElemText = (id, text) => {
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    };

    // API Status
    const apiIndicator = document.getElementById('health-api-indicator');
    const apiText = document.getElementById('health-api-text');
    if (apiIndicator && apiText) {
      if (health.status === 'UP') {
        apiIndicator.className = 'health-indicator';
        apiText.textContent = 'API is Operational (200 OK)';
      } else {
        apiIndicator.className = 'health-indicator down';
        apiText.textContent = 'API Unhealthy';
      }
    }

    // Database Status
    const dbIndicator = document.getElementById('health-db-indicator');
    const dbText = document.getElementById('health-db-text');
    if (dbIndicator && dbText) {
      if (ready.database === 'UP') {
        dbIndicator.className = 'health-indicator';
        dbText.textContent = 'Database Connected (PostgreSQL)';
      } else {
        dbIndicator.className = 'health-indicator down';
        dbText.textContent = 'Database Connection Failed';
      }
    }

    // Metadata
    setElemText('sys-version', info.version || '1.0.0');
    setElemText('sys-env', (info.environment || 'development').toUpperCase());
    setElemText('sys-uptime', info.uptime_seconds ? `${info.uptime_seconds}s` : 'N/A');
  }
}

