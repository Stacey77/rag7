"""Quantum noise model: depolarising, bit-flip, and phase-flip error channels.

Provides :class:`NoiseModel` for simulating realistic quantum error channels
on state vectors and density matrices.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger


class NoiseModel:
    """Simulate quantum noise channels on qubit state vectors.

    Implements three standard error channels:

    * **Depolarising** – replaces the qubit state with the maximally mixed
      state with probability *p*.
    * **Bit-flip** – applies Pauli-X with probability *p*.
    * **Phase-flip** – applies Pauli-Z with probability *p*.
    * **Amplitude damping** – models energy relaxation (T1 decay).

    Attributes:
        depolarising_prob: Default depolarising error probability.
        bit_flip_prob: Default bit-flip error probability.
        phase_flip_prob: Default phase-flip error probability.
        amplitude_damping_gamma: Amplitude damping parameter (0 ≤ gamma ≤ 1).
    """

    _PAULI_X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    _PAULI_Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
    _PAULI_Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
    _I = np.eye(2, dtype=np.complex128)

    def __init__(
        self,
        depolarising_prob: float = 0.01,
        bit_flip_prob: float = 0.01,
        phase_flip_prob: float = 0.01,
        amplitude_damping_gamma: float = 0.01,
        seed: int | None = None,
    ) -> None:
        """Initialise NoiseModel.

        Args:
            depolarising_prob: Probability of depolarising error per gate.
            bit_flip_prob: Probability of bit-flip error per gate.
            phase_flip_prob: Probability of phase-flip error per gate.
            amplitude_damping_gamma: Energy relaxation parameter.
            seed: Random seed.
        """
        for name, val in [
            ("depolarising_prob", depolarising_prob),
            ("bit_flip_prob", bit_flip_prob),
            ("phase_flip_prob", phase_flip_prob),
            ("amplitude_damping_gamma", amplitude_damping_gamma),
        ]:
            if not 0 <= val <= 1:
                raise ValueError(f"{name} must be in [0, 1].")

        self.depolarising_prob = depolarising_prob
        self.bit_flip_prob = bit_flip_prob
        self.phase_flip_prob = phase_flip_prob
        self.amplitude_damping_gamma = amplitude_damping_gamma
        self._rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_kraus(
        self,
        rho: np.ndarray,
        kraus_ops: list[np.ndarray],
    ) -> np.ndarray:
        """Apply a Kraus operator representation to a density matrix.

        Args:
            rho: Density matrix (2×2 or 2^n × 2^n).
            kraus_ops: List of Kraus matrices satisfying sum(K†K) = I.

        Returns:
            Output density matrix.
        """
        return sum(K @ rho @ K.conj().T for K in kraus_ops)

    @staticmethod
    def _pure_to_dm(state: np.ndarray) -> np.ndarray:
        """Convert a pure state vector to a density matrix.

        Args:
            state: 1-D complex state vector.

        Returns:
            Density matrix ρ = |ψ⟩⟨ψ|.
        """
        return np.outer(state, state.conj())

    @staticmethod
    def _dm_to_pure(rho: np.ndarray) -> np.ndarray:
        """Extract the dominant eigenvector from a density matrix.

        Args:
            rho: Density matrix.

        Returns:
            Approximate pure state vector.
        """
        eigenvalues, eigenvectors = np.linalg.eigh(rho)
        return eigenvectors[:, -1]

    # ------------------------------------------------------------------
    # Public noise channels
    # ------------------------------------------------------------------

    def depolarising_channel(
        self,
        state: Any,
        prob: float | None = None,
    ) -> np.ndarray:
        """Apply the depolarising channel to a single-qubit state.

        The channel maps ρ → (1 - p)ρ + (p/4)(I ρ I + X ρ X + Y ρ Y + Z ρ Z)
        = (1 - p)ρ + (p/2)I

        Args:
            state: 1-D state vector or 2×2 density matrix.
            prob: Error probability; defaults to :attr:`depolarising_prob`.

        Returns:
            Output density matrix.
        """
        p = prob if prob is not None else self.depolarising_prob
        arr = np.asarray(state, dtype=np.complex128)
        rho = arr if arr.ndim == 2 else self._pure_to_dm(arr)

        kraus = [
            np.sqrt(1 - p) * self._I,
            np.sqrt(p / 3) * self._PAULI_X,
            np.sqrt(p / 3) * self._PAULI_Y,
            np.sqrt(p / 3) * self._PAULI_Z,
        ]
        return self._apply_kraus(rho, kraus)

    def bit_flip_channel(
        self,
        state: Any,
        prob: float | None = None,
    ) -> np.ndarray:
        """Apply the bit-flip channel.

        Maps ρ → (1-p)ρ + p X ρ X

        Args:
            state: State vector or density matrix.
            prob: Bit-flip probability; defaults to :attr:`bit_flip_prob`.

        Returns:
            Output density matrix.
        """
        p = prob if prob is not None else self.bit_flip_prob
        arr = np.asarray(state, dtype=np.complex128)
        rho = arr if arr.ndim == 2 else self._pure_to_dm(arr)
        kraus = [np.sqrt(1 - p) * self._I, np.sqrt(p) * self._PAULI_X]
        return self._apply_kraus(rho, kraus)

    def phase_flip_channel(
        self,
        state: Any,
        prob: float | None = None,
    ) -> np.ndarray:
        """Apply the phase-flip channel.

        Maps ρ → (1-p)ρ + p Z ρ Z

        Args:
            state: State vector or density matrix.
            prob: Phase-flip probability; defaults to :attr:`phase_flip_prob`.

        Returns:
            Output density matrix.
        """
        p = prob if prob is not None else self.phase_flip_prob
        arr = np.asarray(state, dtype=np.complex128)
        rho = arr if arr.ndim == 2 else self._pure_to_dm(arr)
        kraus = [np.sqrt(1 - p) * self._I, np.sqrt(p) * self._PAULI_Z]
        return self._apply_kraus(rho, kraus)

    def amplitude_damping_channel(
        self,
        state: Any,
        gamma: float | None = None,
    ) -> np.ndarray:
        """Apply the amplitude damping channel (T1 relaxation).

        Kraus operators: K0 = [[1,0],[0,sqrt(1-gamma)]], K1 = [[0,sqrt(gamma)],[0,0]]

        Args:
            state: State vector or density matrix.
            gamma: Damping parameter; defaults to :attr:`amplitude_damping_gamma`.

        Returns:
            Output density matrix.
        """
        g = gamma if gamma is not None else self.amplitude_damping_gamma
        arr = np.asarray(state, dtype=np.complex128)
        rho = arr if arr.ndim == 2 else self._pure_to_dm(arr)

        K0 = np.array([[1, 0], [0, np.sqrt(1 - g)]], dtype=np.complex128)
        K1 = np.array([[0, np.sqrt(g)], [0, 0]], dtype=np.complex128)
        return self._apply_kraus(rho, [K0, K1])

    def apply_noise_to_circuit(
        self,
        state_vector: Any,
        gate_count: int,
        noise_type: str = "depolarising",
    ) -> dict[str, Any]:
        """Apply noise after each gate in a circuit.

        Simulates accumulated noise over a sequence of gates.

        Args:
            state_vector: Initial state vector of length ``2^n``.
            gate_count: Number of gates in the circuit.
            noise_type: ``"depolarising"``, ``"bit_flip"``, or
                ``"phase_flip"``.

        Returns:
            Dict with ``final_density_matrix`` (list of lists),
            ``fidelity_with_ideal`` (float), ``purity`` (float).
        """
        arr = np.asarray(state_vector, dtype=np.complex128)
        ideal_rho = self._pure_to_dm(arr)
        rho = ideal_rho.copy()

        channel_map = {
            "depolarising": self.depolarising_channel,
            "bit_flip": self.bit_flip_channel,
            "phase_flip": self.phase_flip_channel,
        }
        if noise_type not in channel_map:
            raise ValueError(f"noise_type must be one of {list(channel_map)}")

        channel = channel_map[noise_type]

        if rho.shape == (2, 2):
            for _ in range(gate_count):
                rho = channel(rho)
        else:
            # Apply noise to each 2x2 sub-block (approximate)
            n = rho.shape[0]
            for _ in range(gate_count):
                p = (self.depolarising_prob + self.bit_flip_prob) / 2
                rho = (1 - p) * rho + p * np.eye(n, dtype=np.complex128) / n

        fidelity = float(np.real(np.trace(ideal_rho @ rho)))
        purity = float(np.real(np.trace(rho @ rho)))

        logger.debug(
            f"Noise circuit: {gate_count} gates, fidelity={fidelity:.4f}, "
            f"purity={purity:.4f}"
        )
        return {
            "final_density_matrix": rho.tolist(),
            "fidelity_with_ideal": round(fidelity, 6),
            "purity": round(purity, 6),
            "gate_count": gate_count,
            "noise_type": noise_type,
        }
