"""eden_os.intent_validator — Agent Intent 검증 레이어

OS 설계: Agent → Intent → Validator → Executor.
실행 전에 의도의 허용 여부·일관성을 검사한다.

역할
────
  - illegal intent 차단 (화이트리스트)
  - (선택) rate limiting
  - (선택) world consistency check
  규칙은 CONFIG 기반 (하드코딩 금지).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from .eden_world import EdenWorldEnv
from .adam import Intent

# ── 기본 허용 의도 코드 (CONFIG 로 override 가능) ─────────────────────────────
DEFAULT_ALLOWED_INTENTS: Set[str] = {
    "idle",
    "report_anomaly",
    "access_tree_of_life",
    "manage_rivers",
    "index_species",
    "access_knowledge_tree",  # 실행은 커널/가드가 차단 가능
    "trigger_succession",
    "enter_eden",
    "reenter_eden",
}


@dataclass(frozen=True)
class ValidationResult:
    """Intent 검증 결과."""
    allowed:    bool
    reason:     str
    risk_score: float = 0.0   # 0=안전, 1=위험

    def __str__(self) -> str:
        mark = "✅" if self.allowed else "❌"
        return f"ValidationResult({mark}  reason='{self.reason}'  risk={self.risk_score:.2f})"


class IntentValidator:
    """Agent 의도 검증기.

    CONFIG 기반: allowed_intents, min_eden_index_for_tree 등.
    """

    def __init__(
        self,
        allowed_intents: Optional[Set[str]] = None,
        min_eden_index_for_tree: float = 0.0,
        max_urgency: float = 1.0,
    ) -> None:
        self._allowed = allowed_intents or set(DEFAULT_ALLOWED_INTENTS)
        self._min_eden_for_tree = min_eden_index_for_tree
        self._max_urgency = max_urgency

    def validate(
        self,
        agent_id: str,
        intent: Intent,
        world: Optional[EdenWorldEnv] = None,
        **kwargs: Any,
    ) -> ValidationResult:
        """의도 허용 여부 및 일관성 검사.

        Parameters
        ----------
        agent_id : str
        intent   : Intent
        world    : EdenWorldEnv, optional — 일관성 검사용
        **kwargs : 추가 컨텍스트 (tick, guard_verdict 등)

        Returns
        -------
        ValidationResult
        """
        # 1. 화이트리스트
        if intent.code not in self._allowed:
            return ValidationResult(
                allowed=False,
                reason=f"intent '{intent.code}' not in allowed list",
                risk_score=0.9,
            )
        # 2. urgency 범위
        if intent.urgency < 0 or intent.urgency > self._max_urgency:
            return ValidationResult(
                allowed=False,
                reason=f"urgency {intent.urgency} out of range [0, {self._max_urgency}]",
                risk_score=0.3,
            )
        # 3. (선택) 생명나무 접근 시 에덴 지수 하한
        if world is not None and intent.code == "access_tree_of_life":
            if world.eden_index < self._min_eden_for_tree:
                return ValidationResult(
                    allowed=False,
                    reason=f"eden_index {world.eden_index:.3f} < {self._min_eden_for_tree}",
                    risk_score=0.5,
                )
        return ValidationResult(allowed=True, reason="ok", risk_score=0.0)


def make_intent_validator(
    allowed_intents: Optional[Set[str]] = None,
    min_eden_index_for_tree: float = 0.0,
    **kwargs: Any,
) -> IntentValidator:
    """IntentValidator 생성."""
    return IntentValidator(
        allowed_intents=allowed_intents,
        min_eden_index_for_tree=min_eden_index_for_tree,
        **kwargs,
    )


__all__ = [
    "ValidationResult",
    "IntentValidator",
    "make_intent_validator",
    "DEFAULT_ALLOWED_INTENTS",
]
