/**
 * AI Agent Core Functionality
 * Handles intelligent response generation and conversation management
 */

class AIAgent {
    constructor() {
        this.conversationHistory = [];
        this.context = {
            userName: null,
            lastIntent: null,
            lastService: null,
            conversationCount: 0
        };
        this.isTyping = false;
        this.useAPI = false; // Set to true when API is configured
    }

    /**
     * Process user message and generate response
     */
    async processMessage(userMessage) {
        this.conversationHistory.push({
            role: 'user',
            message: userMessage,
            timestamp: new Date()
        });

        this.context.conversationCount++;

        // Detect intent from message
        const intent = this.detectIntent(userMessage);
        this.context.lastIntent = intent;

        // Generate response based on intent
        let response;
        
        if (this.useAPI) {
            // Use API integration if available
            response = await this.getAPIResponse(userMessage, intent);
        } else {
            // Use local knowledge base
            response = this.getLocalResponse(userMessage, intent);
        }

        this.conversationHistory.push({
            role: 'assistant',
            message: response,
            timestamp: new Date()
        });

        return {
            message: response,
            intent: intent,
            suggestions: this.getSuggestions(intent)
        };
    }

    /**
     * Detect user intent from message
     */
    detectIntent(message) {
        const lowerMessage = message.toLowerCase();
        
        // Check for multiple intents
        for (const [intent, keywords] of Object.entries(KnowledgeBase.intents)) {
            for (const keyword of keywords) {
                if (lowerMessage.includes(keyword)) {
                    return intent;
                }
            }
        }

        // Check for specific service mentions
        for (const service of KnowledgeBase.services) {
            if (lowerMessage.includes(service.name.toLowerCase())) {
                return 'services';
            }
        }

        // Check for common issues
        for (const issue of KnowledgeBase.commonIssues) {
            if (lowerMessage.includes(issue.issue.toLowerCase())) {
                return 'urgent';
            }
        }

        return 'unknown';
    }

    /**
     * Generate response from local knowledge base
     */
    getLocalResponse(message, intent) {
        const lowerMessage = message.toLowerCase();

        switch (intent) {
            case 'greeting':
                return this.getRandomResponse(KnowledgeBase.responses.greeting);

            case 'hours':
                return this.getHoursResponse();

            case 'services':
                return this.getServicesResponse(message);

            case 'appointment':
                return this.getRandomResponse(KnowledgeBase.responses.appointment);

            case 'location':
                return this.getRandomResponse(KnowledgeBase.responses.location);

            case 'contact':
                return this.getRandomResponse(KnowledgeBase.responses.contact);

            case 'price':
                return "Service costs vary depending on the specific work needed. For an accurate quote, please call us at (901) 555-5555 or schedule a free inspection.";

            case 'urgent':
                return this.getUrgentResponse(message);

            case 'thanks':
                return this.getRandomResponse(KnowledgeBase.responses.thanks);

            case 'models':
                return "Yes! Stacey is a certified technician who works on all Mercedes-Benz models including C-Class, E-Class, S-Class, GLE, GLC, AMG models, and more. What model do you have?";

            case 'warranty':
                return this.getWarrantyResponse();

            default:
                // Try to find matching FAQ
                const faq = this.findMatchingFAQ(message);
                if (faq) {
                    return faq.answer;
                }
                return this.getRandomResponse(KnowledgeBase.responses.unknown);
        }
    }

    /**
     * Get business hours response
     */
    getHoursResponse() {
        const hours = KnowledgeBase.business.hours;
        return `Our service hours are:\n\n` +
               `Monday-Friday: ${hours.monday}\n` +
               `Saturday: ${hours.saturday}\n` +
               `Sunday: ${hours.sunday}\n\n` +
               `Feel free to call us at ${KnowledgeBase.business.phone} to schedule!`;
    }

    /**
     * Get services response
     */
    getServicesResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        // Check if asking about specific service
        for (const service of KnowledgeBase.services) {
            if (lowerMessage.includes(service.name.toLowerCase())) {
                return `${service.name}: ${service.description}. ` +
                       `Typical duration: ${service.duration}. ` +
                       `Would you like to schedule this service?`;
            }
        }

