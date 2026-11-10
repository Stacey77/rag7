"""Async model server for LLM inference serving."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class ModelConfig:
    """Configuration for a served model.

    Attributes:
        model_id: Unique identifier for the model.
        model_path: File path or URI of the model artefact.
        max_batch_size: Maximum number of requests in a single batch.
        timeout_seconds: Per-request inference timeout.
        max_sequence_length: Maximum token length accepted.
    """

    model_id: str
    model_path: str
    max_batch_size: int = 32
    timeout_seconds: float = 5.0
    max_sequence_length: int = 2048


@dataclass
class PredictResult:
    """Inference result from a single prediction.

    Attributes:
        model_id: Identifier of the model that produced the output.
        output: Generated text or structured output.
        latency_ms: Wall-clock inference latency in milliseconds.
        tokens_generated: Number of output tokens produced.
        confidence: Optional confidence score.
    """

    model_id: str
    output: str
    latency_ms: float
    tokens_generated: int
    confidence: float = 1.0


@dataclass
class HealthStatus:
    """Health check response for the model server.

    Attributes:
        healthy: Overall health flag.
        model_loaded: Whether a model is currently loaded.
        uptime_seconds: Seconds since the server started.
        requests_served: Total inference requests completed.
        error_rate: Fraction of requests that resulted in errors.
    """

    healthy: bool
    model_loaded: bool
    uptime_seconds: float
    requests_served: int
    error_rate: float


class ModelServer:
    """Async inference server for LLM models.

    Supports single-request and batch prediction, health-checking, and
    model hot-swapping.  The default implementation simulates inference
    without requiring an actual model runtime.

    Attributes:
        config: Currently loaded model configuration.
        _loaded: Whether a model is currently ready for inference.
        _start_time: Server start timestamp (monotonic).
        _requests_served: Counter of completed requests.
        _error_count: Counter of failed requests.
    """

    def __init__(self) -> None:
        """Initialise the model server in an unloaded state."""
        self.config: ModelConfig | None = None
        self._loaded: bool = False
        self._start_time: float = time.monotonic()
        self._requests_served: int = 0
        self._error_count: int = 0
        logger.info("ModelServer initialised")

    async def load_model(self, config: ModelConfig) -> None:
        """Load a model into the server.

        Args:
            config: Model configuration specifying the artefact path and
                serving parameters.

        Raises:
            RuntimeError: If a model is already loaded; call ``unload_model``
                first.
        """
        if self._loaded:
            raise RuntimeError(
                f"Model '{self.config.model_id}' already loaded. "  # type: ignore[union-attr]
                "Call unload_model() first."
            )
        logger.info("Loading model '{}' from '{}'", config.model_id, config.model_path)
        await asyncio.sleep(0)  # Simulate I/O loading
        self.config = config
        self._loaded = True
        logger.info("Model '{}' loaded successfully", config.model_id)

    async def unload_model(self) -> None:
        """Unload the current model and free resources."""
        if not self._loaded or self.config is None:
            logger.warning("No model is currently loaded")
            return
        logger.info("Unloading model '{}'", self.config.model_id)
        await asyncio.sleep(0)
        self.config = None
        self._loaded = False

    async def predict(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> PredictResult:
        """Run inference on a single prompt.

        Args:
            prompt: Input text to the model.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0 = greedy, higher = more random).

        Returns:
            Inference result with generated text and latency.

        Raises:
            RuntimeError: If no model is loaded.
            asyncio.TimeoutError: If inference exceeds the configured timeout.
        """
        if not self._loaded or self.config is None:
            self._error_count += 1
            raise RuntimeError("No model loaded. Call load_model() first.")

        start = time.monotonic()
        try:
            result = await asyncio.wait_for(
                self._run_inference(prompt, max_tokens, temperature),
                timeout=self.config.timeout_seconds,
            )
        except asyncio.TimeoutError:
            self._error_count += 1
            raise
        else:
            self._requests_served += 1
            latency_ms = (time.monotonic() - start) * 1000
            result.latency_ms = round(latency_ms, 2)
            return result

    async def _run_inference(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> PredictResult:
        """Simulate model inference.

        Args:
            prompt: Input text.
            max_tokens: Output length budget.
            temperature: Sampling temperature.

        Returns:
            Simulated prediction result.
        """
        await asyncio.sleep(0)
        rng = np.random.default_rng(seed=hash(prompt) % (2**32))
        tokens_generated = int(rng.integers(10, min(max_tokens, 200)))
        simulated_output = f"[{self.config.model_id}] Analysis of '{prompt[:40]}...': " \
                           f"Simulated response with {tokens_generated} tokens."
        confidence = float(rng.uniform(0.7, 0.99))

        return PredictResult(
            model_id=self.config.model_id,  # type: ignore[union-attr]
            output=simulated_output,
            latency_ms=0.0,  # filled by caller
            tokens_generated=tokens_generated,
            confidence=round(confidence, 4),
        )

    async def batch_predict(
        self,
        prompts: list[str],
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> list[PredictResult]:
        """Run inference on a batch of prompts.

        Prompts are processed concurrently up to ``config.max_batch_size``.

        Args:
            prompts: List of input prompts.
            max_tokens: Maximum tokens per output.
            temperature: Sampling temperature.

        Returns:
            List of inference results in the same order as ``prompts``.

        Raises:
            RuntimeError: If no model is loaded.
            ValueError: If ``prompts`` is empty.
        """
        if not prompts:
            raise ValueError("prompts must not be empty")
        if not self._loaded or self.config is None:
            raise RuntimeError("No model loaded. Call load_model() first.")

        max_batch = self.config.max_batch_size
        results: list[PredictResult] = []

        for batch_start in range(0, len(prompts), max_batch):
            batch = prompts[batch_start: batch_start + max_batch]
            batch_results = await asyncio.gather(
                *[self.predict(p, max_tokens, temperature) for p in batch]
            )
            results.extend(batch_results)

        logger.debug("Batch predict: {} prompts, {} results", len(prompts), len(results))
        return results

    async def health_check(self) -> HealthStatus:
        """Return the current health status of the server.

        Returns:
            :class:`HealthStatus` snapshot.
        """
        await asyncio.sleep(0)
        uptime = time.monotonic() - self._start_time
        total = self._requests_served + self._error_count
        error_rate = self._error_count / total if total > 0 else 0.0

        status = HealthStatus(
            healthy=self._loaded,
            model_loaded=self._loaded,
            uptime_seconds=round(uptime, 2),
            requests_served=self._requests_served,
            error_rate=round(error_rate, 4),
        )
        return status
