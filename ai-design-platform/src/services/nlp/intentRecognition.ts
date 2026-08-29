/**
 * Intent Recognition Service - Natural language understanding
 * Classifies user intents and extracts entities from text
 */

export type IntentType = 'navigate' | 'query' | 'command' | 'chat' | 'help';

export interface Intent {
  type: IntentType;
  confidence: number;
  entities: Entity[];
  originalText: string;
}

export interface Entity {
  type: EntityType;
  value: string;
  confidence: number;
  position?: {
    start: number;
    end: number;
  };
}

export type EntityType = 
  | 'section' 
  | 'model' 
  | 'action' 
  | 'feature' 
  | 'setting' 
  | 'query_type'
  | 'number'
  | 'color';

interface IntentPattern {
  type: IntentType;
  patterns: RegExp[];
  keywords: string[];
}

const INTENT_PATTERNS: IntentPattern[] = [
  {
    type: 'navigate',
    patterns: [
      /\b(go to|navigate to|open|show me|take me to)\s+(\w+)/i,
      /\b(switch to|change to|move to)\s+(\w+)/i,
      /\b(view|display|see)\s+(the\s+)?(\w+)\s+(section|page|panel)/i
    ],
    keywords: ['navigate', 'go', 'open', 'show', 'switch', 'move', 'view', 'display']
  },
  {
    type: 'query',
    patterns: [
      /\b(what|how|when|where|why|who)\b/i,
      /\b(tell me|show me|explain|describe)\b/i,
      /\b(can you|could you|would you)\s+(tell|show|explain)/i
    ],
    keywords: ['what', 'how', 'when', 'where', 'why', 'tell', 'explain', 'describe']
  },
  {
    type: 'command',
    patterns: [
      /\b(create|generate|make|build)\s+(\w+)/i,
      /\b(delete|remove|clear)\s+(\w+)/i,
      /\b(save|export|download)\s+(\w+)/i,
      /\b(start|stop|pause|resume)\s+(\w+)/i
    ],
    keywords: ['create', 'generate', 'make', 'delete', 'remove', 'save', 'export', 'start', 'stop']
  },
  {
    type: 'help',
    patterns: [
      /\b(help|assist|support)\b/i,
      /\b(how do i|how can i|what can i)\b/i,
      /\b(tutorial|guide|documentation)\b/i
    ],
    keywords: ['help', 'assist', 'support', 'tutorial', 'guide', 'how']
  }
];

const ENTITY_PATTERNS: Record<EntityType, RegExp[]> = {
  section: [
    /\b(dashboard|home|models|generators|settings|profile|analytics|history)\b/i
  ],
  model: [
    /\b(gpt|claude|llama|palm|gemini|dall-e|stable diffusion|midjourney)\b/i,
    /\b(text|image|audio|video|3d)\s+model\b/i
  ],
  action: [
    /\b(create|delete|update|edit|modify|generate|analyze|process)\b/i
  ],
  feature: [
    /\b(speech|voice|chat|conversation|assistant|companion)\b/i,
    /\b(recognition|synthesis|translation|summarization)\b/i
  ],
  setting: [
    /\b(theme|language|volume|rate|pitch|personality)\b/i,
    /\b(dark mode|light mode|auto save|notifications)\b/i
  ],
  query_type: [
    /\b(status|information|details|summary|overview)\b/i
  ],
  number: [
    /\b(\d+)\b/
  ],
  color: [
    /\b(red|blue|green|yellow|orange|purple|pink|black|white|gray)\b/i,
    /#[0-9a-f]{6}/i
  ]
};

/**
 * Calculate text similarity using Levenshtein distance
 */
function calculateSimilarity(str1: string, str2: string): number {
  const longer = str1.length > str2.length ? str1 : str2;
  const shorter = str1.length > str2.length ? str2 : str1;
  
  if (longer.length === 0) return 1.0;
  
  const editDistance = levenshteinDistance(longer.toLowerCase(), shorter.toLowerCase());
  return (longer.length - editDistance) / longer.length;
}

