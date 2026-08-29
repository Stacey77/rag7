/**
 * Conversation Memory Service - Context persistence and history management
 * Stores conversation history in localStorage with session management
 */

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  metadata?: Record<string, unknown>;
}

export interface ConversationContext {
  sessionId: string;
  startTime: number;
  messageCount: number;
  lastActivity: number;
  metadata?: Record<string, unknown>;
}

const STORAGE_KEY_MESSAGES = 'ai_design_platform_conversation_history';
const STORAGE_KEY_CONTEXT = 'ai_design_platform_conversation_context';
const MAX_MESSAGES = 100;

class ConversationMemory {
  private messages: ConversationMessage[] = [];
  private context: ConversationContext;
  private sessionId: string;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.context = this.initializeContext();
    this.loadFromStorage();
  }

  /**
   * Generate unique session ID
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Initialize conversation context
   */
  private initializeContext(): ConversationContext {
    return {
      sessionId: this.sessionId,
      startTime: Date.now(),
      messageCount: 0,
      lastActivity: Date.now()
    };
  }

  /**
   * Load conversation history from localStorage
   */
  private loadFromStorage(): void {
    try {
      const storedMessages = localStorage.getItem(STORAGE_KEY_MESSAGES);
      const storedContext = localStorage.getItem(STORAGE_KEY_CONTEXT);

      if (storedMessages) {
        this.messages = JSON.parse(storedMessages);
      }

      if (storedContext) {
        const parsedContext = JSON.parse(storedContext);
        const timeSinceLastActivity = Date.now() - parsedContext.lastActivity;
        
        if (timeSinceLastActivity < 24 * 60 * 60 * 1000) {
          this.context = parsedContext;
          this.sessionId = parsedContext.sessionId;
        }
      }
    } catch (error) {
      console.error('Error loading conversation from storage:', error);
      this.messages = [];
    }
  }

  /**
   * Save conversation history to localStorage
   */
  private saveToStorage(): void {
    try {
      localStorage.setItem(STORAGE_KEY_MESSAGES, JSON.stringify(this.messages));
      localStorage.setItem(STORAGE_KEY_CONTEXT, JSON.stringify(this.context));
    } catch (error) {
      console.error('Error saving conversation to storage:', error);
    }
  }

  /**
   * Generate unique message ID
   */
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Trim messages to maximum limit
   */
  private trimMessages(): void {
    if (this.messages.length > MAX_MESSAGES) {
      this.messages = this.messages.slice(-MAX_MESSAGES);
    }
  }

  /**
   * Save a message to conversation history
   */
  public saveMessage(
    role: 'user' | 'assistant',
    content: string,
    metadata?: Record<string, unknown>
  ): ConversationMessage {
    const message: ConversationMessage = {
      id: this.generateMessageId(),
      role,
      content,
      timestamp: Date.now(),
      metadata
    };

    this.messages.push(message);
    this.trimMessages();

    this.context.messageCount = this.messages.length;
    this.context.lastActivity = Date.now();

    this.saveToStorage();

    return message;
  }

  /**
   * Get conversation history
   */
  public getHistory(limit?: number): ConversationMessage[] {
    if (limit && limit > 0) {
      return this.messages.slice(-limit);
    }
    return [...this.messages];
  }

  /**
   * Get messages by role
   */
  public getMessagesByRole(role: 'user' | 'assistant', limit?: number): ConversationMessage[] {
    const filtered = this.messages.filter(msg => msg.role === role);
    if (limit && limit > 0) {
      return filtered.slice(-limit);
    }
    return filtered;
  }

  /**
   * Get recent context (last N messages)
   */
  public getContext(messageCount: number = 10): ConversationMessage[] {
    return this.messages.slice(-messageCount);
  }

  /**
   * Get conversation summary
   */
  public getSummary(): {
    totalMessages: number;
    userMessages: number;
    assistantMessages: number;
    sessionDuration: number;
  } {
    const userMessages = this.messages.filter(msg => msg.role === 'user').length;
    const assistantMessages = this.messages.filter(msg => msg.role === 'assistant').length;
    const sessionDuration = Date.now() - this.context.startTime;

    return {
      totalMessages: this.messages.length,
      userMessages,
      assistantMessages,
      sessionDuration
    };
  }

  /**
   * Clear conversation history
   */
  public clearHistory(): void {
    this.messages = [];
    this.context = this.initializeContext();
    
    try {
      localStorage.removeItem(STORAGE_KEY_MESSAGES);
      localStorage.removeItem(STORAGE_KEY_CONTEXT);
    } catch (error) {
      console.error('Error clearing conversation storage:', error);
    }
  }

  /**
   * Search messages by content
   */
  public searchMessages(query: string): ConversationMessage[] {
    const lowerQuery = query.toLowerCase();
    return this.messages.filter(msg => 
      msg.content.toLowerCase().includes(lowerQuery)
    );
  }

  /**
   * Get session information
   */
  public getSessionInfo(): ConversationContext {
    return { ...this.context };
  }

  /**
   * Update session metadata
   */
  public updateMetadata(metadata: Record<string, unknown>): void {
    this.context.metadata = { ...this.context.metadata, ...metadata };
    this.saveToStorage();
  }

  /**
   * Export conversation as JSON
   */
  public exportConversation(): string {
    return JSON.stringify({
      context: this.context,
      messages: this.messages
    }, null, 2);
  }

  /**
   * Import conversation from JSON
   */
  public importConversation(json: string): boolean {
    try {
      const data = JSON.parse(json);
      if (data.messages && Array.isArray(data.messages)) {
        this.messages = data.messages;
        if (data.context) {
          this.context = data.context;
          this.sessionId = data.context.sessionId;
        }
        this.saveToStorage();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error importing conversation:', error);
      return false;
    }
  }
}

const conversationMemory = new ConversationMemory();

export const saveMessage = (
  role: 'user' | 'assistant',
  content: string,
  metadata?: Record<string, unknown>
): ConversationMessage => conversationMemory.saveMessage(role, content, metadata);

export const getHistory = (limit?: number): ConversationMessage[] => 
  conversationMemory.getHistory(limit);

export const clearHistory = (): void => conversationMemory.clearHistory();

export const getContext = (messageCount?: number): ConversationMessage[] => 
  conversationMemory.getContext(messageCount);

export const getMessagesByRole = (role: 'user' | 'assistant', limit?: number): ConversationMessage[] =>
  conversationMemory.getMessagesByRole(role, limit);

export const getSummary = () => conversationMemory.getSummary();

export const searchMessages = (query: string): ConversationMessage[] =>
  conversationMemory.searchMessages(query);

export const getSessionInfo = (): ConversationContext =>
  conversationMemory.getSessionInfo();

export const updateMetadata = (metadata: Record<string, unknown>): void =>
  conversationMemory.updateMetadata(metadata);

export const exportConversation = (): string =>
  conversationMemory.exportConversation();

export const importConversation = (json: string): boolean =>
  conversationMemory.importConversation(json);

export default conversationMemory;
