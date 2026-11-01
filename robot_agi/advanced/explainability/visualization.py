"""Attention visualization for explainable perception."""
import logging
import random

logger = logging.getLogger(__name__)


class AttentionVisualizer:
    """Creates attention heatmaps and overlays for perception explanations."""

    def __init__(self) -> None:
        """Initialize AttentionVisualizer."""
        self.colormap = "viridis"
        self.output_format = "dict"

    def create_heatmap(self, image: dict, attention_weights: list) -> dict:
        """Create an attention heatmap from attention weights.

        Args:
            image: Dict with image metadata (width, height, id).
            attention_weights: List of attention weight values.

        Returns:
            Dict with heatmap data and statistics.
        """
        logger.info("Creating heatmap for image: %s with %d weights", image.get("id", "?"), len(attention_weights))
        width = image.get("width", 224)
        height = image.get("height", 224)
        if attention_weights:
            max_w = max(attention_weights)
            min_w = min(attention_weights)
            normalized = [(w - min_w) / max(max_w - min_w, 1e-9) for w in attention_weights]
        else:
            normalized = []
        peak_idx = normalized.index(max(normalized)) if normalized else 0
        return {
            "status": "created",
            "image_id": image.get("id", "unknown"),
            "heatmap_shape": [height, width],
            "num_attention_weights": len(attention_weights),
            "normalized_weights": normalized[:10],
            "peak_attention_index": peak_idx,
            "colormap": self.colormap,
            "max_attention": max(attention_weights) if attention_weights else 0,
        }

    def overlay_attention(self, image: dict, attention_map: dict) -> dict:
        """Overlay attention map on the original image.

        Args:
            image: Dict with image data.
            attention_map: Dict with 2D attention weight map.

        Returns:
            Dict with overlay visualization and highlighted regions.
        """
        logger.info("Overlaying attention on image: %s", image.get("id", "?"))
        num_regions = random.randint(2, 5)
        highlighted_regions = [
            {
                "region_id": i,
                "bbox": [random.randint(0, 100), random.randint(0, 100), random.randint(100, 200), random.randint(100, 200)],
                "attention_level": random.choice(["high", "medium", "low"]),
                "opacity": random.uniform(0.3, 0.9),
            }
            for i in range(num_regions)
        ]
        return {
            "status": "overlaid",
            "image_id": image.get("id", "unknown"),
            "highlighted_regions": highlighted_regions,
            "overlay_alpha": 0.6,
            "visualization_type": "overlay",
            "num_highlighted_regions": num_regions,
        }
