// API Integration Layer
class API {
    constructor() {
        this.baseUrl = '/api'; // Change to actual API endpoint
        this.mockMode = true; // Set to false when real API is available
    }

    // Generic request method
    async request(endpoint, options = {}) {
        if (this.mockMode) {
            return this.mockRequest(endpoint, options);
        }

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Mock request handler for development
    async mockRequest(endpoint, options = {}) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 300));

        // Load mock data
        const mockData = await this.loadMockData();

        // Route mock requests
        if (endpoint.includes('/agents')) {
            return mockData.agents;
        } else if (endpoint.includes('/activities')) {
            return mockData.activities;
        } else if (endpoint.includes('/policies')) {
            return mockData.policies;
        } else if (endpoint.includes('/metrics')) {
            return mockData.metrics;
        } else if (endpoint.includes('/regions')) {
            return mockData.regions;
        } else if (endpoint.includes('/blast-radius')) {
            return mockData.blastRadius;
        }

        return mockData;
    }

    // Load mock data from JSON file
    async loadMockData() {
        try {
            const response = await fetch('data/mock-data.json');
            return await response.json();
        } catch (error) {
            console.error('Failed to load mock data:', error);
            return this.getDefaultMockData();
        }
    }

    // Default mock data if JSON file is not available
    getDefaultMockData() {
        return {
            platform: {
                status: 'operational',
                activeAgents: 4,
                queueSize: 12,
                systemHealth: 98
            },
            agents: [
                {
                    id: 'policy',
                    name: 'Policy Agent',
                    status: 'active',
                    metrics: {
                        policiesEnforced: 247,
                        violations: 3,
                        lastCheck: '2 min ago'
                    }
                },
                {
                    id: 'intent',
                    name: 'Intent Agent',
                    status: 'active',
                    metrics: {
                        activeIntents: 8,
                        scriptsGenerated: 156,
                        queueSize: 5
                    }
                },
                {
                    id: 'deployment',
                    name: 'Deployment Agent',
                    status: 'active',
                    metrics: {
                        activeDeployments: 12,
                        regions: 5,
                        successRate: '99.2%'
                    }
                },
                {
                    id: 'compliance',
                    name: 'Compliance Agent',
                    status: 'active',
                    metrics: {
                        complianceScore: '96%',
                        auditEvents: 1234,
                        markers: 45
                    }
                }
            ],
            activities: [
                {
                    type: 'policy',
                    title: 'Policy Violation Detected',
                    description: 'Cost threshold exceeded in us-east-1',
                    time: '2 minutes ago'
                },
                {
                    type: 'deployment',
                    title: 'Deployment Completed',
                    description: 'Successfully deployed version 2.1.4 to production',
                    time: '15 minutes ago'
                },
                {
                    type: 'compliance',
                    title: 'Compliance Check Passed',
                    description: 'All resources meet compliance requirements',
                    time: '1 hour ago'
                }
            ],
            policies: [
                {
                    id: 'pol-1',
                    name: 'Resource Quota Enforcement',
                    description: 'Ensures CPU and memory limits are not exceeded',
                    status: 'active',
                    enforced: 247
                },
                {
                    id: 'pol-2',
                    name: 'Security Group Validation',
                    description: 'Validates security group rules against best practices',
                    status: 'active',
                    enforced: 89
                },
                {
                    id: 'pol-3',
                    name: 'Cost Threshold Alert',
                    description: 'Alerts when spending exceeds budget thresholds',
                    status: 'warning',
                    violations: 3,
                    checks: 156
                }
            ],
            metrics: {
                bandwidth: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    data: [65, 59, 80, 81, 56, 55, 40]
                },
                compute: {
                    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
                    data: [75, 82, 88, 91, 85, 78]
                },
                storage: {
                    used: 67,
                    free: 33
                },
                costTrend: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    data: [1200, 1150, 1100, 1050, 1080, 1020]
                }
            },
            regions: [
                { id: 'us-east', name: 'US East', status: 'healthy' },
                { id: 'us-west', name: 'US West', status: 'healthy' },
                { id: 'eu-central', name: 'EU Central', status: 'healthy' },
                { id: 'asia-pacific', name: 'Asia Pacific', status: 'warning' },
                { id: 'south-america', name: 'South America', status: 'healthy' }
            ],
            blastRadius: {
                riskLevel: 'medium',
                affectedResources: 24,
                impactedUsers: 156,
                categories: ['Compute', 'Storage', 'Network', 'Security'],
                values: [12, 5, 4, 3]
            }
        };
    }

    // API Methods
    async getPlatformStatus() {
        return this.request('/platform/status');
    }

    async getAgents() {
        return this.request('/agents');
    }

    async getAgentStatus(agentId) {
        return this.request(`/agents/${agentId}`);
    }

    async startAgent(agentId) {
        return this.request(`/agents/${agentId}/start`, { method: 'POST' });
    }

    async stopAgent(agentId) {
        return this.request(`/agents/${agentId}/stop`, { method: 'POST' });
    }

    async getActivities(filter = 'all') {
        return this.request(`/activities?filter=${filter}`);
    }

    async getPolicies() {
        return this.request('/policies');
    }

    async getMetrics() {
        return this.request('/metrics');
    }

    async getRegions() {
        return this.request('/regions');
    }

    async getBlastRadius() {
        return this.request('/blast-radius');
    }

    async simulatePolicy(policyId) {
        return this.request(`/policies/${policyId}/simulate`, { method: 'POST' });
    }

    async exportComplianceReport(format = 'pdf') {
        return this.request(`/compliance/export?format=${format}`);
    }
}

// Export API instance
const api = new API();
