"""underworld.rules — 거시 룰 정책 (데이터)

HadesObserver가 사용하는 룰 목록·스코어링·메시지.
hades.py는 이 모듈을 참조할 뿐, 룰 내용은 여기서만 수정하면 됨.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

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
    """DeepSnapshot 또는 유사 객체에서 key에 해당하는 '정상 여부' 읽기."""
    return getattr(snap, key, True)


# 기본 룰셋: listen() 하드코딩을 여기로 이전.
# 우선순위 = 리스트 순서 (먼저 걸린 룰이 signal_type/message 결정, severity는 max 취합).
DEFAULT_RULES: List[RuleSpec] = [
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


def evaluate_rules(
    deep_snapshot: Any,
    rules: Optional[List[RuleSpec]] = None,
) -> tuple[float, str, str]:
    """DeepSnapshot에 대해 룰 평가.

    Returns
    -------
    (severity, signal_type, message)
        위반 없으면 (0.0, QUIET용, ""). 위반 있으면 가장 높은 severity와 해당 룰의 signal_type/message.
    """
    if rules is None:
        rules = DEFAULT_RULES
    severity = 0.0
    signal_type = "QUIET"
    message = ""
    for r in rules:
        ok = _ok_from_snapshot(deep_snapshot, r.check_key)
        if not ok:
            if r.violation_severity > severity:
                severity = r.violation_severity
                signal_type = r.signal_type
                message = r.message
    return severity, signal_type, message
