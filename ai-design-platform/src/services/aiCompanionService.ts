/**
 * AI Companion Service - Conversational AI with multiple personalities
 * Handles natural language conversations with context awareness
 */

import { classifyIntent, extractEntities, Intent, Entity } from './nlp/intentRecognition';
import { analyzeSentiment, detectEmotion, SentimentAnalysis, EmotionAnalysis } from './sentiment/sentimentAnalyzer';
import { saveMessage, getContext, clearHistory as clearMemoryHistory, getHistory, ConversationMessage } from './memory/conversationMemory';

export type AIPersonality = 'professional' | 'friendly' | 'teacher' | 'mentor';

export interface AIResponse {
  message: string;
  intent: Intent;
  sentiment: SentimentAnalysis;
  emotion: EmotionAnalysis;
  suggestions?: string[];
  actions?: AIAction[];
}

export interface AIAction {
  type: 'navigate' | 'execute' | 'display';
  target: string;
  parameters?: Record<string, unknown>;
}

interface PersonalityTrait {
  greeting: string[];
  responseStyle: string;
  helpfulness: number;
  formality: number;
  examples: string[];
}

const PERSONALITIES: Record<AIPersonality, PersonalityTrait> = {
  professional: {
    greeting: [
      'Hello. How may I assist you today?',
      'Good day. What can I help you with?',
      'Welcome. How can I be of service?'
    ],
    responseStyle: 'formal and concise',
    helpfulness: 0.8,
    formality: 0.9,
    examples: [
      'I can help you navigate the platform, analyze data, or answer questions about features.',
      'Please let me know if you need assistance with any specific functionality.'
    ]
  },
  friendly: {
    greeting: [
      'Hey there! How can I help you today?',
      'Hi! What would you like to do?',
      'Hello friend! Ready to create something awesome?'
    ],
    responseStyle: 'casual and warm',
    helpfulness: 0.9,
    formality: 0.3,
    examples: [
      "I'm here to help! Just let me know what you need.",
      "Let's make something great together!"
    ]
  },
  teacher: {
    greeting: [
      'Welcome! Ready to learn something new?',
      'Hello! I\'m here to guide you through the platform.',
      'Great to see you! What would you like to explore today?'
    ],
    responseStyle: 'educational and patient',
    helpfulness: 1.0,
    formality: 0.6,
    examples: [
      'Let me explain how this works...',
      'Here\'s what you need to know about this feature...',
      'Would you like me to show you step by step?'
    ]
  },
  mentor: {
    greeting: [
      'Hello! I\'m here to support your creative journey.',
      'Welcome back! How can I help you grow today?',
      'Great to see you! What are you working on?'
    ],
    responseStyle: 'supportive and insightful',
    helpfulness: 0.95,
    formality: 0.5,
    examples: [
      'Based on your experience, I recommend...',
      'Have you considered trying...',
      'This could be a great opportunity to...'
    ]
  }
};

const NAVIGATION_TARGETS: Record<string, string[]> = {
  dashboard: ['dashboard', 'home', 'main', 'overview'],
  models: ['models', 'ai models', 'model library', 'generators'],
  settings: ['settings', 'preferences', 'configuration', 'options'],
  profile: ['profile', 'account', 'user'],
  analytics: ['analytics', 'stats', 'statistics', 'metrics'],
  history: ['history', 'past', 'previous', 'recent']
};

class AICompanionService {
  private currentPersonality: AIPersonality = 'mentor';
  private conversationContext: ConversationMessage[] = [];
  private maxContextMessages = 10;

  constructor() {
    this.loadContext();
  }

  /**
   * Load conversation context
   */
  private loadContext(): void {
    this.conversationContext = getContext(this.maxContextMessages);
  }

  /**
   * Generate response based on personality
   */
  private generatePersonalityResponse(
    intent: Intent,
    sentiment: SentimentAnalysis,
    emotion: EmotionAnalysis
  ): string {
    const personality = PERSONALITIES[this.currentPersonality];
    
    switch (intent.type) {
      case 'navigate':
        return this.generateNavigationResponse(intent, personality);
      
      case 'query':
        return this.generateQueryResponse(intent, personality);
      
      case 'command':
        return this.generateCommandResponse(intent, personality);
      
      case 'help':
        return this.generateHelpResponse(personality);
      
      case 'chat':
        return this.generateChatResponse(sentiment, emotion, personality);
      
      default:
        return this.generateDefaultResponse(personality);
    }
  }

