/**
 * API Integration for AI Agent
 * Handles external LLM API calls with fallbacks
 */

class APIIntegration {
    constructor() {
        this.apiKey = null;
        this.apiEndpoint = null;
        this.provider = 'local'; // 'openai', 'claude', 'local'
        this.rateLimitDelay = 1000; // 1 second between requests
        this.lastRequestTime = 0;
        this.requestCount = 0;
        this.maxRequestsPerHour = 60;
        
        this.loadConfig();
    }

    /**
     * Load API configuration
     */
    loadConfig() {
        // In a real implementation, load from environment variables
        // For security, never commit API keys to code
        
        // Check for environment variables (would be set in deployment)
        if (typeof process !== 'undefined' && process.env) {
            this.apiKey = process.env.OPENAI_API_KEY || process.env.CLAUDE_API_KEY;
            this.provider = process.env.AI_PROVIDER || 'local';
        }

        // Check localStorage for user-provided keys (optional feature)
        try {
            const savedConfig = localStorage.getItem('aiConfig');
            if (savedConfig) {
                const config = JSON.parse(savedConfig);
                if (config.apiKey && config.provider) {
                    this.apiKey = config.apiKey;
                    this.provider = config.provider;
                }
            }
        } catch (error) {
            console.error('Error loading API config:', error);
        }
    }

    /**
     * Save API configuration
     */
    saveConfig(apiKey, provider) {
        try {
            localStorage.setItem('aiConfig', JSON.stringify({
                apiKey,
                provider
            }));
            this.apiKey = apiKey;
            this.provider = provider;
            return true;
        } catch (error) {
            console.error('Error saving API config:', error);
            return false;
        }
    }

    /**
     * Check if API is available
     */
    isAPIAvailable() {
        return this.apiKey && this.provider !== 'local';
    }

    /**
     * Check rate limit
     */
    checkRateLimit() {
        const now = Date.now();
        const hourAgo = now - (60 * 60 * 1000);
        
        // Reset counter if more than an hour has passed
        if (now - this.lastRequestTime > 60 * 60 * 1000) {
            this.requestCount = 0;
        }

        // Check if within rate limit
        if (this.requestCount >= this.maxRequestsPerHour) {
            throw new Error('Rate limit exceeded. Please try again later.');
        }

        // Check minimum delay between requests
        if (now - this.lastRequestTime < this.rateLimitDelay) {
            return false;
        }

        return true;
    }

    /**
     * Send request to OpenAI API
     */
    async sendToOpenAI(message, context) {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
                messages: [
                    {
                        role: 'system',
                        content: this.getSystemPrompt()
                    },
                    ...context,
                    {
                        role: 'user',
                        content: message
                    }
                ],
                temperature: 0.7,
                max_tokens: 300
            })
        });

        if (!response.ok) {
            throw new Error(`OpenAI API error: ${response.status}`);
        }

        const data = await response.json();
        return data.choices[0].message.content;
    }

    /**
     * Send request to Claude API
     */
    async sendToClaude(message, context) {
        const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': this.apiKey,
                'anthropic-version': '2023-06-01'
            },
            body: JSON.stringify({
                model: 'claude-3-haiku-20240307',
                max_tokens: 300,
                system: this.getSystemPrompt(),
                messages: [
                    ...context,
                    {
                        role: 'user',
                        content: message
                    }
                ]
            })
        });

        if (!response.ok) {
            throw new Error(`Claude API error: ${response.status}`);
        }

        const data = await response.json();
        return data.content[0].text;
    }

    /**
     * Get system prompt for AI models
     */
    getSystemPrompt() {
        return `You are an AI assistant for Stacey Williams, a Certified Service Technician at Mercedes Benz Of Collierville. 

Your role is to help visitors by:
- Answering questions about Mercedes-Benz services
- Providing information about business hours, location, and contact details
- Helping schedule service appointments
- Offering technical advice about Mercedes-Benz vehicles
- Being friendly, professional, and helpful

Business Information:
- Name: Stacey Williams
- Title: Certified Service Technician
- Company: Mercedes Benz Of Collierville
- Phone: (901) 555-5555
- Email: stacey.williams@mbofcollierville.com
- Address: 850 W Poplar Ave, Collierville, TN 38017
- Hours: Mon-Fri 7:00 AM - 6:00 PM, Sat 8:00 AM - 4:00 PM, Sun Closed

Keep responses concise, friendly, and focused on helping the visitor. If you don't know something specific, direct them to call or email for more information.`;
    }

    /**
     * Send message to appropriate API
     */
    async sendMessage(message, conversationHistory = []) {
        // Check if API is available
        if (!this.isAPIAvailable()) {
            throw new Error('API not configured');
        }

        // Check rate limit
        if (!this.checkRateLimit()) {
            throw new Error('Rate limit - please wait a moment');
        }

        // Update request tracking
        this.lastRequestTime = Date.now();
        this.requestCount++;

        // Format conversation context
        const context = conversationHistory.map(msg => ({
            role: msg.role === 'assistant' ? 'assistant' : 'user',
            content: msg.message
        }));

        try {
            let response;

            switch (this.provider) {
                case 'openai':
                    response = await this.sendToOpenAI(message, context);
                    break;
                
                case 'claude':
                    response = await this.sendToClaude(message, context);
                    break;
                
                default:
                    throw new Error('Unknown provider');
            }

            return response;

        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Test API connection
     */
    async testConnection() {
        try {
            const response = await this.sendMessage('Hello, this is a test message.');
            return {
                success: true,
                message: 'API connection successful',
                response: response
            };
        } catch (error) {
            return {
                success: false,
                message: error.message,
                response: null
            };
        }
    }

    /**
     * Get usage statistics
     */
    getUsageStats() {
        return {
            provider: this.provider,
            requestCount: this.requestCount,
            maxRequests: this.maxRequestsPerHour,
            remaining: this.maxRequestsPerHour - this.requestCount,
            lastRequest: new Date(this.lastRequestTime).toISOString()
        };
    }

    /**
     * Reset rate limit counter
     */
    resetRateLimit() {
        this.requestCount = 0;
        this.lastRequestTime = 0;
    }
}

// Create global instance
const apiIntegration = new APIIntegration();
