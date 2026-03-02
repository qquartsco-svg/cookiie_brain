"""eden_os.kernel.life_kernel — 에덴 커널 레이어  (Kernel / 0)

KERNEL LAYER — 피조물 에이전트가 직접 접근 불가.
KernelProxy 를 통해서만 읽기 전용 접근 허용.

역할
────
  TreeOfLife 와 KnowledgeTree 를 커널 공간으로 격리.

  보안 원칙:
    - Agent(adam.py, eve.py)는 이 파일을 직접 import 금지
    - 모든 접근은 kernel_proxy.KernelProxy 를 경유
    - Kernel 이 Agent 의 요청을 평가해 허용/거부를 결정
    - "선악과 섭취" = Kernel Trap → 커널이 먼저 토큰 만료 후 추방

권한 강등 순서 (Kernel Trap)
──────────────────────────────────────────────
  1. agent.knowledge_consumed = True  (트리거)
  2. Kernel 이 즉시 감지 → admin 토큰 만료
  3. Agent 권한 IMMORTAL_ADMIN → MORTAL_NPC 강제 강등
  4. CherubimGuard 에게 "추방 집행" 위임
  → 이 순서가 보장되어야 privilege escalation 불가

레이어 분리
──────────────────────────────────────────────
  PHYSICAL_FACT : 접근 효과 수치 (Config 주입)
  SCENARIO      : 상태 전이 규칙
  LORE          : 생명나무 · 선악과 의미
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Tuple

from ..eden_world import EdenWorldEnv
from ..tree_of_life import (
    TreeOfLife,
    KnowledgeTree,
    TreeState,
    KnowledgeState,
    AccessResult,
    KnowledgeAccessResult,
    make_trees,
    DEFAULT_TREE_EFFECT,
    KNOWLEDGE_PENALTY,
)

# ── 레이어 상수 ──────────────────────────────────────────────────────────────
PHYSICAL = "PHYSICAL_FACT"
SCENARIO  = "SCENARIO"
LORE      = "LORE"


# ═══════════════════════════════════════════════════════════════════════════════
#  KernelToken — 커널이 발행하는 세션 토큰
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class KernelToken:
    """커널이 Agent 에게 발행하는 세션 토큰.

    frozen=True : 발행 후 수정 불가 (불변 레코드)
    """
    agent_id:   str
    is_admin:   bool
    issued_at:  int          # tick 번호
    token_hash: str          # 발행 시 해시 (위변조 감지)
    expired:    bool = False  # 커널이 만료 처리

    @classmethod
    def issue(cls, agent_id: str, is_admin: bool, tick: int) -> "KernelToken":
        """토큰 발행 (커널 내부 전용)."""
        raw = f"{agent_id}:{is_admin}:{tick}:{time.monotonic_ns()}"
        token_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return cls(
            agent_id   = agent_id,
            is_admin   = is_admin,
            issued_at  = tick,
            token_hash = token_hash,
        )

    @property
    def valid(self) -> bool:
        return not self.expired

    def expire(self) -> "KernelToken":
        """토큰 만료 — 새 frozen 객체 반환 (원본 불변 유지)."""
        return KernelToken(
            agent_id   = self.agent_id,
            is_admin   = False,          # ← 관리자 권한 박탈
            issued_at  = self.issued_at,
            token_hash = self.token_hash,
            expired    = True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  KernelTrapResult — 선악과 섭취 감지 → 강제 권한 강등 결과
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class KernelTrapResult:
    """선악과 Kernel Trap 실행 결과.

    이 객체가 생성된 순간 권한 강등은 이미 완료됨.
    CherubimGuard 는 이 결과를 받아 추방을 집행한다.
    """
    agent_id:          str
    token_expired:     bool    # 토큰 만료 여부
    admin_revoked:     bool    # 관리자 권한 박탈 여부
    entropy_injected:  float   # 주입된 엔트로피
    expulsion_ready:   bool    # 체루빔 추방 집행 준비 완료
    tick:              int
    log_entry:         str

    @property
    def ok(self) -> bool:
        return self.token_expired and self.admin_revoked and self.expulsion_ready


# ═══════════════════════════════════════════════════════════════════════════════
#  EdenKernel — 에덴 커널 (직접 접근 금지)
# ═══════════════════════════════════════════════════════════════════════════════

class EdenKernel:
    """에덴 운영 체제 커널.

    ⚠️  이 클래스는 Agent 가 직접 import/instantiate 금지.
        KernelProxy 를 통해서만 접근할 것.

    책임
    ────
      1. KernelToken 발행 · 만료 관리
      2. 생명나무 / 선악과 상태 보호
      3. Kernel Trap : 선악과 섭취 감지 → 즉시 권한 강등
      4. CherubimGuard 에 추방 집행 위임 신호 전달
    """

    def __init__(
        self,
        world:             Optional[EdenWorldEnv] = None,
        tree_effect:       Optional[Dict] = None,
        knowledge_penalty: Optional[Dict] = None,
    ) -> None:
        self._world = world
        self._life_tree, self._know_tree = make_trees(
            world             = world,
            tree_effect       = tree_effect,
            knowledge_penalty = knowledge_penalty,
        )
        self._tokens:  Dict[str, KernelToken] = {}
        self._log:     List[str] = []
        self._tick:    int = 0
        self._trap_fired: bool = False    # Kernel Trap 발동 여부 (비가역)

    # ── 토큰 관리 ─────────────────────────────────────────────────────────────

    def issue_token(self, agent_id: str, is_admin: bool = True) -> KernelToken:
        """에이전트에게 세션 토큰 발행."""
        token = KernelToken.issue(agent_id, is_admin, self._tick)
        self._tokens[agent_id] = token
        self._log.append(
            f"[tick={self._tick:04d}] TOKEN_ISSUED  {agent_id}  "
            f"admin={is_admin}  hash={token.token_hash}"
        )
        return token

    def validate_token(self, agent_id: str) -> bool:
        """토큰 유효성 검사."""
        token = self._tokens.get(agent_id)
        return token is not None and token.valid and token.is_admin

    def expire_token(self, agent_id: str) -> Optional[KernelToken]:
        """토큰 강제 만료 (Kernel Trap 전용)."""
        token = self._tokens.get(agent_id)
        if token is None:
            return None
        expired = token.expire()
        self._tokens[agent_id] = expired
        self._log.append(
            f"[tick={self._tick:04d}] TOKEN_EXPIRED  {agent_id}  "
            f"⚠ 관리자 권한 박탈"
        )
        return expired

    # ── 생명나무 접근 (Kernel 경유) ───────────────────────────────────────────

    def request_tree_access(
        self, agent_id: str
    ) -> AccessResult:
        """생명나무 접근 요청.

        커널이 토큰 검사 → 허용/거부 결정 → 결과 반환.
        Agent 가 직접 TreeOfLife.access() 를 호출하지 않음.
        """
        is_admin = self.validate_token(agent_id)
        return self._life_tree.access(agent_id=agent_id, is_admin=is_admin)

    def release_tree(self, agent_id: str) -> None:
        """생명나무 접속 해제."""
        self._life_tree.release(agent_id)

    # ── Kernel Trap — 선악과 섭취 감지 ────────────────────────────────────────

    def trap_knowledge_consumed(self, agent_id: str) -> KernelTrapResult:
        """Kernel Trap: 선악과 섭취 신호 수신 → 즉시 권한 강등.

        실행 순서 (불변):
          1. KnowledgeTree.consume() 호출
          2. 토큰 즉시 만료 (관리자 권한 박탈)
          3. 생명나무 잠금 (접속 해제 + lock)
          4. CherubimGuard 추방 준비 완료 신호 반환

        이 순서가 보장되어야 agent 가 권한 강등 전에
        system call 을 더 실행할 수 없음.
        """
        if self._trap_fired:
            raise RuntimeError(
                "KernelTrap: 이미 발동됨. 이 이벤트는 비가역입니다."
            )

        # Step 1 — 선악과 consume
        know_result = self._know_tree.consume(agent_id)

        # Step 2 — 토큰 즉시 만료 (관리자 권한 박탈)
        expired_token = self.expire_token(agent_id)

        # Step 3 — 생명나무 잠금
        self._life_tree.release(agent_id)   # 접속 해제
        self._life_tree.lock(reason=f"Kernel Trap: {agent_id} knowledge_consumed")

        # Step 4 — Trap 발동 상태 기록 (비가역)
        self._trap_fired = True

        log_entry = (
            f"[tick={self._tick:04d}] KERNEL_TRAP  {agent_id}  "
            f"entropy={know_result.entropy_injected:.2f}  "
            f"token_expired={expired_token is not None}  "
            f"tree_locked=True  expulsion_ready=True"
        )
        self._log.append(log_entry)

        return KernelTrapResult(
            agent_id         = agent_id,
            token_expired    = expired_token is not None,
            admin_revoked    = True,
            entropy_injected = know_result.entropy_injected,
            expulsion_ready  = True,
            tick             = self._tick,
            log_entry        = log_entry,
        )

    # ── 상태 조회 (읽기 전용) ─────────────────────────────────────────────────

    @property
    def tree_state(self) -> TreeState:
        return self._life_tree.state

    @property
    def knowledge_state(self) -> KnowledgeState:
        return self._know_tree.state

    @property
    def trap_fired(self) -> bool:
        return self._trap_fired

    def get_life_tree(self) -> TreeOfLife:
        """Runner 조립용 — Proxy 경유 없이 직접 접근 (내부 전용)."""
        return self._life_tree

    def get_know_tree(self) -> KnowledgeTree:
        """Runner 조립용 — Proxy 경유 없이 직접 접근 (내부 전용)."""
        return self._know_tree

    def step(self, tick: int = 1) -> None:
        self._tick += tick
        self._life_tree.step(tick)
        self._know_tree.step(tick)

    def get_log(self) -> List[str]:
        return list(self._log)

    def print_kernel_log(self, tail: int = 10) -> None:
        print("\n" + "=" * 68)
        print("  🔐 EdenKernel — 커널 로그")
        print("=" * 68)
        print(f"  tick={self._tick}  trap_fired={self._trap_fired}")
        print(f"  tree_state={self.tree_state.value}  "
              f"knowledge_state={self.knowledge_state.value}")
        print(f"\n  토큰 레지스트리:")
        for agent_id, token in self._tokens.items():
            status = "✅ VALID" if token.valid else "❌ EXPIRED"
            print(f"    {agent_id:<12}  {status}  admin={token.is_admin}  "
                  f"hash={token.token_hash}")
        print(f"\n  최근 로그 (최대 {tail}건):")
        for line in self._log[-tail:]:
            print(f"    {line}")
        print("=" * 68)


# ═══════════════════════════════════════════════════════════════════════════════
#  공개 팩토리
# ═══════════════════════════════════════════════════════════════════════════════

def make_eden_kernel(
    world:             Optional[EdenWorldEnv] = None,
    tree_effect:       Optional[Dict] = None,
    knowledge_penalty: Optional[Dict] = None,
) -> EdenKernel:
    """EdenKernel 생성.

    Parameters
    ----------
    world             : EdenWorldEnv, optional
    tree_effect       : dict, optional — 생명나무 접속 효과
    knowledge_penalty : dict, optional — 선악과 페널티

    Returns
    -------
    EdenKernel  —  KernelProxy 를 통해 에이전트에 노출할 것
    """
    return EdenKernel(
        world             = world,
        tree_effect       = tree_effect,
        knowledge_penalty = knowledge_penalty,
    )
