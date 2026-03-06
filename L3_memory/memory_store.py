"""MemoryStore — 동적 우물 관리 (기억 생애주기)

솔라시스템: 행성의 탄생·성장·소멸
인지과학: 기억의 형성·강화·망각
물리: V(x, t)의 시간 진화

수식:
  강화: A_i += η · exp(-||x - c_i||²/(2σ²)) · dt
  망각: A_i *= exp(-λ · dt)
  생성: min_dist(x, centers) > d_create → new well
  소멸: A_i < A_min → delete

Author: GNJz (Qquarts)
"""

from __future__ import annotations
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
import logging

from L1_dynamics.Phase_B.multi_well_potential import GaussianWell, MultiWellPotential


class MemoryStore:
    """동적 우물 관리: 생성·강화·감쇠·소멸

    WellRegistry의 정적 저장소를 시간 의존 시스템으로 확장한다.
    """

    def __init__(self, config, dim: int = 1):
        self.config = config
        self.dim = dim
        self._wells: List[GaussianWell] = []
        self._visit_counts: List[int] = []
        self._ages: List[float] = []
        self._total_time: float = 0.0
        self._version: int = 0
        self.logger = logging.getLogger("MemoryStore")

    @property
    def count(self) -> int:
        return len(self._wells)

    @property
    def version(self) -> int:
        return self._version

    @property
    def wells(self) -> List[GaussianWell]:
        return list(self._wells)

    @property
    def amplitudes(self) -> np.ndarray:
        if not self._wells:
            return np.array([])
        return np.array([w.amplitude for w in self._wells])

    @property
    def centers(self) -> np.ndarray:
        if not self._wells:
            return np.empty((0, self.dim))
        return np.array([w.center for w in self._wells])

    def encode(self, pattern: np.ndarray, strength: float = 1.0) -> int:
        """새 입력 패턴을 기억으로 인코딩

        Returns: 생성 또는 강화된 우물 인덱스
        """
        pattern = np.asarray(pattern, dtype=float)
        nearest_idx, nearest_dist = self._find_nearest(pattern)

        if nearest_idx >= 0 and nearest_dist < self.config.merge_distance:
            return self._strengthen(nearest_idx, pattern, strength)
        if nearest_idx >= 0 and nearest_dist < self.config.creation_distance:
            return self._strengthen(nearest_idx, pattern, strength)
        return self._create(pattern, strength)

    def step(self, x: np.ndarray, dt: float) -> None:
        """매 시뮬레이션 스텝: 근접 강화 + 전체 감쇠 + 소멸 검사"""
        x = np.asarray(x, dtype=float)
        self._reinforce_nearby(x, dt)
        self._decay_all(dt)
        self._prune()
        self._total_time += dt

    def recall(self, cue: np.ndarray) -> Optional[int]:
        """부분 단서로 가장 가까운 기억 인출"""
        if not self._wells:
            return None
        cue = np.asarray(cue, dtype=float)
        idx, _ = self._find_nearest(cue)
        return idx if idx >= 0 else None

    def export_potential(self) -> Optional[MultiWellPotential]:
        """현재 우물 상태를 MultiWellPotential로 내보내기"""
        if not self._wells:
            return None
        return MultiWellPotential(list(self._wells))

    def info(self) -> Dict[str, Any]:
        return {
            "n_wells": self.count,
            "total_time": self._total_time,
            "version": self._version,
            "wells": [
                {
                    "index": i,
                    "center": w.center.tolist(),
                    "amplitude": round(w.amplitude, 4),
                    "sigma": round(w.sigma, 4),
                    "visits": self._visit_counts[i],
                    "age": round(self._ages[i], 2),
                }
                for i, w in enumerate(self._wells)
            ],
        }

    # ── 내부 메커니즘 ──

    def _create(self, pattern: np.ndarray, strength: float) -> int:
        if self.count >= self.config.max_wells:
            weakest = int(np.argmin(self.amplitudes))
            self._remove(weakest)

        A = min(self.config.amplitude_init * strength, self.config.amplitude_max)
        well = GaussianWell(center=pattern.copy(), amplitude=A, sigma=self.config.sigma_init)
        self._wells.append(well)
        self._visit_counts.append(1)
        self._ages.append(0.0)
        self._version += 1
        self.logger.info(f"Well #{self.count - 1} created: center={pattern.tolist()}, A={A:.4f}")
        return self.count - 1

    def _strengthen(self, idx: int, pattern: np.ndarray, strength: float) -> int:
        old = self._wells[idx]
        proximity = np.exp(-np.dot(pattern - old.center, pattern - old.center) / (2.0 * old.sigma ** 2))
        delta_A = self.config.eta * strength * proximity
        new_A = min(old.amplitude + delta_A, self.config.amplitude_max)
        self._wells[idx] = GaussianWell(center=old.center, amplitude=new_A, sigma=old.sigma)
        self._visit_counts[idx] += 1
        self._version += 1
        return idx

    def _reinforce_nearby(self, x: np.ndarray, dt: float) -> None:
        threshold = getattr(self.config, "reinforce_proximity_threshold", 0.01)
        for i, w in enumerate(self._wells):
            d = x - w.center
            proximity = np.exp(-np.dot(d, d) / (2.0 * w.sigma ** 2))
            if proximity > threshold:
                delta_A = self.config.eta * proximity * dt
                new_A = min(w.amplitude + delta_A, self.config.amplitude_max)
                self._wells[i] = GaussianWell(center=w.center, amplitude=new_A, sigma=w.sigma)

    def _decay_all(self, dt: float) -> None:
        if self.config.decay_rate <= 0:
            return
        factor = np.exp(-self.config.decay_rate * dt)
        amp_floor = self.config.amplitude_min * 0.01
        for i, w in enumerate(self._wells):
            new_A = w.amplitude * factor
            self._wells[i] = GaussianWell(center=w.center, amplitude=max(new_A, amp_floor), sigma=w.sigma)
            self._ages[i] += dt

    def _prune(self) -> None:
        to_remove = [i for i, w in enumerate(self._wells) if w.amplitude < self.config.amplitude_min]
        for idx in reversed(to_remove):
            self._remove(idx)

    def _remove(self, idx: int) -> None:
        self.logger.info(f"Well #{idx} pruned: A={self._wells[idx].amplitude:.6f} < threshold {self.config.amplitude_min}")
        self._wells.pop(idx)
        self._visit_counts.pop(idx)
        self._ages.pop(idx)
        self._version += 1

    def _find_nearest(self, point: np.ndarray) -> Tuple[int, float]:
        if not self._wells:
            return -1, float("inf")
        dists = [np.linalg.norm(point - w.center) for w in self._wells]
        idx = int(np.argmin(dists))
        return idx, dists[idx]
