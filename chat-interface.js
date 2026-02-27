/**
 * Chat Interface Handler
 * Manages the AI chat UI and user interactions
 */

class ChatInterface {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.init();
    }

    /**
     * Initialize chat interface
     */
    init() {
        // Get DOM elements
        this.chatToggle = document.getElementById('ai-chat-toggle');
        this.chatContainer = document.getElementById('ai-chat-container');
        this.closeBtn = document.getElementById('ai-close-btn');
        this.messagesContainer = document.getElementById('ai-chat-messages');
        this.input = document.getElementById('ai-chat-input');
        this.sendBtn = document.getElementById('ai-send-btn');
        this.typingIndicator = document.getElementById('ai-typing-indicator');

        // Bind event listeners
        this.bindEvents();

        // Load conversation history from localStorage
        this.loadHistory();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Toggle chat
        this.chatToggle.addEventListener('click', () => this.toggleChat());
        this.closeBtn.addEventListener('click', () => this.closeChat());

        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Quick action buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-action-btn')) {
                this.handleQuickAction(e.target.dataset.action);
            }
        });

        // Auto-resize input
        this.input.addEventListener('input', () => {
            this.input.style.height = 'auto';
            this.input.style.height = this.input.scrollHeight + 'px';
        });
    }

    /**
     * Toggle chat open/closed
     */
    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    /**
     * Open chat
     */
    openChat() {
        this.isOpen = true;
        this.chatContainer.classList.add('open');
        this.chatToggle.classList.add('active');
        this.input.focus();
        
        // Scroll to bottom
        this.scrollToBottom();

        // Mark as read
        this.clearBadge();
    }

    /**
     * Close chat
     */
    closeChat() {
        this.isOpen = false;
        this.chatContainer.classList.remove('open');
        this.chatToggle.classList.remove('active');
    }

    /**
     * Send message
     */
    async sendMessage() {
        const message = this.input.value.trim();
        
        if (!message) return;

        // Clear input
        this.input.value = '';
        this.input.style.height = 'auto';

        // Add user message to UI
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTyping();

        // Get AI response
        try {
            const response = await aiAgent.processMessage(message);
            
            // Simulate typing delay for natural feel
            await this.delay(800 + Math.random() * 400);

            // Hide typing indicator
            this.hideTyping();

            // Add bot response to UI
            this.addMessage(response.message, 'bot', response.suggestions);

            // Save to history
            this.saveHistory();

        } catch (error) {
            console.error('Error processing message:', error);
            this.hideTyping();
            this.addMessage(
                "I apologize, but I'm having trouble processing your request. Please try calling us at (901) 555-5555.",
                'bot'
            );
        }
    }

    /**
     * Add message to chat
     */
    addMessage(text, sender, suggestions = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ai-message-${sender}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-message-content';

        const textP = document.createElement('p');
        textP.textContent = text;
        textP.style.whiteSpace = 'pre-line'; // Preserve line breaks
        contentDiv.appendChild(textP);

        // Add suggestions if provided
        if (suggestions && suggestions.length > 0) {
            const suggestionsDiv = document.createElement('div');
            suggestionsDiv.className = 'ai-quick-actions';
            
            suggestions.forEach(suggestion => {
                const btn = document.createElement('button');
                btn.className = 'quick-action-btn';
                btn.textContent = suggestion;
                btn.onclick = () => this.handleSuggestionClick(suggestion);
                suggestionsDiv.appendChild(btn);
            });

            contentDiv.appendChild(suggestionsDiv);
        }

        messageDiv.appendChild(contentDiv);
        this.messagesContainer.appendChild(messageDiv);

        // Scroll to bottom
        this.scrollToBottom();

        // Animate in
        setTimeout(() => {
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 10);
    }

    /**
     * Handle quick action button click
     */
    handleQuickAction(action) {
        const actionMessages = {
            'services': 'What services do you offer?',
            'hours': 'What are your business hours?',
            'appointment': 'I would like to schedule a service appointment',
            'location': 'Where are you located?'
        };

        const message = actionMessages[action];
        if (message) {
            this.input.value = message;
            this.sendMessage();
        }
    }

    /**
     * Handle suggestion click
     */
    handleSuggestionClick(suggestion) {
        this.input.value = suggestion;
        this.sendMessage();
    }

    /**
     * Show typing indicator
     */
    showTyping() {
        this.isTyping = true;
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    hideTyping() {
        this.isTyping = false;
        this.typingIndicator.style.display = 'none';
    }

    /**
     * Scroll to bottom of messages
     */
    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    /**
     * Show notification badge
     */
    showBadge(count = 1) {
        const badge = document.getElementById('ai-badge');
        if (badge) {
            badge.textContent = count > 9 ? '9+' : count;
            badge.style.display = 'block';
        }
    }

    /**
     * Clear notification badge
     */
    clearBadge() {
        const badge = document.getElementById('ai-badge');
        if (badge) {
            badge.style.display = 'none';
        }
    }

    /**
     * Save conversation history to localStorage
     */
    saveHistory() {
        try {
            const history = aiAgent.exportHistory();
            localStorage.setItem('aiChatHistory', history);
        } catch (error) {
            console.error('Error saving chat history:', error);
        }
    }

    /**
     * Load conversation history from localStorage
     */
    loadHistory() {
        try {
            const history = localStorage.getItem('aiChatHistory');
            if (history) {
                const messages = JSON.parse(history);
                // Only load recent messages (last 10)
                const recentMessages = messages.slice(-10);
                
                recentMessages.forEach(msg => {
                    if (msg.role === 'user' || msg.role === 'assistant') {
                        this.addMessage(
                            msg.message,
                            msg.role === 'user' ? 'user' : 'bot'
                        );
                    }
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    /**
     * Clear conversation history
     */
    clearHistory() {
        this.messagesContainer.innerHTML = `
            <div class="ai-message ai-message-bot">
                <div class="ai-message-content">
                    <p>👋 Hi! I'm Stacey's AI assistant. How can I help you today?</p>
                    <div class="ai-quick-actions">
                        <button class="quick-action-btn" data-action="services">Services Offered</button>
                        <button class="quick-action-btn" data-action="hours">Business Hours</button>
                        <button class="quick-action-btn" data-action="appointment">Schedule Service</button>
                        <button class="quick-action-btn" data-action="location">Location & Directions</button>
                    </div>
                </div>
            </div>
        `;
        
        aiAgent.clearHistory();
        localStorage.removeItem('aiChatHistory');
    }

    /**
     * Delay helper
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Show welcome message for first-time visitors
     */
    showWelcome() {
        // Check if user has visited before
        const hasVisited = localStorage.getItem('hasVisited');
        
        if (!hasVisited) {
            setTimeout(() => {
                this.showBadge(1);
                localStorage.setItem('hasVisited', 'true');
            }, 3000);
        }
    }
}

// Initialize chat interface when DOM is ready
let chatInterface;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        chatInterface = new ChatInterface();
        chatInterface.showWelcome();
    });
} else {
    chatInterface = new ChatInterface();
    chatInterface.showWelcome();
}
