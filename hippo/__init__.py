"""hippo — 운영층 (태양/장기기억)

솔라시스템의 태양 = 인지과학의 해마(Hippocampus).
trunk(물리 엔진)이 만든 궤적 위에서 우물(기억)의 생애주기를 관리하고,
에너지 주입 I(x,v,t)를 자동 제어한다.

구조:
  hippo/
  ├── memory_store.py       (A) 우물 생성·강화·감쇠·소멸
  ├── energy_budgeter.py    (B) I(x,v,t) 자동 제어 (탐색/정착/리콜)
  └── hippo_memory_engine.py     통합 엔진

trunk 위에 hippo(운영층)가, hippo 위에 analysis(분석층)가 올라간다.
"""

from hippo.memory_store import MemoryStore
from hippo.energy_budgeter import EnergyBudgeter
from hippo.hippo_memory_engine import HippoMemoryEngine, HippoConfig

__all__ = [
    "MemoryStore",
    "EnergyBudgeter",
    "HippoMemoryEngine",
    "HippoConfig",
]
