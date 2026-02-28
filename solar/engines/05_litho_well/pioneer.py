"""Pioneer biosphere — harsh-environment colonizers (lichen, moss, mycelium-like).

세차운동과 동일한 설계 철학:
  "물리 법칙/관측값을 수식으로 넣으면, 결과가 자연스럽게 나온다"

토양 형성 관측값 (근거):
  - 용암지대(하와이): pioneer 착생 후 ~300~500년 → 원시 토양
  - 빙하 후퇴지:     ~200~600년 → 이끼·이끼류 토양
  - 고위도 암반:     ~1,000~3,000년 → 얇은 토양층
  - 지구 전체 평균:  ~500~2,000년 추정
  목표: 지구 전체 0D 모델 → ~500~2,000년 내 임계 도달

핵심 물리:
  1. pioneer capacity: organic_layer가 쌓일수록 더 많은 pioneer를 부양 가능
     → K_carrying = K0 + K_soil * organic_layer  (양성 피드백)
     → d_pioneer/dt = r_pioneer * pioneer * (1 - pioneer/K) - m * pioneer
     (로지스틱 성장. 세차처럼 비선형 ODE)

  2. 풍화(weathering) 기여: pioneer가 암석을 물리·화학적으로 부수는 속도
     → d_mineral/dt = W_rate * pioneer  (pioneer 있을수록 빠름)
     → mineral_layer는 humus와 합쳐져 토양 용적을 형성

  3. organic 축적:
     → d_organic/dt = ETA * m * pioneer       (사체 → humus)
                    + W_mineral * mineral       (풍화 광물이 humus 안정화 기여)
                    - LAMBDA(T) * organic       (분해 — 온도 의존)
"""

import math
from ._constants import (
    T_MID_PIONEER,
    SIGMA_T_PIONEER,
    R_PIONEER,
    M_PIONEER,
    ETA_ORGANIC,
    LAMBDA_DECAY,
    K_SOIL_FEEDBACK,
    K0_CARRYING,
    W_WEATHERING,
    W_MINERAL_HUMUS,
    LAMBDA_T_SCALE,
    EPS,
)


def f_T_pioneer(T: float) -> float:
    """Broad temperature tolerance. Gaussian centered at T_MID_PIONEER."""
    return math.exp(-0.5 * ((T - T_MID_PIONEER) / max(SIGMA_T_PIONEER, EPS)) ** 2)


def f_W_pioneer(water_phase: str, H2O: float, organic_layer: float) -> float:
    """Moisture availability 0~1.
    liquid water → 1.0
    vapor + organic retention → 부분 점수 (organic이 수분 보유력 향상)
    """
    if water_phase == "liquid":
        return 1.0
    w_vap = min(1.0, H2O * 50.0)
    w_org = min(1.0, organic_layer * 2.0)
    return max(0.0, min(1.0, 0.3 * w_vap + 0.7 * w_org))


def lambda_decay(T: float) -> float:
    """온도 의존 분해 속도 [1/yr].
    Q10 = 2: 온도 10K 오를 때마다 분해속도 2배.
    기준 T_REF = 283 K (10°C).
    """
    T_REF = 283.0
    return LAMBDA_DECAY * (2.0 ** ((T - T_REF) / 10.0))


def carrying_capacity(organic_layer: float) -> float:
    """Pioneer 최대 부양 가능 생체량 [kg C/m²].
    돌땅: K0 (최소)
    토양 쌓일수록 수분·영양 보유력 증가 → K 증가 (양성 피드백)
    """
    return K0_CARRYING + K_SOIL_FEEDBACK * organic_layer


def npp_pioneer(T: float, water_phase: str, H2O: float, organic_layer: float,
                pioneer_biomass: float) -> float:
    """Pioneer 순생산량 [kg C/m²/yr]. 로지스틱 성장.
    r * P * (1 - P/K) * f_T * f_W
    """
    K = carrying_capacity(organic_layer)
    logistic = max(0.0, 1.0 - pioneer_biomass / max(K, EPS))
    return R_PIONEER * pioneer_biomass * logistic * f_T_pioneer(T) * f_W_pioneer(water_phase, H2O, organic_layer)


def d_pioneer_dt(
    pioneer_biomass: float,
    organic_layer: float,
    mineral_layer: float,
    T: float,
    water_phase: str,
    H2O: float,
) -> tuple:
    """세 상태변수의 시간 미분.

    Returns: (d_pioneer, d_organic, d_mineral)

    pioneer [kg C/m²]:
        d/dt = NPP_logistic - M * pioneer

    mineral [kg/m²]:  (풍화로 생성된 암석 입자 — 토양 골격)
        d/dt = W_WEATHERING * pioneer * f_T * f_W
              (pioneer가 물리·화학적으로 암석을 깎아냄)

    organic [kg C/m²]:  (humus — 토양 임계의 핵심)
        d/dt = ETA * M * pioneer          (사체 → humus)
             + W_MINERAL_HUMUS * mineral   (광물 입자가 유기물 안정화 기여)
             - lambda(T) * organic         (미생물 분해)
    """
    f_T = f_T_pioneer(T)
    f_W = f_W_pioneer(water_phase, H2O, organic_layer)

    npp = npp_pioneer(T, water_phase, H2O, organic_layer, pioneer_biomass)

    d_pioneer = npp - M_PIONEER * pioneer_biomass

    # 풍화: pioneer 활동 × 온도·수분 조건
    d_mineral = W_WEATHERING * pioneer_biomass * f_T * f_W

    # 유기층: 사체 humus화 + 광물 안정화 - 분해
    d_organic = (
        ETA_ORGANIC * M_PIONEER * pioneer_biomass
        + W_MINERAL_HUMUS * mineral_layer
        - lambda_decay(T) * organic_layer
    )

    return d_pioneer, d_organic, d_mineral
