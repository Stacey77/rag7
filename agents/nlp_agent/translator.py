"""Multi-language translation module (simulated)."""
from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Language detection heuristics (character n-gram patterns)
_LANG_PATTERNS: Dict[str, List[str]] = {
    "es": ["el", "la", "los", "las", "de", "en", "que", "por", "con", "una"],
    "fr": ["le", "la", "les", "de", "du", "des", "en", "que", "est", "une"],
    "de": ["der", "die", "das", "und", "ist", "nicht", "ein", "mit", "ich", "auf"],
    "it": ["il", "la", "di", "che", "in", "un", "per", "una", "con", "sono"],
    "pt": ["de", "da", "do", "que", "em", "para", "uma", "com", "por", "não"],
    "zh": [],  # detected by Unicode range
    "ja": [],  # detected by Unicode range
    "ko": [],  # detected by Unicode range
    "ar": [],  # detected by Unicode range
    "en": ["the", "is", "are", "was", "and", "for", "this", "that", "with", "have"],
}

# Simple phrase-level translation glossary (simulated)
_GLOSSARY: Dict[str, Dict[str, str]] = {
    "es": {
        "hello": "hola", "goodbye": "adiós", "thank you": "gracias",
        "yes": "sí", "no": "no", "please": "por favor",
        "error": "error", "server": "servidor", "database": "base de datos",
        "deploy": "desplegar", "service": "servicio", "configuration": "configuración",
    },
    "fr": {
        "hello": "bonjour", "goodbye": "au revoir", "thank you": "merci",
        "yes": "oui", "no": "non", "please": "s'il vous plaît",
        "error": "erreur", "server": "serveur", "database": "base de données",
        "deploy": "déployer", "service": "service", "configuration": "configuration",
    },
    "de": {
        "hello": "hallo", "goodbye": "auf wiedersehen", "thank you": "danke",
        "yes": "ja", "no": "nein", "please": "bitte",
        "error": "fehler", "server": "server", "database": "datenbank",
        "deploy": "bereitstellen", "service": "dienst", "configuration": "konfiguration",
    },
    "it": {
        "hello": "ciao", "goodbye": "arrivederci", "thank you": "grazie",
        "yes": "sì", "no": "no", "please": "per favore",
        "error": "errore", "server": "server", "database": "database",
        "deploy": "distribuire", "service": "servizio", "configuration": "configurazione",
    },
    "pt": {
        "hello": "olá", "goodbye": "tchau", "thank you": "obrigado",
        "yes": "sim", "no": "não", "please": "por favor",
        "error": "erro", "server": "servidor", "database": "banco de dados",
        "deploy": "implantar", "service": "serviço", "configuration": "configuração",
    },
}

_SUPPORTED_LANGUAGES = {"en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko", "ar"}

_LANGUAGE_NAMES: Dict[str, str] = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "zh": "Chinese", "ja": "Japanese",
    "ko": "Korean", "ar": "Arabic",
}


@dataclass
class TranslationResult:
    """Result of a translation operation."""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_text: str = ""
    translated_text: str = ""
    source_language: str = ""
    target_language: str = ""
    confidence: float = 0.0
    word_count: int = 0
    glossary_hits: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


def _detect_unicode_script(text: str) -> Optional[str]:
    for char in text:
        code = ord(char)
        if 0x4E00 <= code <= 0x9FFF:
            return "zh"
        if 0x3040 <= code <= 0x30FF:
            return "ja"
        if 0xAC00 <= code <= 0xD7AF:
            return "ko"
        if 0x0600 <= code <= 0x06FF:
            return "ar"
    return None


class LanguageDetector:
    """Heuristic language detector using word frequency patterns."""

    def detect(self, text: str) -> Tuple[str, float]:
        unicode_lang = _detect_unicode_script(text)
        if unicode_lang:
            return unicode_lang, 0.95

        words = set(re.findall(r"\b\w+\b", text.lower()))
        scores: Dict[str, int] = {}
        for lang, markers in _LANG_PATTERNS.items():
            scores[lang] = sum(1 for m in markers if m in words)

        if not any(scores.values()):
            return "en", 0.4  # default

        best_lang = max(scores, key=lambda l: scores[l])
        total_markers = sum(len(markers) for markers in _LANG_PATTERNS.values())
        confidence = min(0.95, 0.4 + scores[best_lang] * 0.06)
        return best_lang, confidence


