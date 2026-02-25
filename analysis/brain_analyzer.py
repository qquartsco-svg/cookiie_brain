"""BrainAnalyzer — trunk(Phase A~C) 궤적을 analysis(Layer 1~6)로 자동 분석

CookiieBrainEngine이 만든 궤적(x, v, t)을 받아서
Layer 1~6 분석 도구를 유기적으로 엮어 한 번에 결과를 뽑는다.

사용법:
    from analysis.brain_analyzer import BrainAnalyzer

    analyzer = BrainAnalyzer(mwp, gamma=0.1, temperature=1.0, mass=1.0)
    report = analyzer.run(positions, velocities, dt)

    print(report["layer1"]["entropy_production_rate"])
    print(report["layer1"]["transition_matrix"])
    print(report["layer5"]["equilibrium_density"])
    print(report["layer6"]["fisher_metric"])

흐름:
    PFE 궤적 (x, v)
        │
        ├─→ Layer 1: 전이 확률, 엔트로피 생산, 체류 시간
        ├─→ Layer 5: 확률 밀도 ρ(x,t), 확률류 J, Nelson 분해
        ├─→ Layer 6: Fisher 계량, 곡률, 민감도
        │
        └─→ 통합 리포트
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, Optional

from trunk.Phase_B.multi_well_potential import MultiWellPotential


@dataclass
class AnalyzerConfig:
    """BrainAnalyzer 분석 임계값 설정

    분석 판정에 사용되는 수치 기준을 한 곳에 모은다.
    """
    ep_min_trajectory_len: int = 200
    ep_window_default: int = 100
    equilibrium_ep_scale: float = 0.1
    equilibrium_db_threshold: float = 0.1
    density_mask_threshold: float = 0.01
    density_match_threshold: float = 0.1
    curvature_nontrivial_eps: float = 1e-6
    layer6_x_padding: float = 3.0
    layer6_grid_points: int = 500

from analysis.Layer_1 import (
    kramers_rate_matrix,
    TransitionAnalyzer,
    entropy_production_rate,
    entropy_production_trajectory,
)
from analysis.Layer_5 import (
    FokkerPlanckSolver1D,
    NelsonDecomposition,
    ProbabilityCurrent,
)
from analysis.Layer_6 import (
    FisherMetricCalculator,
)


class BrainAnalyzer:
    """trunk 궤적 → Layer 1~6 통합 분석.

    Parameters
    ----------
    mwp : MultiWellPotential
        다중 우물 퍼텐셜 (trunk Phase B에서 생성)
    gamma : float
        감쇠 계수
    temperature : float
        온도 T
    mass : float
        질량 m
    """

    def __init__(
        self,
        mwp: MultiWellPotential,
        gamma: float,
        temperature: float,
        mass: float = 1.0,
        config: Optional[AnalyzerConfig] = None,
    ):
        self.mwp = mwp
        self.gamma = gamma
        self.T = temperature
        self.mass = mass
        self.D = temperature / (mass * gamma) if gamma > 0 else 0.0
        self.cfg = config or AnalyzerConfig()

    # ────────────────────────────────────────────────────
    #  통합 실행
    # ────────────────────────────────────────────────────

    def run(
        self,
        positions: np.ndarray,
        velocities: np.ndarray,
        dt: float,
        fp_x_range: tuple = (-4.0, 4.0),
        fp_nx: int = 400,
        fisher_lam_ranges: Optional[tuple] = None,
    ) -> Dict[str, Any]:
        """궤적을 받아 Layer 1~6 분석을 한 번에 실행.

        Parameters
        ----------
        positions : (n_steps, dim)
            위치 궤적
        velocities : (n_steps, dim)
            속도 궤적
        dt : float
            시간 간격
        fp_x_range : tuple
            Fokker-Planck 격자 범위 (1D)
        fp_nx : int
            Fokker-Planck 격자 점 수
        fisher_lam_ranges : tuple or None
            Fisher 계량 매개변수 범위. None이면 우물 중심 기반 자동 설정.

        Returns
        -------
        dict
            layer1, layer5, layer6, summary 키를 가진 분석 결과
        """
        report: Dict[str, Any] = {}

        report["layer1"] = self._analyze_layer1(positions, velocities, dt)
        report["layer5"] = self._analyze_layer5(positions, fp_x_range, fp_nx)
        report["layer6"] = self._analyze_layer6(fisher_lam_ranges)
        report["summary"] = self._build_summary(report)

        return report

    # ────────────────────────────────────────────────────
    #  Layer 1: 통계역학
    # ────────────────────────────────────────────────────

    def _analyze_layer1(
        self,
        positions: np.ndarray,
        velocities: np.ndarray,
        dt: float,
    ) -> Dict[str, Any]:
        n_wells = len(self.mwp.wells)
        result: Dict[str, Any] = {}

        K = kramers_rate_matrix(self.mwp, self.T, self.gamma, self.mass)
        result["kramers_rate_matrix"] = K

        analyzer = TransitionAnalyzer(n_wells=n_wells)
        for i in range(len(positions)):
            analyzer.observe(positions[i], self.mwp, dt)

        result["transition_matrix"] = analyzer.transition_matrix()
        result["transition_counts"] = analyzer.transition_counts()
        result["occupation_fractions"] = analyzer.occupation_fractions()
        result["mean_residence_times"] = analyzer.mean_residence_times()
        result["detailed_balance_violation"] = analyzer.detailed_balance_violation()
        result["net_circulation"] = analyzer.net_circulation()

        ep_rate = entropy_production_rate(
            velocities, self.gamma, self.T, self.mass
        )
        result["entropy_production_rate"] = ep_rate

        if len(velocities) >= self.cfg.ep_min_trajectory_len:
            window = min(self.cfg.ep_window_default, len(velocities) // 2)
            ep_traj = entropy_production_trajectory(
                velocities, self.gamma, self.T, self.mass, window=window
            )
            result["entropy_trajectory"] = ep_traj
            result["entropy_trajectory_mean"] = float(np.mean(ep_traj))

        result["is_equilibrium"] = (
            abs(ep_rate) < self.cfg.equilibrium_ep_scale * self.gamma * self.T / self.mass
            and analyzer.detailed_balance_violation() < self.cfg.equilibrium_db_threshold
        )

        return result

    # ────────────────────────────────────────────────────
    #  Layer 5: 확률역학 (1D 전용)
    # ────────────────────────────────────────────────────

    def _analyze_layer5(
        self,
        positions: np.ndarray,
        x_range: tuple,
        nx: int,
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        dim = positions.shape[-1] if positions.ndim > 1 else 1
        if dim != 1:
            result["skipped"] = True
            result["reason"] = f"Layer 5 FP is 1D only, got dim={dim}"
            return result

        pos_1d = positions.ravel()

        def V_1d(x):
            return np.array([self.mwp.potential(np.array([xi])) for xi in x])

        x_grid = np.linspace(x_range[0], x_range[1], nx)
        dx = x_grid[1] - x_grid[0]

        V_vals = V_1d(x_grid)
        log_rho = -V_vals / self.T
        log_rho -= np.max(log_rho)
        rho_eq = np.exp(log_rho)
        rho_eq /= np.trapezoid(rho_eq, x_grid)

        result["x_grid"] = x_grid
        result["equilibrium_density"] = rho_eq

        hist, bin_edges = np.histogram(pos_1d, bins=nx, range=x_range, density=True)
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
        result["observed_density"] = hist
        result["observed_density_x"] = bin_centers

        rho_interp = np.interp(bin_centers, x_grid, rho_eq)
        mask = rho_interp > self.cfg.density_mask_threshold
        if np.any(mask):
            l1_err = float(np.mean(np.abs(hist[mask] - rho_interp[mask])))
            result["density_l1_error"] = l1_err
            result["density_match"] = l1_err < self.cfg.density_match_threshold

        dV = np.gradient(V_vals, dx)
        b = -dV / (self.mass * self.gamma)

        pc = ProbabilityCurrent()
        J = pc.compute(rho_eq, b, self.D, dx)
        result["equilibrium_current_max"] = float(np.max(np.abs(J[2:-2])))

        v_osm = NelsonDecomposition.osmotic_velocity(rho_eq, dx, self.D)
        v_cur = NelsonDecomposition.current_velocity(x_grid, dV, self.mass, self.gamma)
        result["nelson_osmotic_rms"] = float(np.sqrt(np.mean(v_osm**2)))
        result["nelson_current_rms"] = float(np.sqrt(np.mean(v_cur**2)))

        return result

    # ────────────────────────────────────────────────────
    #  Layer 6: 정보 기하학
    # ────────────────────────────────────────────────────

    def _analyze_layer6(
        self,
        lam_ranges: Optional[tuple],
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        dim = self.mwp.dim
        if dim != 1:
            result["skipped"] = True
            result["reason"] = f"Layer 6 Fisher metric is 1D only, got dim={dim}"
            return result

        n_wells = len(self.mwp.wells)
        if n_wells < 2:
            result["skipped"] = True
            result["reason"] = "Need >= 2 wells for Fisher metric analysis"
            return result

        centers = [w.center[0] for w in self.mwp.wells]
        x_min = min(centers) - self.cfg.layer6_x_padding
        x_max = max(centers) + self.cfg.layer6_x_padding
        x_grid = np.linspace(x_min, x_max, self.cfg.layer6_grid_points)

        amps = [w.amplitude for w in self.mwp.wells]
        sigs = [w.sigma for w in self.mwp.wells]

        def V_param(x, lam1, lam2):
            v = np.zeros_like(x)
            for c, a, s in zip(centers, amps, sigs):
                v += -a * np.exp(-((x - c) ** 2) / (2 * s**2))
            v += lam1 * x + lam2 * x**2
            return v

        fisher = FisherMetricCalculator(x_grid, V_param, self.T)

        g_origin = fisher.metric_tensor(0.0, 0.0)
        result["fisher_metric_origin"] = g_origin
        result["fisher_positive_definite"] = bool(np.all(np.linalg.eigvalsh(g_origin) > 0))

        K = fisher.gaussian_curvature(0.0, 0.0)
        result["gaussian_curvature_origin"] = K
        result["curvature_nontrivial"] = abs(K) > self.cfg.curvature_nontrivial_eps

        path = np.array([[0.0, 0.0], [0.5, 0.0], [0.5, 0.5], [0.0, 0.5], [0.0, 0.0]])
        L_fisher = fisher.geodesic_distance(path)
        L_euclid = sum(np.linalg.norm(path[i + 1] - path[i]) for i in range(len(path) - 1))
        result["fisher_distance"] = L_fisher
        result["euclidean_distance"] = L_euclid

        return result

    # ────────────────────────────────────────────────────
    #  통합 요약
    # ────────────────────────────────────────────────────

    def _build_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        s: Dict[str, Any] = {}

        l1 = report["layer1"]
        s["n_wells"] = len(self.mwp.wells)
        s["total_transitions"] = int(l1["transition_counts"].sum())
        s["is_equilibrium"] = l1["is_equilibrium"]
        s["entropy_production_rate"] = l1["entropy_production_rate"]
        s["most_occupied_well"] = int(np.argmax(l1["occupation_fractions"]))
        s["detailed_balance_violation"] = l1["detailed_balance_violation"]

        l5 = report["layer5"]
        if not l5.get("skipped"):
            s["density_match"] = l5.get("density_match", None)

        l6 = report["layer6"]
        if not l6.get("skipped"):
            s["curvature_nontrivial"] = l6.get("curvature_nontrivial", None)
            s["fisher_positive_definite"] = l6.get("fisher_positive_definite", None)

        return s

    # ────────────────────────────────────────────────────
    #  리포트 출력
    # ────────────────────────────────────────────────────

    @staticmethod
    def print_report(report: Dict[str, Any]) -> None:
        """분석 결과를 사람이 읽을 수 있게 출력."""
        print("=" * 60)
        print("  CookiieBrain 통합 분석 리포트")
        print("=" * 60)

        s = report["summary"]
        print(f"\n우물 수: {s['n_wells']}")
        print(f"총 전이 횟수: {s['total_transitions']}")
        print(f"가장 많이 머문 우물: #{s['most_occupied_well']}")
        print(f"평형 상태: {'예' if s['is_equilibrium'] else '아니오'}")
        print(f"엔트로피 생산률 Ṡ: {s['entropy_production_rate']:.6f}")
        print(f"상세 균형 위반: {s['detailed_balance_violation']:.4f}")

        l1 = report["layer1"]
        print(f"\n--- Layer 1: 통계역학 ---")
        print(f"점유 비율: {l1['occupation_fractions']}")
        print(f"평균 체류 시간: {l1['mean_residence_times']}")
        print(f"전이 행렬:\n{l1['transition_matrix']}")

        l5 = report["layer5"]
        print(f"\n--- Layer 5: 확률역학 ---")
        if l5.get("skipped"):
            print(f"  건너뜀: {l5['reason']}")
        else:
            if "density_match" in l5:
                match = "일치" if l5["density_match"] else "불일치"
                print(f"  관측 밀도 ↔ 볼츠만: {match} (L1 오차: {l5.get('density_l1_error', '?'):.4f})")
            print(f"  평형 확률류 |J|_max: {l5['equilibrium_current_max']:.2e}")
            print(f"  Nelson 삼투속도 RMS: {l5['nelson_osmotic_rms']:.4f}")

        l6 = report["layer6"]
        print(f"\n--- Layer 6: 정보 기하학 ---")
        if l6.get("skipped"):
            print(f"  건너뜀: {l6['reason']}")
        else:
            print(f"  Fisher 계량 양정치: {'예' if l6['fisher_positive_definite'] else '아니오'}")
            print(f"  가우스 곡률 K: {l6['gaussian_curvature_origin']:.6f}")
            print(f"  Fisher 거리: {l6['fisher_distance']:.4f}")
            print(f"  유클리드 거리: {l6['euclidean_distance']:.4f}")

        print("\n" + "=" * 60)
