"""
Example: Emotional Reasoning Demo
Demonstrates the emotional intelligence capabilities of the AGI system
"""
from agi_system import create_agi_system
from agi_system.reasoning.emotional.emotional_engine import EmotionType


def test_emotion_recognition():
    """Test emotion recognition from various inputs"""
    print("\n" + "=" * 80)
    print("Emotion Recognition Demo")
    print("=" * 80 + "\n")
    
    agi = create_agi_system()
    
    test_inputs = [
        "I'm so happy and excited about this project!",
        "This is really frustrating and making me angry.",
        "I'm worried and anxious about the upcoming presentation.",
        "That's surprising! I didn't expect that at all.",
        "I feel sad and disappointed about the results.",
        "I trust your judgment and feel confident about this decision.",
    ]
    
    for i, text in enumerate(test_inputs, 1):
        print(f"{i}. Input: \"{text}\"")
        result = agi.emotional_engine.process_input(text)
        
        print(f"   Primary Emotion: {result['affective_state']['primary_emotion']}")
        print(f"   Valence: {result['affective_state']['valence']:.2f} (negative ← 0 → positive)")
        print(f"   Arousal: {result['affective_state']['arousal']:.2f} (low ← 0 → high)")
        print(f"   Empathetic Response: \"{result['empathetic_response']}\"")
        print()


def test_emotional_context():
    """Test emotional context assessment over multiple interactions"""
    print("\n" + "=" * 80)
    print("Emotional Context Assessment Demo")
    print("=" * 80 + "\n")
    
    agi = create_agi_system()
    
    conversation = [
        "I'm excited to start this new project!",
        "But I'm a bit worried about the complexity.",
        "Actually, I'm getting quite frustrated with the requirements.",
        "Now I'm really angry about the constant changes!",
        "Wait, I think I understand it better now.",
        "I'm feeling more confident and happy about this.",
    ]
    
    print("Simulating a conversation with emotional shifts:\n")
    
    for i, message in enumerate(conversation, 1):
        print(f"Turn {i}: \"{message}\"")
        result = agi.emotional_engine.process_input(message)
        
        context = result['emotional_context']
        print(f"  → Emotion: {result['affective_state']['primary_emotion']}")
        print(f"  → Overall Valence: {context['overall_valence']:.2f}")
        print(f"  → Emotional Volatility: {context['emotional_volatility']:.2f}")
        print(f"  → Requires Support: {context['requires_support']}")
        print()


def test_emotion_influenced_decisions():
    """Test how emotions influence decision making"""
    print("\n" + "=" * 80)
    print("Emotion-Influenced Decision Making Demo")
    print("=" * 80 + "\n")
    
    agi = create_agi_system()
    
    decision_scenarios = [
        {
            "emotion": "fear",
            "input": "I'm really scared about making this risky investment.",
            "options": ["High-risk investment", "Moderate-risk investment", "Safe investment"]
        },
        {
            "emotion": "joy",
            "input": "I'm so happy and optimistic about new opportunities!",
            "options": ["Conservative approach", "Balanced approach", "Aggressive approach"]
        },
        {
            "emotion": "anger",
            "input": "I'm furious about how this was handled!",
            "options": ["Immediate action", "Measured response", "Wait and reflect"]
        }
    ]
    
    for scenario in decision_scenarios:
        print(f"Scenario: {scenario['emotion'].upper()}")
        print(f"Input: \"{scenario['input']}\"")
        
        # Process emotional state
        agi.emotional_engine.process_input(scenario['input'])
        
        # Get decision influenced by emotion
        decision = agi.emotional_engine.factor_emotion_in_decision(
            decision_options=[{"option": opt} for opt in scenario['options']]
        )
        
        print(f"Emotional Influence: {decision['emotional_influence']}")
        print(f"Modifiers: {decision['modifiers']}")
        print(f"Reasoning: {decision['reasoning']}")
        print()


def main():
    """Run all emotional reasoning demos"""
    print("\n" + "=" * 80)
    print("AGI System - Emotional Reasoning Demonstrations")
    print("=" * 80)
    
    test_emotion_recognition()
    test_emotional_context()
    test_emotion_influenced_decisions()
    
    print("\n" + "=" * 80)
    print("Emotional Reasoning Demo Completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
