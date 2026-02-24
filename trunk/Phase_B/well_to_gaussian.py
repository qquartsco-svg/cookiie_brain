"""WellFormation → Gaussian Bridge

WellFormationEngine 결과(W, b)를 GaussianWell로 변환하고 누적·관리.

핵심 문제:
  Hopfield V(x) = -½x'Wx - b'x → 연속 공간에서 지역 최솟값 최대 1개.
  공전에는 분리된 여러 최솟값이 필요.
  → WellFormation을 반복 호출, 결과를 누적하여 다중 Gaussian 우물 생성.

변환:
  center:
    "pattern" (기본): mean(post_activity)  — 경험 패턴 중심
    "solve":          -(W + εI)⁻¹b         — Hopfield 임계점 (b≠0 필요)

  amplitude:
    spectral_radius(W) × scale — W의 최대 고유값 크기 (기억 강도)

  sigma:
    scale / √(mean|λ_neg|) — W의 음 고유값 역수 (유인 범위)

WellRegistry:
  우물 누적 저장소. 거리 기반 중복 제거(병합) 포함.
  wells ≥ min_wells_for_orbit이면 Gaussian 모드 활성.

Author: GNJz (Qquarts)
Version: 0.3.0-dev
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
import logging

from .multi_well_potential import GaussianWell, MultiWellPotential


@dataclass
class WellToGaussianConfig:
    """W, b → GaussianWell 변환 설정

    Attributes:
        center_mode: "pattern" = mean(post_activity), "solve" = -(W+εI)⁻¹b
        regularization: solve 모드 Tikhonov 정규화 ε
        amplitude_scale: spectral_radius(W) × 이 값
        amplitude_min/max: 클램프 범위
        sigma_scale: 1/√(mean|λ|) × 이 값
        sigma_min/max: 클램프 범위
        sigma_default: 고유값 퇴화 시 기본값
        dedup_distance: 이 거리 이내 우물은 중복 처리
        min_wells_for_orbit: Gaussian 모드 전환 최소 우물 수
        merge_strategy: "weighted_average" | "replace" | "skip"
    """
    center_mode: str = "pattern"
    regularization: float = 1e-6

    amplitude_scale: float = 1.0
    amplitude_min: float = 0.1
    amplitude_max: float = 10.0

    sigma_scale: float = 1.0
    sigma_min: float = 0.3
    sigma_max: float = 5.0
    sigma_default: float = 1.0

    dedup_distance: float = 0.5
    min_wells_for_orbit: int = 3
    merge_strategy: str = "weighted_average"


# ------------------------------------------------------------------ #
#  변환 함수
# ------------------------------------------------------------------ #

def compute_center(
    W: np.ndarray,
    b: np.ndarray,
    config: WellToGaussianConfig,
    episodes: Optional[List] = None,
) -> np.ndarray:
    """우물 중심 계산

    "pattern": mean(post_activity) — BiasConfig.policy="zero"에서도 동작
    "solve":   -(W + εI)⁻¹b       — b≠0 필요, W 특이 시 정규화
    """
    if config.center_mode == "solve":
        n = len(b)
        W_reg = W + config.regularization * np.eye(n)
        try:
            center = -np.linalg.solve(W_reg, b)
        except np.linalg.LinAlgError:
            center = -np.linalg.lstsq(W_reg, b, rcond=None)[0]
        return center

    if config.center_mode == "pattern":
        if episodes is None or len(episodes) == 0:
            raise ValueError(
                "center_mode='pattern' requires non-empty episodes"
            )
        activities = []
        for ep in episodes:
            pa = getattr(ep, "post_activity", None)
            if pa is None and isinstance(ep, dict):
                pa = ep.get("post_activity")
            if pa is not None:
                activities.append(np.asarray(pa, dtype=float))
        if not activities:
            raise ValueError("No valid post_activity found in episodes")
        return np.mean(activities, axis=0)

    raise ValueError(f"Unknown center_mode: {config.center_mode}")


def compute_amplitude(
    W: np.ndarray, config: WellToGaussianConfig
) -> float:
    """기억 강도: spectral_radius(W) × scale

    W의 최대 |고유값|이 클수록 강한 기억(깊은 우물).
    """
    eigenvalues = np.linalg.eigvalsh(W)
    spectral_radius = float(np.max(np.abs(eigenvalues)))
    if spectral_radius < 1e-10:
        return config.amplitude_min
    amplitude = spectral_radius * config.amplitude_scale
    return float(np.clip(amplitude, config.amplitude_min, config.amplitude_max))


def compute_sigma(
    W: np.ndarray, config: WellToGaussianConfig
) -> float:
    """유인 범위: σ = scale / √(mean|λ_neg|)

    W의 음 고유값 → Hopfield 곡률.
    곡률 클수록 좁은 우물, 작을수록 넓은 우물.
    """
    eigenvalues = np.linalg.eigvalsh(W)
    neg_eigenvalues = eigenvalues[eigenvalues < -1e-10]

    if len(neg_eigenvalues) == 0:
        return config.sigma_default

    mean_curvature = float(np.mean(np.abs(neg_eigenvalues)))
    if mean_curvature < 1e-10:
        return config.sigma_default

    sigma = config.sigma_scale / np.sqrt(mean_curvature)
    return float(np.clip(sigma, config.sigma_min, config.sigma_max))


def well_result_to_gaussian(
    well_result: Any,
    config: WellToGaussianConfig,
    episodes: Optional[List] = None,
) -> GaussianWell:
    """WellFormationResult → GaussianWell 단일 변환"""
    if isinstance(well_result, dict):
        W = np.asarray(well_result["W"], dtype=float)
        b = np.asarray(well_result["b"], dtype=float)
    else:
        W = np.asarray(well_result.W, dtype=float)
        b = np.asarray(well_result.b, dtype=float)

    center = compute_center(W, b, config, episodes)
    amplitude = compute_amplitude(W, config)
    sigma = compute_sigma(W, config)

    return GaussianWell(center=center, amplitude=amplitude, sigma=sigma)


# ------------------------------------------------------------------ #
#  WellRegistry — 우물 누적 저장소
# ------------------------------------------------------------------ #

class WellRegistry:
    """우물 누적 저장소

    WellFormation 결과를 반복 수신, GaussianWell로 변환하여 누적.
    거리 기반 중복 제거(병합) 포함.

    사용:
        registry = WellRegistry(config)
        registry.add(well_result_1, episodes_1)
        registry.add(well_result_2, episodes_2)
        ...
        if registry.ready_for_orbit:
            mwp = registry.export_potential()
    """

    def __init__(self, config: Optional[WellToGaussianConfig] = None):
        self.config = config or WellToGaussianConfig()
        self._wells: List[GaussianWell] = []
        self._metadata: List[Dict[str, Any]] = []
        self._merge_counts: List[int] = []
        self._version: int = 0
        self.logger = logging.getLogger("WellRegistry")

    @property
    def count(self) -> int:
        return len(self._wells)

    @property
    def version(self) -> int:
        return self._version

    @property
    def ready_for_orbit(self) -> bool:
        return self.count >= self.config.min_wells_for_orbit

    @property
    def wells(self) -> List[GaussianWell]:
        return list(self._wells)

    def add(
        self,
        well_result: Any,
        episodes: Optional[List] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> int:
        """WellFormationResult 추가 (변환 + 중복 검사)

        Returns:
            추가/병합된 우물 인덱스
        """
        new_well = well_result_to_gaussian(
            well_result, self.config, episodes
        )
        return self.add_well(new_well, meta)

    def add_well(
        self,
        well: GaussianWell,
        meta: Optional[Dict[str, Any]] = None,
    ) -> int:
        """GaussianWell 직접 추가 (수동 배치 또는 외부 변환용)

        Returns:
            추가/병합된 우물 인덱스
        """
        nearest_idx, nearest_dist = self._find_nearest(well.center)

        if nearest_idx >= 0 and nearest_dist < self.config.dedup_distance:
            idx = self._handle_duplicate(nearest_idx, well, meta)
        else:
            self._wells.append(well)
            self._metadata.append(meta or {})
            self._merge_counts.append(1)
            idx = len(self._wells) - 1
            self.logger.info(
                f"Well #{idx}: center={well.center.tolist()}, "
                f"A={well.amplitude:.4f}, σ={well.sigma:.4f}"
            )

        self._version += 1
        return idx

    def _find_nearest(self, center: np.ndarray) -> Tuple[int, float]:
        if not self._wells:
            return -1, float("inf")
        dists = [np.linalg.norm(center - w.center) for w in self._wells]
        idx = int(np.argmin(dists))
        return idx, dists[idx]

    def _handle_duplicate(
        self, idx: int, new_well: GaussianWell,
        meta: Optional[Dict[str, Any]],
    ) -> int:
        strategy = self.config.merge_strategy

        if strategy == "skip":
            self.logger.debug(f"Well near #{idx}, skipping")
            return idx

        if strategy == "replace":
            self._wells[idx] = new_well
            self._metadata[idx] = meta or {}
            self._merge_counts[idx] += 1
            self.logger.info(f"Well #{idx} replaced")
            return idx

        old = self._wells[idx]
        n = self._merge_counts[idx]
        merged_center = (old.center * n + new_well.center) / (n + 1)
        merged_amplitude = (old.amplitude * n + new_well.amplitude) / (n + 1)
        merged_sigma = (old.sigma * n + new_well.sigma) / (n + 1)

        self._wells[idx] = GaussianWell(
            center=merged_center,
            amplitude=merged_amplitude,
            sigma=merged_sigma,
        )
        self._merge_counts[idx] = n + 1
        if meta:
            self._metadata[idx].update(meta)
        self.logger.info(
            f"Well #{idx} merged (x{n + 1}): "
            f"center={merged_center.tolist()}"
        )
        return idx

    def export_potential(self) -> MultiWellPotential:
        """누적된 우물들로 MultiWellPotential 생성"""
        if not self._wells:
            raise ValueError("No wells in registry")
        return MultiWellPotential(list(self._wells))

    def clear(self):
        """레지스트리 초기화"""
        self._wells.clear()
        self._metadata.clear()
        self._merge_counts.clear()
        self._version += 1

    def info(self) -> Dict[str, Any]:
        """레지스트리 상태 요약"""
        return {
            "n_wells": self.count,
            "ready_for_orbit": self.ready_for_orbit,
            "min_wells_for_orbit": self.config.min_wells_for_orbit,
            "version": self._version,
            "wells": [
                {
                    "index": i,
                    "center": w.center.tolist(),
                    "amplitude": w.amplitude,
                    "sigma": w.sigma,
                    "merge_count": self._merge_counts[i],
                }
                for i, w in enumerate(self._wells)
            ],
        }
