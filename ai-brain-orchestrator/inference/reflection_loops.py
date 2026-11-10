"""Reflection Loops – self-correction through iterative error identification.

The reflection loop re-evaluates a previous output, identifies logical or
factual errors, and applies targeted corrections, iterating until a
quality threshold is reached or a maximum number of passes is exhausted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

from shared.common.logger import get_logger

log = get_logger(__name__, service="ai-brain-orchestrator")

# Evaluator: takes a candidate output dict, returns a quality score in [0,1].
EvaluatorFn = Callable[[dict[str, Any]], Coroutine[Any, Any, float]]

# Corrector: takes a candidate output + list of errors, returns corrected output.
CorrectorFn = Callable[
    [dict[str, Any], list[str]], Coroutine[Any, Any, dict[str, Any]]
]


@dataclass
class ReflectionPass:
    """Record of a single reflection iteration.

    Attributes:
        pass_number: 1-indexed iteration count.
        errors_found: Error descriptions identified in this pass.
        quality_score: Post-correction quality score.
        corrections_applied: List of corrections made.
    """

    pass_number: int
    errors_found: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    corrections_applied: list[str] = field(default_factory=list)


@dataclass
class ReflectionReport:
    """Final summary of a complete reflection loop run.

    Attributes:
        passes: Ordered list of :class:`ReflectionPass` records.
        final_output: The output after all passes.
        converged: Whether the quality threshold was reached.
        final_score: Quality score of the final output.
    """

    passes: list[ReflectionPass] = field(default_factory=list)
    final_output: dict[str, Any] = field(default_factory=dict)
    converged: bool = False
    final_score: float = 0.0


class ReflectionLoops:
    """Iterative self-correction loop for AI model outputs.

    Attributes:
        _quality_threshold: Minimum quality score to stop iterating.
        _max_passes: Maximum reflection iterations.
    """

    def __init__(
        self,
        quality_threshold: float = 0.85,
        max_passes: int = 5,
    ) -> None:
        """Initialise the reflection loop engine.

        Args:
            quality_threshold: Quality score target. Iteration stops when this
                is reached or exceeded. Defaults to ``0.85``.
            max_passes: Hard cap on reflection iterations. Defaults to ``5``.

        Raises:
            ValueError: If *quality_threshold* is outside ``(0, 1]`` or
                *max_passes* < 1.
        """
        if not (0 < quality_threshold <= 1.0):
            raise ValueError(f"quality_threshold must be in (0, 1], got {quality_threshold}")
        if max_passes < 1:
            raise ValueError(f"max_passes must be at least 1, got {max_passes}")
        self._quality_threshold = quality_threshold
        self._max_passes = max_passes
        log.info(
            "ReflectionLoops initialised",
            quality_threshold=quality_threshold,
            max_passes=max_passes,
        )

    async def reflect(
        self,
        output: dict[str, Any],
        evaluator: EvaluatorFn,
        corrector: CorrectorFn,
    ) -> ReflectionReport:
        """Run the full reflection loop until convergence or max passes.

        Args:
            output: The initial model output to reflect on.
            evaluator: Async callable scoring output quality in ``[0, 1]``.
            corrector: Async callable that applies corrections given errors.

        Returns:
            :class:`ReflectionReport` summarising all passes and the final output.
        """
        report = ReflectionReport(final_output=dict(output))
        current_output = dict(output)

        for pass_num in range(1, self._max_passes + 1):
            errors = await self.identify_errors(current_output)
            score = await evaluator(current_output)

            reflection_pass = ReflectionPass(
                pass_number=pass_num,
                errors_found=errors,
                quality_score=score,
            )

            if score >= self._quality_threshold:
                report.converged = True
                report.passes.append(reflection_pass)
                log.info(
                    "Reflection converged",
                    pass_number=pass_num,
                    score=f"{score:.3f}",
                )
                break

            if errors:
                corrected = await self.correct(current_output, errors, corrector)
                reflection_pass.corrections_applied = [
                    f"corrected key: {k}" for k in corrected if corrected.get(k) != current_output.get(k)
                ]
                current_output = corrected

            report.passes.append(reflection_pass)
            log.debug(
                "Reflection pass complete",
                pass_number=pass_num,
                score=f"{score:.3f}",
                errors=len(errors),
            )

        report.final_output = current_output
        report.final_score = report.passes[-1].quality_score if report.passes else 0.0
        log.info(
            "Reflection loop finished",
            passes=len(report.passes),
            converged=report.converged,
            final_score=f"{report.final_score:.3f}",
        )
        return report

    async def identify_errors(self, output: dict[str, Any]) -> list[str]:
        """Analyse *output* and return a list of identified error descriptions.

        This base implementation uses heuristic checks.  Subclasses or callers
        can inject domain-specific logic via the *corrector* callable.

        Args:
            output: The model output dict to inspect.

        Returns:
            List of string error descriptions (empty when no errors found).
        """
        errors: list[str] = []

        if not output:
            errors.append("Output is empty")
            return errors

        # Check for explicit error flags.
        if output.get("error"):
            errors.append(f"Output contains error flag: {output['error']}")

        # Check for NaN / None values in numeric fields.
        for key, value in output.items():
            if value is None:
                errors.append(f"Field '{key}' is None")
            elif isinstance(value, float) and (value != value):  # NaN check
                errors.append(f"Field '{key}' is NaN")

        log.debug("Errors identified", count=len(errors))
        return errors

    async def correct(
        self,
        output: dict[str, Any],
        errors: list[str],
        corrector: CorrectorFn,
    ) -> dict[str, Any]:
        """Apply the *corrector* callable to fix identified errors.

        Args:
            output: Current model output.
            errors: List of error descriptions from :meth:`identify_errors`.
            corrector: Async callable that returns a corrected output dict.

        Returns:
            Corrected output dict.
        """
        try:
            corrected = await corrector(output, errors)
            log.debug("Corrections applied", error_count=len(errors))
            return corrected
        except Exception as exc:  # noqa: BLE001
            log.error("Correction failed", error=str(exc))
            return dict(output)  # Return unchanged on failure.
