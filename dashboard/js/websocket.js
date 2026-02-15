// WebSocket Manager for Real-Time Updates
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.listeners = {};
        this.simulationMode = true; // Set to false when real WebSocket is available
        this.simulationInterval = null;
    }

    connect(url = 'ws://localhost:8080') {
        if (this.simulationMode) {
            this.startSimulation();
            return;
        }

        try {
            this.ws = new WebSocket(url);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                this.emit('connected');
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.emit('error', error);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus(false);
                this.emit('disconnected');
                this.attemptReconnect();
            };
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }

    disconnect() {
        if (this.simulationMode) {
            this.stopSimulation();
        } else if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    send(message) {
        if (this.simulationMode) {
            console.log('Simulation mode: Message not sent', message);
            return;
        }

        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket is not connected');
        }
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    off(event, callback) {
        if (!this.listeners[event]) return;
        
        this.listeners[event] = this.listeners[event].filter(
            listener => listener !== callback
        );
    }

    emit(event, data) {
        if (!this.listeners[event]) return;
        
        this.listeners[event].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('Error in event listener:', error);
            }
        });
    }

    handleMessage(data) {
        const { type, payload } = data;
        
        switch (type) {
            case 'agent_status':
                this.emit('agentStatus', payload);
                break;
            case 'activity':
                this.emit('activity', payload);
                break;
            case 'metric_update':
                this.emit('metricUpdate', payload);
                break;
            case 'policy_violation':
                this.emit('policyViolation', payload);
                break;
            case 'deployment_event':
                this.emit('deploymentEvent', payload);
                break;
            case 'compliance_alert':
                this.emit('complianceAlert', payload);
                break;
            default:
                console.log('Unknown message type:', type);
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

        setTimeout(() => {
            this.connect();
        }, this.reconnectDelay);
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('wsStatus');
        if (!statusElement) return;

        const statusDot = statusElement.querySelector('.status-dot');
        const statusText = statusElement.querySelector('.status-text');

        if (connected) {
            statusDot.style.background = 'var(--status-success)';
            statusText.textContent = 'Connected';
        } else {
            statusDot.style.background = 'var(--status-error)';
            statusText.textContent = 'Disconnected';
        }
    }

    // Simulation mode methods
    startSimulation() {
        console.log('Starting WebSocket simulation mode');
        this.updateConnectionStatus(true);
        this.emit('connected');

        // Simulate real-time updates every 5 seconds
        this.simulationInterval = setInterval(() => {
            this.simulateUpdate();
        }, 5000);
    }

    stopSimulation() {
        if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
            this.simulationInterval = null;
        }
        this.updateConnectionStatus(false);
    }

    simulateUpdate() {
        const updateTypes = [
            'agent_status',
            'activity',
            'metric_update'
        ];

        const randomType = updateTypes[Math.floor(Math.random() * updateTypes.length)];
        
        switch (randomType) {
            case 'agent_status':
                this.emit('agentStatus', {
                    agentId: ['policy', 'intent', 'deployment', 'compliance'][Math.floor(Math.random() * 4)],
                    status: 'active',
                    timestamp: new Date().toISOString()
                });
                break;

            case 'activity':
                const activities = [
                    {
                        type: 'policy',
                        title: 'Policy Check Completed',
                        description: 'All policies validated successfully',
                        time: 'just now'
                    },
                    {
                        type: 'deployment',
                        title: 'Deployment Initiated',
                        description: 'Starting deployment to us-west-2',
                        time: 'just now'
                    },
                    {
                        type: 'compliance',
                        title: 'Audit Event Recorded',
                        description: 'Configuration change logged',
                        time: 'just now'
                    }
                ];
                this.emit('activity', activities[Math.floor(Math.random() * activities.length)]);
                break;

            case 'metric_update':
                this.emit('metricUpdate', {
                    type: 'system_health',
                    value: 95 + Math.floor(Math.random() * 5),
                    timestamp: new Date().toISOString()
                });
                break;
        }
    }
}

// Export WebSocket manager instance
const wsManager = new WebSocketManager();

// Auto-connect on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        wsManager.connect();
    });
} else {
    wsManager.connect();
}
