"""
Grid Engine 호환 Ring Attractor — solar 경량 엔진 래핑

Grid 2D 엔진의 ring_adapter가 기대하는 API:
  RingAttractorEngine(size=15, config=..., seed=..., debug=...)
  inject(direction_idx=int, strength=float)
  run(duration_ms=float) -> RingState
  RingState.center (0 ~ size-1)

이 shim은 solar.cognitive.ring_attractor를 래핑해 위 API를 제공합니다.
00_BRAIN의 2.Ring_Attractor_Engine에 v4 의존성이 없을 때 이 경로가 우선 사용됩니다.
"""

from dataclasses import dataclass
from typing import Optional
import math

# solar 경량 Ring Attractor (의존성 없음)
from solar.cognitive.ring_attractor import RingAttractorEngine as _SolarEngine, RingState as _SolarState


@dataclass
class RingState:
    """Grid Engine 계약: center(0~size-1), width, active_count, stability, drift, sustained."""
    center: float
    width: float
    active_count: int
    stability: float
    drift: float
    sustained: bool
    orbit_stability: float = 1.0


class RingAttractorEngine:
    """Grid API: size, config, inject(direction_idx, strength), run(duration_ms) -> RingState."""

    def __init__(
        self,
        size: int = 15,
        config: str = "case2",
        seed: Optional[int] = None,
        debug: bool = False,
    ):
        if seed is not None:
            import numpy as np
            np.random.seed(seed)
        self.size = size
        self.config = config
        self.debug = debug
        # solar 엔진: n_neurons=size, 기본 tau/w_exc/w_inh/sigma
        self._engine = _SolarEngine(
            n_neurons=size,
            tau=1.0,
            w_exc=2.0,
            w_inh=0.8,
            sigma=2.0,
        )

    def inject(self, direction_idx: int, strength: float = 0.8) -> None:
        phase_rad = (direction_idx % self.size) / self.size * (2.0 * math.pi)
        self._engine.inject(phase=phase_rad, strength=strength)

    def release_input(self) -> None:
        pass  # solar 엔진은 입력 제거 별도 API 없음; run에서 자유 진화

    def run(self, duration_ms: Optional[float] = None) -> RingState:
        if duration_ms is None:
            duration_ms = 10.0
        duration_sec = duration_ms / 1000.0
        self._engine.run(duration=duration_sec, dt=0.01)
        s = self._engine.get_state()
        # phase [rad] -> center [0..size-1]
        center = (s.phase / (2.0 * math.pi)) * self.size
        center = center % self.size
        width = 1.0 if s.amplitude > 0 else 0.0
        active_count = self.size if s.sustained else 0
        return RingState(
            center=center,
            width=width,
            active_count=active_count,
            stability=s.stability,
            drift=s.drift,
            sustained=s.sustained,
            orbit_stability=min(1.0, s.stability + 0.5),
        )

    def get_state(self) -> RingState:
        s = self._engine.get_state()
        center = (s.phase / (2.0 * math.pi)) * self.size
        center = center % self.size
        return RingState(
            center=center,
            width=1.0 if s.amplitude > 0 else 0.0,
            active_count=self.size if s.sustained else 0,
            stability=s.stability,
            drift=s.drift,
            sustained=s.sustained,
            orbit_stability=min(1.0, s.stability + 0.5),
        )

    def reset(self) -> None:
        self._engine.reset()
