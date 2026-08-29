/**
 * Sentiment Analyzer Service - Emotion and sentiment detection
 * Analyzes text for sentiment polarity and emotion classification
 */

export type SentimentType = 'positive' | 'negative' | 'neutral';

export type EmotionType = 'joy' | 'sadness' | 'anger' | 'fear' | 'surprise' | 'neutral';

export interface SentimentAnalysis {
  sentiment: SentimentType;
  score: number;
  intensity: number;
  confidence: number;
}

export interface EmotionAnalysis {
  primaryEmotion: EmotionType;
  emotions: EmotionScore[];
  intensity: number;
  confidence: number;
}

export interface EmotionScore {
  emotion: EmotionType;
  score: number;
}

interface SentimentLexicon {
  positive: string[];
  negative: string[];
  intensifiers: string[];
  negations: string[];
}

const SENTIMENT_LEXICON: SentimentLexicon = {
  positive: [
    'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like',
    'happy', 'joy', 'pleased', 'satisfied', 'perfect', 'awesome', 'brilliant', 'superb',
    'beautiful', 'delightful', 'enjoy', 'appreciate', 'thank', 'thanks', 'helpful',
    'useful', 'impressive', 'outstanding', 'remarkable', 'best', 'better', 'yes'
  ],
  negative: [
    'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'poor', 'worst',
    'sad', 'angry', 'upset', 'disappointed', 'frustrated', 'annoyed', 'unhappy',
    'disgusted', 'useless', 'wrong', 'error', 'fail', 'failed', 'broken', 'issue',
    'problem', 'difficult', 'hard', 'confusing', 'complicated', 'no', 'not', 'never'
  ],
  intensifiers: [
    'very', 'extremely', 'really', 'so', 'quite', 'absolutely', 'completely',
    'totally', 'highly', 'incredibly', 'exceptionally', 'particularly'
  ],
  negations: [
    'not', 'no', 'never', 'neither', 'nobody', 'nothing', 'none', 'nowhere',
    "don't", "doesn't", "didn't", "won't", "wouldn't", "can't", "couldn't"
  ]
};

const EMOTION_KEYWORDS: Record<EmotionType, string[]> = {
  joy: [
    'happy', 'joy', 'joyful', 'delighted', 'pleased', 'cheerful', 'glad',
    'excited', 'thrilled', 'wonderful', 'amazing', 'fantastic', 'great',
    'love', 'enjoy', 'celebrate', 'fun', 'laugh', 'smile'
  ],
  sadness: [
    'sad', 'unhappy', 'depressed', 'disappointed', 'miserable', 'upset',
    'sorrowful', 'gloomy', 'blue', 'down', 'cry', 'crying', 'tears',
    'lonely', 'heartbroken', 'grieving', 'melancholy'
  ],
  anger: [
    'angry', 'mad', 'furious', 'rage', 'annoyed', 'irritated', 'frustrated',
    'outraged', 'hate', 'hatred', 'hostile', 'aggressive', 'resentful',
    'bitter', 'pissed', 'enraged', 'livid'
  ],
  fear: [
    'afraid', 'scared', 'frightened', 'terrified', 'fear', 'fearful', 'anxious',
    'worried', 'nervous', 'panic', 'dread', 'horror', 'alarmed', 'uneasy',
    'threatened', 'intimidated', 'insecure'
  ],
  surprise: [
    'surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'startled',
    'unexpected', 'sudden', 'wow', 'incredible', 'unbelievable', 'amazing',
    'astounded', 'speechless'
  ],
  neutral: [
    'okay', 'ok', 'fine', 'normal', 'regular', 'standard', 'average',
    'moderate', 'typical', 'usual', 'ordinary'
  ]
};

/**
 * Normalize text for analysis
 */
function normalizeText(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(word => word.length > 0);
}

/**
 * Calculate sentiment score
 */
function calculateSentimentScore(words: string[]): { score: number; positiveCount: number; negativeCount: number } {
  let score = 0;
  let positiveCount = 0;
  let negativeCount = 0;
  let negationActive = false;
  let intensifierMultiplier = 1;

  for (let i = 0; i < words.length; i++) {
    const word = words[i];

    if (SENTIMENT_LEXICON.negations.includes(word)) {
      negationActive = true;
      continue;
    }

    if (SENTIMENT_LEXICON.intensifiers.includes(word)) {
      intensifierMultiplier = 1.5;
      continue;
    }

    let wordScore = 0;

    if (SENTIMENT_LEXICON.positive.includes(word)) {
      wordScore = 1 * intensifierMultiplier;
      positiveCount++;
    } else if (SENTIMENT_LEXICON.negative.includes(word)) {
      wordScore = -1 * intensifierMultiplier;
      negativeCount++;
    }

    if (negationActive && wordScore !== 0) {
      wordScore *= -1;
      negationActive = false;
    }

    score += wordScore;
    intensifierMultiplier = 1;
  }

  return { score, positiveCount, negativeCount };
}

