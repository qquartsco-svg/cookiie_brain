"""eden_os.kernel.kernel_proxy — 커널 프록시  (Kernel / 1)

에이전트(adam.py, eve.py)가 커널에 접근하는 **유일한 인터페이스**.

보안 경계
─────────
  ┌──────────────────────┐
  │  Agent 공간           │
  │  adam.py  eve.py     │
  └──────────┬───────────┘
             │  KernelProxy 만 접근 가능
             ▼
  ┌──────────────────────┐
  │  KernelProxy          │
  │  (읽기 전용 인터페이스)│
  └──────────┬───────────┘
             │  내부 위임
             ▼
  ┌──────────────────────┐
  │  EdenKernel           │
  │  (커널 공간)          │
  │  TreeOfLife          │
  │  KnowledgeTree       │
  └──────────────────────┘

허용 연산
─────────
  proxy.request_tree_access(agent_id)  → AccessResult (읽기)
  proxy.release_tree(agent_id)
  proxy.is_tree_locked                 → bool (읽기)
  proxy.is_knowledge_consumed          → bool (읽기)

금지 연산 (프록시가 차단)
─────────
  proxy.kernel                         → AttributeError (커널 객체 직접 노출 금지)
  TreeOfLife.lock() 직접 호출          → 프록시 경유 시 차단
  KnowledgeTree.consume() 직접 호출    → 프록시 경유 시 차단

Kernel Trap 트리거 방식
─────────
  Agent 가 knowledge_consumed=True 를 보고하면,
  프록시가 kernel.trap_knowledge_consumed() 를 위임 호출.
  커널이 먼저 토큰 만료 → 프록시는 결과(KernelTrapResult)만 반환.
"""

from __future__ import annotations

from typing import Optional

from .life_kernel import EdenKernel, KernelToken, KernelTrapResult, make_eden_kernel
from ..eden_world import EdenWorldEnv
from ..tree_of_life import AccessResult, TreeState, KnowledgeState


