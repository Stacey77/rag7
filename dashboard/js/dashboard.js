// Main Dashboard JavaScript
class Dashboard {
    constructor() {
        this.currentFilter = 'all';
        this.activities = [];
        this.refreshInterval = null;
    }

    async initialize() {
        await this.loadDashboardData();
        this.setupEventListeners();
        this.startAutoRefresh();
        
        // Initialize sub-modules
        await agentManager.initialize();
    }

    async loadDashboardData() {
        try {
            const data = await api.getDefaultMockData();
            
            // Update platform status
            this.updatePlatformStatus(data.platform);
            
            // Update activities
            this.activities = data.activities;
            this.renderActivities();
            
            // Initialize charts
            chartManager.initializeCharts(data.metrics);
            
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    }

    updatePlatformStatus(platform) {
        // Update platform status badge
        const statusElement = document.getElementById('platformStatus');
        if (statusElement) {
            statusElement.textContent = platform.status.charAt(0).toUpperCase() + platform.status.slice(1);
            statusElement.className = `status-badge ${platform.status}`;
        }

        // Update stats
        this.updateStat('activeAgents', platform.activeAgents);
        this.updateStat('queueSize', platform.queueSize);
        this.updateStat('systemHealth', platform.systemHealth + '%');
    }

    updateStat(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    renderActivities() {
        const feedElement = document.getElementById('activityFeed');
        if (!feedElement) return;

        const filteredActivities = this.currentFilter === 'all' 
            ? this.activities 
            : this.activities.filter(a => a.type === this.currentFilter);

        if (filteredActivities.length === 0) {
            feedElement.innerHTML = `
                <div style="text-align: center; padding: 40px; color: var(--text-gray);">
                    <i class="fas fa-inbox" style="font-size: 48px; margin-bottom: 15px; opacity: 0.5;"></i>
                    <p>No activities to display</p>
                </div>
            `;
            return;
        }

        feedElement.innerHTML = filteredActivities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon ${activity.type}">
                    <i class="fas fa-${this.getActivityIcon(activity.type)}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-description">${activity.description}</div>
                    <div class="activity-time">
                        <i class="fas fa-clock"></i> ${activity.time}
                    </div>
                </div>
            </div>
        `).join('');
    }

    getActivityIcon(type) {
        const icons = {
            policy: 'shield-alt',
            deployment: 'rocket',
            compliance: 'clipboard-check',
            alert: 'exclamation-triangle'
        };
        return icons[type] || 'info-circle';
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refresh();
            });
        }

        // Activity filters
        document.querySelectorAll('.filter-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                // Update active state
                document.querySelectorAll('.filter-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');

                // Update filter and re-render
                this.currentFilter = e.target.dataset.filter;
                this.renderActivities();
            });
        });

        // Policy search
        const policySearch = document.getElementById('policySearch');
        if (policySearch) {
            policySearch.addEventListener('input', (e) => {
                this.searchPolicies(e.target.value);
            });
        }

        // Simulate policy button
        const simulatePolicyBtn = document.getElementById('simulatePolicyBtn');
        if (simulatePolicyBtn) {
            simulatePolicyBtn.addEventListener('click', () => {
                this.simulatePolicy();
            });
        }

        // Listen to WebSocket events
        wsManager.on('activity', (activity) => {
            this.addActivity(activity);
        });

        wsManager.on('metricUpdate', (data) => {
            this.handleMetricUpdate(data);
        });
    }

    async refresh() {
        const refreshBtn = document.getElementById('refreshBtn');
        const icon = refreshBtn.querySelector('i');
        
        // Add rotation animation
        icon.style.animation = 'spin 1s linear';
        
        await this.loadDashboardData();
        
        // Remove animation after 1 second
        setTimeout(() => {
            icon.style.animation = '';
        }, 1000);

        agentManager.showNotification('Dashboard refreshed', 'success');
    }

    addActivity(activity) {
        // Add to beginning of activities array
        this.activities.unshift(activity);
        
        // Keep only last 50 activities
        if (this.activities.length > 50) {
            this.activities = this.activities.slice(0, 50);
        }
        
        // Re-render if current filter matches
        if (this.currentFilter === 'all' || this.currentFilter === activity.type) {
            this.renderActivities();
        }
    }

    handleMetricUpdate(data) {
        if (data.type === 'system_health') {
            this.updateStat('systemHealth', data.value + '%');
        }
    }

    searchPolicies(query) {
        const policyItems = document.querySelectorAll('.policy-item');
        const searchLower = query.toLowerCase();

        policyItems.forEach(item => {
            const title = item.querySelector('h4').textContent.toLowerCase();
            const description = item.querySelector('p').textContent.toLowerCase();
            
            if (title.includes(searchLower) || description.includes(searchLower)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    async simulatePolicy() {
        agentManager.showNotification('Running policy simulation...', 'info');
        
        // Simulate delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const results = {
            passed: Math.floor(Math.random() * 50) + 150,
            failed: Math.floor(Math.random() * 10),
            warnings: Math.floor(Math.random() * 20)
        };

        const message = `Simulation complete: ${results.passed} passed, ${results.failed} failed, ${results.warnings} warnings`;
        agentManager.showNotification(message, results.failed > 0 ? 'warning' : 'success');
    }

    startAutoRefresh() {
        // Auto-refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    destroy() {
        this.stopAutoRefresh();
        chartManager.destroyAllCharts();
        agentManager.destroy();
    }
}

// Add rotation animation for refresh button
const rotationStyle = document.createElement('style');
rotationStyle.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(rotationStyle);

// Initialize dashboard when DOM is ready
let dashboard;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        dashboard = new Dashboard();
        dashboard.initialize();
    });
} else {
    dashboard = new Dashboard();
    dashboard.initialize();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboard) {
        dashboard.destroy();
    }
    wsManager.disconnect();
});
