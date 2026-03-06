"""EnergyBudgeter — I(x,v,t) 자동 제어

솔라시스템: 태양의 에너지 배분 — 폭발(탐색), 중력(정착), 포획(리콜)
인지과학: 주의(Attention) — 분산(탐색), 집중(정착), 방향성(리콜)
물리: I(x,v,t) = α_e·I_explore + α_x·I_exploit + α_r·I_recall

Author: GNJz (Qquarts)
"""

from __future__ import annotations
import numpy as np
from typing import Any, Dict, Optional

from L3_memory.memory_store import MemoryStore

_NORM_EPS = 1e-10


class EnergyBudgeter:
    """에너지 주입 정책: 탐색/정착/리콜"""

    def __init__(self, config, rng_seed: Optional[int] = None):
        self.config = config
        self._rng = np.random.default_rng(rng_seed)
        self._alpha_explore: float = 0.5
        self._alpha_exploit: float = 0.5
        self._recall_target: Optional[np.ndarray] = None
        self._mode: str = "balanced"

    @property
    def mode(self) -> str:
        return self._mode

    def set_recall_target(self, target: Optional[np.ndarray]) -> None:
        if target is not None:
            target = np.asarray(target, dtype=float)
        self._recall_target = target

    def update_policy(self, entropy_rate: float, transition_rate: float) -> None:
        """분석 결과를 기반으로 탐색/정착 비율 자동 조절"""
        s = self.config.mode_switch_smoothing

        if entropy_rate < self.config.entropy_threshold_low:
            self._alpha_explore = min(1.0, self._alpha_explore + s)
            self._alpha_exploit = max(0.0, self._alpha_exploit - s)
            self._mode = "explore"
        elif transition_rate > self.config.transition_rate_high:
            self._alpha_explore = max(0.0, self._alpha_explore - s)
            self._alpha_exploit = min(1.0, self._alpha_exploit + s)
            self._mode = "exploit"
        else:
            self._alpha_explore += s * (0.5 - self._alpha_explore)
            self._alpha_exploit += s * (0.5 - self._alpha_exploit)
            self._mode = "balanced"

    def compute_injection(self, x: np.ndarray, v: np.ndarray, store: MemoryStore) -> np.ndarray:
        """현재 상태에서 에너지 주입 벡터 I(x,v,t) 계산"""
        dim = len(x)
        I = np.zeros(dim)
        I += self._alpha_explore * self._explore(dim)
        I += self._alpha_exploit * self._exploit(x, store)
        if self._recall_target is not None:
            I += self._recall(x)
        return I

    def _explore(self, dim: int) -> np.ndarray:
        direction = self._rng.standard_normal(dim)
        norm = np.linalg.norm(direction)
        if norm > _NORM_EPS:
            direction /= norm
        return self.config.explore_strength * direction

    def _exploit(self, x: np.ndarray, store: MemoryStore) -> np.ndarray:
        if store.count == 0:
            return np.zeros(len(x))
        idx, dist = store._find_nearest(x)
        if idx < 0 or dist < _NORM_EPS:
            return np.zeros(len(x))
        direction = store._wells[idx].center - x
        direction /= np.linalg.norm(direction)
        strength = self.config.exploit_strength * np.exp(-dist / self.config.exploit_range)
        return strength * direction

    def _recall(self, x: np.ndarray) -> np.ndarray:
        if self._recall_target is None:
            return np.zeros(len(x))
        displacement = self._recall_target - x
        return self.config.recall_strength * displacement

    def info(self) -> Dict[str, Any]:
        return {
            "mode": self._mode,
            "alpha_explore": round(self._alpha_explore, 4),
            "alpha_exploit": round(self._alpha_exploit, 4),
            "recall_active": self._recall_target is not None,
        }
