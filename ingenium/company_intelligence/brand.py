"""Brand: the company's voice, tone, and visual identity guardrails."""
import logging

logger = logging.getLogger(__name__)


class Brand:
    """Holds brand voice guidelines that agent-side content must respect."""

    def __init__(self) -> None:
        """Initialize Brand with default empty guidelines."""
        self.voice: str = ""
        self.tone_words: list[str] = []
        self.taboo_words: list[str] = []

    def set_voice(self, voice: str, tone_words: list[str] | None = None) -> dict:
        """Set the brand voice description and tone descriptors.

        Args:
            voice: Short description of the brand voice.
            tone_words: Adjectives describing the desired tone.

        Returns:
            Dict with the stored voice configuration.
        """
        logger.info("Setting brand voice")
        self.voice = voice
        self.tone_words = list(tone_words or [])
        return self.snapshot()

    def add_taboo_word(self, word: str) -> dict:
        """Register a word or phrase the brand must never use.

        Args:
            word: The disallowed word or phrase.

        Returns:
            Dict with the updated taboo list.
        """
        logger.info("Adding taboo word '%s'", word)
        if word not in self.taboo_words:
            self.taboo_words.append(word)
        return {"taboo_words": list(self.taboo_words)}

    def snapshot(self) -> dict:
        """Return the current brand guardrails.

        Returns:
            Dict with voice, tone words, and taboo words.
        """
        return {
            "voice": self.voice,
            "tone_words": list(self.tone_words),
            "taboo_words": list(self.taboo_words),
        }
