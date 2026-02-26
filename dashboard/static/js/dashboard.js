/* Resolver Agent Health Dashboard – real-time update script */

const STATUS_BADGE = document.getElementById('status-badge');
const AGENT_CARDS  = document.getElementById('agent-cards');
const ALERTS_LIST  = document.getElementById('alerts-list');
const LAST_UPDATED = document.getElementById('last-updated');

function statusClass(status) {
  const s = (status || 'unknown').toLowerCase();
  if (s === 'healthy')  return 'healthy';
  if (s === 'degraded') return 'degraded';
  if (s === 'critical') return 'critical';
  return 'unknown';
}

function renderHealth(data) {
  // Overall status
  const overall = (data.overall_status || 'unknown').toUpperCase();
  STATUS_BADGE.textContent = overall;
  STATUS_BADGE.className = 'badge ' + statusClass(data.overall_status);

  // Agent cards
  AGENT_CARDS.innerHTML = '';
  const agents = data.agents || {};
  Object.entries(agents).forEach(([name, info]) => {
    const sc = statusClass(info.status);
    const card = document.createElement('div');
    card.className = 'agent-card ' + sc;
    card.innerHTML = `
      <h3>${name}</h3>
      <p class="metric">Status: <span>${(info.status || 'unknown').toUpperCase()}</span></p>
      <p class="metric">CPU: <span>${(info.cpu_usage || 0).toFixed(1)}%</span></p>
      <p class="metric">Memory: <span>${(info.memory_usage || 0).toFixed(1)}%</span></p>
      <p class="metric">Error rate: <span>${((info.error_rate || 0) * 100).toFixed(1)}%</span></p>
      <p class="metric">Response: <span>${(info.response_time || 0).toFixed(2)}s</span></p>
    `;
    AGENT_CARDS.appendChild(card);
  });

  // Alerts
  const alerts = data.alerts || [];
  ALERTS_LIST.innerHTML = '';
  if (alerts.length === 0) {
    ALERTS_LIST.innerHTML = '<li class="no-alerts">No active alerts ✓</li>';
  } else {
    alerts.forEach(alert => {
      const li = document.createElement('li');
      li.textContent = alert.message || JSON.stringify(alert);
      ALERTS_LIST.appendChild(li);
    });
  }

  LAST_UPDATED.textContent = 'Last updated: ' + new Date().toLocaleTimeString();
}

// Use Server-Sent Events for real-time updates
function connectSSE() {
  const source = new EventSource('/api/stream');
  source.onmessage = (event) => {
    try {
      renderHealth(JSON.parse(event.data));
    } catch (e) {
      console.error('Failed to parse health data', e);
    }
  };
  source.onerror = () => {
    console.warn('SSE disconnected; retrying via polling');
    source.close();
    pollHealth();
  };
}

// Fallback: poll every 5 s when SSE is unavailable
function pollHealth() {
  setInterval(() => {
    fetch('/api/health')
      .then(r => r.json())
      .then(renderHealth)
      .catch(e => console.error('Health poll failed', e));
  }, 5000);
}

// Attempt initial fetch immediately, then start SSE
fetch('/api/health')
  .then(r => r.json())
  .then(data => { renderHealth(data); connectSSE(); })
  .catch(() => pollHealth());
