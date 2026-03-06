"""_08_ice_age.feedback — 빙상-알베도 피드백 / 전지구 온도 결합

빙상 확장 → 행성 알베도 상승 → 전지구 냉각 → 빙상 추가 성장
이 양의 피드백 루프가 빙하시대의 핵심 동력이다.

물리 모델:
  행성 알베도:
    α_global = α_ice · f_ice + α_ref · (1 − f_ice)
    f_ice    = (1 − sin φ_ice)  [빙상이 덮는 반구 면적 비율]

  복사 강제력:
    ΔQ = −S₀/4 · (α_global − α₀)  [W/m²]
    (음수 = 냉각 강제)

  전지구 기온 응답:
    T_global = T_ref + S_clim · (ΔQ + Q_co2)  [K]
    S_clim   = 0.8 K/(W/m²)  [Equilibrium Climate Sensitivity ÷ S₀/4 비율 보정]

  극지 온도 (Polar Amplification):
    T_pole = T_pole_0 + PA · (T_global − T_global_0)
    PA     = 2.5  [극 증폭 계수, 관측 기반]

스노우볼 임계 (Budyko 1969):
  빙하선이 30°N 이하로 내려가면 알베도 런어웨이 → 전지구 결빙 가능성

참조:
  Budyko 1969, Tellus
  North 1981, J. Atmos. Sci.
  Pitman 2003 (polar amplification)
  IPCC AR6 (ECS ≈ 3K / 3.7 W/m²)
"""

from __future__ import annotations

from math import sin, pi


# ── 복사 상수 ──────────────────────────────────────────────────────────────────
S0              = 1361.0        # W/m²  태양 상수

# ── 기준 알베도 ────────────────────────────────────────────────────────────────
ALPHA_GLOBAL_0  = 0.30          # 충돌 전 전지구 알베도
ALPHA_ICE       = 0.65          # 대륙 빙상 알베도 (더 높음, 해빙보다)
ALPHA_NONICE    = ALPHA_GLOBAL_0 # 빙상 없는 영역 기준 알베도

# ── 기후 감도 ──────────────────────────────────────────────────────────────────
# ECS = 3 K/2xCO₂ ≈ 3K / (3.7 W/m²) → S_clim = 3/3.7 = 0.81 K/(W/m²)
LAMBDA_CLIMATE  = 0.8           # K/(W/m²)

# ── 기준 온도 ──────────────────────────────────────────────────────────────────
T_GLOBAL_0_K    = 288.0         # K  충돌 전 전지구 평균 기온
POLAR_AMPLIFY   = 2.5           # 극 증폭 계수

# ── 스노우볼 임계 ─────────────────────────────────────────────────────────────
PHI_SNOWBALL_DEG = 30.0         # °N  이 이하로 빙하선 → 런어웨이


def global_albedo(phi_ice_deg: float) -> float:
    """빙하선 위도 → 행성 알베도.

    Parameters
    ----------
    phi_ice_deg : 빙상 적도측 한계 위도 [°N]  (90=북극에만, 0=전지구 빙하)
    """
    # 빙상이 덮는 반구 면적 비율: f_ice = (1 − sin φ_ice)
    f_ice    = max(0.0, 1.0 - sin(phi_ice_deg * pi / 180.0))
    return ALPHA_ICE * f_ice + ALPHA_NONICE * (1.0 - f_ice)


def radiative_forcing(alpha: float, alpha_ref: float = ALPHA_GLOBAL_0) -> float:
    """알베도 변화 → 복사 강제력 ΔQ [W/m²].

    ΔQ = −S₀/4 · (α − α₀)
    양수 = 온난화, 음수 = 냉각.
    """
    return -(S0 / 4.0) * (alpha - alpha_ref)


def global_temperature(
    T_ref_K:       float,
    delta_Q:       float,
    q_co2_W_m2:    float = 0.0,
    sensitivity:   float = LAMBDA_CLIMATE,
) -> float:
    """복사 강제력 → 전지구 평균 기온 [K].

    T_global = T_ref + S_clim · (ΔQ_albedo + ΔQ_co2)
    """
    return T_ref_K + sensitivity * (delta_Q + q_co2_W_m2)


def polar_temperature(
    T_global_K:      float,
    T_global_init_K: float,
    T_pole_init_K:   float,
    amplify:         float = POLAR_AMPLIFY,
) -> float:
    """전지구 기온 변화 → 극지 기온 [K].

    T_pole = T_pole_0 + PA · (T_global − T_global_0)
    """
    return T_pole_init_K + amplify * (T_global_K - T_global_init_K)


def is_snowball(phi_ice_deg: float) -> bool:
    """알베도 런어웨이 임계 도달 여부 (Budyko criterion)."""
    return phi_ice_deg <= PHI_SNOWBALL_DEG


__all__ = [
    "global_albedo", "radiative_forcing",
    "global_temperature", "polar_temperature", "is_snowball",
    "S0", "ALPHA_GLOBAL_0", "ALPHA_ICE",
    "LAMBDA_CLIMATE", "T_GLOBAL_0_K", "POLAR_AMPLIFY",
    "PHI_SNOWBALL_DEG",
]
