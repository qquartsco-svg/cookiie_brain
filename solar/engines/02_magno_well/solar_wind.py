"""Solar Wind — 태양풍 (플라즈마: 동압 + 입자 플럭스 + IMF)
=========================================================

태양에서 방사되는 하전 입자(플라즈마) 흐름.
core/의 Body3D 위치를 읽어서 임의 지점에서의
태양풍 동압·플럭스·IMF를 계산한다.

중요: 복사압(P_rad = F/c)은 이 모듈의 범위가 아니다.
  복사(photons)와 플라즈마(solar wind)는 물리적으로 독립.
  복사압은 solar_luminosity.py에서 광도(L)로부터 유도한다.
  이 모듈은 플라즈마만 다룬다.

물리:
  태양풍 동압:
    P_sw(r) = P₀ · (r₀/r)²
    P₀ ≈ 2.0 nPa  (1 AU 기준)

  입자 플럭스 (양성자):
    Φ(r) = n(r) · v_sw
    n(r) = n₀ · (r₀/r)²
    n₀ ≈ 7 cm⁻³,  v_sw ≈ 400 km/s (1 AU 기준)

  행성간 자기장 (IMF):
    단순화: 파커 스파이럴의 방사 성분만 고려
    B_sw(r) ≈ B₀_sw · (r₀/r)²
    B₀_sw ≈ 5 nT (1 AU 기준)

단위계:
  거리: AU
  동압: P₀ 단위 (1 AU 태양풍 동압 = 1.0)
  플럭스: Φ₀ 단위 (1 AU 플럭스 = 1.0)
  IMF: B_sw₀ 단위 (1 AU IMF = 1.0)

의존: numpy + solar.core (Body3D.pos 읽기 전용)
이 모듈은 core/를 수정하지 않는다. 관측자 레이어.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional

from ._constants import EPS_ZERO


@dataclass
class SolarWindState:
    """특정 위치에서의 태양풍(플라즈마) 상태.

    복사압은 포함하지 않는다 — solar_luminosity.py 참조.
    """
    position: np.ndarray            # 관측 위치 [AU]
    distance_au: float              # 태양으로부터의 거리 [AU]
    direction: np.ndarray           # 태양풍 방향 (태양 → 관측점, 단위 벡터)
    dynamic_pressure: float         # 동압 [P₀ 단위]
    particle_flux: float            # 입자 플럭스 [Φ₀ 단위]
    imf_magnitude: float            # 행성간 자기장 세기 [B_sw₀ 단위]
    velocity: float                 # 태양풍 속도 [v₀ 단위, 1AU = 1.0]


class SolarWind:
    """태양풍(플라즈마) 모델.

    태양 위치에서 방사되는 하전 입자 흐름.
    모든 물리량은 1/r² 법칙을 따른다.

    복사압(photon momentum)은 이 클래스의 범위가 아니다.
    복사압은 SolarLuminosity에서 L → F → P_rad = F/c로 유도한다.

    Parameters
    ----------
    sun_name : str
        태양 천체 이름 (EvolutionEngine에서 find()).
    P0 : float
        1 AU에서의 동압 [정규화, 기본 1.0].
    Phi0 : float
        1 AU에서의 입자 플럭스 [정규화, 기본 1.0].
        P0과 별도로 관리하여 동압/플럭스 의미 혼합 방지.
    v_sw : float
        태양풍 속도 [정규화, 기본 1.0]. 실제 ≈ 400 km/s.
    imf_B0 : float
        1 AU에서의 행성간 자기장 세기 [정규화, 기본 1.0].
    r_ref : float
        기준 거리 [AU]. 기본 1.0 AU.
    """

    def __init__(
        self,
        sun_name: str = "Sun",
        P0: float = 1.0,
        Phi0: float = 1.0,
        v_sw: float = 1.0,
        imf_B0: float = 1.0,
        r_ref: float = 1.0,
    ):
        self.sun_name = sun_name
        self.P0 = P0
        self.Phi0 = Phi0
        self.v_sw = v_sw
        self.imf_B0 = imf_B0
        self.r_ref = r_ref

    def _r_factor(self, r: float) -> float:
        """1/r² 감쇠 인자."""
        if r < EPS_ZERO:
            return 0.0
        return (self.r_ref / r) ** 2

    def dynamic_pressure(self, distance_au: float) -> float:
        """동압 P_sw(r) = P₀ · (r₀/r)²."""
        return self.P0 * self._r_factor(distance_au)

    def particle_flux(self, distance_au: float) -> float:
        """입자 플럭스 Φ(r) = Φ₀ · (r₀/r)²."""
        return self.Phi0 * self._r_factor(distance_au)

    def imf_strength(self, distance_au: float) -> float:
        """행성간 자기장 세기 B_sw(r) ≈ B₀ · (r₀/r)²."""
        return self.imf_B0 * self._r_factor(distance_au)

    def wind_direction(
        self, position: np.ndarray, sun_pos: np.ndarray,
    ) -> np.ndarray:
        """태양풍 방향 (태양 → 관측점, 방사상)."""
        d = position - sun_pos
        norm = np.linalg.norm(d)
        if norm < EPS_ZERO:
            return np.array([1.0, 0.0, 0.0])
        return d / norm

    def state_at(
        self,
        position: np.ndarray,
        sun_pos: np.ndarray,
    ) -> SolarWindState:
        """임의 위치에서의 태양풍 전체 상태.

        Parameters
        ----------
        position : ndarray, shape (3,)
            관측 지점 [AU].
        sun_pos : ndarray, shape (3,)
            태양 중심 위치 [AU].

        Returns
        -------
        SolarWindState
        """
        r_vec = position - sun_pos
        r = np.linalg.norm(r_vec)
        direction = r_vec / r if r > EPS_ZERO else np.array([1.0, 0.0, 0.0])

        return SolarWindState(
            position=position.copy(),
            distance_au=r,
            direction=direction,
            dynamic_pressure=self.dynamic_pressure(r),
            particle_flux=self.particle_flux(r),
            imf_magnitude=self.imf_strength(r),
            velocity=self.v_sw,
        )

    def pressure_at_planets(
        self,
        planet_positions: dict,
        sun_pos: np.ndarray,
    ) -> dict:
        """다수 행성에서의 태양풍 동압 일괄 계산.

        Parameters
        ----------
        planet_positions : dict
            {name: position_ndarray}
        sun_pos : ndarray
            태양 위치.

        Returns
        -------
        dict
            {name: SolarWindState}
        """
        result = {}
        for name, pos in planet_positions.items():
            result[name] = self.state_at(pos, sun_pos)
        return result
