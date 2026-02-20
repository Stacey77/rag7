"""Quantum-inspired neural network with parameterised rotation gates.

Provides :class:`QuantumNeuralNetwork` implementing a quantum-circuit-inspired
neural network layer stack using classical NumPy simulation.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger


class QuantumNeuralNetwork:
    """Quantum-inspired neural network using parameterised rotation gates.

    Each layer applies:

    1. **Ry rotation** – ``R_y(theta) = [[cos(t/2), -sin(t/2)], [sin(t/2), cos(t/2)]]``
       applied element-wise as an activation-like non-linearity.
    2. **Rz rotation** – phase shift ``R_z(phi) = diag(e^{-i phi/2}, e^{i phi/2})``,
       simulated as a magnitude-preserving phase rotation.
    3. **Entanglement layer** – a parameterised mixing matrix derived from a
       random unitary to simulate CNOT-based entanglement.

    Attributes:
        n_qubits: Width of the network (number of quantum feature dimensions).
        n_layers: Depth of the network.
        learning_rate: Parameter update step for gradient-free training.
        seed: Random seed.
    """

    def __init__(
        self,
        n_qubits: int = 4,
        n_layers: int = 3,
        learning_rate: float = 0.01,
        seed: int | None = None,
    ) -> None:
        """Initialise QuantumNeuralNetwork.

        Args:
            n_qubits: Number of qubits (input/output feature dimension).
            n_layers: Circuit depth.
            learning_rate: Step size for parameter updates.
            seed: Random seed.
        """
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.learning_rate = learning_rate
        self._rng = np.random.default_rng(seed)

        # Initialise trainable parameters: theta (Ry), phi (Rz), mixing matrix
        self.thetas = self._rng.uniform(0, 2 * np.pi, (n_layers, n_qubits))
        self.phis = self._rng.uniform(0, 2 * np.pi, (n_layers, n_qubits))
        self.mixing = [
            self._random_unitary(n_qubits) for _ in range(n_layers)
        ]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _random_unitary(self, n: int) -> np.ndarray:
        """Generate a random orthogonal matrix via QR decomposition.

        Args:
            n: Matrix dimension.

        Returns:
            n×n orthogonal matrix.
        """
        A = self._rng.standard_normal((n, n))
        Q, _ = np.linalg.qr(A)
        return Q

    def _ry_gate(self, x: np.ndarray, theta: np.ndarray) -> np.ndarray:
        """Apply element-wise Ry rotation.

        Args:
            x: Input feature vector.
            theta: Rotation angles.

        Returns:
            Rotated vector.
        """
        return x * np.cos(theta / 2) + np.roll(x, 1) * np.sin(theta / 2)

    def _rz_gate(self, x: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Apply element-wise Rz phase gate (real-valued approximation).

        Args:
            x: Input feature vector.
            phi: Phase angles.

        Returns:
            Phase-shifted vector.
        """
        return x * np.cos(phi) - np.roll(x, 1) * np.sin(phi)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def forward(self, x: Any) -> np.ndarray:
        """Forward pass through the quantum-inspired network.

        Args:
            x: Input feature vector of length ``n_qubits`` or batch of shape
               ``(batch_size, n_qubits)``.

        Returns:
            Output array of the same shape.

        Raises:
            ValueError: If the last dimension of *x* does not match
                ``n_qubits``.
        """
        arr = np.asarray(x, dtype=np.float64)
        single = arr.ndim == 1
        if single:
            arr = arr[np.newaxis, :]

        if arr.shape[-1] != self.n_qubits:
            raise ValueError(
                f"Input last dim {arr.shape[-1]} != n_qubits {self.n_qubits}"
            )

        out = arr.copy()
        for layer in range(self.n_layers):
            out = self._ry_gate(out, self.thetas[layer])
            out = self._rz_gate(out, self.phis[layer])
            out = out @ self.mixing[layer].T
            # Non-linear activation (tanh as quantum measurement-like squashing)
            out = np.tanh(out)

        return out[0] if single else out

    def update_params(
        self,
        grad_thetas: np.ndarray,
        grad_phis: np.ndarray,
    ) -> None:
        """Update trainable parameters via gradient descent.

        Args:
            grad_thetas: Gradient array of shape ``(n_layers, n_qubits)``
                for theta parameters.
            grad_phis: Gradient array of shape ``(n_layers, n_qubits)``
                for phi parameters.
        """
        self.thetas -= self.learning_rate * grad_thetas
        self.phis -= self.learning_rate * grad_phis

    def parameter_shift_gradient(
        self,
        x: Any,
        loss_fn: Any,
        shift: float = np.pi / 2,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Estimate gradients using the parameter-shift rule.

        The parameter-shift rule: ``dE/dtheta = (E(theta+pi/2) - E(theta-pi/2)) / 2``

        Args:
            x: Input feature vector.
            loss_fn: Callable that takes a forward-pass output and returns a
                scalar loss.
            shift: Shift angle (default pi/2 for standard shift rule).

        Returns:
            Tuple of ``(grad_thetas, grad_phis)`` each of shape
            ``(n_layers, n_qubits)``.
        """
        grad_thetas = np.zeros_like(self.thetas)
        grad_phis = np.zeros_like(self.phis)

        for l in range(self.n_layers):
            for q in range(self.n_qubits):
                # Theta gradients
                self.thetas[l, q] += shift
                loss_plus = loss_fn(self.forward(x))
                self.thetas[l, q] -= 2 * shift
                loss_minus = loss_fn(self.forward(x))
                self.thetas[l, q] += shift
                grad_thetas[l, q] = (loss_plus - loss_minus) / 2

                # Phi gradients
                self.phis[l, q] += shift
                loss_plus = loss_fn(self.forward(x))
                self.phis[l, q] -= 2 * shift
                loss_minus = loss_fn(self.forward(x))
                self.phis[l, q] += shift
                grad_phis[l, q] = (loss_plus - loss_minus) / 2

        return grad_thetas, grad_phis

    def get_params(self) -> dict[str, Any]:
        """Return current trainable parameters.

        Returns:
            Dict with keys ``thetas``, ``phis`` as nested lists.
        """
        return {
            "thetas": self.thetas.tolist(),
            "phis": self.phis.tolist(),
            "n_layers": self.n_layers,
            "n_qubits": self.n_qubits,
        }
