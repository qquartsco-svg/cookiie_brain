"""underworld.rules — 거시 룰 정책 (데이터)

HadesObserver가 사용하는 룰 목록·스코어링·메시지.
hades.py는 이 모듈을 참조할 뿐, 룰 내용은 여기서만 수정하면 됨.

Layer: L0 (Foundation). Allowed deps: stdlib only. Forbidden: consciousness, deep_monitor, hades, propagation, wave_bus, siren, solar.eden.
See LAYERS.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

# SignalType 값 문자열 (consciousness.SignalType 과 맞춤)
RULE_VIOLATION   = "RULE_VIOLATION"
ENTROPY_WARNING  = "ENTROPY_WARNING"
SYSTEM_PANIC     = "SYSTEM_PANIC"


@dataclass
class RuleSpec:
    """단일 거시 룰 명세.

    check_key: DeepSnapshot 에서 읽을 필드명 (예: magnetic_ok).
    violation_severity: 위반 시 부여할 severity [0~1].
    signal_type: ConsciousnessSignal.signal_type 값.
    message: 고정 메시지 또는 template.
    """
    check_key:           str
    violation_severity:   float
    signal_type:         str
    message:              str


def _ok_from_snapshot(snap: Any, key: str) -> bool:
    """DeepSnapshot 또는 유사 객체에서 key에 해당하는 '정상 여부' 읽기.
    firmament_ok: shield_strength 가 없으면 True(미제공). 있으면 shield_strength >= 0.5 이면 True.
    """
    if key == "firmament_ok":
        s = getattr(snap, "shield_strength", None)
        return True if s is None else (s >= 0.5)
    return getattr(snap, key, True)


# 기본 룰셋: listen() 하드코딩을 여기로 이전.
# 우선순위 = 리스트 순서 (먼저 걸린 룰이 signal_type/message 결정, severity는 max 취합).
DEFAULT_RULES: List[RuleSpec] = [
    RuleSpec(
        check_key="firmament_ok",
        violation_severity=0.5,
        signal_type=ENTROPY_WARNING,
        message="거시 룰: 궁창/보호막 약화 (S 하락)",
    ),
    RuleSpec(
        check_key="magnetic_ok",
        violation_severity=0.6,
        signal_type=RULE_VIOLATION,
        message="거시 룰: 자기장 이상 감지",
    ),
    RuleSpec(
        check_key="thermal_ok",
        violation_severity=0.5,
        signal_type=ENTROPY_WARNING,
        message="거시 룰: 열역학적 불안정",
    ),
    RuleSpec(
        check_key="gravity_ok",
        violation_severity=0.9,
        signal_type=SYSTEM_PANIC,
        message="거시 룰: 중력장 이상 — 시스템 패닉",
    ),
]


def _sensitivity_factor(world_snapshot: Any) -> float:
    """지상 스냅샷에서 민감도 보정 계수. 덕 타이핑만 사용.

    eden_index 가 낮을수록(환경 악화) severity 를 더 크게 반영.
    기본 1.0 (world_snapshot 없거나 eden_index 없으면 보정 없음).
    """
    if world_snapshot is None:
        return 1.0
    idx = getattr(world_snapshot, "eden_index", None)
    if idx is None:
        return 1.0
    try:
        v = float(idx)
    except (TypeError, ValueError):
        return 1.0
    # v 가 낮을수록 계수 > 1 (severity 증폭). v=1 → 1.0, v=0.5 → 2.0, 하한 0.01
    return 1.0 / max(0.01, min(1.0, v))


def evaluate_rules(
    deep_snapshot: Any,
    rules: Optional[List[RuleSpec]] = None,
    world_snapshot: Any = None,
) -> tuple[float, str, str]:
    """DeepSnapshot에 대해 룰 평가.

    Parameters
    ----------
    world_snapshot : optional
        지상 스냅샷 (덕 타이핑). getattr(world_snapshot, "eden_index", 1.0) 으로 민감도 보정.

    Returns
    -------
    (severity, signal_type, message)
        위반 없으면 (0.0, QUIET용, ""). 위반 있으면 보정된 severity와 해당 룰의 signal_type/message.
    """
    if rules is None:
        rules = DEFAULT_RULES
    sensitivity = _sensitivity_factor(world_snapshot)
    severity = 0.0
    signal_type = "QUIET"
    message = ""
    for r in rules:
        ok = _ok_from_snapshot(deep_snapshot, r.check_key)
        if not ok:
            adj = min(1.0, r.violation_severity * sensitivity)
            if adj > severity:
                severity = adj
                signal_type = r.signal_type
                message = r.message
    return severity, signal_type, message


def evaluate_rules_all(
    deep_snapshot: Any,
    rules: Optional[List[RuleSpec]] = None,
    world_snapshot: Any = None,
) -> List[Tuple[float, str, str]]:
    """DeepSnapshot에 대해 모든 위반 룰을 반환.

    Parameters
    ----------
    world_snapshot : optional
        지상 스냅샷 (덕 타이핑). getattr(world_snapshot, "eden_index", 1.0) 으로 severity 민감도 보정.

    Returns
    -------
    List of (severity, signal_type, message)
        위반 없으면 []. 위반 있으면 각 위반당 한 항목 (severity 는 민감도 보정 적용).
    """
    if rules is None:
        rules = DEFAULT_RULES
    sensitivity = _sensitivity_factor(world_snapshot)
    out: List[Tuple[float, str, str]] = []
    for r in rules:
        ok = _ok_from_snapshot(deep_snapshot, r.check_key)
        if not ok:
            adj = min(1.0, r.violation_severity * sensitivity)
            out.append((adj, r.signal_type, r.message))
    return out
