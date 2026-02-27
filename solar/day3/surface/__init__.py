"""solar/surface/ — 땅과 바다의 분리 (셋째날 / Phase 7)

창세기 셋째날: "물을 한 곳으로 모으고 땅이 드러나게 하시니라"

표면 타입(육지/바다)과 알베도.
atmosphere/ 레이어가 복사 계산에 사용할 유효 알베도를 제공한다.

의존: 없음 (상수만 사용). atmosphere/가 이 레이어를 읽음.
"""

from .surface_schema import SurfaceSchema, effective_albedo

__all__ = [
    "SurfaceSchema",
    "effective_albedo",
]
