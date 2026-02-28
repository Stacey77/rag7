"""
AGI System - Emotional Reasoning Engine
Implements emotion recognition, affective state modeling, and empathy simulation
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
from loguru import logger

try:
    from textblob import TextBlob
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    logger.warning("Sentiment analysis libraries not available")


class EmotionType(Enum):
    """Primary emotion types based on Plutchik's wheel of emotions"""
    JOY = "joy"
    TRUST = "trust"
    FEAR = "fear"
    SURPRISE = "surprise"
    SADNESS = "sadness"
    DISGUST = "disgust"
    ANGER = "anger"
    ANTICIPATION = "anticipation"
    NEUTRAL = "neutral"


class EmotionIntensity(Enum):
    """Emotion intensity levels"""
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 1.0


@dataclass
class Emotion:
    """Represents an emotion with its properties"""
    emotion_type: EmotionType
    intensity: float = 0.5  # 0.0 to 1.0
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)
    context: str = ""
    triggers: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate intensity range"""
        self.intensity = max(0.0, min(1.0, self.intensity))


@dataclass
class AffectiveState:
    """Represents the overall affective/emotional state"""
    primary_emotion: Emotion
    secondary_emotions: List[Emotion] = field(default_factory=list)
    valence: float = 0.0  # -1 (negative) to +1 (positive)
    arousal: float = 0.0  # -1 (low) to +1 (high)
    dominance: float = 0.0  # -1 (submissive) to +1 (dominant)
    timestamp: float = field(default_factory=time.time)
    
    def get_emotional_profile(self) -> Dict[str, float]:
        """Get the emotional profile as a dictionary"""
        profile = {self.primary_emotion.emotion_type.value: self.primary_emotion.intensity}
        for emotion in self.secondary_emotions:
            profile[emotion.emotion_type.value] = emotion.intensity
        return profile


class EmotionRecognition:
    """Recognizes emotions from text and context"""
    
    def __init__(self):
        self.vader_analyzer = None
        if SENTIMENT_AVAILABLE:
            try:
                self.vader_analyzer = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.warning(f"Could not initialize VADER: {e}")
        
        # Emotion keyword mappings
        self.emotion_keywords = {
            EmotionType.JOY: ['happy', 'joy', 'pleased', 'delighted', 'excited', 'cheerful'],
            EmotionType.SADNESS: ['sad', 'unhappy', 'depressed', 'miserable', 'sorrow', 'grief'],
            EmotionType.ANGER: ['angry', 'furious', 'mad', 'irritated', 'annoyed', 'rage'],
            EmotionType.FEAR: ['afraid', 'scared', 'terrified', 'anxious', 'worried', 'fearful'],
            EmotionType.SURPRISE: ['surprised', 'amazed', 'astonished', 'shocked', 'startled'],
            EmotionType.DISGUST: ['disgusted', 'revolted', 'repulsed', 'sick', 'nauseated'],
            EmotionType.TRUST: ['trust', 'confident', 'secure', 'assured', 'certain'],
            EmotionType.ANTICIPATION: ['anticipate', 'expect', 'await', 'hope', 'looking forward'],
        }
        
        logger.info("Emotion Recognition initialized")
    
    def recognize_from_text(self, text: str) -> List[Emotion]:
        """Recognize emotions from text"""
        emotions = []
        
        # Sentiment analysis
        if self.vader_analyzer:
            sentiment_scores = self.vader_analyzer.polarity_scores(text)
            
            # Map sentiment to emotions
            compound = sentiment_scores['compound']
            
            if compound > 0.5:
                emotions.append(Emotion(
                    emotion_type=EmotionType.JOY,
                    intensity=abs(compound),
                    context=text
                ))
            elif compound < -0.5:
                emotions.append(Emotion(
                    emotion_type=EmotionType.SADNESS,
                    intensity=abs(compound),
                    context=text
                ))
        
        # Keyword-based emotion detection
        text_lower = text.lower()
        for emotion_type, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    intensity = 0.6 + (text_lower.count(keyword) * 0.1)
                    intensity = min(intensity, 1.0)
                    emotions.append(Emotion(
                        emotion_type=emotion_type,
                        intensity=intensity,
                        context=text,
                        triggers=[keyword]
                    ))
                    break
        
        # Default to neutral if no emotions detected
        if not emotions:
            emotions.append(Emotion(
                emotion_type=EmotionType.NEUTRAL,
                intensity=0.5,
                context=text
            ))
        
        logger.debug(f"Recognized {len(emotions)} emotions from text")
        return emotions
    
    def classify_emotion(self, valence: float, arousal: float) -> EmotionType:
        """Classify emotion based on valence-arousal model"""
        if valence > 0.3 and arousal > 0.3:
            return EmotionType.JOY
        elif valence > 0.3 and arousal < -0.3:
            return EmotionType.TRUST
        elif valence < -0.3 and arousal > 0.3:
            return EmotionType.ANGER
        elif valence < -0.3 and arousal < -0.3:
            return EmotionType.SADNESS
        elif abs(valence) < 0.3 and arousal > 0.3:
            return EmotionType.SURPRISE
        elif abs(valence) < 0.3 and arousal < -0.3:
            return EmotionType.ANTICIPATION
        else:
            return EmotionType.NEUTRAL


class AffectiveStateModel:
    """Models emotional states and their transitions"""
    
    def __init__(self):
        self.current_state: Optional[AffectiveState] = None
        self.state_history: List[AffectiveState] = []
        self.max_history = 100
        
        # Emotion transition probabilities (simplified)
        self.transition_matrix = self._init_transition_matrix()
        
        logger.info("Affective State Model initialized")
    
    def _init_transition_matrix(self) -> Dict[EmotionType, Dict[EmotionType, float]]:
        """Initialize emotion transition probabilities"""
        # Simplified transition matrix
        # In reality, this would be learned from data
        matrix = {}
        for emotion in EmotionType:
            matrix[emotion] = {e: 0.1 for e in EmotionType}
            matrix[emotion][emotion] = 0.4  # Higher probability to stay in same state
        
        # Specific transitions
        matrix[EmotionType.JOY][EmotionType.TRUST] = 0.3
        matrix[EmotionType.ANGER][EmotionType.DISGUST] = 0.3
        matrix[EmotionType.FEAR][EmotionType.SURPRISE] = 0.3
        matrix[EmotionType.SADNESS][EmotionType.FEAR] = 0.2
        
        return matrix
    
    def update_state(self, emotions: List[Emotion]) -> AffectiveState:
        """Update the affective state based on new emotions"""
        if not emotions:
            return self.current_state
        
        # Select primary emotion (highest intensity)
        primary_emotion = max(emotions, key=lambda e: e.intensity)
        secondary_emotions = [e for e in emotions if e != primary_emotion]
        
        # Calculate valence, arousal, dominance
        valence = self._calculate_valence(emotions)
        arousal = self._calculate_arousal(emotions)
        dominance = self._calculate_dominance(emotions)
        
        # Create new state
        new_state = AffectiveState(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            valence=valence,
            arousal=arousal,
            dominance=dominance
        )
        
        # Update history
        if self.current_state:
            self.state_history.append(self.current_state)
            if len(self.state_history) > self.max_history:
                self.state_history.pop(0)
        
        self.current_state = new_state
        logger.debug(f"Updated affective state: {primary_emotion.emotion_type.value}")
        
        return new_state
    
    def _calculate_valence(self, emotions: List[Emotion]) -> float:
        """Calculate emotional valence (positive/negative)"""
        positive_emotions = [EmotionType.JOY, EmotionType.TRUST, EmotionType.ANTICIPATION]
        negative_emotions = [EmotionType.SADNESS, EmotionType.ANGER, EmotionType.FEAR, EmotionType.DISGUST]
        
        valence = 0.0
        for emotion in emotions:
            if emotion.emotion_type in positive_emotions:
                valence += emotion.intensity
            elif emotion.emotion_type in negative_emotions:
                valence -= emotion.intensity
        
        # Normalize to [-1, 1]
        return max(-1.0, min(1.0, valence / len(emotions))) if emotions else 0.0
    
    def _calculate_arousal(self, emotions: List[Emotion]) -> float:
        """Calculate emotional arousal (activation level)"""
        high_arousal = [EmotionType.ANGER, EmotionType.FEAR, EmotionType.SURPRISE, EmotionType.JOY]
        low_arousal = [EmotionType.SADNESS, EmotionType.TRUST]
        
        arousal = 0.0
        for emotion in emotions:
            if emotion.emotion_type in high_arousal:
                arousal += emotion.intensity
            elif emotion.emotion_type in low_arousal:
                arousal -= emotion.intensity
        
        return max(-1.0, min(1.0, arousal / len(emotions))) if emotions else 0.0
    
    def _calculate_dominance(self, emotions: List[Emotion]) -> float:
        """Calculate emotional dominance (control/power)"""
        dominant = [EmotionType.ANGER, EmotionType.TRUST, EmotionType.ANTICIPATION]
        submissive = [EmotionType.FEAR, EmotionType.SADNESS]
        
        dominance = 0.0
        for emotion in emotions:
            if emotion.emotion_type in dominant:
                dominance += emotion.intensity * 0.5
            elif emotion.emotion_type in submissive:
                dominance -= emotion.intensity * 0.5
        
        return max(-1.0, min(1.0, dominance))
    
    def predict_next_state(self) -> Optional[EmotionType]:
        """Predict the next emotional state"""
        if not self.current_state:
            return None
        
        current_emotion = self.current_state.primary_emotion.emotion_type
        transitions = self.transition_matrix[current_emotion]
        
        # Select most likely transition (simplified)
        next_emotion = max(transitions.items(), key=lambda x: x[1])[0]
        return next_emotion
    
    def get_emotional_trajectory(self, num_states: int = 5) -> List[EmotionType]:
        """Get recent emotional trajectory"""
        recent_states = self.state_history[-num_states:] if len(self.state_history) >= num_states else self.state_history
        return [state.primary_emotion.emotion_type for state in recent_states]


class EmpathySimulator:
    """Simulates empathetic responses and emotional understanding"""
    
    def __init__(self):
        self.empathy_level = 0.7  # 0.0 to 1.0
        self.emotional_memory: List[Tuple[str, AffectiveState]] = []
        logger.info("Empathy Simulator initialized")
    
    def generate_empathetic_response(self, user_emotion: Emotion, context: str = "") -> str:
        """Generate an empathetic response based on detected emotion"""
        responses = {
            EmotionType.JOY: [
                "I'm glad to hear that! It's wonderful to see you happy.",
                "That's great! Your joy is contagious.",
                "I share in your happiness! This is exciting."
            ],
            EmotionType.SADNESS: [
                "I understand this must be difficult for you.",
                "I'm here for you. It's okay to feel sad.",
                "I can sense your sadness. Would you like to talk about it?"
            ],
            EmotionType.ANGER: [
                "I can see you're upset. Your feelings are valid.",
                "It's understandable to feel angry in this situation.",
                "I hear your frustration. Let's work through this together."
            ],
            EmotionType.FEAR: [
                "I understand your concerns. It's natural to feel anxious.",
                "Your fears are valid. Let's address them together.",
                "I'm here to support you through this uncertainty."
            ],
            EmotionType.SURPRISE: [
                "That is indeed surprising! How do you feel about it?",
                "Wow, I didn't expect that either!",
                "That's quite unexpected. Let's explore this further."
            ],
            EmotionType.NEUTRAL: [
                "I'm listening. Please tell me more.",
                "I understand. How can I help you?",
                "Thank you for sharing. What would you like to discuss?"
            ]
        }
        
        # Select response based on emotion and empathy level
        emotion_responses = responses.get(user_emotion.emotion_type, responses[EmotionType.NEUTRAL])
        
        # Adjust response intensity based on emotion intensity
        if user_emotion.intensity > 0.7:
            response = emotion_responses[0]  # Strong empathy
        elif user_emotion.intensity > 0.4:
            response = emotion_responses[1] if len(emotion_responses) > 1 else emotion_responses[0]
        else:
            response = emotion_responses[-1]
        
        # Store in emotional memory
        self.emotional_memory.append((context, user_emotion))
        if len(self.emotional_memory) > 100:
            self.emotional_memory.pop(0)
        
        logger.debug(f"Generated empathetic response for {user_emotion.emotion_type.value}")
        return response
    
    def assess_emotional_context(self, text: str) -> Dict[str, Any]:
        """Assess the emotional context of a conversation"""
        # Analyze emotional patterns
        if not self.emotional_memory:
            return {
                "overall_valence": 0.0,
                "emotional_volatility": 0.0,
                "dominant_emotion": EmotionType.NEUTRAL,
                "requires_support": False
            }
        
        # Calculate metrics from memory
        recent_emotions = [em[1] for em in self.emotional_memory[-10:]]
        
        # Overall valence
        positive_count = sum(1 for e in recent_emotions if e.emotion_type in [EmotionType.JOY, EmotionType.TRUST])
        negative_count = sum(1 for e in recent_emotions if e.emotion_type in [EmotionType.SADNESS, EmotionType.ANGER, EmotionType.FEAR])
        overall_valence = (positive_count - negative_count) / len(recent_emotions)
        
        # Emotional volatility
        emotion_changes = sum(1 for i in range(1, len(recent_emotions)) if recent_emotions[i].emotion_type != recent_emotions[i-1].emotion_type)
        volatility = emotion_changes / max(len(recent_emotions) - 1, 1)
        
        # Dominant emotion
        emotion_counts = {}
        for emotion in recent_emotions:
            emotion_type = emotion.emotion_type
            emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        
        # Requires support
        requires_support = overall_valence < -0.3 or dominant_emotion in [EmotionType.SADNESS, EmotionType.FEAR, EmotionType.ANGER]
        
        return {
            "overall_valence": overall_valence,
            "emotional_volatility": volatility,
            "dominant_emotion": dominant_emotion,
            "requires_support": requires_support
        }


class EmotionalReasoningEngine:
    """Main emotional reasoning engine integrating all components"""
    
    def __init__(self):
        self.emotion_recognition = EmotionRecognition()
        self.affective_model = AffectiveStateModel()
        self.empathy_simulator = EmpathySimulator()
        logger.info("Emotional Reasoning Engine initialized")
    
    def process_input(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process input text and update emotional state"""
        # Recognize emotions
        emotions = self.emotion_recognition.recognize_from_text(text)
        
        # Update affective state
        affective_state = self.affective_model.update_state(emotions)
        
        # Generate empathetic response
        primary_emotion = affective_state.primary_emotion
        empathetic_response = self.empathy_simulator.generate_empathetic_response(primary_emotion, text)
        
        # Assess context
        emotional_context = self.empathy_simulator.assess_emotional_context(text)
        
        return {
            "detected_emotions": [
                {
                    "type": e.emotion_type.value,
                    "intensity": e.intensity,
                    "triggers": e.triggers
                }
                for e in emotions
            ],
            "affective_state": {
                "primary_emotion": primary_emotion.emotion_type.value,
                "valence": affective_state.valence,
                "arousal": affective_state.arousal,
                "dominance": affective_state.dominance,
                "emotional_profile": affective_state.get_emotional_profile()
            },
            "empathetic_response": empathetic_response,
            "emotional_context": emotional_context
        }
    
    def factor_emotion_in_decision(self, decision_options: List[Dict[str, Any]], current_emotion: Optional[EmotionType] = None) -> Dict[str, Any]:
        """Factor emotional state into decision-making"""
        if not self.affective_model.current_state and not current_emotion:
            return {"selected_option": decision_options[0] if decision_options else None, "reasoning": "No emotional context available"}
        
        emotion = current_emotion or self.affective_model.current_state.primary_emotion.emotion_type
        
        # Adjust decision based on emotional state
        emotion_modifiers = {
            EmotionType.FEAR: {"risk_aversion": 0.8, "caution": 0.9},
            EmotionType.ANGER: {"aggression": 0.7, "impulsiveness": 0.6},
            EmotionType.JOY: {"optimism": 0.8, "risk_taking": 0.6},
            EmotionType.SADNESS: {"pessimism": 0.7, "avoidance": 0.6},
            EmotionType.TRUST: {"cooperation": 0.9, "openness": 0.8},
        }
        
        modifiers = emotion_modifiers.get(emotion, {"neutral": 0.5})
        
        return {
            "selected_option": decision_options[0] if decision_options else None,
            "emotional_influence": emotion.value,
            "modifiers": modifiers,
            "reasoning": f"Decision influenced by {emotion.value} emotion"
        }
    
    def get_emotional_intelligence_metrics(self) -> Dict[str, Any]:
        """Get emotional intelligence metrics"""
        return {
            "empathy_level": self.empathy_simulator.empathy_level,
            "emotional_memory_size": len(self.empathy_simulator.emotional_memory),
            "state_history_size": len(self.affective_model.state_history),
            "current_state": self.affective_model.current_state.primary_emotion.emotion_type.value if self.affective_model.current_state else "none"
        }
