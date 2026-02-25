"""Solar Luminosity — 태양 광도 (빛이 있으라)
=============================================

"그리고 빛이 있으라" — 중력장이 공간을 지배하고, 행성이 궤도를 돌고,
자기장이 방어막을 세운 그 위에, 마침내 빛이 켜진다.

빛이 켜지는 순간, 어둠 속의 질량들에 형태가 생기고,
그림자가 생기고, 낮과 밤이 나뉘고, 존재가 의미를 갖기 시작한다.

물리:
  질량-광도 관계 (주계열):
    L/L☉ = (M/M☉)^α
    α ≈ 4.0  (0.43 < M/M☉ < 2)
    α ≈ 3.5  (2 < M/M☉ < 55)

  복사 조도 (inverse-square law):
    F(r) = L / (4π r²)
    지구(1 AU): F = 1361 W/m²  (태양 상수, Solar Constant)

  복사압:
    P_rad = F / c
    1 AU: ≈ 4.54 μPa

  평형 온도 (이상 흑체):
    T_eq = [ F·(1-A) / (4σ) ]^(1/4)
    A: 본드 알베도 (지구 ≈ 0.306)
    σ: 슈테판-볼츠만 상수

  태양 참값:
    L☉ = 3.828 × 10²⁶ W
    T_eff = 5,778 K
    R☉ = 6.957 × 10⁸ m

단위계:
  광도: L☉ 단위 (태양 광도 = 1.0)
  거리: AU
  조도: F☉ 단위 (1 AU 태양 상수 = 1.0 = 1361 W/m²)
  온도: K (평형 온도 계산 시)

의존: numpy
이 모듈은 core/를 수정하지 않는다. 관측자 레이어.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Dict

from ._constants import EPS_ZERO


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  물리 상수 (SI → 정규화 변환용)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

L_SUN_SI = 3.828e26           # W
F_SUN_1AU_SI = 1361.0         # W/m² (Solar Constant)
STEFAN_BOLTZMANN = 5.6704e-8  # W/(m²·K⁴)
C_LIGHT_SI = 2.998e8          # m/s
AU_TO_M = 1.496e11            # m


@dataclass
class IrradianceState:
    """특정 위치에서의 복사 상태."""
    body_name: str
    distance_au: float
    luminosity: float             # [L☉]
    irradiance: float             # [F☉] (1 AU = 1.0 = 1361 W/m²)
    irradiance_si: float          # [W/m²]
    radiation_pressure: float     # [P₀ 단위] (solar_wind 연동용)
    radiation_pressure_si: float  # [Pa]
    equilibrium_temp_k: float     # [K] (알베도 0 기준)
    direction: np.ndarray         # 빛 방향 (태양 → 행성, 단위벡터)


class SolarLuminosity:
    """태양 광도 모델 — 빛이 있으라.

    질량에서 광도를 유도하고,
    임의 거리에서의 복사 조도·복사압·평형 온도를 계산한다.

    Parameters
    ----------
    star_name : str
        항성 이름.
    mass_solar : float
        항성 질량 [M☉]. 기본 1.0.
    luminosity_override : float or None
        광도 직접 지정 [L☉]. None이면 질량-광도 관계로 자동 계산.
    alpha : float
        질량-광도 관계 지수. 기본 4.0 (0.43~2 M☉ 범위).
    P0_sw : float
        태양풍 동압 기준값 [정규화]. solar_wind.py 연동용.
    """

    def __init__(
        self,
        star_name: str = "Sun",
        mass_solar: float = 1.0,
        luminosity_override: Optional[float] = None,
        alpha: float = 4.0,
        P0_sw: float = 1.0,
    ):
        self.star_name = star_name
        self.mass_solar = mass_solar
        self.alpha = alpha
        self.P0_sw = P0_sw

        if luminosity_override is not None:
            self.luminosity = luminosity_override
        else:
            self.luminosity = self._mass_luminosity(mass_solar)

        self._F0 = self.luminosity
        self._F0_si = self.luminosity * F_SUN_1AU_SI

    def _mass_luminosity(self, M: float) -> float:
        """질량-광도 관계: L/L☉ = (M/M☉)^α."""
        if M < EPS_ZERO:
            return 0.0
        return M ** self.alpha

    def irradiance(self, distance_au: float) -> float:
        """복사 조도 F(r) = L/(4πr²) [F☉ 단위].

        F☉ = 1.0 at 1 AU = 1361 W/m².
        """
        if distance_au < EPS_ZERO:
            return 0.0
        return self._F0 / (distance_au ** 2)

    def irradiance_si(self, distance_au: float) -> float:
        """복사 조도 [W/m²]."""
        if distance_au < EPS_ZERO:
            return 0.0
        return self._F0_si / (distance_au ** 2)

    def radiation_pressure_si(self, distance_au: float) -> float:
        """복사압 P_rad = F/c [Pa]."""
        return self.irradiance_si(distance_au) / C_LIGHT_SI

    def radiation_pressure_normalized(self, distance_au: float) -> float:
        """복사압 [P₀ 단위]. solar_wind.py 연동용.

        P₀ = 1 AU 태양풍 동압 = 1.0.
        P_rad(1 AU) ≈ 0.002 × P₀ (자연 비율 보존).
        """
        F_ratio = self.irradiance(distance_au)
        return self.P0_sw * 0.002 * F_ratio

    def equilibrium_temperature(
        self, distance_au: float, albedo: float = 0.0,
    ) -> float:
        """평형 온도 T_eq = [F·(1-A)/(4σ)]^(1/4) [K].

        Parameters
        ----------
        distance_au : float
            항성으로부터의 거리 [AU].
        albedo : float
            본드 알베도 (0~1). 기본 0 (이상 흑체).
        """
        F = self.irradiance_si(distance_au)
        if F < EPS_ZERO:
            return 0.0
        absorbed = F * (1.0 - albedo)
        return (absorbed / (4.0 * STEFAN_BOLTZMANN)) ** 0.25

    def state_at(
        self,
        position: np.ndarray,
        star_pos: np.ndarray,
        body_name: str = "",
        albedo: float = 0.0,
    ) -> IrradianceState:
        """임의 위치에서의 복사 전체 상태.

        Parameters
        ----------
        position : ndarray, shape (3,)
            관측 위치 [AU].
        star_pos : ndarray, shape (3,)
            항성 위치 [AU].
        body_name : str
            관측 천체 이름 (라벨용).
        albedo : float
            본드 알베도.
        """
        r_vec = position - star_pos
        r = np.linalg.norm(r_vec)
        direction = r_vec / r if r > EPS_ZERO else np.array([1.0, 0.0, 0.0])

        return IrradianceState(
            body_name=body_name,
            distance_au=r,
            luminosity=self.luminosity,
            irradiance=self.irradiance(r),
            irradiance_si=self.irradiance_si(r),
            radiation_pressure=self.radiation_pressure_normalized(r),
            radiation_pressure_si=self.radiation_pressure_si(r),
            equilibrium_temp_k=self.equilibrium_temperature(r, albedo),
            direction=direction,
        )

    def illuminate_system(
        self,
        planet_positions: Dict[str, np.ndarray],
        star_pos: np.ndarray,
        albedos: Optional[Dict[str, float]] = None,
    ) -> Dict[str, IrradianceState]:
        """전체 태양계를 한번에 조명.

        Parameters
        ----------
        planet_positions : dict
            {행성명: position_ndarray}
        star_pos : ndarray
            항성 위치.
        albedos : dict or None
            {행성명: 알베도}. None이면 전부 0 (이상 흑체).
        """
        if albedos is None:
            albedos = {}
        result = {}
        for name, pos in planet_positions.items():
            a = albedos.get(name, 0.0)
            result[name] = self.state_at(pos, star_pos, body_name=name, albedo=a)
        return result
