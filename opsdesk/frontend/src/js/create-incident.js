/**
 * Create Incident View Controller
 */
class CreateIncidentController {
  static async init() {
    try {
      const users = await App.getUsers();
      this.populateUserDropdowns(users);
    } catch (error) {
      App.showToast(`Failed to load user directory: ${error.message}`, 'error');
    }
  }

  static populateUserDropdowns(users) {
    const reporterSelect = document.getElementById('create-reporter');
    const assigneeSelect = document.getElementById('create-assignee');

    const reporters = (users || []).filter(u => u.role === 'REPORTER' || u.role === 'MANAGER');
    const technicians = (users || []).filter(u => u.role === 'TECHNICIAN' || u.role === 'MANAGER');

    if (reporterSelect) {
      reporterSelect.innerHTML = reporters.map(r => `<option value="${r.id}">${r.name} (${r.role})</option>`).join('');
    }
    if (assigneeSelect) {
      assigneeSelect.innerHTML = `<option value="">-- Unassigned --</option>` +
        technicians.map(t => `<option value="${t.id}">${t.name} (${t.role})</option>`).join('');
    }
  }

  static async submit(event) {
    event.preventDefault();

    const title = document.getElementById('create-title').value.trim();
    const description = document.getElementById('create-description').value.trim();
    const priority = document.getElementById('create-priority').value;
    const category = document.getElementById('create-category').value;
    const reporterId = parseInt(document.getElementById('create-reporter').value, 10);
    const assigneeVal = document.getElementById('create-assignee').value;
    const assignedTo = assigneeVal ? parseInt(assigneeVal, 10) : null;

    if (!title || title.length < 3) {
      App.showToast('Please enter a descriptive title (at least 3 characters)', 'warning');
      return;
    }

    if (!description || description.length < 5) {
      App.showToast('Please provide an incident description (at least 5 characters)', 'warning');
      return;
    }

    if (!reporterId) {
      App.showToast('Please select a reporter', 'warning');
      return;
    }

    const payload = {
      title,
      description,
      priority,
      category,
      reporter_id: reporterId,
      assigned_to: assignedTo,
    };

    const submitBtn = document.getElementById('btn-submit-incident');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';

    try {
      const created = await ApiService.createIncident(payload);
      App.showToast(`Incident ${created.incident_number} created successfully!`, 'success');
      
      // Reset form
      document.getElementById('create-incident-form').reset();
      
      // Navigate to created incident
      App.navigateToDetail(created.id);
    } catch (error) {
      App.showToast(`Failed to create incident: ${error.message}`, 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Create Incident';
    }
  }
}
