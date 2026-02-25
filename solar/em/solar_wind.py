"""Solar Wind — 태양풍 (입자 플럭스 + 복사압)
=============================================

태양에서 방사되는 하전 입자 흐름과 전자기 복사압.
core/의 Body3D 위치를 읽어서 임의 지점에서의
태양풍 동압·플럭스·복사압을 계산한다.

물리:
  태양풍 동압:
    P_sw(r) = P₀ · (r₀/r)²
    P₀ ≈ 2.0 nPa  (1 AU 기준)

  입자 플럭스 (양성자):
    Φ(r) = n(r) · v_sw
    n(r) = n₀ · (r₀/r)²
    n₀ ≈ 7 cm⁻³,  v_sw ≈ 400 km/s (1 AU 기준)

  복사압:
    P_rad(r) = L_sun / (4π r² c)
    1 AU에서 ≈ 4.56 μPa (태양풍 동압의 ~1/500)

  행성간 자기장 (IMF):
    단순화: 파커 스파이럴의 방사 성분만 고려
    B_sw(r) ≈ B₀_sw · (r₀/r)²
    B₀_sw ≈ 5 nT (1 AU 기준)

단위계:
  거리: AU
  동압: P₀ 단위 (1 AU 태양풍 동압 = 1.0)
  플럭스: Φ₀ 단위 (1 AU 플럭스 = 1.0)
  복사압: P₀ 단위로 정규화 (P_rad/P_sw 비율 보존)

의존: numpy + solar.core (Body3D.pos 읽기 전용)
이 모듈은 core/를 수정하지 않는다. 관측자 레이어.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class SolarWindState:
    """특정 위치에서의 태양풍 상태."""
    position: np.ndarray            # 관측 위치 [AU]
    distance_au: float              # 태양으로부터의 거리 [AU]
    direction: np.ndarray           # 태양풍 방향 (태양 → 관측점, 단위 벡터)
    dynamic_pressure: float         # 동압 [P₀ 단위]
    particle_flux: float            # 입자 플럭스 [Φ₀ 단위]
    radiation_pressure: float       # 복사압 [P₀ 단위]
    imf_magnitude: float            # 행성간 자기장 세기 [B_sw₀ 단위]
    velocity: float                 # 태양풍 속도 [v₀ 단위, 1AU = 1.0]


class SolarWind:
    """태양풍 모델.

    태양 위치에서 방사되는 입자 흐름과 복사압.
    모든 물리량은 1/r² 법칙을 따른다.

    Parameters
    ----------
    sun_name : str
        태양 천체 이름 (EvolutionEngine에서 find()).
    P0 : float
        1 AU에서의 동압 [정규화, 기본 1.0].
    v_sw : float
        태양풍 속도 [정규화, 기본 1.0]. 실제 ≈ 400 km/s.
    radiation_ratio : float
        복사압 / 동압 비율. 실제 ≈ 0.002 (1 AU 기준).
    imf_B0 : float
        1 AU에서의 행성간 자기장 세기 [정규화, 기본 1.0].
    r_ref : float
        기준 거리 [AU]. 기본 1.0 AU.
    """

    def __init__(
        self,
        sun_name: str = "Sun",
        P0: float = 1.0,
        v_sw: float = 1.0,
        radiation_ratio: float = 0.002,
        imf_B0: float = 1.0,
        r_ref: float = 1.0,
    ):
        self.sun_name = sun_name
        self.P0 = P0
        self.v_sw = v_sw
        self.radiation_ratio = radiation_ratio
        self.imf_B0 = imf_B0
        self.r_ref = r_ref

    def _r_factor(self, r: float) -> float:
        """1/r² 감쇠 인자."""
        if r < 1e-30:
            return 0.0
        return (self.r_ref / r) ** 2

    def dynamic_pressure(self, distance_au: float) -> float:
        """동압 P_sw(r) = P₀ · (r₀/r)²."""
        return self.P0 * self._r_factor(distance_au)

    def particle_flux(self, distance_au: float) -> float:
        """입자 플럭스 Φ(r) = Φ₀ · (r₀/r)²."""
        return self.P0 * self._r_factor(distance_au)

    def radiation_pressure(self, distance_au: float) -> float:
        """복사압 P_rad(r) = P₀ · ratio · (r₀/r)²."""
        return self.P0 * self.radiation_ratio * self._r_factor(distance_au)

    def imf_strength(self, distance_au: float) -> float:
        """행성간 자기장 세기 B_sw(r) ≈ B₀ · (r₀/r)²."""
        return self.imf_B0 * self._r_factor(distance_au)

    def wind_direction(
        self, position: np.ndarray, sun_pos: np.ndarray,
    ) -> np.ndarray:
        """태양풍 방향 (태양 → 관측점, 방사상)."""
        d = position - sun_pos
        norm = np.linalg.norm(d)
        if norm < 1e-30:
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
        direction = r_vec / r if r > 1e-30 else np.array([1.0, 0.0, 0.0])

        return SolarWindState(
            position=position.copy(),
            distance_au=r,
            direction=direction,
            dynamic_pressure=self.dynamic_pressure(r),
            particle_flux=self.particle_flux(r),
            radiation_pressure=self.radiation_pressure(r),
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
