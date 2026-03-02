"""eden_os.evolution_config — 계승·진화 레이어 설정

mutation_rate(정책 변형률)는 Agent/Lineage 소유가 아니라
evolution(시나리오) 레이어에서 정의하고 주입한다.

역할
────
  - policy_mutation_rate: 계승 시 다음 세대 정책 변형 강도 [0~1]
  - make_eve() / make_eden_os_runner() 에서 이 값을 읽어 Eve 에 주입
"""

from __future__ import annotations

from typing import Dict, Any

# 계승 시 정책 변형 — evolution 레이어에서 정의
EVOLUTION_CONFIG: Dict[str, Any] = {
    "policy_mutation_rate": 0.05,  # 5% — 세대 간 정책 진화 강도
}

def get_policy_mutation_rate(override: float | None = None) -> float:
    """정책 변형률 반환. override 가 있으면 그대로, 없으면 EVOLUTION_CONFIG 사용."""
    if override is not None:
        return float(override)
    return float(EVOLUTION_CONFIG.get("policy_mutation_rate", 0.05))


__all__ = [
    "EVOLUTION_CONFIG",
    "get_policy_mutation_rate",
]
