"""LSTM-based time-series forecasting (simulated with math/statistics)."""
from __future__ import annotations
import math
import logging
import statistics
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


@dataclass
class LSTMConfig:
    hidden_size: int = 32
    num_layers: int = 2
    seq_len: int = 10
    learning_rate: float = 0.01
    epochs: int = 50


class LSTMCell:
    """Simulated LSTM cell using tanh/sigmoid approximations."""

    def __init__(self, input_size: int, hidden_size: int) -> None:
        self.input_size = input_size
        self.hidden_size = hidden_size
        import random
        rng = random.Random(42)
        def rand_weights(n: int) -> List[float]:
            return [rng.gauss(0, 0.1) for _ in range(n)]
        self.W_f = rand_weights(input_size + hidden_size)
        self.W_i = rand_weights(input_size + hidden_size)
        self.W_o = rand_weights(input_size + hidden_size)
        self.W_c = rand_weights(input_size + hidden_size)

    @staticmethod
    def _sigmoid(x: float) -> float:
        return 1.0 / (1.0 + math.exp(-max(-500.0, min(500.0, x))))

    @staticmethod
    def _tanh(x: float) -> float:
        return math.tanh(max(-500.0, min(500.0, x)))

    def _gate(self, weights: List[float], combined: List[float]) -> float:
        s = sum(w * x for w, x in zip(weights, combined))
        return s

    def forward(self, x: float, h_prev: List[float],
                c_prev: List[float]) -> Tuple[List[float], List[float]]:
        combined = [x] + h_prev
        f = self._sigmoid(self._gate(self.W_f[:len(combined)], combined))
        i = self._sigmoid(self._gate(self.W_i[:len(combined)], combined))
        o = self._sigmoid(self._gate(self.W_o[:len(combined)], combined))
        c_tilde = self._tanh(self._gate(self.W_c[:len(combined)], combined))
        c_new = [f * c_prev[k] + i * c_tilde for k in range(self.hidden_size)]
        h_new = [o * self._tanh(c_new[k]) for k in range(self.hidden_size)]
        return h_new, c_new


class LSTMPredictor:
    def __init__(self, config: Optional[LSTMConfig] = None) -> None:
        self.config = config or LSTMConfig()
        self.cells = [LSTMCell(1, self.config.hidden_size)
                      for _ in range(self.config.num_layers)]
        self._trained = False
        self._history: List[float] = []
        self._mean: float = 0.0
        self._std: float = 1.0
        logger.info("LSTMPredictor initialised: %s", self.config)

    def _normalize(self, series: List[float]) -> List[float]:
        self._mean = statistics.mean(series)
        self._std = statistics.stdev(series) if len(series) > 1 else 1.0
        return [(x - self._mean) / (self._std + 1e-9) for x in series]

    def _denormalize(self, val: float) -> float:
        return val * self._std + self._mean

    def _run_cells(self, seq: List[float]) -> float:
        h = [[0.0] * self.config.hidden_size for _ in range(self.config.num_layers)]
        c = [[0.0] * self.config.hidden_size for _ in range(self.config.num_layers)]
        out = 0.0
        for x in seq:
            inp = x
            for layer_idx, cell in enumerate(self.cells):
                h[layer_idx], c[layer_idx] = cell.forward(inp, h[layer_idx], c[layer_idx])
                inp = h[layer_idx][0]
            out = h[-1][0]
        return out

    def fit(self, time_series: List[float]) -> None:
        logger.info("Fitting LSTMPredictor on %d samples", len(time_series))
        self._history = list(time_series)
        norm = self._normalize(time_series)
        for epoch in range(self.config.epochs):
            for i in range(len(norm) - self.config.seq_len - 1):
                seq = norm[i: i + self.config.seq_len]
                _ = self._run_cells(seq)
        self._trained = True
        logger.info("Training complete. mean=%.4f std=%.4f", self._mean, self._std)

    def predict(self, steps_ahead: int = 1) -> List[float]:
        if not self._trained:
            raise RuntimeError("Call fit() before predict()")
        logger.info("Predicting %d steps ahead", steps_ahead)
        norm = self._normalize(self._history)
        window = list(norm[-self.config.seq_len:])
        predictions = []
        for _ in range(steps_ahead):
            out = self._run_cells(window)
            predictions.append(self._denormalize(out))
            window = window[1:] + [out]
        return predictions

    def rolling_forecast(self, horizon: int = 5) -> List[float]:
        logger.info("Rolling forecast for horizon=%d", horizon)
        results = []
        for i in range(horizon):
            preds = self.predict(steps_ahead=1)
            results.append(preds[0])
            self._history.append(preds[0])
        return results

    def anomaly_score(self, value: float) -> float:
        if len(self._history) < 2:
            return 0.0
        mean = statistics.mean(self._history[-50:])
        std = statistics.stdev(self._history[-50:]) if len(self._history[-50:]) > 1 else 1.0
        score = abs(value - mean) / (std + 1e-9)
        logger.debug("Anomaly score for %.4f: %.4f", value, score)
        return round(score, 4)

    def evaluate(self, test_data: List[float]) -> dict:
        logger.info("Evaluating on %d test points", len(test_data))
        preds = self.predict(steps_ahead=len(test_data))
        errors = [abs(p - a) for p, a in zip(preds, test_data)]
        mae = statistics.mean(errors)
        rmse = math.sqrt(statistics.mean([e ** 2 for e in errors]))
        return {"mae": round(mae, 4), "rmse": round(rmse, 4),
                "n": len(test_data), "predictions": preds}
