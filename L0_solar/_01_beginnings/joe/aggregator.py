"""조(JOE) Coarse Aggregator — PANGEA §4. 스냅샷 → planet_stress, instability.

PANGEA §4 수식은 _core(독립 엔진과 동일)에서만 수행. 계수는 CONFIG로 주입, 사용된 config는 결과에 기록.
solar 전용: 스냅샷의 rotation_stable=False이면 stress 보정 적용(상위 레이어 연동).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from ._core import (
    DEFAULT_CONFIG,
    instability_raw,
    normalize,
    planet_stress_raw,
    saturate,
)


def _label_habit(stress: float, inst: float) -> str:
    if stress >= 0.7 or inst >= 0.7:
        return "extreme"
    if stress >= 0.4 or inst >= 0.4:
        return "low"
    if stress >= 0.2 or inst >= 0.2:
        return "moderate"
    return "high"


@dataclass
class JoeAssessmentResult:
    """JOE 평가 결과. 사용된 config를 기록해 재현 가능."""
    planet_stress: float
    instability: float
    habitability_label: str
    config_used: Dict[str, Any] = field(default_factory=dict)
    rotation_stable: bool = True

    def summary(self) -> str:
        return (
            f"planet_stress={self.planet_stress:.3f}, instability={self.instability:.3f}, "
            f"habitability={self.habitability_label}, rotation_stable={self.rotation_stable}"
        )


def assess(
    snapshot: Dict[str, Any],
    config: None | Dict[str, Any] = None,
) -> JoeAssessmentResult:
    """스냅샷 + 선택적 CONFIG → JoeAssessmentResult. config 없으면 DEFAULT_CONFIG.
    PANGEA §4는 _core와 동일. solar만: rotation_stable=False면 stress 보정."""
    cfg = dict(DEFAULT_CONFIG)
    if config:
        cfg.update({k: v for k, v in config.items() if k in cfg})

    raw = planet_stress_raw(
        snapshot,
        a1=cfg["a1"], a2=cfg["a2"], a3=cfg["a3"], a4=cfg["a4"], a5=cfg["a5"],
        p_ref=cfg["p_ref"],
    )
    stress = normalize(raw, cfg["ref_min"], cfg["ref_max"])

    # solar 전용: Feature Layer가 채운 rotation_stable이 False면 stress 보정
    rotation_stable = snapshot.get("rotation_stable", True)
    if not rotation_stable:
        stress = min(1.0, stress + 0.5)

    inst_raw = instability_raw(stress, snapshot, b1=cfg["b1"], b2=cfg["b2"], b3=cfg["b3"])
    instability = saturate(inst_raw)
    label = _label_habit(stress, instability)

    return JoeAssessmentResult(
        planet_stress=stress,
        instability=instability,
        habitability_label=label,
        config_used=cfg,
        rotation_stable=rotation_stable,
    )


__all__ = [
    "DEFAULT_CONFIG",
    "JoeAssessmentResult",
    "assess",
    "planet_stress_raw",
    "normalize",
    "instability_raw",
    "saturate",
]
