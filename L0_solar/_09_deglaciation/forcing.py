"""forcing.py — CO₂ 복사 강제 + 밀란코비치 궤도 강제

현재 지구(2024년)에서 작동 중인 두 가지 탈빙하기 드라이버:
  1. CO₂ 강제: 산업화 이후 인위적 온실가스 증가 → 복사 강제
  2. 밀란코비치: 지구 자전축·공전 궤도 변화 → 수만 년 주기 에너지 변조

Sources:
  IPCC AR6 WG1 (2021), Berger & Loutre (1991),
  Laskar et al. (2004)
"""
from __future__ import annotations
from math import log, pi, sin, exp
from dataclasses import dataclass


# ── 기준값 ─────────────────────────────────────────────────────────────
CO2_PREINDUSTRIAL  = 280.0    # ppm  (1750년 기준)
CO2_2024           = 422.0    # ppm  (2024년 관측값, NOAA)
CO2_FORCING_COEFF  = 5.35     # W/m²  (IPCC: ΔF = 5.35 × ln(C/C₀))
T_PREINDUSTRIAL    = 13.8     # °C   (산업화 이전 전지구 평균)
T_2024             = 15.0     # °C   (2024년 기준 전지구 평균 ≈ +1.1~1.2°C 이상)
T_ARCTIC_2024      = -14.5   # °C   (북극 연평균 기온 근사)
T_ANT_2024         = -28.0   # °C   (남극 연평균 기온 근사)

# ── 기후 민감도 ─────────────────────────────────────────────────────────
# ECS(Equilibrium Climate Sensitivity): CO₂ 2배 시 전지구 온도 변화
# IPCC AR6 최적 추정치: 3.0 K / doubling → 0.8 K/(W/m²)
CLIMATE_SENSITIVITY_K_per_Wm2 = 0.8   # K per W/m²

# 극 증폭(Polar Amplification)
ARCTIC_AMPLIFY   = 3.0   # 북극: 전지구 평균의 3배 온난화
ANTARCTIC_AMPLIFY = 1.5  # 남극: 1.5배 (바다-대륙 차이 때문에 상대적으로 느림)


# ── RCP 시나리오 CO₂ 궤적 ────────────────────────────────────────────────

def co2_trajectory_ppm(t_yr: float, scenario: str = "rcp85") -> float:
    """
    2024년 기준 t년 후 대기 CO₂ 농도 [ppm].

    Parameters
    ----------
    t_yr     : 2024년으로부터 경과 연수
    scenario : 'rcp26' | 'rcp45' | 'rcp60' | 'rcp85' | 'current'

    RCP 궤적 근사 (2024→2100 구간 기준):
      rcp26 : 2050년 ~490ppm 정점 후 감소, 2100년 ~430ppm
      rcp45 : 2070년 ~550ppm 정점 후 안정화
      rcp60 : 2080년 ~670ppm 정점
      rcp85 : 2100년 ~1050ppm (계속 증가)
      current: 2024년 실측 증가율 ~2.4ppm/yr 선형 연장 (단기 추정용)
    """
    C0 = CO2_2024
    if scenario == "rcp26":
        # 2050년 정점 490ppm, 이후 감소
        if t_yr <= 26:
            return C0 + (490 - C0) * (t_yr / 26)
        else:
            return 490 - (490 - 430) * min(1.0, (t_yr - 26) / 50)

    elif scenario == "rcp45":
        # 2070년 550ppm 정점, 이후 안정
        peak_yr = 46
        if t_yr <= peak_yr:
            return C0 + (550 - C0) * (t_yr / peak_yr)
        else:
            return 550.0

    elif scenario == "rcp60":
        peak_yr = 60
        if t_yr <= peak_yr:
            return C0 + (670 - C0) * (t_yr / peak_yr)
        else:
            return 670 - (670 - 620) * min(1.0, (t_yr - peak_yr) / 100)

    elif scenario == "rcp85":
        # 2100년까지 가파르게 증가 후 계속 상승
        if t_yr <= 76:
            return C0 + (1050 - C0) * (t_yr / 76) ** 1.2
        else:
            return 1050 + 5.0 * (t_yr - 76)

    elif scenario == "current":
        # 현재 추세: ~2.4 ppm/yr 선형 증가
        return C0 + 2.4 * t_yr

    else:
        raise ValueError(f"Unknown scenario: {scenario}")


def co2_radiative_forcing(co2_ppm: float) -> float:
    """
    현재 CO₂ 농도에 의한 복사 강제 [W/m²] (산업화 이전 대비).
    ΔF = 5.35 × ln(C / C₀)
    """
    return CO2_FORCING_COEFF * log(max(co2_ppm, 1.0) / CO2_PREINDUSTRIAL)


def milankovitch_forcing(t_yr: float) -> float:
    """
    현재 시점(2024) 기준 t년 후 밀란코비치 복사 강제 변화 [W/m²].

    주요 주기 (Berger & Loutre 1991):
      - 이심률(eccentricity):  ~100,000yr 주기
      - 자전축 경사(obliquity): ~41,000yr 주기
      - 세차운동(precession):   ~21,000yr 주기

    현재 지구는 홀로세 중반부터 극지방 여름 일사량이 서서히 감소 중.
    다음 빙기는 ~50,000년 후로 추정.
    현재 궤도 강제는 실질적으로 ~0 (빙하 증대 방향으로 약간 기울어짐).

    단순 근사: 세 주기 합산 (이심률 지배)
    """
    # 현재 위상 기준 — 지구는 현재 약한 냉각 궤도 위상
    ecc_forcing  = -0.3 * sin(2 * pi * t_yr / 100_000)   # 이심률
    obl_forcing  =  0.5 * sin(2 * pi * t_yr / 41_000)    # 경사각
    prec_forcing = -0.2 * sin(2 * pi * t_yr / 21_000)    # 세차
    return ecc_forcing + obl_forcing + prec_forcing


def total_forcing(t_yr: float, scenario: str = "rcp85") -> float:
    """
    총 복사 강제 [W/m²] = CO₂ 강제 + 밀란코비치 강제.
    t_yr: 2024년으로부터 경과 연수
    """
    co2  = co2_radiative_forcing(co2_trajectory_ppm(t_yr, scenario))
    mila = milankovitch_forcing(t_yr)
    return co2 + mila


def delta_T_global(forcing_W_m2: float) -> float:
    """복사 강제 → 전지구 온도 변화 [K]"""
    return CLIMATE_SENSITIVITY_K_per_Wm2 * forcing_W_m2


def delta_T_arctic(forcing_W_m2: float) -> float:
    """복사 강제 → 북극 온도 변화 [K]  (극 증폭 적용)"""
    return CLIMATE_SENSITIVITY_K_per_Wm2 * ARCTIC_AMPLIFY * forcing_W_m2


def delta_T_antarctic(forcing_W_m2: float) -> float:
    """복사 강제 → 남극 온도 변화 [K]"""
    return CLIMATE_SENSITIVITY_K_per_Wm2 * ANTARCTIC_AMPLIFY * forcing_W_m2
