"""eden_os.lifespan_budget — 에너지/비용 동역학으로 수명 산출 (하드코딩 없음)

궁창 전/후와 아담 계열·일반 인류의 수명이 C(t), S(t), L_env, 세대에 의해
동역학으로 결정되도록 한다.

목표 수치 (문서/계보 기준, 시뮬에서 재현할 타깃):
  - 궁창 전: 아담 계열 ~900년, 일반 인류 120년(상한)
  - 궁창 후: 일반 인류 평균 20~40년, 아담 계열 세대별 600→400→200→175년(아브라함)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# 그룹: 관리자 계열(아담→노아→셈→…→아브라함) vs 일반 인류
Group = Literal["admin_line", "general"]

# 수치 상수 (동역학 공식의 계수 — CONFIG로 빼도 됨)
_LIFESPAN_PRE_ADMIN_YR = 900.0
_LIFESPAN_PRE_GENERAL_YR = 120.0
_LIFESPAN_POST_GENERAL_LO = 20.0
_LIFESPAN_POST_GENERAL_HI = 40.0
_LIFESPAN_POST_GENERAL_MID = 30.0  # 평균 대표값
_LIFESPAN_POST_ADMIN_GEN0_YR = 600.0   # 노아 세대
_LIFESPAN_POST_ADMIN_ABRAHAM_YR = 175.0
_ABRAHAM_GENERATION = 10   # 노아=0 기준 대략 10세대 후 아브라함


@dataclass(frozen=True)
class LifespanBudgetResult:
    """한 시점의 수명 예산 결과."""
    expected_lifespan_yr: float
    shield_strength: float
    env_load: float
    group: str
    generation: int
    is_post_flood: bool


def expected_lifespan_yr(
    shield_strength: float,
    env_load: float,
    group: Group,
    generation: int = 0,
) -> float:
    """S(t), L_env, 그룹, 세대로 기대 수명(년) 계산. 하드코딩 없이 공식만 사용.

    Parameters
    ----------
    shield_strength : float [0, 1]
        궁창 보호막 강도. 1=궁창 완전(대홍수 전), 0=붕괴(대홍수 후).
    env_load : float >= 0
        환경 부하 L_env(t). S=0 일 때 크고, S=1 일 때 0에 가깝게 둠.
    group : "admin_line" | "general"
        아담 계열(관리자) vs 일반 인류.
    generation : int >= 0
        아담 계열 세대. 0=노아, 1=셈, … 10≈아브라함. general 이면 무시.

    Returns
    -------
    float
        기대 수명 [년]. 궁창 전/후·그룹·세대에 따라 동역학으로 결정됨.
    """
    if group not in ("admin_line", "general"):
        group = "general"
    S = max(0.0, min(1.0, shield_strength))

    # 궁창 전 (S≈1): 비용이 낮음 → 수명 길음
    if group == "admin_line":
        lifespan_pre = _LIFESPAN_PRE_ADMIN_YR
    else:
        lifespan_pre = _LIFESPAN_PRE_GENERAL_YR

    # 궁창 후 (S≈0): C_env·C_repair 폭증 → 수명 단축
    if group == "general":
        lifespan_post = _LIFESPAN_POST_GENERAL_MID
    else:
        # 아담 계열: 세대마다 E_cap/회복 감소 → 600 → … → 175
        # lifespan_post(gen) = 600 * (175/600)^(gen/10)
        g = max(0, generation)
        lifespan_post = _LIFESPAN_POST_ADMIN_GEN0_YR * (
            _LIFESPAN_POST_ADMIN_ABRAHAM_YR / _LIFESPAN_POST_ADMIN_GEN0_YR
        ) ** (g / max(1, _ABRAHAM_GENERATION))
        lifespan_post = max(_LIFESPAN_POST_ADMIN_ABRAHAM_YR, lifespan_post)

    # 전이 구간: S로 선형 보간 (S=1 → pre, S=0 → post)
    lifespan = S * lifespan_pre + (1.0 - S) * lifespan_post
    return max(1.0, lifespan)


def env_decay_per_tick(
    expected_lifespan_yr: float,
    ticks_per_year: float = 1.0,
    theta2: float = 0.40,
) -> float:
    """기대 수명을 integrity 감쇠율(틱당)로 변환.

    integrity가 theta2 이하로 N틱 유지되면 MORTAL 전이한다고 할 때,
    매 틱 (1 - theta2) / (T_yr * ticks_per_yr) 만큼 누적 스트레스가 올라가면
    대략 T_yr년 후에 해당 수준에 도달하도록 하는 계수.

    Parameters
    ----------
    expected_lifespan_yr : float
        기대 수명 [년].
    ticks_per_year : float
        1년당 틱 수. 1이면 1틱=1년.
    theta2 : float
        MORTAL 전이 임계 (integrity < theta2).

    Returns
    -------
    float
        틱당 누적할 env_stress 증분 (상한 1.0).
    """
    if expected_lifespan_yr <= 0:
        return 1.0
    total_ticks = expected_lifespan_yr * ticks_per_year
    if total_ticks < 1:
        return 1.0
    return min(1.0, (1.0 - theta2) / total_ticks)


def compute_lifespan_budget(
    shield_strength: float,
    env_load: float,
    group: Group,
    generation: int = 0,
) -> LifespanBudgetResult:
    """LifespanBudgetResult 한 번에 계산."""
    S = max(0.0, min(1.0, shield_strength))
    lifespan = expected_lifespan_yr(S, env_load, group, generation)
    return LifespanBudgetResult(
        expected_lifespan_yr=lifespan,
        shield_strength=S,
        env_load=env_load,
        group=group,
        generation=generation,
        is_post_flood=(S < 0.5),
    )
