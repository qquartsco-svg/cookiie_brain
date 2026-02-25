"""Magnetosphere — 자기권 (쌍극자 vs 태양풍 균형)
================================================

MagneticDipole의 B필드와 SolarWind의 동압이 만나
자기권(magnetosphere)의 경계와 내부 구조를 결정한다.

물리:
  마그네토포즈 (Chapman-Ferraro 근사):
    자기 압력 = 태양풍 동압
    B²/(2μ₀) = P_sw
    → r_mp = R_eq · (B₀²/(2μ₀ · P_sw))^(1/6)

    지구 실측: r_mp ≈ 10 R_E (하부태양점)

  보우 쇼크:
    r_bs ≈ 1.3 · r_mp (초음속 → 아음속 전이)

  자기꼬리:
    야간 측은 태양풍에 의해 뒤로 끌려
    길이 ~100-200 R_E까지 뻗어나감

  차폐 효과:
    자기권 내부는 태양풍 입자로부터 차폐됨
    극 쿠스프(cusp) 근처에서 부분적 침투 허용

  인지적 해석 (구조적 유비):
    자기권 = 내부 상태를 외부 교란으로부터 보호하는 경계층
    마그네토포즈 = 필터 반지름 (결합 강도 임계값)
    극 쿠스프 = 선택적 입력 채널

단위계:
  거리: AU (또는 R_eq 배수로 표시)
  압력: P₀ 단위 (1 AU 태양풍 동압 = 1.0)
  자기장: B₀ 단위 (표면 적도 자기장 = 1.0)

의존: numpy + solar.em.magnetic_dipole + solar.em.solar_wind
이 모듈은 core/를 직접 참조하지 않는다 — em/ 내부 결합만.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional

from ._constants import EPS_ZERO
from .magnetic_dipole import MagneticDipole
from .solar_wind import SolarWind


@dataclass
class MagnetosphereState:
    """자기권 상태 관측값."""
    body_name: str
    body_pos: np.ndarray            # 행성 위치 [AU]
    body_radius: float              # 행성 반지름 [AU]

    # 태양풍 입력
    sw_dynamic_pressure: float      # P_sw [P₀ 단위]
    sw_direction: np.ndarray        # 태양풍 방향 (단위 벡터)
    sw_imf: float                   # 행성간 자기장 [B_sw₀]

    # 자기장 입력
    surface_B0: float               # 표면 적도 자기장 [B₀]
    magnetic_axis: np.ndarray       # 자기축 단위 벡터

    # 자기권 출력
    magnetopause_r: float           # 마그네토포즈 반지름 [AU]
    magnetopause_R_eq: float        # 마그네토포즈 반지름 [R_eq 배수]
    bow_shock_r: float              # 보우 쇼크 반지름 [AU]
    bow_shock_R_eq: float           # 보우 쇼크 반지름 [R_eq 배수]
    tail_length_R_eq: float         # 자기꼬리 길이 추정 [R_eq]

    # 차폐 지표
    shielding_factor: float         # 0.0 (무방비) ~ 1.0 (완전 차폐)
    cusp_penetration: float         # 극 쿠스프 침투율 (0~1)
    energy_input_fraction: float    # 자기권으로 유입되는 에너지 비율


class Magnetosphere:
    """자기권 모델 — MagneticDipole과 SolarWind의 균형점.

    Parameters
    ----------
    dipole : MagneticDipole
        자기쌍극자 모델.
    wind : SolarWind
        태양풍 모델.
    bow_shock_ratio : float
        보우 쇼크 / 마그네토포즈 비율. 기본 1.3.
    tail_factor : float
        자기꼬리 길이 = tail_factor × r_mp. 기본 15.0.
    cusp_half_angle_deg : float
        극 쿠스프 반각 [°]. 기본 15°.
    reconnection_efficiency : float
        자기 재결합 효율 (IMF Bz 남향 시). 기본 0.1.
    """

    def __init__(
        self,
        dipole: MagneticDipole,
        wind: SolarWind,
        magnetic_pressure_ratio: float = 1.9e5,
        bow_shock_ratio: float = 1.3,
        tail_factor: float = 15.0,
        cusp_half_angle_deg: float = 15.0,
        reconnection_efficiency: float = 0.1,
    ):
        self.dipole = dipole
        self.wind = wind
        self.k_mp = magnetic_pressure_ratio
        self.bow_shock_ratio = bow_shock_ratio
        self.tail_factor = tail_factor
        self.cusp_half_angle = np.radians(cusp_half_angle_deg)
        self.reconnection_eff = reconnection_efficiency

    def magnetopause_distance(
        self,
        body_radius: float,
        B0: float,
        P_sw: float,
    ) -> float:
        """마그네토포즈 하부태양점 거리 (Chapman-Ferraro).

        r_mp = R_eq · (k · B₀² / P_sw)^(1/6)

        k = magnetic_pressure_ratio = B₀²_real / (2μ₀ · P_sw_real)
        지구: k ≈ 1.9×10⁵ → r_mp ≈ 7.6 R_E (실측 ~10 R_E)

        Parameters
        ----------
        body_radius : float
            행성 적도 반지름 [AU].
        B0 : float
            표면 적도 자기장 [B₀ 단위].
        P_sw : float
            태양풍 동압 [P₀ 단위].

        Returns
        -------
        float
            마그네토포즈 반지름 [AU].
        """
        if P_sw < EPS_ZERO:
            return float('inf')

        ratio = self.k_mp * B0 ** 2 / P_sw
        r_mp = body_radius * ratio ** (1.0 / 6.0)
        return r_mp

    def shielding(self, r_mp_Req: float) -> float:
        """차폐 지표 계산.

        r_mp/R_eq가 클수록 차폐가 강함.
        지구 기준: r_mp ≈ 10 R_eq → shielding ≈ 0.95

        sigmoid 모델: shield = 1 - exp(-r_mp_Req / 5)
        """
        if r_mp_Req < 0.01:
            return 0.0
        return 1.0 - np.exp(-r_mp_Req / 5.0)

    def cusp_penetration_fraction(
        self, magnetic_axis: np.ndarray, sw_direction: np.ndarray,
    ) -> float:
        """극 쿠스프 침투율.

        자기축과 태양풍 방향의 관계에 따라
        쿠스프 열림 정도가 변한다.

        Returns
        -------
        float
            0.0 (완전 차폐) ~ 1.0 (완전 침투)
        """
        cos_angle = abs(np.dot(magnetic_axis, sw_direction))
        cusp_opening = np.sin(self.cusp_half_angle) ** 2
        return float(cusp_opening * (1.0 - 0.5 * cos_angle))

    def energy_input(
        self,
        P_sw: float,
        r_mp: float,
        imf_magnitude: float,
    ) -> float:
        """자기권으로 유입되는 에너지 비율.

        E_in ∝ reconnection_eff × P_sw × π · r_mp²
        정규화하여 0~1 비율로 반환.
        """
        cross_section = np.pi * r_mp ** 2
        raw = self.reconnection_eff * P_sw * cross_section * imf_magnitude
        return float(min(1.0, raw / (raw + 1.0)))

    def evaluate(
        self,
        body_pos: np.ndarray,
        body_radius: float,
        spin_axis: np.ndarray,
        sun_pos: np.ndarray,
    ) -> MagnetosphereState:
        """자기권 전체 상태 평가.

        Parameters
        ----------
        body_pos : ndarray
            행성 위치 [AU].
        body_radius : float
            행성 적도 반지름 [AU].
        spin_axis : ndarray
            자전축 단위 벡터.
        sun_pos : ndarray
            태양 위치 [AU].

        Returns
        -------
        MagnetosphereState
        """
        sw_state = self.wind.state_at(body_pos, sun_pos)
        m_hat = self.dipole.magnetic_axis(spin_axis)
        B0 = self.dipole.magnetic_moment

        r_mp = self.magnetopause_distance(body_radius, B0, sw_state.dynamic_pressure)
        r_mp_Req = r_mp / body_radius if body_radius > EPS_ZERO else 0.0

        r_bs = r_mp * self.bow_shock_ratio
        r_bs_Req = r_bs / body_radius if body_radius > EPS_ZERO else 0.0

        tail_Req = r_mp_Req * self.tail_factor

        shield = self.shielding(r_mp_Req)
        cusp = self.cusp_penetration_fraction(m_hat, sw_state.direction)
        e_in = self.energy_input(
            sw_state.dynamic_pressure, r_mp, sw_state.imf_magnitude,
        )

        return MagnetosphereState(
            body_name=self.dipole.body_name,
            body_pos=body_pos.copy(),
            body_radius=body_radius,
            sw_dynamic_pressure=sw_state.dynamic_pressure,
            sw_direction=sw_state.direction.copy(),
            sw_imf=sw_state.imf_magnitude,
            surface_B0=B0,
            magnetic_axis=m_hat.copy(),
            magnetopause_r=r_mp,
            magnetopause_R_eq=r_mp_Req,
            bow_shock_r=r_bs,
            bow_shock_R_eq=r_bs_Req,
            tail_length_R_eq=tail_Req,
            shielding_factor=shield,
            cusp_penetration=cusp,
            energy_input_fraction=e_in,
        )
