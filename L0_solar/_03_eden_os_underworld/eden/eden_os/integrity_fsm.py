"""eden_os.integrity_fsm — N-tick 연속 조건 감시 → 자연 전이

IMMORTAL_ADMIN → (integrity < θ1 for N ticks) → DEGRADED_ADMIN
DEGRADED_ADMIN → (integrity < θ2 for N ticks) → MORTAL_NPC (비가역)

선악과 = 대량 stress_injection → integrity 즉시 θ2 이하 → N 대기 없이 MORTAL 전이.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class IntegrityState(str, Enum):
    """항상성 FSM 상태 (동역학 전이용)."""
    IMMORTAL_ADMIN = "immortal_admin"
    DEGRADED_ADMIN = "degraded_admin"
    MORTAL_NPC     = "mortal_npc"


@dataclass
class IntegrityFSM:
    """N tick 연속 조건으로 자연 전이하는 FSM.

    - integrity >= theta1: IMMORTAL_ADMIN 유지
    - integrity < theta1 연속 N tick: → DEGRADED_ADMIN
    - integrity < theta2 연속 N tick: → MORTAL_NPC (비가역)
    - 선악과(stress_injection 대량) 시 integrity 가 한 번에 θ2 이하로 꺾이면
      consecutive 카운트를 N 으로 채워 즉시 MORTAL_NPC 전이 가능.
    """

    def __init__(
        self,
        theta1: float = 0.75,
        theta2: float = 0.40,
        n_ticks: int = 3,
    ):
        self.theta1 = theta1
        self.theta2 = theta2
        self.n_ticks = n_ticks
        self._state = IntegrityState.IMMORTAL_ADMIN
        self._consecutive_low: int = 0
        self._consecutive_very_low: int = 0
        self._last_integrity: float = 1.0
        self._last_tick: int = 0

    @property
    def state(self) -> IntegrityState:
        return self._state

    @property
    def is_mortal(self) -> bool:
        return self._state == IntegrityState.MORTAL_NPC

    @property
    def is_degraded(self) -> bool:
        return self._state == IntegrityState.DEGRADED_ADMIN

    @property
    def is_immortal(self) -> bool:
        return self._state == IntegrityState.IMMORTAL_ADMIN

    def step(self, tick: int, integrity: float) -> IntegrityState:
        """한 틱 진행. integrity 갱신 후 전이 조건 검사.

        Parameters
        ----------
        tick : int
            현재 틱.
        integrity : float
            HomeostasisEngine 에서 받은 0~1 값.

        Returns
        -------
        IntegrityState
            전이 후 상태 (변경 없으면 동일).
        """
        self._last_tick = tick
        self._last_integrity = integrity

        if self._state == IntegrityState.MORTAL_NPC:
            return self._state  # 비가역

        if integrity < self.theta2:
            self._consecutive_very_low += 1
            self._consecutive_low += 1
            if self._consecutive_very_low >= self.n_ticks:
                self._state = IntegrityState.MORTAL_NPC
        elif integrity < self.theta1:
            self._consecutive_very_low = 0
            self._consecutive_low += 1
            if self._consecutive_low >= self.n_ticks and self._state == IntegrityState.IMMORTAL_ADMIN:
                self._state = IntegrityState.DEGRADED_ADMIN
        else:
            self._consecutive_low = 0
            self._consecutive_very_low = 0
            if self._state == IntegrityState.DEGRADED_ADMIN:
                self._state = IntegrityState.IMMORTAL_ADMIN  # 회복 가능

        return self._state

    def force_mortal(self) -> None:
        """즉시 MORTAL_NPC 로 전이 (선악과 등 외부 트리거 후 호출)."""
        self._state = IntegrityState.MORTAL_NPC
        self._consecutive_very_low = self.n_ticks
        self._consecutive_low = self.n_ticks


def make_integrity_fsm(
    theta1: float = 0.75,
    theta2: float = 0.40,
    n_ticks: int = 3,
) -> IntegrityFSM:
    """IntegrityFSM 생성."""
    return IntegrityFSM(theta1=theta1, theta2=theta2, n_ticks=n_ticks)