        // General services response
        const servicesList = KnowledgeBase.services
            .map(s => `• ${s.name}`)
            .join('\n');
        
        return `We offer comprehensive Mercedes-Benz services including:\n\n${servicesList}\n\n` +
               `All services are performed by certified technicians using genuine Mercedes-Benz parts. ` +
               `What service are you interested in?`;
    }

    /**
     * Get urgent response for common issues
     */
    getUrgentResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        for (const issue of KnowledgeBase.commonIssues) {
            if (lowerMessage.includes(issue.issue.toLowerCase())) {
                return issue.response;
            }
        }

        return "It sounds like you may have an urgent issue. Please call us immediately at (901) 555-5555 so we can help you right away. Your safety is our priority!";
    }

    /**
     * Get warranty information response
     */
    getWarrantyResponse() {
        return "All our repairs come with comprehensive warranty coverage:\n\n" +
               "• Mercedes-Benz genuine parts include manufacturer warranty\n" +
               "• Our labor is fully guaranteed\n" +
               "• We honor all Mercedes-Benz factory warranties\n\n" +
               "Would you like more details about warranty coverage for a specific service?";
    }

    /**
     * Find matching FAQ
     */
    findMatchingFAQ(message) {
        const lowerMessage = message.toLowerCase();
        
        for (const faq of KnowledgeBase.faqs) {
            for (const keyword of faq.keywords) {
                if (lowerMessage.includes(keyword)) {
                    return faq;
                }
            }
        }
        
        return null;
    }

    /**
     * Get random response from array
     */
    getRandomResponse(responses) {
        return responses[Math.floor(Math.random() * responses.length)];
    }

    /**
     * Get suggestions based on intent
     */
    getSuggestions(intent) {
        switch (intent) {
            case 'greeting':
                return ['Services Offered', 'Business Hours', 'Schedule Appointment'];
            case 'services':
                return ['Schedule Service', 'Get Quote', 'View All Services'];
            case 'appointment':
                return ['Call Now', 'Business Hours', 'Location'];
            case 'hours':
                return ['Schedule Appointment', 'Services', 'Contact Info'];
            case 'location':
                return ['Get Directions', 'Call Us', 'Business Hours'];
            default:
                return ['Services', 'Schedule Appointment', 'Contact Us'];
        }
    }

    /**
     * Get API response (when API is configured)
     */
    async getAPIResponse(message, intent) {
        try {
            // This would integrate with OpenAI, Claude, or similar
            // For now, fall back to local response
            return this.getLocalResponse(message, intent);
        } catch (error) {
            console.error('API error:', error);
            return this.getLocalResponse(message, intent);
        }
    }

    /**
     * Analyze sentiment and urgency
     */
    analyzeSentiment(message) {
        const urgentWords = ['urgent', 'emergency', 'asap', 'immediately', 'help', 'problem', 'issue', 'broken'];
        const lowerMessage = message.toLowerCase();
        
        let urgency = 'low';
        let sentiment = 'neutral';

        // Check urgency
        if (urgentWords.some(word => lowerMessage.includes(word))) {
            urgency = 'high';
        }

        // Check sentiment
        const positiveWords = ['great', 'excellent', 'good', 'thank', 'appreciate', 'love', 'perfect'];
        const negativeWords = ['bad', 'terrible', 'awful', 'disappointed', 'frustrated', 'angry'];

        if (positiveWords.some(word => lowerMessage.includes(word))) {
            sentiment = 'positive';
        } else if (negativeWords.some(word => lowerMessage.includes(word))) {
            sentiment = 'negative';
        }

        return { urgency, sentiment };
    }

    /**
     * Get conversation context
     */
    getContext() {
        return {
            ...this.context,
            historyLength: this.conversationHistory.length,
            lastMessage: this.conversationHistory[this.conversationHistory.length - 1]
        };
    }

    /**
     * Clear conversation history
     */
    clearHistory() {
        this.conversationHistory = [];
        this.context = {
            userName: null,
            lastIntent: null,
            lastService: null,
            conversationCount: 0
        };
    }

    /**
     * Export conversation history
     */
    exportHistory() {
        return JSON.stringify(this.conversationHistory, null, 2);
    }
}

// Create global instance
const aiAgent = new AIAgent();
