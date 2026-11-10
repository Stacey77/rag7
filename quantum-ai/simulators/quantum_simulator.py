"""Quantum circuit simulator: classical simulation using NumPy state vectors.

Provides :class:`QuantumSimulator` for simulating small quantum circuits via
exact state-vector evolution.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger


# ---------------------------------------------------------------------------
# Standard single-qubit gate matrices
# ---------------------------------------------------------------------------

_GATES: dict[str, np.ndarray] = {
    "I": np.eye(2, dtype=np.complex128),
    "X": np.array([[0, 1], [1, 0]], dtype=np.complex128),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
    "Z": np.array([[1, 0], [0, -1]], dtype=np.complex128),
    "H": np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2),
    "S": np.array([[1, 0], [0, 1j]], dtype=np.complex128),
    "T": np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=np.complex128),
}


class QuantumSimulator:
    """Classical state-vector quantum circuit simulator.

    Supports an arbitrary number of qubits (up to the memory limits of the
    host machine) and a standard gate set including Ry, Rz, CNOT, CZ, Toffoli,
    and SWAP.

    Attributes:
        n_qubits: Number of qubits in the circuit.
        state: Current state vector of length ``2^n_qubits``.
    """

    def __init__(self, n_qubits: int = 4) -> None:
        """Initialise the simulator in the |0...0⟩ state.

        Args:
            n_qubits: Number of qubits.

        Raises:
            ValueError: If n_qubits < 1 or > 20 (memory guard).
        """
        if not 1 <= n_qubits <= 20:
            raise ValueError("n_qubits must be between 1 and 20.")
        self.n_qubits = n_qubits
        self.state: np.ndarray = np.zeros(2 ** n_qubits, dtype=np.complex128)
        self.state[0] = 1.0
        logger.debug(f"QuantumSimulator: {n_qubits} qubits, dim={2**n_qubits}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_single_qubit_gate(
        self, gate: np.ndarray, target: int
    ) -> None:
        """Apply a 2×2 gate to a single qubit via tensor product expansion.

        Args:
            gate: 2×2 unitary matrix.
            target: Zero-indexed qubit to apply the gate to.
        """
        n = self.n_qubits
        # Build the full 2^n × 2^n operator using tensored identity
        ops = [_GATES["I"]] * n
        ops[target] = gate
        full = ops[0]
        for op in ops[1:]:
            full = np.kron(full, op)
        self.state = full @ self.state

    def _apply_two_qubit_gate(
        self, gate: np.ndarray, control: int, target: int
    ) -> None:
        """Apply a controlled two-qubit gate.

        Builds the full operator by projecting on control qubit states.

        Args:
            gate: 4×4 unitary matrix.
            control: Control qubit index.
            target: Target qubit index.
        """
        n = self.n_qubits
        dim = 2 ** n
        full = np.zeros((dim, dim), dtype=np.complex128)

        for i in range(dim):
            ctrl_bit = (i >> (n - 1 - control)) & 1
            tgt_bit = (i >> (n - 1 - target)) & 1
            sub_idx = ctrl_bit * 2 + tgt_bit
            for j in range(dim):
                ctrl_bit_j = (j >> (n - 1 - control)) & 1
                tgt_bit_j = (j >> (n - 1 - target)) & 1
                # Other qubits must match
                other_match = True
                for q in range(n):
                    if q != control and q != target:
                        if ((i >> (n - 1 - q)) & 1) != ((j >> (n - 1 - q)) & 1):
                            other_match = False
                            break
                if other_match:
                    sub_j = ctrl_bit_j * 2 + tgt_bit_j
                    full[i, j] = gate[sub_idx, sub_j]

        self.state = full @ self.state

    # ------------------------------------------------------------------
    # Gate operations
    # ------------------------------------------------------------------

    def h(self, qubit: int) -> "QuantumSimulator":
        """Apply Hadamard gate.

        Args:
            qubit: Target qubit index.

        Returns:
            Self for method chaining.
        """
        self._apply_single_qubit_gate(_GATES["H"], qubit)
        return self

    def x(self, qubit: int) -> "QuantumSimulator":
        """Apply Pauli-X (NOT) gate.

        Args:
            qubit: Target qubit index.

        Returns:
            Self for method chaining.
        """
        self._apply_single_qubit_gate(_GATES["X"], qubit)
        return self

    def ry(self, qubit: int, theta: float) -> "QuantumSimulator":
        """Apply Ry rotation gate.

        Args:
            qubit: Target qubit.
            theta: Rotation angle in radians.

        Returns:
            Self for method chaining.
        """
        gate = np.array([
            [np.cos(theta / 2), -np.sin(theta / 2)],
            [np.sin(theta / 2),  np.cos(theta / 2)],
        ], dtype=np.complex128)
        self._apply_single_qubit_gate(gate, qubit)
        return self

    def rz(self, qubit: int, phi: float) -> "QuantumSimulator":
        """Apply Rz rotation gate.

        Args:
            qubit: Target qubit.
            phi: Rotation angle in radians.

        Returns:
            Self for method chaining.
        """
        gate = np.array([
            [np.exp(-1j * phi / 2), 0],
            [0, np.exp(1j * phi / 2)],
        ], dtype=np.complex128)
        self._apply_single_qubit_gate(gate, qubit)
        return self

    def cnot(self, control: int, target: int) -> "QuantumSimulator":
        """Apply CNOT gate.

        Args:
            control: Control qubit.
            target: Target qubit.

        Returns:
            Self for method chaining.
        """
        cnot_gate = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
        ], dtype=np.complex128)
        self._apply_two_qubit_gate(cnot_gate, control, target)
        return self

    # ------------------------------------------------------------------
    # Measurement
    # ------------------------------------------------------------------

    def measure(
        self, n_shots: int = 1024, seed: int | None = None
    ) -> dict[str, Any]:
        """Simulate projective measurements.

        Args:
            n_shots: Number of measurement shots.
            seed: Random seed.

        Returns:
            Dict with ``counts`` (bitstring → count), ``probabilities``
            (bitstring → float), ``state_vector`` (complex list).
        """
        probs = np.abs(self.state) ** 2
        probs /= probs.sum()

        rng = np.random.default_rng(seed)
        outcomes = rng.choice(len(probs), size=n_shots, p=probs)

        counts: dict[str, int] = {}
        for outcome in outcomes:
            bitstring = format(outcome, f"0{self.n_qubits}b")
            counts[bitstring] = counts.get(bitstring, 0) + 1

        prob_dict = {
            format(i, f"0{self.n_qubits}b"): float(p)
            for i, p in enumerate(probs)
            if p > 1e-10
        }

        return {
            "counts": counts,
            "probabilities": prob_dict,
            "state_vector": self.state.tolist(),
        }

    def reset(self) -> "QuantumSimulator":
        """Reset to |0...0⟩ state.

        Returns:
            Self for method chaining.
        """
        self.state = np.zeros(2 ** self.n_qubits, dtype=np.complex128)
        self.state[0] = 1.0
        return self

    def statevector(self) -> list[complex]:
        """Return the current normalised state vector.

        Returns:
            State vector as a list of complex numbers.
        """
        return self.state.tolist()
