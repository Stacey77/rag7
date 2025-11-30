# rag7

RAG7 - Repository for channel data and testing.

## Channel Data

This repository includes curated and generated channel datasets for testing and development:

- **Sample Channels**: 60 curated channels (30 satellite + 30 digital) with realistic data
- **Generated Channels**: 500+ synthetic channels for scale testing

See [src/data/README.md](src/data/README.md) for more details.

## Repository Structure

```
rag7/
├── src/
│   └── data/
│       ├── channels.sample.json      # 60 curated sample channels
│       ├── channels.generated.json   # 500+ synthetic channels
│       ├── generate_channels.py      # Generator script
│       └── README.md                 # Data documentation
└── README.md                         # This file
```