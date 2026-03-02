"""eden_os.kernel — 에덴 커널 레이어

⚠️  Agent 코드는 이 패키지를 직접 import 금지.
    KernelProxy 만 사용할 것.

공개 인터페이스
──────────────
  KernelProxy      : 에이전트 ↔ 커널 읽기 전용 인터페이스
  EdenKernel       : 커널 본체 (Runner 조립 시 생성)
  KernelToken      : 세션 토큰 (frozen)
  KernelTrapResult : Kernel Trap 결과 (frozen)
  make_eden_kernel : 커널 팩토리
  make_kernel_proxy: 프록시 팩토리
"""

from .life_kernel import (
    EdenKernel,
    KernelToken,
    KernelTrapResult,
    make_eden_kernel,
)
from .kernel_proxy import KernelProxy, make_kernel_proxy

__all__ = [
    "EdenKernel",
    "KernelToken",
    "KernelTrapResult",
    "make_eden_kernel",
    "KernelProxy",
    "make_kernel_proxy",
]
