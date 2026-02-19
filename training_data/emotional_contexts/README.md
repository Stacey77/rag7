# Emotional Contexts Training Data

Labeled emotional context datasets for training empathy detection and
emotional intelligence models.

## Emotion Categories

| Category | Description | Valence | Arousal |
|----------|-------------|---------|---------|
| joy | Positive excitement and happiness | +0.8 | +0.7 |
| sadness | Low energy negative state | -0.7 | -0.5 |
| anger | High arousal negative state | -0.8 | +0.9 |
| fear | Threat-response state | -0.6 | +0.8 |
| frustration | Goal-blocked negative state | -0.5 | +0.6 |
| excitement | High energy positive state | +0.7 | +0.9 |
| neutral | Baseline state | 0.0 | 0.3 |
| overwhelm | Cognitive overload state | -0.6 | +0.7 |

## Contextual Scenarios

### Technical Frustration
- User encountering repeated errors
- Complex debugging sessions
- Unclear documentation

### Achievement and Success
- Successful deployments
- Performance improvements
- Learning breakthroughs

### Stress Under Pressure
- Incident response scenarios
- Deadline pressure
- Production outages

### Collaborative Joy
- Team accomplishments
- Helping others succeed
- Knowledge sharing wins

## Data Format

```json
{
  "text": "I've been trying to fix this for 3 hours and nothing works!",
  "emotion": "frustration",
  "valence": -0.6,
  "arousal": 0.7,
  "context_type": "technical_frustration",
  "stress_level": "high",
  "recommended_response_tone": {
    "warmth": 0.95,
    "formality": 0.3,
    "directness": 0.7,
    "empathy_level": 1.0
  },
  "sample_empathy_response": "That sounds really frustrating. Let's tackle this together - can you share the error message?"
}
```

## Annotation Guidelines

1. Annotate primary and secondary emotions
2. Rate valence (-1 to +1) and arousal (0 to 1)
3. Include contextual signals (exclamation marks, caps, urgency words)
4. Annotate recommended AI response tone
5. Minimum 300 examples per emotion category
