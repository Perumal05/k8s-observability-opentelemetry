/**
 * Incident Details View Controller
 */
class IncidentDetailController {
  static currentIncidentId = null;

  static async load(incidentId) {
    this.currentIncidentId = incidentId;
    try {
      const [incident, comments, history, users] = await Promise.all([
        ApiService.getIncidentById(incidentId),
        ApiService.getIncidentComments(incidentId),
        ApiService.getIncidentHistory(incidentId),
        App.getUsers(),
      ]);

      this.renderIncidentDetails(incident, users);
      this.renderComments(comments, users);
      this.renderTimeline(history);
    } catch (error) {
      App.showToast(`Failed to load incident #${incidentId}: ${error.message}`, 'error');
      App.switchView('incidents');
    }
  }

  static renderIncidentDetails(incident, users) {
    document.getElementById('detail-incident-number').textContent = incident.incident_number;
    document.getElementById('detail-title').textContent = incident.title;
    document.getElementById('detail-desc').textContent = incident.description;
    document.getElementById('detail-category').textContent = incident.category;
    document.getElementById('detail-reporter').textContent = incident.reporter ? incident.reporter.name : 'Unknown';
    document.getElementById('detail-created').textContent = App.formatDate(incident.created_at);
    document.getElementById('detail-updated').textContent = App.formatDate(incident.updated_at);
    document.getElementById('detail-resolved').textContent = incident.resolved_at ? App.formatDate(incident.resolved_at) : 'Not Resolved';

    // Status Badge & Dropdown
    const statusSelect = document.getElementById('detail-status-select');
    statusSelect.value = incident.status;

    // Priority Badge & Dropdown
    const prioritySelect = document.getElementById('detail-priority-select');
    prioritySelect.value = incident.priority;

    // Assignee Dropdown
    const assigneeSelect = document.getElementById('detail-assignee-select');
    const technicians = users.filter(u => u.role === 'TECHNICIAN' || u.role === 'MANAGER');
    assigneeSelect.innerHTML = `<option value="">-- Unassigned --</option>` +
      technicians.map(t => `<option value="${t.id}" ${incident.assigned_to === t.id ? 'selected' : ''}>${t.name} (${t.role})</option>`).join('');
  }

  static renderComments(comments, users) {
    const list = document.getElementById('detail-comments-list');
    if (!comments.length) {
      list.innerHTML = `<div class="empty-state" style="padding: 16px;">No comments yet.</div>`;
      return;
    }

    list.innerHTML = comments.map(c => `
      <div class="comment-item">
        <div class="comment-author">
          <span>${c.user ? c.user.name : `User #${c.user_id}`}</span>
          <span class="comment-time">${App.formatDate(c.created_at)}</span>
        </div>
        <div>${App.escapeHtml(c.comment)}</div>
      </div>
    `).join('');
  }

  static renderTimeline(history) {
    const list = document.getElementById('detail-timeline-list');
    if (!history.length) {
      list.innerHTML = `<div class="empty-state" style="padding: 16px;">No history recorded.</div>`;
      return;
    }

    list.innerHTML = history.map(h => {
      let desc = '';
      if (h.action === 'INCIDENT_CREATED') {
        desc = `Incident created with status <strong>${h.new_value}</strong>`;
      } else if (h.action === 'STATUS_CHANGED') {
        desc = `Status updated from <span class="badge badge-${(h.old_value || '').toLowerCase()}">${h.old_value}</span> to <span class="badge badge-${(h.new_value || '').toLowerCase()}">${h.new_value}</span>`;
      } else if (h.action === 'PRIORITY_CHANGED') {
        desc = `Priority changed from <strong>${h.old_value}</strong> to <strong>${h.new_value}</strong>`;
      } else if (h.action === 'ASSIGNMENT_CHANGED') {
        desc = `Assignment changed (User ID: ${h.new_value})`;
      } else {
        desc = `${h.action}: ${h.new_value || ''}`;
      }

      return `
        <div class="timeline-item">
          <div class="timeline-marker"></div>
          <div class="timeline-content">
            <div>${desc}</div>
            <div class="timeline-meta">${App.formatDate(h.created_at)}</div>
          </div>
        </div>
      `;
    }).join('');
  }

  static async updateStatus() {
    const newStatus = document.getElementById('detail-status-select').value;
    try {
      await ApiService.updateIncidentStatus(this.currentIncidentId, newStatus);
      App.showToast(`Status updated to ${newStatus}`, 'success');
      this.load(this.currentIncidentId);
    } catch (error) {
      App.showToast(error.message, 'error');
    }
  }

  static async updatePriority() {
    const newPriority = document.getElementById('detail-priority-select').value;
    try {
      await ApiService.updateIncidentPriority(this.currentIncidentId, newPriority);
      App.showToast(`Priority updated to ${newPriority}`, 'success');
      this.load(this.currentIncidentId);
    } catch (error) {
      App.showToast(error.message, 'error');
    }
  }

  static async updateAssignee() {
    const val = document.getElementById('detail-assignee-select').value;
    const assignedTo = val ? parseInt(val, 10) : null;
    try {
      await ApiService.assignIncident(this.currentIncidentId, assignedTo);
      App.showToast('Assignee updated successfully', 'success');
      this.load(this.currentIncidentId);
    } catch (error) {
      App.showToast(error.message, 'error');
    }
  }

  static async submitComment() {
    const textarea = document.getElementById('new-comment-text');
    const text = textarea.value.trim();
    if (!text) {
      App.showToast('Please enter a comment before submitting', 'warning');
      return;
    }

    const users = await App.getUsers();
    const technician = users.find(u => u.role === 'TECHNICIAN') || users[0];

    try {
      await ApiService.addComment(this.currentIncidentId, technician.id, text);
      textarea.value = '';
      App.showToast('Comment added', 'success');
      this.load(this.currentIncidentId);
    } catch (error) {
      App.showToast(error.message, 'error');
    }
  }

  static async deleteCurrentIncident() {
    if (!confirm('Are you sure you want to delete this incident? This action cannot be undone.')) {
      return;
    }

    try {
      await ApiService.deleteIncident(this.currentIncidentId);
      App.showToast('Incident deleted successfully', 'success');
      App.switchView('incidents');
    } catch (error) {
      App.showToast(error.message, 'error');
    }
  }
}
