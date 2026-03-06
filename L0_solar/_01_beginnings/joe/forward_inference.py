"""JOE Forward / Inference 모드 — 역추적 계약.

역추적 = "역적분"이 아니라 "추정/동화(assimilation)".
- Forward: 초기 거시 상태 x0 → 시간에 따른 macro snapshot 시퀀스.
- Inference: 관측(현재 지구 스냅샷) → 초기 후보 집합 + MAP 추정치.

이 모듈은 **인터페이스(함수 시그니처·계약)**만 정의한다.
구체적 동역학(정방향 ODE/이산 모델) 및 동화 알고리즘(스윕/베이지안/필터)은
별도 구현으로 채운다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple

# Snapshot = 조 표준 스냅샷 (dict). JOE_SNAPSHOT_SCHEMA_V02 참고.
Snapshot = Dict[str, Any]


@dataclass
class ForwardResult:
    """정방향 동역학 결과: 시점별 거시 스냅샷."""
    t_span: List[float]       # 시간 격자 (예: [0, 1e9, 4.5e9] yr)
    snapshots: List[Snapshot]  # 각 시점의 macro snapshot
    state_trajectory: Optional[List[Dict[str, Any]]] = None  # 원시 상태벡터 시퀀스 (선택)


@dataclass
class InferenceResult:
    """역추적(Inference) 결과: 초기 후보 + MAP."""
    x0_hat: Snapshot          # MAP 추정 초기 스냅샷
    candidates: List[Snapshot] = field(default_factory=list)  # 초기 후보 집합
    confidence: Optional[float] = None   # 0~1 또는 유사도
    range_bounds: Optional[Dict[str, Tuple[float, float]]] = None  # 키별 [min, max]
    config_used: Dict[str, Any] = field(default_factory=dict)


class ForwardDynamicsProtocol(Protocol):
    """정방향 거시 동역학 프로토콜. 구현체는 초기 상태 → 시계열 스냅샷."""

    def __call__(
        self,
        x0: Snapshot,
        t_span: List[float],
        *,
        config: Optional[Dict[str, Any]] = None,
    ) -> ForwardResult:
        """초기 거시 상태 x0와 시간 격자 t_span → 시점별 스냅샷."""
        ...


def forward_dynamics(
    x0: Snapshot,
    t_span: List[float],
    *,
    config: Optional[Dict[str, Any]] = None,
) -> ForwardResult:
    """정방향 동역학: x0 → snap(t).

    계약: x0는 조 표준 스냅샷 또는 상태벡터(dict).
    반환: t_span 각 시점에 대응하는 macro snapshot 리스트.

    현재: 스텁. 실제 동역학(조석 마찰, 궤도 진화, 맨틀 냉각 등)은
    별도 모듈에서 구현 후 여기서 호출하거나, 외부에서 이 시그니처를 만족하는
    함수를 주입한다.
    """
    if not t_span:
        return ForwardResult(t_span=[], snapshots=[])
    n = len(t_span)
    snapshots = [dict(x0) for _ in range(n)]
    return ForwardResult(t_span=t_span, snapshots=snapshots)


def infer_initial_candidates(
    y_now: Snapshot,
    *,
    constraints: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
    max_candidates: int = 10,
) -> InferenceResult:
    """역추적: 관측(현재 지구 스냅샷) → 초기 후보 집합 + MAP.

    계약:
    - y_now: 현재 시점의 macro snapshot (관측).
    - constraints: 키별 범위 등 제약 (선택).
    - 반환: x0_hat(MAP 추정), candidates(후보 리스트), confidence/range_bounds.

    현재: 스텁. 실제 구현은 파라미터 스윕, 베이지안 최적화, EKF/UKF/Particle Filter 등
    동화(assimilation)로 채운다.
    """
    x0_hat = dict(y_now)
    candidates = [x0_hat]
    return InferenceResult(
        x0_hat=x0_hat,
        candidates=candidates,
        confidence=0.0,
        config_used=config or {},
    )


__all__ = [
    "Snapshot",
    "ForwardResult",
    "InferenceResult",
    "ForwardDynamicsProtocol",
    "forward_dynamics",
    "infer_initial_candidates",
]