/**
 * Analyze sentiment of text
 */
export function analyzeSentiment(text: string): SentimentAnalysis {
  if (!text || text.trim().length === 0) {
    return {
      sentiment: 'neutral',
      score: 0,
      intensity: 0,
      confidence: 0
    };
  }

  const words = normalizeText(text);
  const { score, positiveCount, negativeCount } = calculateSentimentScore(words);

  const totalSentimentWords = positiveCount + negativeCount;
  const normalizedScore = words.length > 0 ? score / words.length : 0;
  
  let sentiment: SentimentType;
  if (normalizedScore > 0.05) {
    sentiment = 'positive';
  } else if (normalizedScore < -0.05) {
    sentiment = 'negative';
  } else {
    sentiment = 'neutral';
  }

  const intensity = Math.min(Math.abs(normalizedScore) * 2, 1);
  
  const confidence = totalSentimentWords > 0 
    ? Math.min(totalSentimentWords / words.length * 2, 1)
    : 0.5;

  return {
    sentiment,
    score: normalizedScore,
    intensity,
    confidence
  };
}

/**
 * Detect emotions in text
 */
export function detectEmotion(text: string): EmotionAnalysis {
  if (!text || text.trim().length === 0) {
    return {
      primaryEmotion: 'neutral',
      emotions: [{ emotion: 'neutral', score: 1 }],
      intensity: 0,
      confidence: 0
    };
  }

  const words = normalizeText(text);
  const emotionScores: Record<EmotionType, number> = {
    joy: 0,
    sadness: 0,
    anger: 0,
    fear: 0,
    surprise: 0,
    neutral: 0
  };

  for (const word of words) {
    for (const [emotion, keywords] of Object.entries(EMOTION_KEYWORDS)) {
      if (keywords.includes(word)) {
        emotionScores[emotion as EmotionType] += 1;
      }
    }
  }

  const totalEmotionWords = Object.values(emotionScores).reduce((sum, count) => sum + count, 0);

  if (totalEmotionWords === 0) {
    emotionScores.neutral = 1;
  }

  const emotions: EmotionScore[] = (Object.entries(emotionScores) as [EmotionType, number][])
    .map(([emotion, count]) => ({
      emotion,
      score: totalEmotionWords > 0 ? count / totalEmotionWords : (emotion === 'neutral' ? 1 : 0)
    }))
    .filter(e => e.score > 0)
    .sort((a, b) => b.score - a.score);

  const primaryEmotion = emotions[0].emotion;
  const intensity = emotions[0].score;
  const confidence = totalEmotionWords > 0 
    ? Math.min(totalEmotionWords / words.length * 2, 1)
    : 0.5;

  return {
    primaryEmotion,
    emotions,
    intensity,
    confidence
  };
}

/**
 * Get combined sentiment and emotion analysis
 */
export function analyzeText(text: string): {
  sentiment: SentimentAnalysis;
  emotion: EmotionAnalysis;
} {
  return {
    sentiment: analyzeSentiment(text),
    emotion: detectEmotion(text)
  };
}

/**
 * Check if text has specific emotion
 */
export function hasEmotion(text: string, emotion: EmotionType, threshold: number = 0.3): boolean {
  const analysis = detectEmotion(text);
  const emotionScore = analysis.emotions.find(e => e.emotion === emotion);
  return emotionScore ? emotionScore.score >= threshold : false;
}

/**
 * Check if text has specific sentiment
 */
export function hasSentiment(text: string, sentiment: SentimentType): boolean {
  const analysis = analyzeSentiment(text);
  return analysis.sentiment === sentiment;
}

/**
 * Get sentiment intensity level
 */
export function getSentimentIntensity(text: string): 'low' | 'medium' | 'high' {
  const analysis = analyzeSentiment(text);
  if (analysis.intensity < 0.3) return 'low';
  if (analysis.intensity < 0.7) return 'medium';
  return 'high';
}
