"""
06_vision_language_demo.py — Vision-Language Model Demo
========================================================
Demonstrates CLIPInterface, ImageCaptioner, and VisualQA with a synthetic
image.  Works standalone with just numpy; models load only when their
dependencies (transformers, torch) are installed.
"""

from __future__ import annotations

import logging

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def make_synthetic_image(height: int = 224, width: int = 224) -> np.ndarray:
    """Return a small random RGB numpy image suitable for VLM inference."""
    rng = np.random.default_rng(42)  # same seed used across all demo scripts
    return rng.integers(0, 256, (height, width, 3), dtype=np.uint8)


# ---------------------------------------------------------------------------
# VLM demo helpers
# ---------------------------------------------------------------------------


def demo_clip_classify(image: np.ndarray) -> None:
    """Use CLIP to classify the image against a set of text labels."""
    logger.info("--- CLIPInterface.classify demo ---")
    try:
        from vision.vlm.clip_interface import CLIPInterface

        clip = CLIPInterface(device="cpu")
        labels = ["a cat", "a dog", "a car", "a person", "a building"]
        scores = clip.classify(image, labels)
        for label, score in zip(labels, scores):
            logger.info("  %-20s %.4f", label, float(score))
        best = labels[int(np.argmax(scores))]
        logger.info("Best match: %s", best)
    except ImportError as exc:
        logger.warning("CLIPInterface.classify skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("CLIPInterface.classify error: %s", exc)


def demo_clip_find_object(image: np.ndarray) -> None:
    """Use CLIP to score a natural-language object query against the image."""
    logger.info("--- CLIPInterface.find_object demo ---")
    try:
        from vision.vlm.clip_interface import CLIPInterface

        clip = CLIPInterface(device="cpu")
        query = "a red cup on a table"
        score = clip.classify(image, [query, "something else"])[0]
        logger.info("Query: '%s'  score: %.4f", query, float(score))
    except ImportError as exc:
        logger.warning("CLIPInterface.find_object skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("CLIPInterface.find_object error: %s", exc)


def demo_image_captioner(image: np.ndarray) -> None:
    """Generate a caption for *image*."""
    logger.info("--- ImageCaptioner demo ---")
    try:
        from vision.vlm.image_captioner import ImageCaptioner

        captioner = ImageCaptioner(device="cpu")
        caption = captioner.caption(image)
        logger.info("Generated caption: %s", caption)
    except ImportError as exc:
        logger.warning("ImageCaptioner skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("ImageCaptioner error: %s", exc)


def demo_visual_qa(image: np.ndarray) -> None:
    """Answer a question about *image* using VisualQA."""
    logger.info("--- VisualQA demo ---")
    try:
        from vision.vlm.visual_qa import VisualQA

        vqa = VisualQA(device="cpu")
        question = "What objects are visible in the image?"
        answer = vqa.answer(image, question)
        logger.info("Q: %s", question)
        logger.info("A: %s", answer)
    except ImportError as exc:
        logger.warning("VisualQA skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("VisualQA error: %s", exc)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the vision-language demo."""
    logger.info("=== Vision-Language Model Demo ===")
    image = make_synthetic_image()
    logger.info("Synthetic image shape: %s", image.shape)

    demo_clip_classify(image)
    demo_clip_find_object(image)
    demo_image_captioner(image)
    demo_visual_qa(image)

    logger.info("=== Demo complete ===")


if __name__ == "__main__":
    main()
