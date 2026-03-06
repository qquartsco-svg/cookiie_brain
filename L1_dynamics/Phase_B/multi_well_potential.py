"""Multi-Well Potential (Gaussian Sum)

Phase B-1: 다중 우물 퍼텐셜

기존 Hopfield 이차 퍼텐셜(V = -½ x'Wx - b'x)은 연속 공간에서 단일 최솟값만 가진다.
다중 우물 구조를 위해 가우시안 합성 퍼텐셜을 사용한다.

수식:
  V(x) = -Σᵢ Aᵢ exp(-||x - cᵢ||² / (2σᵢ²))

  각 가우시안이 하나의 우물(기억)을 형성:
    cᵢ : 우물 중심 (기억 패턴)
    Aᵢ : 우물 깊이 (기억 강도, 양수)
    σᵢ : 우물 폭   (기억의 유인 범위)

  필드 (gradient):
    g(x) = -∇V(x) = -Σᵢ (Aᵢ/σᵢ²)(x - cᵢ) exp(-||x-cᵢ||²/(2σᵢ²))
    → 우물 방향으로 끌림 (인력)

  안장점 (saddle point):
    두 우물 사이 장벽의 꼭대기.
    E > V_saddle → 전이 가능 (공전)
    E < V_saddle → 하나의 우물 안에 갇힘

개념적 배경:
  Hopfield (1982) 이산 패턴 → 가우시안으로 연속 확장.
  각 가우시안 = 하나의 attractor (기억).
  장벽 = 기억 간 분리.
  공전 = 보존 에너지로 장벽을 넘는 순환.

Author: GNJz (Qquarts)
Version: 0.3.0-dev
"""

import numpy as np
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class GaussianWell:
    """단일 가우시안 우물

    V_i(x) = -A exp(-||x - c||² / (2σ²))

    Attributes:
        center: 우물 중심 (기억 패턴)
        amplitude: 우물 깊이 A (양수, 클수록 깊음)
        sigma: 우물 폭 σ (클수록 넓은 유인 범위)
    """
    center: np.ndarray
    amplitude: float = 1.0
    sigma: float = 1.0

    def __post_init__(self):
        self.center = np.asarray(self.center, dtype=float)
        if self.amplitude <= 0:
            raise ValueError(f"amplitude must be positive (got {self.amplitude})")
        if self.sigma <= 0:
            raise ValueError(f"sigma must be positive (got {self.sigma})")


