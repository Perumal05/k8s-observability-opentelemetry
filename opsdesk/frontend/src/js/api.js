/**
 * OpsDesk API Client
 */
const API_BASE = window.location.origin.includes(':3000') || window.location.origin.includes(':8080')
  ? '' // In Docker/NGINX proxy setups, API is relative
  : 'http://localhost:8000'; // Default fallback for local dev

class ApiService {
  static async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (response.status === 204) {
        return null;
      }

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorMessage = data.detail || `HTTP Error ${response.status}: ${response.statusText}`;
        throw new Error(errorMessage);
      }

      return data;
    } catch (error) {
      console.error(`API Request Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Dashboard
  static getDashboardSummary() {
    return this.request('/api/dashboard/summary');
  }

  static getDashboardStatistics() {
    return this.request('/api/dashboard/statistics');
  }

  // Incidents
  static getIncidents(params = {}) {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page);
    if (params.limit) query.append('limit', params.limit);
    if (params.status) query.append('status', params.status);
    if (params.priority) query.append('priority', params.priority);
    if (params.category) query.append('category', params.category);
    if (params.search) query.append('search', params.search);

    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request(`/api/incidents${qs}`);
  }

  static getIncidentById(id) {
    return this.request(`/api/incidents/${id}`);
  }

  static createIncident(payload) {
    return this.request('/api/incidents', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  static updateIncident(id, payload) {
    return this.request(`/api/incidents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  static updateIncidentStatus(id, status, changedBy = null) {
    return this.request(`/api/incidents/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status, changed_by: changedBy }),
    });
  }

  static updateIncidentPriority(id, priority, changedBy = null) {
    return this.request(`/api/incidents/${id}/priority`, {
      method: 'PUT',
      body: JSON.stringify({ priority, changed_by: changedBy }),
    });
  }

  static assignIncident(id, assignedTo, changedBy = null) {
    return this.request(`/api/incidents/${id}/assign`, {
      method: 'PUT',
      body: JSON.stringify({ assigned_to: assignedTo, changed_by: changedBy }),
    });
  }

  static deleteIncident(id) {
    return this.request(`/api/incidents/${id}`, {
      method: 'DELETE',
    });
  }

  // Comments & History
  static getIncidentComments(id) {
    return this.request(`/api/incidents/${id}/comments`);
  }

  static addComment(id, userId, comment) {
    return this.request(`/api/incidents/${id}/comments`, {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, comment }),
    });
  }

  static getIncidentHistory(id) {
    return this.request(`/api/incidents/${id}/history`);
  }

  // Users
  static getUsers() {
    return this.request('/api/users');
  }

  // System & Health
  static getHealth() {
    return this.request('/health');
  }

  static getReady() {
    return this.request('/ready');
  }

  static getSystemInfo() {
    return this.request('/api/system/info');
  }
}

