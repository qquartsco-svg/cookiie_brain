"""eden_os.scheduler — EdenOS 단계 스케줄러

OS 설계: sequential script 가 아닌 phase 기반 tick.
Runner.step() = tick 증가 + scheduler.tick(runner) 호출.

역할
────
  - 단계(phase) 순서를 한 곳에서 정의.
  - scheduler.tick(runner) → runner 가 한 틱 실행 후 TickLog 반환.
  - 향후 확장: phase 별로 runner._run_phase(phase) 분리 가능.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, List


class EdenPhase(Enum):
    """EdenOS 한 틱 내 실행 단계 순서."""
    ENV_UPDATE       = "env"       # Step 1 — 환경 상태 확인
    INFRA_UPDATE     = "infra"    # Step 2–3 — rivers, tree(kernel)
    SECURITY_CHECK   = "guard"    # Step 4 — 체루빔 틱
    AGENT_EXECUTION  = "agents"   # Step 5 — Adam/Eve observe→decide→act
    LINEAGE_UPDATE   = "lineage"  # Step 6 — 계승 검사·실행
    LOG_COMMIT       = "log"      # Step 7 — 틱 로그 저장


# Runner.step() 과 동일한 순서 (7단계를 6 phase 로 그룹)
DEFAULT_PHASES: List[EdenPhase] = [
    EdenPhase.ENV_UPDATE,
    EdenPhase.INFRA_UPDATE,
    EdenPhase.SECURITY_CHECK,
    EdenPhase.AGENT_EXECUTION,
    EdenPhase.LINEAGE_UPDATE,
    EdenPhase.LOG_COMMIT,
]


class EdenScheduler:
    """EdenOS 단계 스케줄러.

    Runner 가 한 틱 실행할 때 이 스케줄러를 통해 phase 순서로 실행한다.
    """

    def __init__(self, phases: List[EdenPhase] | None = None) -> None:
        self.phases = phases or list(DEFAULT_PHASES)

    def tick(self, runner: Any) -> Any:
        """한 틱 실행 — runner._execute_tick() 호출.

        Parameters
        ----------
        runner : EdenOSRunner
            실행할 러너. _execute_tick() 메서드를 제공해야 함.

        Returns
        -------
        TickLog (또는 runner._execute_tick() 반환값)
        """
        return runner._execute_tick()


def make_scheduler(phases: List[EdenPhase] | None = None) -> EdenScheduler:
    """EdenScheduler 생성."""
    return EdenScheduler(phases=phases)


__all__ = [
    "EdenPhase",
    "DEFAULT_PHASES",
    "EdenScheduler",
    "make_scheduler",
]