class MultiWellPotential:
    """가우시안 합성 다중 우물 퍼텐셜

    V(x) = -Σᵢ Aᵢ exp(-||x - cᵢ||² / (2σᵢ²))

    PotentialFieldEngine과 통합:
        mwp = MultiWellPotential(wells)
        engine = PotentialFieldEngine(
            potential_func=mwp.potential,
            field_func=mwp.field,
            omega_coriolis=omega,
        )
    """

    def __init__(self, wells: List[GaussianWell]):
        if len(wells) < 1:
            raise ValueError("At least one well is required")
        dim = len(wells[0].center)
        for w in wells:
            if len(w.center) != dim:
                raise ValueError(
                    f"All wells must have same dimension. "
                    f"Expected {dim}, got {len(w.center)}"
                )
        self.wells = wells
        self.dim = dim

    # ------------------------------------------------------------------ #
    #  핵심 함수 — PotentialFieldEngine에 직접 전달
    # ------------------------------------------------------------------ #

    def potential(self, x: np.ndarray) -> float:
        """V(x) = -Σᵢ Aᵢ exp(-||x - cᵢ||² / (2σᵢ²))"""
        x = np.asarray(x, dtype=float)
        V = 0.0
        for w in self.wells:
            d = x - w.center
            V -= w.amplitude * np.exp(-np.dot(d, d) / (2.0 * w.sigma ** 2))
        return V

    def field(self, x: np.ndarray) -> np.ndarray:
        """g(x) = -∇V(x) = -Σᵢ (Aᵢ/σᵢ²)(x - cᵢ) exp(-||x-cᵢ||²/(2σᵢ²))

        결과 벡터는 우물 중심 방향을 가리킨다 (인력).
        """
        x = np.asarray(x, dtype=float)
        g = np.zeros(self.dim, dtype=float)
        for w in self.wells:
            d = x - w.center
            exp_term = np.exp(-np.dot(d, d) / (2.0 * w.sigma ** 2))
            g -= (w.amplitude / w.sigma ** 2) * d * exp_term
        return g

    # ------------------------------------------------------------------ #
    #  장벽 분석
    # ------------------------------------------------------------------ #

    def find_saddle_between(
        self, i: int, j: int, n_search: int = 2000
    ) -> Tuple[np.ndarray, float]:
        """우물 i, j 사이의 안장점 근사 (직선 탐색)

        두 우물 중심을 잇는 직선 위에서 V(x) 최대인 점.
        대칭 우물이면 중점, 비대칭이면 약한 우물 쪽으로 치우침.

        한계:
            직선 위만 탐색하므로, 비대칭 우물이나 3개 이상 우물이
            상호작용하는 경우 실제 안장점이 직선 밖에 있을 수 있다.
            고차원/비대칭 구성에서는 근사값으로 취급할 것.

        Returns:
            (saddle_position, V_saddle)
        """
        c_i = self.wells[i].center
        c_j = self.wells[j].center

        t_values = np.linspace(0.0, 1.0, n_search)
        line_points = c_i[np.newaxis, :] + t_values[:, np.newaxis] * (c_j - c_i)[np.newaxis, :]

        V_values = np.array([self.potential(p) for p in line_points])
        idx_max = np.argmax(V_values)

        saddle_pos = line_points[idx_max]
        return saddle_pos, V_values[idx_max]

    def barrier_height(self, i: int, j: int) -> float:
        """우물 i, j 사이 장벽의 상대 높이

        barrier = V_saddle - min(V(cᵢ), V(cⱼ))

        더 깊은 우물 바닥 기준 (conservative).
        양수면 장벽 존재. 절대 에너지 기준은 min_energy_for_orbit() 참조.
        """
        _, V_saddle = self.find_saddle_between(i, j)
        V_i = self.potential(self.wells[i].center)
        V_j = self.potential(self.wells[j].center)
        V_deeper = min(V_i, V_j)
        return V_saddle - V_deeper

    def min_energy_for_orbit(self, i: int, j: int) -> float:
        """우물 i↔j 순환에 필요한 최소 총 에너지 (절대값)

        E > V_saddle 이면 전이 가능.
        barrier_height()는 상대 높이, 이 함수는 절대 에너지 기준.
        """
        _, V_saddle = self.find_saddle_between(i, j)
        return V_saddle

    # ------------------------------------------------------------------ #
    #  진단/유틸리티
    # ------------------------------------------------------------------ #

    def nearest_well(self, x: np.ndarray) -> int:
        """가장 가까운 우물 인덱스"""
        x = np.asarray(x, dtype=float)
        dists = [np.linalg.norm(x - w.center) for w in self.wells]
        return int(np.argmin(dists))

    def landscape_info(self) -> dict:
        """퍼텐셜 지형 요약 (디버깅/검증용)"""
        info = {
            "n_wells": len(self.wells),
            "dim": self.dim,
            "wells": [],
            "barriers": [],
        }

        for idx, w in enumerate(self.wells):
            info["wells"].append({
                "index": idx,
                "center": w.center.tolist(),
                "amplitude": w.amplitude,
                "sigma": w.sigma,
                "V_center": self.potential(w.center),
            })

        for i in range(len(self.wells)):
            for j in range(i + 1, len(self.wells)):
                saddle_pos, V_saddle = self.find_saddle_between(i, j)
                info["barriers"].append({
                    "wells": (i, j),
                    "saddle_position": saddle_pos.tolist(),
                    "V_saddle": V_saddle,
                    "barrier_height": self.barrier_height(i, j),
                })

        return info


# ------------------------------------------------------------------ #
#  편의 함수
# ------------------------------------------------------------------ #

def create_symmetric_wells(
    centers: List[np.ndarray],
    amplitude: float = 1.0,
    sigma: float = 1.0,
) -> MultiWellPotential:
    """동일 깊이/폭의 대칭 우물 생성

    Args:
        centers: 우물 중심 리스트
        amplitude: 공통 깊이
        sigma: 공통 폭

    Returns:
        MultiWellPotential 인스턴스
    """
    wells = [
        GaussianWell(center=np.asarray(c, dtype=float), amplitude=amplitude, sigma=sigma)
        for c in centers
    ]
    return MultiWellPotential(wells)
