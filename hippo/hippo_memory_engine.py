"""HippoMemoryEngine — 기억의 생애주기 + 에너지 배분 (태양)

MemoryStore + EnergyBudgeter를 통합.
CookiieBrainEngine의 update() 루프 안에서 매 스텝 호출된다.

1. 현재 위치로 MemoryStore 갱신 (강화/감쇠)
2. EnergyBudgeter로 I(x,v,t) 계산
3. V(x,t) 변화 시 PFE에 새 potential 전달

극한 일관성:
  η=0, λ=0 → 정적 시스템 (하위 호환)
  λ>0, η=0 → 모든 우물 소멸 → 평탄 지형
  I=0       → Phase C 요동으로만 전이

Author: GNJz (Qquarts)
Version: 0.6.0
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import logging

from trunk.Phase_B.multi_well_potential import MultiWellPotential
from hippo.memory_store import MemoryStore
from hippo.energy_budgeter import EnergyBudgeter


@dataclass
class HippoConfig:
    """HippoMemoryEngine 설정

    솔라시스템 비유:
      η = 핵반응 강도 (기억 강화 속도)
      λ = 행성 소멸 속도 (기억 망각 속도)
      d_create = 새 행성 형성 최소 거리
      A_min = 행성 소멸 임계질량
    """
    # ── 기억 강화/망각 ──
    eta: float = 0.1
    decay_rate: float = 0.001
    amplitude_init: float = 1.0
    amplitude_min: float = 0.05
    amplitude_max: float = 10.0
    sigma_init: float = 1.0

    # ── 우물 생성/병합 ──
    creation_distance: float = 2.0
    merge_distance: float = 0.5
    max_wells: int = 20
    reinforce_proximity_threshold: float = 0.01

    # ── 에너지 주입 정책 ──
    explore_strength: float = 0.5
    exploit_strength: float = 0.05
    exploit_range: float = 3.0
    recall_strength: float = 2.0
    entropy_threshold_low: float = 0.01
    transition_rate_high: float = 0.5
    mode_switch_smoothing: float = 0.05


class HippoMemoryEngine:
    """기억의 태양: MemoryStore + EnergyBudgeter 통합"""

    def __init__(
        self,
        config: Optional[HippoConfig] = None,
        dim: int = 1,
        rng_seed: Optional[int] = None,
    ):
        self.config = config or HippoConfig()
        self.dim = dim
        self.store = MemoryStore(self.config, dim=dim)
        self.budgeter = EnergyBudgeter(self.config, rng_seed=rng_seed)
        self._prev_version: int = 0
        self.logger = logging.getLogger("HippoMemoryEngine")

    @property
    def potential_changed(self) -> bool:
        return self.store.version != self._prev_version

    def encode(self, pattern: np.ndarray, strength: float = 1.0) -> int:
        """외부 입력을 기억으로 인코딩"""
        return self.store.encode(pattern, strength)

    def recall(self, cue: np.ndarray) -> Optional[int]:
        """부분 단서로 기억 인출, 리콜 타깃 자동 설정"""
        idx = self.store.recall(cue)
        if idx is not None:
            self.budgeter.set_recall_target(self.store._wells[idx].center)
        return idx

    def clear_recall(self) -> None:
        self.budgeter.set_recall_target(None)

    def step(self, x: np.ndarray, v: np.ndarray, dt: float) -> Tuple[np.ndarray, bool]:
        """매 시뮬레이션 스텝에서 호출

        Returns: (injection, potential_changed)
        """
        self.store.step(x, dt)
        injection = self.budgeter.compute_injection(x, v, self.store)
        changed = self.potential_changed
        if changed:
            self._prev_version = self.store.version
        return injection, changed

    def update_policy(self, entropy_rate: float, transition_rate: float) -> None:
        self.budgeter.update_policy(entropy_rate, transition_rate)

    def export_potential(self) -> Optional[MultiWellPotential]:
        return self.store.export_potential()

    def info(self) -> Dict[str, Any]:
        return {
            "store": self.store.info(),
            "budgeter": self.budgeter.info(),
        }
