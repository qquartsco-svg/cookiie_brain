"""underworld.rules — 거시 룰 정책 (데이터)"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

RULE_VIOLATION   = "RULE_VIOLATION"
ENTROPY_WARNING  = "ENTROPY_WARNING"
SYSTEM_PANIC     = "SYSTEM_PANIC"


@dataclass
class RuleSpec:
    """단일 거시 룰 명세."""
    check_key:           str
    violation_severity:   float
    signal_type:         str
    message:              str


def _ok_from_snapshot(snap: Any, key: str) -> bool:
    return getattr(snap, key, True)


def _sensitivity_factor(world_snapshot: Any) -> float:
    """지상 스냅샷에서 민감도 보정 계수. 덕 타이핑만 사용."""
    if world_snapshot is None:
        return 1.0
    idx = getattr(world_snapshot, "eden_index", None)
    if idx is None:
        return 1.0
    try:
        v = float(idx)
    except (TypeError, ValueError):
        return 1.0
    return 1.0 / max(0.01, min(1.0, v))


DEFAULT_RULES: List[RuleSpec] = [
    RuleSpec("magnetic_ok", 0.6, RULE_VIOLATION, "거시 룰: 자기장 이상 감지"),
    RuleSpec("thermal_ok",  0.5, ENTROPY_WARNING, "거시 룰: 열역학적 불안정"),
    RuleSpec("gravity_ok",  0.9, SYSTEM_PANIC, "거시 룰: 중력장 이상 — 시스템 패닉"),
]


def evaluate_rules(
    deep_snapshot: Any,
    rules: Optional[List[RuleSpec]] = None,
) -> tuple[float, str, str]:
    """위반 없으면 (0.0, QUIET용, ""). 위반 있으면 최고 severity와 해당 룰."""
    if rules is None:
        rules = DEFAULT_RULES
    severity, signal_type, message = 0.0, "QUIET", ""
    for r in rules:
        if not _ok_from_snapshot(deep_snapshot, r.check_key) and r.violation_severity > severity:
            severity, signal_type, message = r.violation_severity, r.signal_type, r.message
    return severity, signal_type, message


def evaluate_rules_all(
    deep_snapshot: Any,
    rules: Optional[List[RuleSpec]] = None,
    world_snapshot: Any = None,
) -> List[Tuple[float, str, str]]:
    """모든 위반 룰 반환. world_snapshot 있으면 severity 민감도 보정."""
    if rules is None:
        rules = DEFAULT_RULES
    sensitivity = _sensitivity_factor(world_snapshot)
    out: List[Tuple[float, str, str]] = []
    for r in rules:
        if not _ok_from_snapshot(deep_snapshot, r.check_key):
            adj = min(1.0, r.violation_severity * sensitivity)
            out.append((adj, r.signal_type, r.message))
    return out
