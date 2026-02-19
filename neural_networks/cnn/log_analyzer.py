"""Log pattern recognition using CNN-simulated sliding-window feature extraction."""
from __future__ import annotations
import re
import math
import logging
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

_SEVERITY_MAP = {"debug": 0.1, "info": 0.3, "warn": 0.5, "warning": 0.5,
                 "error": 0.8, "critical": 1.0, "fatal": 1.0}

_KEYWORDS = ["timeout", "exception", "fail", "error", "retry", "connect",
             "disconnect", "success", "start", "stop", "deploy", "crash"]


@dataclass
class LogPattern:
    pattern_id: str
    regex: str
    label: str
    severity: float = 0.3
    examples: List[str] = field(default_factory=list)


@dataclass
class LogSample:
    text: str
    label: str
    features: List[float] = field(default_factory=list)


class LogFeatureExtractor:
    def extract(self, log_line: str) -> List[float]:
        lower = log_line.lower()
        severity = 0.3
        for kw, val in _SEVERITY_MAP.items():
            if kw in lower:
                severity = val
                break
        length_feat = min(1.0, len(log_line) / 500.0)
        keyword_counts = [1.0 if kw in lower else 0.0 for kw in _KEYWORDS]
        digit_ratio = sum(1 for c in log_line if c.isdigit()) / (len(log_line) + 1e-9)
        upper_ratio = sum(1 for c in log_line if c.isupper()) / (len(log_line) + 1e-9)
        has_ip = 1.0 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', log_line) else 0.0
        has_ts = 1.0 if re.search(r'\d{4}-\d{2}-\d{2}', log_line) else 0.0
        word_count = min(1.0, len(log_line.split()) / 50.0)
        return [severity, length_feat, digit_ratio, upper_ratio,
                has_ip, has_ts, word_count] + keyword_counts


class LogCNNClassifier:
    """1-D convolution simulated with sliding-window feature averaging."""

    def __init__(self, kernel_size: int = 3, num_filters: int = 8) -> None:
        self.kernel_size = kernel_size
        self.num_filters = num_filters
        self._class_centroids: Dict[str, List[float]] = {}
        self._labels: List[str] = []

    def _convolve(self, features: List[float]) -> List[float]:
        if len(features) < self.kernel_size:
            return features
        pooled = []
        for i in range(len(features) - self.kernel_size + 1):
            window = features[i: i + self.kernel_size]
            pooled.append(sum(window) / self.kernel_size)
        return pooled

    def fit(self, samples: List[LogSample]) -> None:
        logger.info("Training LogCNNClassifier on %d samples", len(samples))
        class_feats: Dict[str, List[List[float]]] = defaultdict(list)
        for s in samples:
            conv = self._convolve(s.features)
            class_feats[s.label].append(conv)
        self._labels = list(class_feats.keys())
        for label, feat_list in class_feats.items():
            min_len = min(len(f) for f in feat_list)
            centroid = [statistics.mean(f[d] for f in feat_list if d < len(f))
                        for d in range(min_len)]
            self._class_centroids[label] = centroid
        logger.info("Trained on labels: %s", self._labels)

    def classify(self, features: List[float]) -> Tuple[str, float]:
        conv = self._convolve(features)
        if not self._class_centroids:
            return "unknown", 0.0
        best_label, best_score = "unknown", -float("inf")
        for label, centroid in self._class_centroids.items():
            min_len = min(len(conv), len(centroid))
            score = sum(conv[d] * centroid[d] for d in range(min_len))
            if score > best_score:
                best_score, best_label = score, label
        norm = (best_score + 10) / 20.0
        return best_label, round(max(0.0, min(1.0, norm)), 4)


class LogAnalyzer:
    def __init__(self) -> None:
        self.extractor = LogFeatureExtractor()
        self.classifier = LogCNNClassifier()
        self._patterns: List[LogPattern] = []
        self._trained = False
        logger.info("LogAnalyzer initialised")

    def train(self, log_examples: List[Tuple[str, str]]) -> None:
        logger.info("Training on %d log examples", len(log_examples))
        samples = []
        for text, label in log_examples:
            feats = self.extractor.extract(text)
            samples.append(LogSample(text=text, label=label, features=feats))
        self.classifier.fit(samples)
        self._trained = True

    def classify(self, log_line: str) -> Tuple[str, float]:
        if not self._trained:
            feats = self.extractor.extract(log_line)
            sev = feats[0]
            if sev >= 0.8:
                return "error", sev
            elif sev >= 0.5:
                return "warning", sev
            return "info", 1.0 - sev
        feats = self.extractor.extract(log_line)
        label, conf = self.classifier.classify(feats)
        logger.debug("Classified log line as '%s' (conf=%.4f)", label, conf)
        return label, conf

    def batch_classify(self, log_lines: List[str]) -> List[Tuple[str, float]]:
        logger.info("Batch classifying %d log lines", len(log_lines))
        return [self.classify(line) for line in log_lines]

    def extract_patterns(self, log_lines: List[str]) -> List[LogPattern]:
        logger.info("Extracting patterns from %d lines", len(log_lines))
        pattern_map: Dict[str, List[str]] = defaultdict(list)
        for line in log_lines:
            template = re.sub(r'\d+', '<NUM>', line)
            template = re.sub(r'\b[0-9a-f-]{8,}\b', '<ID>', template)
            pattern_map[template[:80]].append(line)
        patterns = []
        for i, (tmpl, examples) in enumerate(pattern_map.items()):
            feats = self.extractor.extract(examples[0])
            patterns.append(LogPattern(
                pattern_id=f"P{i:04d}",
                regex=re.escape(tmpl).replace(r'\<NUM\>', r'\d+'),
                label=self.classify(examples[0])[0],
                severity=feats[0],
                examples=examples[:3],
            ))
        self._patterns = patterns
        return patterns

    def cluster_similar_logs(self, log_lines: List[str],
                              n_clusters: int = 5) -> Dict[int, List[str]]:
        logger.info("Clustering %d logs into %d clusters", len(log_lines), n_clusters)
        feats = [self.extractor.extract(line) for line in log_lines]
        clusters: Dict[int, List[str]] = defaultdict(list)
        for line, feat in zip(log_lines, feats):
            key = int(sum(feat) * 10) % n_clusters
            clusters[key].append(line)
        return dict(clusters)
