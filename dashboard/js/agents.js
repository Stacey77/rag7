// Agent Management Module
class AgentManager {
    constructor() {
        this.agents = [];
        this.updateInterval = null;
    }

    async initialize() {
        await this.loadAgents();
        this.setupEventListeners();
        this.startAutoUpdate();
    }

    async loadAgents() {
        try {
            const data = await api.getDefaultMockData();
            this.agents = data.agents;
            this.updateAgentCards();
        } catch (error) {
            console.error('Failed to load agents:', error);
        }
    }

    updateAgentCards() {
        this.agents.forEach(agent => {
            const card = document.querySelector(`.agent-card[data-agent="${agent.id}"]`);
            if (!card) return;

            // Update status
            const statusElement = card.querySelector('.agent-status');
            if (statusElement) {
                statusElement.textContent = agent.status.charAt(0).toUpperCase() + agent.status.slice(1);
                statusElement.className = `agent-status ${agent.status}`;
            }

            // Update metrics
            const metrics = card.querySelectorAll('.metric-value');
            const metricValues = Object.values(agent.metrics);
            
            metrics.forEach((metric, index) => {
                if (metricValues[index] !== undefined) {
                    metric.textContent = metricValues[index];
                }
            });
        });
    }

    setupEventListeners() {
        // Agent control buttons
        document.querySelectorAll('.agent-card .btn-icon').forEach(button => {
            button.addEventListener('click', (e) => {
                const card = e.target.closest('.agent-card');
                const agentId = card.dataset.agent;
                this.toggleAgent(agentId);
            });
        });

        // Listen to WebSocket updates
        wsManager.on('agentStatus', (data) => {
            this.handleAgentStatusUpdate(data);
        });
    }

    async toggleAgent(agentId) {
        const agent = this.agents.find(a => a.id === agentId);
        if (!agent) return;

        try {
            if (agent.status === 'active') {
                await api.stopAgent(agentId);
                agent.status = 'inactive';
                this.showNotification(`${agent.name} stopped`, 'info');
            } else {
                await api.startAgent(agentId);
                agent.status = 'active';
                this.showNotification(`${agent.name} started`, 'success');
            }

            this.updateAgentCards();
            this.updateActiveAgentsCount();
        } catch (error) {
            console.error(`Failed to toggle agent ${agentId}:`, error);
            this.showNotification('Failed to update agent', 'error');
        }
    }

    handleAgentStatusUpdate(data) {
        const agent = this.agents.find(a => a.id === data.agentId);
        if (!agent) return;

        agent.status = data.status;
        this.updateAgentCards();
        this.updateActiveAgentsCount();
    }

    updateActiveAgentsCount() {
        const activeCount = this.agents.filter(a => a.status === 'active').length;
        const element = document.getElementById('activeAgents');
        if (element) {
            element.textContent = activeCount;
        }
    }

    startAutoUpdate() {
        // Update agent metrics every 5 seconds
        this.updateInterval = setInterval(async () => {
            await this.loadAgents();
        }, 5000);
    }

    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    getNotificationColor(type) {
        const colors = {
            success: 'rgba(76, 175, 80, 0.95)',
            error: 'rgba(239, 83, 80, 0.95)',
            warning: 'rgba(255, 167, 38, 0.95)',
            info: 'rgba(66, 165, 245, 0.95)'
        };
        return colors[type] || colors.info;
    }

    destroy() {
        this.stopAutoUpdate();
    }
}

// Add notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Export agent manager instance
const agentManager = new AgentManager();
