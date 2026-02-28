"""
Unit tests for Emotional Reasoning Engine
"""
import pytest
from agi_system.reasoning.emotional.emotional_engine import (
    EmotionalReasoningEngine,
    EmotionRecognition,
    AffectiveStateModel,
    EmpathySimulator,
    EmotionType,
    Emotion
)


class TestEmotionRecognition:
    """Test emotion recognition capabilities"""
    
    def test_initialization(self):
        """Test emotion recognition initialization"""
        er = EmotionRecognition()
        assert er is not None
        assert len(er.emotion_keywords) > 0
    
    def test_recognize_joy(self):
        """Test recognizing joy emotion"""
        er = EmotionRecognition()
        emotions = er.recognize_from_text("I'm so happy and excited!")
        
        assert len(emotions) > 0
        # Check if joy was detected
        joy_detected = any(e.emotion_type == EmotionType.JOY for e in emotions)
        assert joy_detected
    
    def test_recognize_sadness(self):
        """Test recognizing sadness"""
        er = EmotionRecognition()
        emotions = er.recognize_from_text("I feel sad and disappointed.")
        
        assert len(emotions) > 0
        sadness_detected = any(e.emotion_type == EmotionType.SADNESS for e in emotions)
        assert sadness_detected
    
    def test_recognize_anger(self):
        """Test recognizing anger"""
        er = EmotionRecognition()
        emotions = er.recognize_from_text("I'm so angry and frustrated!")
        
        assert len(emotions) > 0
        anger_detected = any(e.emotion_type == EmotionType.ANGER for e in emotions)
        assert anger_detected
    
    def test_neutral_emotion(self):
        """Test neutral emotion for non-emotional text"""
        er = EmotionRecognition()
        emotions = er.recognize_from_text("The meeting is at 3 PM.")
        
        assert len(emotions) > 0
        # Should default to neutral for non-emotional text
        neutral_present = any(e.emotion_type == EmotionType.NEUTRAL for e in emotions)
        assert neutral_present


class TestAffectiveStateModel:
    """Test affective state modeling"""
    
    def test_initialization(self):
        """Test model initialization"""
        model = AffectiveStateModel()
        assert model.current_state is None
        assert len(model.state_history) == 0
    
    def test_update_state(self):
        """Test updating affective state"""
        model = AffectiveStateModel()
        
        emotions = [
            Emotion(emotion_type=EmotionType.JOY, intensity=0.8),
            Emotion(emotion_type=EmotionType.TRUST, intensity=0.5)
        ]
        
        state = model.update_state(emotions)
        
        assert state is not None
        assert state.primary_emotion.emotion_type == EmotionType.JOY
        assert len(state.secondary_emotions) > 0
    
    def test_valence_calculation(self):
        """Test valence calculation (positive/negative)"""
        model = AffectiveStateModel()
        
        # Positive emotions
        positive_emotions = [Emotion(emotion_type=EmotionType.JOY, intensity=0.9)]
        state = model.update_state(positive_emotions)
        assert state.valence > 0
        
        # Negative emotions
        negative_emotions = [Emotion(emotion_type=EmotionType.SADNESS, intensity=0.9)]
        state = model.update_state(negative_emotions)
        assert state.valence < 0
    
    def test_arousal_calculation(self):
        """Test arousal calculation (activation level)"""
        model = AffectiveStateModel()
        
        # High arousal emotions
        high_arousal = [Emotion(emotion_type=EmotionType.ANGER, intensity=0.9)]
        state = model.update_state(high_arousal)
        assert state.arousal > 0
    
    def test_state_history(self):
        """Test state history tracking"""
        model = AffectiveStateModel()
        
        # Update state multiple times
        for i in range(5):
            emotions = [Emotion(emotion_type=EmotionType.JOY, intensity=0.5)]
            model.update_state(emotions)
        
        assert len(model.state_history) == 4  # Current state not in history


class TestEmpathySimulator:
    """Test empathy simulation"""
    
    def test_initialization(self):
        """Test simulator initialization"""
        simulator = EmpathySimulator()
        assert simulator.empathy_level > 0
        assert len(simulator.emotional_memory) == 0
    
    def test_generate_empathetic_response_joy(self):
        """Test empathetic response for joy"""
        simulator = EmpathySimulator()
        emotion = Emotion(emotion_type=EmotionType.JOY, intensity=0.8)
        
        response = simulator.generate_empathetic_response(emotion, "I'm happy!")
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_empathetic_response_sadness(self):
        """Test empathetic response for sadness"""
        simulator = EmpathySimulator()
        emotion = Emotion(emotion_type=EmotionType.SADNESS, intensity=0.7)
        
        response = simulator.generate_empathetic_response(emotion, "I'm sad")
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_emotional_memory(self):
        """Test emotional memory storage"""
        simulator = EmpathySimulator()
        
        for i in range(5):
            emotion = Emotion(emotion_type=EmotionType.JOY, intensity=0.5)
            simulator.generate_empathetic_response(emotion, f"context_{i}")
        
        assert len(simulator.emotional_memory) == 5
    
    def test_assess_emotional_context(self):
        """Test emotional context assessment"""
        simulator = EmpathySimulator()
        
        # Add some emotional memories
        for _ in range(3):
            joy = Emotion(emotion_type=EmotionType.JOY, intensity=0.8)
            simulator.generate_empathetic_response(joy, "happy context")
        
        context = simulator.assess_emotional_context("test")
        
        assert "overall_valence" in context
        assert "emotional_volatility" in context
        assert "dominant_emotion" in context
        assert "requires_support" in context


class TestEmotionalReasoningEngine:
    """Test integrated emotional reasoning engine"""
    
    def test_initialization(self):
        """Test engine initialization"""
        engine = EmotionalReasoningEngine()
        
        assert engine.emotion_recognition is not None
        assert engine.affective_model is not None
        assert engine.empathy_simulator is not None
    
    def test_process_input(self):
        """Test processing input with full pipeline"""
        engine = EmotionalReasoningEngine()
        
        result = engine.process_input("I'm excited about this!")
        
        assert "detected_emotions" in result
        assert "affective_state" in result
        assert "empathetic_response" in result
        assert "emotional_context" in result
    
    def test_detect_multiple_emotions(self):
        """Test detecting multiple emotions"""
        engine = EmotionalReasoningEngine()
        
        result = engine.process_input("I'm happy but also a bit worried.")
        
        assert len(result["detected_emotions"]) > 0
    
    def test_factor_emotion_in_decision(self):
        """Test emotion-influenced decision making"""
        engine = EmotionalReasoningEngine()
        
        # Set emotional state
        engine.process_input("I'm very afraid and anxious")
        
        # Make decision
        options = [
            {"option": "risky", "value": 1},
            {"option": "safe", "value": 2}
        ]
        
        decision = engine.factor_emotion_in_decision(options, EmotionType.FEAR)
        
        assert "emotional_influence" in decision
        assert "modifiers" in decision
        assert "reasoning" in decision
    
    def test_get_metrics(self):
        """Test getting emotional intelligence metrics"""
        engine = EmotionalReasoningEngine()
        
        # Process some inputs
        engine.process_input("I'm happy!")
        engine.process_input("I'm sad.")
        
        metrics = engine.get_emotional_intelligence_metrics()
        
        assert "empathy_level" in metrics
        assert "emotional_memory_size" in metrics
        assert "state_history_size" in metrics
        assert "current_state" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