  /**
   * Generate navigation response
   */
  private generateNavigationResponse(intent: Intent, personality: PersonalityTrait): string {
    const sectionEntity = intent.entities.find(e => e.type === 'section');
    
    if (!sectionEntity) {
      return personality.formality > 0.7
        ? 'I can help you navigate. Where would you like to go?'
        : 'Sure! Where do you want to go?';
    }

    const target = this.resolveNavigationTarget(sectionEntity.value);
    
    if (this.currentPersonality === 'teacher') {
      return `Let me take you to the ${target} section. This is where you can ${this.getFeatureDescription(target)}.`;
    } else if (this.currentPersonality === 'friendly') {
      return `Taking you to ${target} right now! 🚀`;
    } else {
      return `Navigating to ${target}.`;
    }
  }

  /**
   * Generate query response
   */
  private generateQueryResponse(intent: Intent, personality: PersonalityTrait): string {
    const responses: Record<AIPersonality, string> = {
      professional: 'I can provide information on that topic. What specifically would you like to know?',
      friendly: 'Great question! Let me help you with that.',
      teacher: 'Excellent question! Let me explain this in detail.',
      mentor: 'That\'s an important question. Here\'s what you should know...'
    };

    return responses[this.currentPersonality];
  }

  /**
   * Generate command response
   */
  private generateCommandResponse(intent: Intent, personality: PersonalityTrait): string {
    const actionEntity = intent.entities.find(e => e.type === 'action');
    
    if (!actionEntity) {
      return 'What would you like me to do?';
    }

    const action = actionEntity.value.toLowerCase();
    
    if (this.currentPersonality === 'teacher') {
      return `I'll help you ${action}. Here's how it works...`;
    } else if (this.currentPersonality === 'friendly') {
      return `On it! Let's ${action} together!`;
    } else {
      return `Processing ${action} request.`;
    }
  }

  /**
   * Generate help response
   */
  private generateHelpResponse(personality: PersonalityTrait): string {
    const helpMessages: Record<AIPersonality, string> = {
      professional: 'I can assist with navigation, feature explanations, and platform guidance. What do you need help with?',
      friendly: 'I\'m here to help! You can ask me to navigate anywhere, explain features, or just chat. What do you need?',
      teacher: 'I\'d be happy to teach you! I can explain features, guide you through processes, or answer questions. What would you like to learn?',
      mentor: 'I\'m here to support you. I can help with navigation, provide insights, or discuss your creative process. How can I assist?'
    };

    return helpMessages[this.currentPersonality];
  }

  /**
   * Generate chat response
   */
  private generateChatResponse(
    sentiment: SentimentAnalysis,
    emotion: EmotionAnalysis,
    personality: PersonalityTrait
  ): string {
    if (sentiment.sentiment === 'positive' && emotion.primaryEmotion === 'joy') {
      const positiveResponses: Record<AIPersonality, string> = {
        professional: 'I\'m pleased to hear that. How else may I assist you?',
        friendly: 'That\'s awesome! I\'m happy for you! 😊',
        teacher: 'Wonderful! It\'s great to see your enthusiasm!',
        mentor: 'That\'s excellent progress! Keep up the great work!'
      };
      return positiveResponses[this.currentPersonality];
    }

    if (sentiment.sentiment === 'negative') {
      const supportiveResponses: Record<AIPersonality, string> = {
        professional: 'I understand. How can I help address this concern?',
        friendly: 'I hear you. Let me see how I can help make this better!',
        teacher: 'I understand this can be challenging. Let me guide you through it.',
        mentor: 'I appreciate you sharing that. Let\'s work through this together.'
      };
      return supportiveResponses[this.currentPersonality];
    }

    return personality.examples[0] || 'I\'m here to help. What would you like to do?';
  }

  /**
   * Generate default response
   */
  private generateDefaultResponse(personality: PersonalityTrait): string {
    return personality.formality > 0.7
      ? 'How may I assist you?'
      : 'What can I help you with?';
  }

