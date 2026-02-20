"""Grover's search algorithm simulation: pattern matching via amplitude amplification.

Provides :class:`GroverSearch` – a classical simulation of Grover's algorithm
that uses amplitude amplification to find target patterns in a database.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
from loguru import logger


class GroverSearch:
    """Classical simulation of Grover's quantum search algorithm.

    Simulates amplitude amplification over a 2^n dimensional state vector to
    find entries in a database that satisfy an oracle predicate.  Applied to
    trading pattern matching (e.g., finding historical price patterns similar
    to a query window).

    Attributes:
        n_qubits: Number of logical qubits (database size = 2^n_qubits).
        n_iterations: Number of Grover iterations.  Defaults to the optimal
            floor(pi/4 * sqrt(N/k)) where k = expected number of targets.
    """

    def __init__(
        self,
        n_qubits: int = 8,
        n_iterations: int | None = None,
    ) -> None:
        """Initialise GroverSearch.

        Args:
            n_qubits: Number of qubits (search space = 2^n_qubits).
            n_iterations: Grover iterations.  None → use optimal count.
        """
        if n_qubits < 1:
            raise ValueError("n_qubits must be at least 1.")
        self.n_qubits = n_qubits
        self.n_iterations = n_iterations
        self._database_size = 2 ** n_qubits

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _optimal_iterations(self, n_targets: int) -> int:
        """Compute the optimal number of Grover iterations.

        Args:
            n_targets: Expected number of marked items.

        Returns:
            Optimal iteration count.
        """
        N = self._database_size
        k = max(1, n_targets)
        return max(1, int(np.floor(np.pi / 4 * np.sqrt(N / k))))

    def _oracle(
        self, state: np.ndarray, targets: set[int]
    ) -> np.ndarray:
        """Apply the oracle: negate amplitudes of target states.

        Args:
            state: Amplitude vector of length N.
            targets: Set of target indices.

        Returns:
            Modified amplitude vector.
        """
        result = state.copy()
        for t in targets:
            if t < len(result):
                result[t] *= -1
        return result

    @staticmethod
    def _diffusion(state: np.ndarray) -> np.ndarray:
        """Apply the Grover diffusion (inversion about the mean) operator.

        Args:
            state: Current amplitude vector.

        Returns:
            Diffused amplitude vector.
        """
        mean = np.mean(state)
        return 2 * mean - state

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def search(
        self,
        oracle_fn: Callable[[int], bool],
        n_targets: int = 1,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Run Grover search with a given oracle function.

        Args:
            oracle_fn: Callable that takes an integer index and returns True
                if it is a target item.
            n_targets: Expected number of marked items (used to set iterations).
            seed: Random seed (unused in deterministic simulation but kept for
                API consistency).

        Returns:
            Dict with keys ``found_indices`` (list of top candidates),
            ``probabilities`` (full probability vector), ``iterations``,
            ``database_size``.
        """
        N = self._database_size
        iterations = self.n_iterations or self._optimal_iterations(n_targets)

        # Build target set (evaluate oracle classically)
        targets = {i for i in range(N) if oracle_fn(i)}
        if not targets:
            logger.warning("Oracle returned no targets.")
            return {
                "found_indices": [],
                "probabilities": [1 / N] * N,
                "iterations": 0,
                "database_size": N,
            }

        # Uniform superposition
        state = np.ones(N, dtype=np.float64) / np.sqrt(N)

        logger.debug(
            f"Grover search: N={N}, |targets|={len(targets)}, "
            f"iterations={iterations}"
        )

        for _ in range(iterations):
            state = self._oracle(state, targets)
            state = self._diffusion(state)

        probs = state ** 2
        probs = np.clip(probs, 0, None)
        probs /= probs.sum()

        # Top-k candidates by probability
        top_k = min(n_targets * 2, N)
        top_indices = np.argsort(probs)[-top_k:][::-1].tolist()

        return {
            "found_indices": top_indices,
            "probabilities": probs.tolist(),
            "iterations": iterations,
            "database_size": N,
            "true_targets": sorted(targets),
        }

    def pattern_match(
        self,
        query: Any,
        database: Any,
        threshold: float = 0.9,
    ) -> dict[str, Any]:
        """Find patterns in *database* similar to *query* using Grover search.

        Converts cosine similarity to an oracle predicate and runs amplitude
        amplification to boost high-similarity entries.

        Args:
            query: 1-D array-like (normalised) query pattern.
            database: 2-D array-like of shape ``(n_entries, pattern_length)``.
            threshold: Cosine similarity threshold for marking a hit.

        Returns:
            Dict with ``matches`` (list of (index, similarity) tuples),
            ``grover_probabilities`` (top-N), ``n_matches``.
        """
        q = np.asarray(query, dtype=np.float64)
        db = np.asarray(database, dtype=np.float64)
        q_norm = q / (np.linalg.norm(q) + 1e-9)

        similarities = np.array([
            float(np.dot(q_norm, db[i] / (np.linalg.norm(db[i]) + 1e-9)))
            for i in range(len(db))
        ])

        n_db = len(db)
        n_qubits = max(1, int(np.ceil(np.log2(n_db + 1))))
        n_qubits = min(n_qubits, self.n_qubits)
        n_search = 2 ** n_qubits

        oracle_fn = lambda i: i < n_db and similarities[i] >= threshold
        n_targets = max(1, int(np.sum(similarities >= threshold)))

        grover_result = self.search(oracle_fn, n_targets)

        matches = [
            (i, round(float(similarities[i]), 4))
            for i in range(n_db)
            if similarities[i] >= threshold
        ]
        matches.sort(key=lambda x: -x[1])

        return {
            "matches": matches,
            "n_matches": len(matches),
            "grover_probabilities": grover_result["probabilities"][:n_db],
            "similarities": similarities.tolist(),
        }
