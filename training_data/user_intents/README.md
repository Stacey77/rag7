# User Intents Training Data

Labeled intent classification datasets for training the NLU intent classifier.

## Intent Categories

| Intent | Description | Example Utterances |
|--------|-------------|-------------------|
| greeting | User is greeting the system | "Hello", "Hi there", "Good morning" |
| help | Requesting assistance | "How do I deploy?", "What is Kubernetes?" |
| create | Creating a resource | "Create a new service", "Setup a database" |
| deploy | Deploying software | "Deploy version 2.1 to production" |
| monitor | Checking system status | "Show me the metrics", "What's the error rate?" |
| scale | Scaling infrastructure | "Scale the API to 10 replicas" |
| debug | Troubleshooting | "Why is the service failing?" |
| report | Requesting reports | "Generate a cost report for last month" |
| train | Training ML models | "Train the sentiment model on new data" |
| predict | Running inference | "Predict the blast radius of this change" |

## Data Format

CSV format with columns: `text`, `intent`, `confidence`, `entities`

```csv
text,intent,confidence,entities
"Deploy my-service to production",deploy,1.0,"{""service"": ""my-service"", ""environment"": ""production""}"
"Show me the CPU usage for the past hour",monitor,0.95,"{""metric"": ""cpu_usage"", ""duration"": ""1h""}"
```

## Data Collection Guidelines

1. Minimum 200 examples per intent
2. Include variations in phrasing and terminology
3. Include multi-intent utterances for edge case testing
4. Annotate slot/entity spans alongside intent labels
5. Include negative examples (out-of-scope queries)

## Augmentation Strategies

- Synonym substitution for technical terms
- Back-translation for linguistic diversity
- Template-based generation for structured intents
- Crowdsourced paraphrasing for natural diversity
