#!/usr/bin/env python3
"""
Generate synthetic channel data for scale testing.
Produces 500+ channels with varied properties and realistic distribution.
"""

import json
import random
from typing import Dict, List

# Configuration
NUM_CHANNELS = 500
START_ID = 1000

# Data pools for randomization
CATEGORIES = [
    "news", "sports", "movies", "entertainment", "documentary", 
    "kids", "music", "lifestyle", "technology", "gaming",
    "education", "food", "travel", "fashion", "auto"
]

COUNTRIES = [
    "USA", "UK", "Canada", "Australia", "Germany", "France", 
    "Spain", "Italy", "Japan", "India", "Brazil", "Mexico",
    "Netherlands", "Sweden", "Norway", "Switzerland", "Austria",
    "Belgium", "Denmark", "Finland", "Ireland", "Poland",
    "International", "Europe", "Asia"
]

LANGUAGES = [
    "en", "es", "fr", "de", "it", "pt", "ja", "hi", "zh", 
    "ar", "ru", "nl", "sv", "no", "da", "fi", "pl", "multi"
]

CHANNEL_TYPES = ["satellite", "digital", "iptv", "radio"]

# Name components for realistic channel names
PREFIXES = [
    "Global", "Prime", "Ultra", "Elite", "Premium", "Super", "Mega",
    "Pro", "Digital", "Web", "Stream", "Live", "24/7", "Plus",
    "World", "International", "Regional", "Local", "National",
    "First", "Top", "Best", "Star", "Sky", "One", "Max"
]

CATEGORY_WORDS = {
    "news": ["News", "Headlines", "Today", "Live", "24", "Breaking", "Alert"],
    "sports": ["Sports", "Arena", "Stadium", "League", "Game", "Match", "Action"],
    "movies": ["Cinema", "Movies", "Films", "Pictures", "Screen", "Reel"],
    "entertainment": ["TV", "Show", "Entertainment", "Fun", "Comedy", "Drama"],
    "documentary": ["Discovery", "Docs", "Nature", "Science", "History", "Planet"],
    "kids": ["Kids", "Junior", "Children", "Cartoon", "Animation", "Family"],
    "music": ["Music", "Hits", "Rock", "Pop", "Jazz", "Classical", "Beats"],
    "lifestyle": ["Life", "Style", "Home", "Living", "Design", "Fashion"],
    "technology": ["Tech", "Digital", "Gadgets", "Innovation", "Future"],
    "gaming": ["Gaming", "Games", "eSports", "Play", "Arcade"],
    "education": ["Learning", "Education", "School", "Academy", "Knowledge"],
    "food": ["Food", "Cooking", "Chef", "Kitchen", "Taste", "Flavor"],
    "travel": ["Travel", "Journey", "Adventure", "World", "Explore"],
    "fashion": ["Fashion", "Style", "Runway", "Design", "Trends"],
    "auto": ["Auto", "Motor", "Racing", "Drive", "Wheels", "Speed"]
}

SUFFIXES = [
    "HD", "4K", "Plus", "Pro", "Network", "Channel", "TV", 
    "Online", "Stream", "Live", "24/7", "Express", "Direct",
    "Zone", "Hub", "Central", "World", "International"
]


def generate_channel_name(category: str) -> str:
    """Generate a realistic channel name based on category."""
    parts = []
    
    # 60% chance to add a prefix
    if random.random() < 0.6:
        parts.append(random.choice(PREFIXES))
    
    # Add category-specific word
    if category in CATEGORY_WORDS:
        parts.append(random.choice(CATEGORY_WORDS[category]))
    else:
        parts.append(category.capitalize())
    
    # 40% chance to add a suffix
    if random.random() < 0.4:
        parts.append(random.choice(SUFFIXES))
    
    return " ".join(parts)


def generate_tier() -> str:
    """Generate tier with realistic distribution: ~10% gold, ~20% silver, ~70% free."""
    rand = random.random()
    if rand < 0.10:
        return "gold"
    elif rand < 0.30:
        return "silver"
    else:
        return "free"


def generate_channel(channel_id: int) -> Dict:
    """Generate a single synthetic channel."""
    category = random.choice(CATEGORIES)
    channel_type = random.choice(CHANNEL_TYPES)
    
    return {
        "id": channel_id,
        "name": generate_channel_name(category),
        "type": channel_type,
        "category": category,
        "country": random.choice(COUNTRIES),
        "language": random.choice(LANGUAGES),
        "tier": generate_tier(),
        "streamUrl": f"https://cdn.example.com/generated/channel_{channel_id}/stream"
    }


def generate_channels(num_channels: int, start_id: int) -> List[Dict]:
    """Generate multiple synthetic channels."""
    channels = []
    used_names = set()
    
    for i in range(num_channels):
        channel_id = start_id + i
        max_attempts = 10
        
        # Try to generate unique channel name
        for attempt in range(max_attempts):
            channel = generate_channel(channel_id)
            if channel["name"] not in used_names:
                used_names.add(channel["name"])
                channels.append(channel)
                break
            
            # If we've tried max_attempts, just add a number to make it unique
            if attempt == max_attempts - 1:
                channel["name"] = f"{channel['name']} {i+1}"
                used_names.add(channel["name"])
                channels.append(channel)
    
    return channels


def main():
    """Generate and save synthetic channels."""
    print(f"Generating {NUM_CHANNELS} synthetic channels starting at ID {START_ID}...")
    
    channels = generate_channels(NUM_CHANNELS, START_ID)
    
    # Print statistics
    tier_counts = {"gold": 0, "silver": 0, "free": 0}
    type_counts = {}
    
    for channel in channels:
        tier_counts[channel["tier"]] += 1
        type_counts[channel["type"]] = type_counts.get(channel["type"], 0) + 1
    
    print(f"\nGenerated {len(channels)} channels:")
    print(f"  Tier distribution:")
    print(f"    Gold:   {tier_counts['gold']} ({tier_counts['gold']/len(channels)*100:.1f}%)")
    print(f"    Silver: {tier_counts['silver']} ({tier_counts['silver']/len(channels)*100:.1f}%)")
    print(f"    Free:   {tier_counts['free']} ({tier_counts['free']/len(channels)*100:.1f}%)")
    print(f"  Type distribution:")
    for channel_type, count in sorted(type_counts.items()):
        print(f"    {channel_type.capitalize()}: {count} ({count/len(channels)*100:.1f}%)")
    
    # Save to file
    output_file = "channels.generated.json"
    with open(output_file, "w") as f:
        json.dump(channels, f, indent=2)
    
    print(f"\n✓ Saved to {output_file}")


if __name__ == "__main__":
    main()
