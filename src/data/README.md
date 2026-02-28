# Channel Data

This directory contains channel datasets for the RAG7 project.

## Files

### channels.sample.json
60 curated sample channels for testing and development:
- 30 satellite channels
- 30 digital channels
- Gold-tier channels (IDs: 26, 33, 36, 40)
- Mix of categories, countries, and languages

### channels.generated.json
500 synthetic channels for scale testing:
- IDs range from 1000-1499
- Varied types: satellite, digital, iptv, radio
- Tier distribution: ~10% gold, ~20% silver, ~70% free
- Randomized categories, countries, and languages
- Placeholder stream URLs for testing

### generate_channels.py
Python script to generate synthetic channel data. Can be run to regenerate the dataset with different parameters if needed.

## Usage

```python
import json

# Load sample channels
with open('src/data/channels.sample.json') as f:
    sample_channels = json.load(f)

# Load generated channels
with open('src/data/channels.generated.json') as f:
    generated_channels = json.load(f)
```

## Regenerating Data

To regenerate the synthetic channels:

```bash
cd src/data
python3 generate_channels.py
```

Note: The generator uses randomization, so each run produces different data.