class GlossaryTranslator:
    """Word/phrase substitution translator using glossary lookup."""

    def translate(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, int]:
        """Returns (translated_text, glossary_hits)."""
        if source_lang != "en" or target_lang not in _GLOSSARY:
            if target_lang == "en" and source_lang in _GLOSSARY:
                # Reverse translation
                reverse = {v: k for k, v in _GLOSSARY[source_lang].items()}
                return self._apply_glossary(text, reverse)
            return text, 0

        glossary = _GLOSSARY.get(target_lang, {})
        return self._apply_glossary(text, glossary)

    def _apply_glossary(self, text: str, glossary: Dict[str, str]) -> Tuple[str, int]:
        result = text
        hits = 0
        # Sort by length descending to match longer phrases first
        for source, target in sorted(glossary.items(), key=lambda x: -len(x[0])):
            pattern = re.compile(r"\b" + re.escape(source) + r"\b", re.IGNORECASE)
            new_result, n = pattern.subn(target, result)
            if n > 0:
                result = new_result
                hits += n
        return result, hits


class Translator:
    """
    Multi-language translator with automatic language detection,
    glossary-based translation, and batch processing support.
    """

    def __init__(self) -> None:
        self._detector = LanguageDetector()
        self._glossary_translator = GlossaryTranslator()
        self._translation_cache: Dict[str, TranslationResult] = {}
        logger.info("Translator initialized, supported languages: %s", sorted(_SUPPORTED_LANGUAGES))

    def detect_language(self, text: str) -> Tuple[str, float]:
        return self._detector.detect(text)

    def translate(self, text: str, target_language: str,
                  source_language: Optional[str] = None) -> TranslationResult:
        if target_language not in _SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported target language: {target_language}")

        cache_key = f"{text[:100]}:{source_language}:{target_language}"
        if cache_key in self._translation_cache:
            logger.debug("Cache hit for translation")
            return self._translation_cache[cache_key]

        if source_language is None:
            source_language, detect_confidence = self._detector.detect(text)
        else:
            detect_confidence = 1.0

        if source_language == target_language:
            result = TranslationResult(
                source_text=text, translated_text=text,
                source_language=source_language, target_language=target_language,
                confidence=1.0, word_count=len(text.split()),
                metadata={"note": "source and target language are the same"},
            )
            return result

        translated, hits = self._glossary_translator.translate(text, source_language, target_language)

        # Add language marker for unsupported pairs (simulated)
        if hits == 0 and target_language not in ("zh", "ja", "ko", "ar"):
            translated = f"[{_LANGUAGE_NAMES.get(target_language, target_language)}] {text}"
        elif hits == 0:
            translated = f"[{target_language.upper()} translation of: {text[:80]}]"

        confidence = min(0.92, 0.5 + hits * 0.05 + detect_confidence * 0.3)
        result = TranslationResult(
            source_text=text,
            translated_text=translated,
            source_language=source_language,
            target_language=target_language,
            confidence=confidence,
            word_count=len(translated.split()),
            glossary_hits=hits,
            metadata={"detection_confidence": detect_confidence},
        )
        self._translation_cache[cache_key] = result
        logger.debug("Translated: %s -> %s (%d hits)", source_language, target_language, hits)
        return result

    def batch_translate(self, texts: List[str], target_language: str,
                        source_language: Optional[str] = None) -> List[TranslationResult]:
        return [self.translate(t, target_language, source_language) for t in texts]

    def translate_fields(self, data: Dict[str, str], target_language: str) -> Dict[str, str]:
        """Translate all string values in a dictionary."""
        return {k: self.translate(v, target_language).translated_text for k, v in data.items()}

    @property
    def supported_languages(self) -> List[str]:
        return sorted(_SUPPORTED_LANGUAGES)
