"""latitude_bands.py — 위도 밴드 생물권 모델 (Phase 7e)

설계 철학: 세차운동·토양·항상성과 동일
  입력: 자전축 기울기(ε), 위도별 조도·온도·수분 (물리 법칙)
  출력: 척박/비옥 공간 분포, viability field가 자연스럽게 창발

지구는 균일하지 않다:
  - 적도: F 높음, T 높음, 수분 충분 → 열대우림 (비옥)
  - 중위도: F 중간, T 중간 → 온대림 (중간)
  - 극지: F 낮음, T 낮음 → 툰드라/빙하 (척박)

구현:
  - 12개 위도 밴드 (각 15°: 극 → 적도 → 극)
  - 각 밴드 = 독립 BiosphereColumn (기어 분리)
  - F(φ,t) = F0 × max(0, cos(φ - δ(t))) [연속 삼각함수, no if-else]
  - T(φ) = T_eq(F(φ)) — 복사 균형 온도 (대기 온실 포함)
  - 밴드 면적 가중치: dA = cos(φ) dφ
  - 대기 CO₂·O₂: 전 지구 혼합 (단순 평균)

Edge AI 원칙:
  - 중앙 제어 없음
  - 각 밴드 로컬 관측값만 사용
  - 확산 결합 없음 (독립 기어)

단위: 밴드당 [kg C/m²], 플럭스 [kg C/m²/yr]
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .column import BiosphereColumn
from ._constants import O2_FIRE_TH, K_FIRE, EPS as _EPS


# ── 물리 상수 ─────────────────────────────────────────────────────────────────
OBLIQUITY    = 23.45 * math.pi / 180.0   # [rad] 자전축 기울기 ε
SOLAR_CONST  = 1361.0                     # [W/m²] 태양상수 (1 AU)
SIGMA        = 5.6704e-8                  # [W/m²/K⁴] Stefan-Boltzmann
ALBEDO_BASE  = 0.30                       # 육지 기본 알베도
GREENHOUSE_DT = 33.0                      # [K] 온실 효과 (현재 지구 평균)
EPS          = 1e-30


# ── 위도 밴드 정의 ────────────────────────────────────────────────────────────

BAND_COUNT  = 12
BAND_EDGES  = [i * (math.pi / BAND_COUNT) for i in range(BAND_COUNT + 1)]
# 남극(-90°) → 북극(+90°) 12개 밴드
# φ_center = [-82.5, -67.5, ..., +82.5] (도)
BAND_CENTERS_DEG = [
    -90.0 + (i + 0.5) * (180.0 / BAND_COUNT)
    for i in range(BAND_COUNT)
]
BAND_CENTERS_RAD = [d * math.pi / 180.0 for d in BAND_CENTERS_DEG]

# 밴드 면적 가중치 (cos(φ) 적분)
def _band_weight(phi_center_rad: float) -> float:
    """cos(φ) 비례 면적 가중치. 합이 1이 되도록 정규화."""
    return max(0.0, math.cos(phi_center_rad))

_raw_weights = [_band_weight(phi) for phi in BAND_CENTERS_RAD]
_total_weight = sum(_raw_weights) + EPS
BAND_WEIGHTS = [w / _total_weight for w in _raw_weights]


# ── 위도별 조도 계산 ──────────────────────────────────────────────────────────

def solar_flux(phi_rad: float, time_yr: float,
               obliquity_rad: float = OBLIQUITY,
               F0: float = SOLAR_CONST) -> float:
    """
    위도 φ, 시간 t에서의 연평균 복사 조도 [W/m²].

    F(φ) = F0/π × ∫ max(0, cos(zenith)) dh  (일평균)
    단순화: 연평균 = F0 × f(φ, ε)
    f(φ,ε) ≈ (1/π) × [cos(φ)cos(δ)sin(h0) + h0·sin(φ)sin(δ)]
    여기서 δ = ε·sin(2π·t) (계절 변화)

    연평균 근사 (계절 평균):
      F_ann(φ) ≈ F0/π × (cos(φ-ε) + cos(φ+ε))/2  (선형 근사)
    더 정확한 연평균:
      <F(φ)> = F0/π × sin(|φ|+ε) if |φ|+ε < π/2 else F0/π × ...
    여기서는 6단계 수치 적분 (계절 × 일변화)으로 처리.
    """
    # 계절 평균 (4계절 × 연속)
    total = 0.0
    n_season = 8
    for s in range(n_season):
        frac = (s + 0.5) / n_season
        delta = obliquity_rad * math.sin(2.0 * math.pi * frac)  # 태양 적위
        # 정오 zenith angle: cos(z) = sin(φ)sin(δ) + cos(φ)cos(δ)
        cos_z_noon = math.sin(phi_rad) * math.sin(delta) + math.cos(phi_rad) * math.cos(delta)
        # 일조 시간 적분 (연속): 해뜨기/지기 h0
        cos_h0 = -math.tan(phi_rad) * math.tan(delta)
        cos_h0 = max(-1.0, min(1.0, cos_h0))
        h0 = math.acos(cos_h0)
        # 일평균 조도
        f_daily = (F0 / math.pi) * (math.sin(phi_rad) * math.sin(delta) * h0
                                      + math.cos(phi_rad) * math.cos(delta) * math.sin(h0))
        total += max(0.0, f_daily)
    return total / n_season


def surface_temp(F: float, albedo: float = ALBEDO_BASE,
                 greenhouse_dT: float = GREENHOUSE_DT) -> float:
    """
    복사 균형 표면 온도 [K].
    T_eq = [F(1-A)/σ]^(1/4) + ΔT_greenhouse
    """
    T_eq = ((F * (1.0 - albedo)) / (SIGMA + EPS)) ** 0.25
    return T_eq + greenhouse_dT


def soil_moisture_proxy(phi_deg: float) -> float:
    """
    위도별 토양 수분 프록시 [0~1].
    관측 기반 단순화:
      적도: 0.9 (열대우림)
      중위도(30~60°): 0.6 (온대)
      극지(>70°): 0.2 (건조/동결)
    연속 함수로 구현.
    """
    abs_phi = abs(phi_deg)
    # 0°~30°: 0.9 → 0.7
    # 30°~60°: 0.7 → 0.4
    # 60°~90°: 0.4 → 0.1
    if abs_phi <= 30.0:
        return 0.9 - 0.2 * (abs_phi / 30.0)
    elif abs_phi <= 60.0:
        return 0.7 - 0.3 * ((abs_phi - 30.0) / 30.0)
    else:
        return 0.4 - 0.3 * ((abs_phi - 60.0) / 30.0)


# ── LatitudeBands 클래스 ──────────────────────────────────────────────────────

class LatitudeBands:
    """
    12개 위도 밴드 생물권 모델.

    각 밴드 = 독립 BiosphereColumn (기어 분리).
    전 지구 CO₂·O₂ = 면적 가중 평균 (간단한 혼합 가정).

    사용:
      lb = LatitudeBands(CO2_ppm=400, O2_frac=0.21)
      result = lb.step(dt_yr=1.0)
      lb.print_state()
    """

    def __init__(
        self,
        CO2_ppm: float = 400.0,
        O2_frac: float = 0.21,
        obliquity_deg: float = 23.45,
        F0: float = SOLAR_CONST,
        pioneer_init: float = 0.001,
        organic_init: float = 0.0,
        time_yr: float = 0.0,
    ):
        self.CO2_ppm = CO2_ppm
        self.O2_frac = O2_frac
        self.obliquity_rad = obliquity_deg * math.pi / 180.0
        self.F0 = F0
        self.time_yr = time_yr

        # 위도별 열 주 조건
        self.bands: List[BiosphereColumn] = []
        self.band_F:  List[float] = []
        self.band_T:  List[float] = []
        self.band_W:  List[float] = []

        # 대기 환산 상수
        self.LAND_AREA_M2   = 1.48e14
        self.KG_C_PER_PPM   = 2.13e12
        self.KG_O2_PER_FRAC = 1.2e18

        for i, (phi_r, phi_d) in enumerate(
                zip(BAND_CENTERS_RAD, BAND_CENTERS_DEG)):
            F   = solar_flux(phi_r, time_yr, self.obliquity_rad, F0)
            T   = surface_temp(F)
            W   = soil_moisture_proxy(phi_d)
            # 극지: organic 초기값 매우 낮음, 적도: 약간 높음
            org = max(0.0, organic_init + 0.01 * max(0.0, 1.0 - abs(phi_d)/60.0))
            col = BiosphereColumn(
                body_name=f"Band{i:02d}",
                land_fraction=0.29,
                pioneer_biomass_init=pioneer_init,
                organic_layer_init=org,
                mineral_layer_init=0.0,
                B_seed_init=0.0,
            )
            self.bands.append(col)
            self.band_F.append(F)
            self.band_T.append(T)
            self.band_W.append(W)

    def step(self, dt_yr: float = 1.0) -> Dict[str, Any]:
        """1스텝 전진. 전 지구 CO₂·O₂ 면적 가중 갱신."""
        band_results = []
        delta_CO2_global = 0.0  # [ppm] 전 지구 CO₂ 변화
        delta_O2_global  = 0.0  # [mol/mol] 전 지구 O₂ 변화

        for i, (col, phi_r, phi_d) in enumerate(
                zip(self.bands, BAND_CENTERS_RAD, BAND_CENTERS_DEG)):
            # 계절 변화 (현재 시간 기반)
            delta = self.obliquity_rad * math.sin(2.0 * math.pi * self.time_yr)
            F_inst = solar_flux(phi_r, self.time_yr, self.obliquity_rad, self.F0)
            T_inst = surface_temp(F_inst)
            W_inst = soil_moisture_proxy(phi_d)
            self.band_F[i] = F_inst
            self.band_T[i] = T_inst
            self.band_W[i] = W_inst

            env = {
                "F_solar_si":    max(1.0, F_inst),
                "T_surface":     T_inst,
                "P_surface":     101325.0,
                "CO2":           max(1e-6, self.CO2_ppm * 1e-6),
                "H2O":           0.01,
                "O2":            max(0.0, self.O2_frac),
                "water_phase":   "liquid" if T_inst > 273.0 else "solid",
                "soil_moisture": W_inst,
            }

            fb = col.step(env, dt_yr)
            s  = col.state()

            # 면적 가중 CO₂·O₂ 기여
            w = BAND_WEIGHTS[i]
            delta_CO2_global += (
                fb["delta_CO2"] * self.LAND_AREA_M2 / self.KG_C_PER_PPM * w
            )
            delta_O2_global  += (
                fb["delta_O2"] * self.LAND_AREA_M2 / self.KG_O2_PER_FRAC * w
            )

            band_results.append({
                "band": i,
                "phi_deg": phi_d,
                "F":       F_inst,
                "T":       T_inst,
                "W":       W_inst,
                "GPP":     fb["GPP"],
                "NPP":     fb["NPP"],
                "B_wood":  s.B_wood,
                "organic": s.organic_layer,
                "pioneer": s.pioneer_biomass,
                "viability": self._viability(T_inst, W_inst, s.organic_layer),
                "succession": s.succession_phase,
            })

        # ── 전 지구 CO₂·O₂ 갱신 ─────────────────────────────────────────────
        self.CO2_ppm = max(1e-6, self.CO2_ppm + delta_CO2_global * dt_yr)

        # [산불 피드백] O₂ 진짜 attractor — 하드 클램프(min 0.35) 제거
        # fire_sink [mol/mol/yr] = K_FIRE × max(0, O2 - O2_FIRE_TH)²
        # O₂가 25% 이상일 때 산불이 탄소·O₂를 소비 → O₂ 자연 안정화
        o2_excess   = max(0.0, self.O2_frac - O2_FIRE_TH)
        fire_sink   = K_FIRE * o2_excess ** 2      # [mol/mol/yr]
        self.O2_frac = max(0.0,
                          self.O2_frac
                          + delta_O2_global * dt_yr
                          - fire_sink        * dt_yr)
        # 산불로 소비된 O₂는 탄소 연소 = CO₂ 방출 (C + O₂ → CO₂)
        # 몰비 그대로: fire_sink [mol O₂/mol air / yr]
        # CO₂ 환산: 대기 O₂ 총량 × fire_sink → CO₂_ppm 증가
        # 단순화: fire_sink × (KG_O2_PER_FRAC / KG_C_PER_PPM) × (12/32)
        fire_co2_ppm = (fire_sink * dt_yr
                        * self.KG_O2_PER_FRAC / self.KG_C_PER_PPM
                        * (12.0 / 32.0))
        self.CO2_ppm = max(1e-6, self.CO2_ppm + fire_co2_ppm)

        self.time_yr += dt_yr

        return {
            "bands":        band_results,
            "CO2_ppm":      self.CO2_ppm,
            "O2_pct":       self.O2_frac * 100.0,
            "fire_sink_pct": fire_sink * 100.0,   # 산불 O₂ 소비율 [%/yr] 모니터링용
            "time_yr":      self.time_yr,
        }

    def _viability(self, T: float, W: float, organic: float) -> float:
        """
        발아 가능도(viability) ∈ [0,1].
        g_T × g_W × g_soil — 연속 게이트, no if-else.
        """
        # g_T: 온도 삼각형 (Tmin=275K, Topt=295K, Tmax=318K)
        Tmin, Topt, Tmax = 275.0, 295.0, 318.0
        if T < Tmin or T > Tmax:
            g_T = 0.0
        elif T <= Topt:
            g_T = (T - Tmin) / (Topt - Tmin + EPS)
        else:
            g_T = (Tmax - T) / (Tmax - Topt + EPS)
        g_T = max(0.0, g_T)
        # g_W: 수분
        g_W = max(0.0, min(1.0, W))
        # g_soil: 토양 준비도
        g_soil = organic / (organic + 0.4 + EPS)
        return g_T * g_W * g_soil

    def global_gpp(self) -> float:
        """전 지구 면적 가중 GPP [kg C/m²/yr]."""
        total = 0.0
        for i, col in enumerate(self.bands):
            F = self.band_F[i]
            T = self.band_T[i]
            W = self.band_W[i]
            env = {
                "F_solar_si": max(1.0, F), "T_surface": T, "P_surface": 101325.0,
                "CO2": max(1e-6, self.CO2_ppm * 1e-6), "H2O": 0.01,
                "O2": max(0.0, self.O2_frac),
                "water_phase": "liquid" if T > 273.0 else "solid",
                "soil_moisture": W,
            }
            from .photo import gpp
            total += gpp(F, self.CO2_ppm * 1e-6, T, W) * BAND_WEIGHTS[i]
        return total