/**
 * Calculate Levenshtein distance between two strings
 */
function levenshteinDistance(str1: string, str2: string): number {
  const matrix: number[][] = [];

  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i];
  }

  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }

  return matrix[str2.length][str1.length];
}

/**
 * Classify user intent from text
 */
export function classifyIntent(text: string): Intent {
  const normalizedText = text.trim().toLowerCase();
  let maxConfidence = 0;
  let detectedType: IntentType = 'chat';
  
  for (const intentPattern of INTENT_PATTERNS) {
    let confidence = 0;
    
    for (const pattern of intentPattern.patterns) {
      if (pattern.test(normalizedText)) {
        confidence += 0.4;
      }
    }
    
    const words = normalizedText.split(/\s+/);
    const matchingKeywords = intentPattern.keywords.filter(keyword =>
      words.some(word => calculateSimilarity(word, keyword) > 0.8)
    );
    
    confidence += (matchingKeywords.length / intentPattern.keywords.length) * 0.6;
    
    if (confidence > maxConfidence) {
      maxConfidence = confidence;
      detectedType = intentPattern.type;
    }
  }
  
  if (maxConfidence < 0.3) {
    detectedType = 'chat';
    maxConfidence = 0.5;
  }
  
  const entities = extractEntities(text);
  
  return {
    type: detectedType,
    confidence: Math.min(maxConfidence, 1.0),
    entities,
    originalText: text
  };
}

/**
 * Extract entities from text
 */
export function extractEntities(text: string): Entity[] {
  const entities: Entity[] = [];
  
  for (const [entityType, patterns] of Object.entries(ENTITY_PATTERNS)) {
    for (const pattern of patterns) {
      const matches = text.matchAll(new RegExp(pattern, 'gi'));
      
      for (const match of matches) {
        const value = match[1] || match[0];
        const position = {
          start: match.index || 0,
          end: (match.index || 0) + match[0].length
        };
        
        let confidence = 0.8;
        if (match[1]) {
          confidence = 0.9;
        }
        
        const existingEntity = entities.find(
          e => e.position?.start === position.start && e.position?.end === position.end
        );
        
        if (!existingEntity) {
          entities.push({
            type: entityType as EntityType,
            value: value.trim(),
            confidence,
            position
          });
        }
      }
    }
  }
  
  entities.sort((a, b) => (b.confidence || 0) - (a.confidence || 0));
  
  return entities;
}

/**
 * Extract specific entity type
 */
export function extractEntityType(text: string, entityType: EntityType): Entity | null {
  const entities = extractEntities(text);
  const filtered = entities.filter(e => e.type === entityType);
  return filtered.length > 0 ? filtered[0] : null;
}

/**
 * Check if text contains specific intent
 */
export function hasIntent(text: string, intentType: IntentType, threshold: number = 0.5): boolean {
  const intent = classifyIntent(text);
  return intent.type === intentType && intent.confidence >= threshold;
}

/**
 * Get all possible intents with confidence scores
 */
export function getAllIntents(text: string): Array<{ type: IntentType; confidence: number }> {
  const normalizedText = text.trim().toLowerCase();
  const results: Array<{ type: IntentType; confidence: number }> = [];
  
  for (const intentPattern of INTENT_PATTERNS) {
    let confidence = 0;
    
    for (const pattern of intentPattern.patterns) {
      if (pattern.test(normalizedText)) {
        confidence += 0.4;
      }
    }
    
    const words = normalizedText.split(/\s+/);
    const matchingKeywords = intentPattern.keywords.filter(keyword =>
      words.some(word => calculateSimilarity(word, keyword) > 0.8)
    );
    
    confidence += (matchingKeywords.length / intentPattern.keywords.length) * 0.6;
    
    results.push({
      type: intentPattern.type,
      confidence: Math.min(confidence, 1.0)
    });
  }
  
  results.push({ type: 'chat', confidence: 0.5 });
  
  results.sort((a, b) => b.confidence - a.confidence);
  
  return results;
}