class KernelProxy:
    """에이전트 ↔ 커널 사이의 읽기 전용 프록시.

    사용 방법 (Agent 코드)
    ──────────────────────
      # ✅ 허용
      proxy = KernelProxy(kernel)
      result = proxy.request_tree_access("adam")
      locked = proxy.is_tree_locked

      # ❌ 금지 — AttributeError
      proxy._kernel           # 커널 직접 접근 불가
      proxy.kernel            # 프로퍼티 없음

    Parameters
    ----------
    kernel : EdenKernel
        커널 인스턴스 (Runner 조립 시 주입).
    agent_id : str
        이 프록시를 소유하는 에이전트 ID.
    """

    __slots__ = ("_kernel", "_agent_id", "_token")

    def __init__(self, kernel: EdenKernel, agent_id: str) -> None:
        # 커널 참조는 name-mangled 슬롯에만 저장 — 외부 직접 접근 방지
        object.__setattr__(self, "_kernel",   kernel)
        object.__setattr__(self, "_agent_id", agent_id)
        object.__setattr__(self, "_token",    None)

    # ── 슬롯 외 속성 할당 차단 ───────────────────────────────────────────────

    def __setattr__(self, name: str, value) -> None:
        raise AttributeError(
            f"KernelProxy: 속성 설정 불가 ('{name}'). "
            "프록시는 불변입니다."
        )

    # ── 토큰 발행 (Runner 조립 시 1회 호출) ──────────────────────────────────

    def activate(self, is_admin: bool = True) -> KernelToken:
        """커널 토큰 발행 — Runner 조립 시 1회 호출.

        이 메서드는 Runner 가 호출. Agent 코드에서 직접 호출 금지.
        """
        kernel: EdenKernel = object.__getattribute__(self, "_kernel")
        agent_id: str       = object.__getattribute__(self, "_agent_id")
        token = kernel.issue_token(agent_id, is_admin=is_admin)
        object.__setattr__(self, "_token", token)
        return token

    # ── 읽기 전용 상태 조회 ───────────────────────────────────────────────────

    @property
    def is_tree_locked(self) -> bool:
        """생명나무 잠금 여부 (읽기 전용)."""
        kernel: EdenKernel = object.__getattribute__(self, "_kernel")
        return kernel.tree_state in (TreeState.LOCKED, TreeState.REMOVED)

    @property
    def is_knowledge_consumed(self) -> bool:
        """선악과 섭취 여부 (읽기 전용)."""
        kernel: EdenKernel = object.__getattribute__(self, "_kernel")
        return kernel.knowledge_state == KnowledgeState.CONSUMED

    @property
    def tree_state(self) -> TreeState:
        kernel: EdenKernel = object.__getattribute__(self, "_kernel")
        return kernel.tree_state

    @property
    def knowledge_state(self) -> KnowledgeState:
        kernel: EdenKernel = object.__getattribute__(self, "_kernel")
        return kernel.knowledge_state

    @property
    def token_valid(self) -> bool:
        """현재 토큰 유효 여부."""
        kernel: EdenKernel  = object.__getattribute__(self, "_kernel")
        agent_id: str        = object.__getattribute__(self, "_agent_id")
        return kernel.validate_token(agent_id)

    @property
    def agent_id(self) -> str:
        return object.__getattribute__(self, "_agent_id")

    # ── 허용된 연산 ───────────────────────────────────────────────────────────

    def request_tree_access(self) -> AccessResult:
        """생명나무 접근 요청.

        커널이 토큰 유효성 검사 후 허용/거부 결정.
        Agent 가 직접 TreeOfLife 를 건드리지 않음.
        """
        kernel: EdenKernel = object.__getattribute__(self, "_kernel")
        agent_id: str       = object.__getattribute__(self, "_agent_id")
        return kernel.request_tree_access(agent_id)

    def release_tree(self) -> None:
        """생명나무 접속 해제."""
        kernel: EdenKernel = object.__getattribute__(self, "_kernel")
        agent_id: str       = object.__getattribute__(self, "_agent_id")
        kernel.release_tree(agent_id)

    # ── Kernel Trap 트리거 ────────────────────────────────────────────────────

    def trigger_kernel_trap(self) -> KernelTrapResult:
        """선악과 섭취 감지 → Kernel Trap 발동.

        호출 즉시 커널이:
          1. 선악과 consume 처리
          2. 토큰 만료 (admin 권한 박탈)
          3. 생명나무 잠금
          4. 추방 준비 완료 신호 반환

        Agent 는 이 결과를 runner 에 보고만 하면 됨.
        권한 강등은 이미 커널이 처리함.
        """
        kernel: EdenKernel = object.__getattribute__(self, "_kernel")
        agent_id: str       = object.__getattribute__(self, "_agent_id")
        return kernel.trap_knowledge_consumed(agent_id)

    # ── 출력 ──────────────────────────────────────────────────────────────────

    def print_status(self) -> None:
        agent_id: str = object.__getattribute__(self, "_agent_id")
        print(f"\n  KernelProxy [{agent_id}]")
        print(f"    token_valid          : {self.token_valid}")
        print(f"    tree_state           : {self.tree_state.value}")
        print(f"    knowledge_state      : {self.knowledge_state.value}")
        print(f"    is_tree_locked       : {self.is_tree_locked}")
        print(f"    is_knowledge_consumed: {self.is_knowledge_consumed}")


# ═══════════════════════════════════════════════════════════════════════════════
#  공개 팩토리
# ═══════════════════════════════════════════════════════════════════════════════

def make_kernel_proxy(
    kernel:   Optional[EdenKernel] = None,
    agent_id: str = "adam",
    world:    Optional[EdenWorldEnv] = None,
) -> KernelProxy:
    """KernelProxy 생성.

    Parameters
    ----------
    kernel   : EdenKernel, optional — None 이면 새 커널 생성
    agent_id : str                  — 프록시 소유 에이전트 ID
    world    : EdenWorldEnv, optional

    Returns
    -------
    KernelProxy  (activate() 호출 전까지 토큰 없음)
    """
    if kernel is None:
        kernel = make_eden_kernel(world=world)
    return KernelProxy(kernel=kernel, agent_id=agent_id)