  /**
   * Resolve navigation target
   */
  private resolveNavigationTarget(input: string): string {
    const normalizedInput = input.toLowerCase();
    
    for (const [target, aliases] of Object.entries(NAVIGATION_TARGETS)) {
      if (aliases.some(alias => normalizedInput.includes(alias))) {
        return target;
      }
    }
    
    return input;
  }

  /**
   * Get feature description
   */
  private getFeatureDescription(section: string): string {
    const descriptions: Record<string, string> = {
      dashboard: 'view your overview and quick access features',
      models: 'explore and use various AI models',
      settings: 'customize your preferences and configuration',
      profile: 'manage your account information',
      analytics: 'review your usage statistics and insights',
      history: 'access your past activities and conversations'
    };

    return descriptions[section] || 'access this feature';
  }

  /**
   * Generate suggestions based on context
   */
  private generateSuggestions(intent: Intent): string[] {
    const suggestions: string[] = [];

    switch (intent.type) {
      case 'navigate':
        suggestions.push('View analytics', 'Open settings', 'Check history');
        break;
      case 'query':
        suggestions.push('Tell me more', 'Show examples', 'Explain in detail');
        break;
      case 'help':
        suggestions.push('Show tutorial', 'List features', 'Quick start guide');
        break;
      default:
        suggestions.push('What can you do?', 'Show help', 'Navigate to dashboard');
    }

    return suggestions;
  }

  /**
   * Generate actions based on intent
   */
  private generateActions(intent: Intent): AIAction[] {
    const actions: AIAction[] = [];

    if (intent.type === 'navigate') {
      const sectionEntity = intent.entities.find(e => e.type === 'section');
      if (sectionEntity) {
        const target = this.resolveNavigationTarget(sectionEntity.value);
        actions.push({
          type: 'navigate',
          target,
          parameters: { source: 'ai_companion' }
        });
      }
    }

    return actions;
  }

  /**
   * Send message to AI companion
   */
  public sendMessage(message: string): AIResponse {
    const intent = classifyIntent(message);
    const sentiment = analyzeSentiment(message);
    const emotion = detectEmotion(message);

    saveMessage('user', message, {
      intent: intent.type,
      sentiment: sentiment.sentiment,
      emotion: emotion.primaryEmotion
    });

    const responseMessage = this.generatePersonalityResponse(intent, sentiment, emotion);
    const suggestions = this.generateSuggestions(intent);
    const actions = this.generateActions(intent);

    saveMessage('assistant', responseMessage, {
      personality: this.currentPersonality,
      intent: intent.type
    });

    this.loadContext();

    return {
      message: responseMessage,
      intent,
      sentiment,
      emotion,
      suggestions,
      actions
    };
  }

  /**
   * Set AI personality
   */
  public setPersonality(personality: AIPersonality): void {
    this.currentPersonality = personality;
  }

  /**
   * Get current personality
   */
  public getPersonality(): AIPersonality {
    return this.currentPersonality;
  }

  /**
   * Get greeting message
   */
  public getGreeting(): string {
    const personality = PERSONALITIES[this.currentPersonality];
    const greetings = personality.greeting;
    return greetings[Math.floor(Math.random() * greetings.length)];
  }

  /**
   * Clear conversation history
   */
  public clearHistory(): void {
    clearMemoryHistory();
    this.conversationContext = [];
  }

  /**
   * Get conversation history
   */
  public getHistory(limit?: number): ConversationMessage[] {
    return getHistory(limit);
  }

  /**
   * Get personality description
   */
  public getPersonalityDescription(personality?: AIPersonality): string {
    const p = personality || this.currentPersonality;
    return PERSONALITIES[p].responseStyle;
  }
}

const aiCompanionService = new AICompanionService();

export const sendMessage = (message: string): AIResponse => 
  aiCompanionService.sendMessage(message);

export const setPersonality = (personality: AIPersonality): void => 
  aiCompanionService.setPersonality(personality);

export const getPersonality = (): AIPersonality => 
  aiCompanionService.getPersonality();

export const getGreeting = (): string => 
  aiCompanionService.getGreeting();

export const clearHistory = (): void => 
  aiCompanionService.clearHistory();

export const getHistory = (limit?: number): ConversationMessage[] => 
  aiCompanionService.getHistory(limit);

export const getPersonalityDescription = (personality?: AIPersonality): string =>
  aiCompanionService.getPersonalityDescription(personality);

export default aiCompanionService;
