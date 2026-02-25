"""Cookiie Brain 통합 엔진

모든 개별 엔진들을 연결하는 통합 시스템.

통합 엔진:
1. WellFormationEngine → W, b 생성 (Hopfield 에너지)
2. PotentialFieldEngine → 에너지 지형 → 퍼텐셜 필드 변환
3. TidalField → 3계층 중력: 태양(1/r) + 달(조석) [v0.7.0~v0.7.1]
4. HippoMemoryEngine → 장기 기억 시스템
5. CerebellumEngine → 운동 조율 및 학습

Author: GNJz (Qquarts)
Version: 0.7.1
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional, Callable, Union
import numpy as np
import logging
from pathlib import Path
import sys

# BrainCore import
try:
    from brain_core.global_state import GlobalState
    from brain_core.engine_wrappers import SelfOrganizingEngine
except ImportError:
    # 독립 실행을 위한 대체
    try:
        # 메인 폴더 기준: CookiieBrain/ -> 00_BRAIN/
        brain_core_path = Path(__file__).parent.parent / "BrainCore" / "src"
        sys.path.insert(0, str(brain_core_path))
        from brain_core.global_state import GlobalState
        from brain_core.engine_wrappers import SelfOrganizingEngine
    except ImportError:
        raise ImportError(
            "BrainCore가 필요합니다. "
            "BrainCore를 설치하거나 PYTHONPATH에 추가하세요."
        )

# WellFormationEngine import
try:
    # 메인 폴더 기준: CookiieBrain/ -> Brain_Disorder_Simulation_Engine/Unsolved_Problems_Engines/WellFormationEngine/
    well_formation_path = Path(__file__).parent.parent / "Brain_Disorder_Simulation_Engine" / "Unsolved_Problems_Engines" / "WellFormationEngine" / "src"
    sys.path.insert(0, str(well_formation_path))
    from well_formation_engine.engine import WellFormationEngine
    from well_formation_engine.models import WellFormationResult, Episode
    WELL_FORMATION_AVAILABLE = True
except ImportError:
    WELL_FORMATION_AVAILABLE = False
    WellFormationEngine = None
    WellFormationResult = None
    Episode = None

# PotentialFieldEngine import
try:
    # 메인 폴더 기준: CookiieBrain/ -> Brain_Disorder_Simulation_Engine/Unsolved_Problems_Engines/PotentialFieldEngine/
    potential_field_path = Path(__file__).parent.parent / "Brain_Disorder_Simulation_Engine" / "Unsolved_Problems_Engines" / "PotentialFieldEngine"
    sys.path.insert(0, str(potential_field_path))
    from potential_field_engine import PotentialFieldEngine
    from well_formation_integration import create_potential_from_wells, create_field_from_wells
    POTENTIAL_FIELD_AVAILABLE = True
except ImportError:
    POTENTIAL_FIELD_AVAILABLE = False
    PotentialFieldEngine = None
    create_potential_from_wells = None
    create_field_from_wells = None

# CerebellumEngine import
try:
    # 메인 폴더 기준: CookiieBrain/ -> Archive/Integrated/5.Cerebellum_Engine/
    cerebellum_path = Path(__file__).parent.parent / "Archive" / "Integrated" / "5.Cerebellum_Engine" / "package"
    sys.path.insert(0, str(cerebellum_path))
    from cerebellum.cerebellum_engine import CerebellumEngine, CerebellumConfig
    CEREBELLUM_AVAILABLE = True
except ImportError:
    CEREBELLUM_AVAILABLE = False
    CerebellumEngine = None
    CerebellumConfig = None

# Phase_A (Rotational field, 자전) import
try:
    phase_a_path = Path(__file__).parent
    if str(phase_a_path) not in sys.path:
        sys.path.insert(0, str(phase_a_path))
    from trunk.Phase_A import Pole, create_rotational_field
    PHASE_A_AVAILABLE = True
except ImportError:
    PHASE_A_AVAILABLE = False
    Pole = None
    create_rotational_field = None

# Phase_B (Multi-well potential, Gaussian bridge) import
try:
    from trunk.Phase_B.well_to_gaussian import WellRegistry, WellToGaussianConfig
    PHASE_B_AVAILABLE = True
except ImportError:
    PHASE_B_AVAILABLE = False
    WellRegistry = None
    WellToGaussianConfig = None

# HippoMemoryEngine import
try:
    from hippo import HippoMemoryEngine, HippoConfig
    HIPPO_MEMORY_AVAILABLE = True
except ImportError:
    HIPPO_MEMORY_AVAILABLE = False
    HippoMemoryEngine = None
    HippoConfig = None

# TidalField (3계층 중력: 태양+달+조석) import
try:
    from solar import CentralBody, OrbitalMoon, TidalField
    TIDAL_AVAILABLE = True
except ImportError:
    TIDAL_AVAILABLE = False
    CentralBody = None
    OrbitalMoon = None
    TidalField = None

__version__ = "0.7.1"

# BrainAnalyzer import
try:
    from analysis.brain_analyzer import BrainAnalyzer
    BRAIN_ANALYZER_AVAILABLE = True
except ImportError:
    BRAIN_ANALYZER_AVAILABLE = False
    BrainAnalyzer = None


class CookiieBrainEngine(SelfOrganizingEngine):
    """Cookiie Brain 통합 엔진 (v0.7.1)
    
    엔진 연결 순서:
    1. WellFormationEngine → W, b 생성 (Hopfield 에너지)
    2. PotentialFieldEngine → 퍼텐셜 필드 변환
       └── TidalField injection: 태양(1/r) + 달(조석) 힘이 매 스텝 합산
    3. HippoMemoryEngine → 기억 생애주기 + 에너지 배분
    4. CerebellumEngine → 운동 조율 (선택적)
    
    3계층 중력 (enable_tidal=True):
      Tier 1: CentralBody  → V_sun = -GM/(r+ε)  장거리 구속
      Tier 2: GaussianWell  → V_wells (기존 PFE)  국소 끌림
      Tier 3: OrbitalMoon  → V_moon(x,t)         주기적 조석력
      TidalField가 Tier 1+3을 합성하여 PFE injection_func에 주입.
    """
    
    def __init__(
        self,
        enable_well_formation: bool = True,
        enable_potential_field: bool = True,
        enable_hippo_memory: bool = False,
        enable_tidal: bool = False,
        enable_cerebellum: bool = False,
        well_formation_config: Optional[Dict[str, Any]] = None,
        potential_field_config: Optional[Dict[str, Any]] = None,
        tidal_config: Optional[Dict[str, Any]] = None,
        cerebellum_config: Optional[Dict[str, Any]] = None,
        hippo_memory_config: Optional[Dict[str, Any]] = None,
        well_to_gaussian_config: Optional[Dict[str, Any]] = None,
        error_isolation: bool = False,
        enable_logging: bool = True,
    ):
        """CookiieBrainEngine 초기화
        
        Args:
            enable_well_formation: WellFormationEngine 활성화 여부
            enable_potential_field: PotentialFieldEngine 활성화 여부
            enable_hippo_memory: HippoMemoryEngine 활성화 여부
            enable_tidal: TidalField 3계층 중력 활성화 여부
            enable_cerebellum: CerebellumEngine 활성화 여부
            well_formation_config: WellFormationEngine 설정
            potential_field_config: PotentialFieldEngine + 물리 파라미터 설정
            tidal_config: 3계층 중력 설정 (central, moons)
            cerebellum_config: CerebellumEngine 설정
            hippo_memory_config: HippoMemoryEngine 설정 (eta, decay_rate 등)
            well_to_gaussian_config: WellToGaussian 변환 설정
            error_isolation: True면 엔진 실패 시 격리
            enable_logging: 로깅 활성화 여부
        """
        self.enable_well_formation = enable_well_formation
        self.enable_potential_field = enable_potential_field
        self.enable_hippo_memory = enable_hippo_memory
        self.enable_tidal = enable_tidal
        self.enable_cerebellum = enable_cerebellum
        self.error_isolation = error_isolation
        
        # PotentialFieldEngine / 물리 파라미터 설정
        self.potential_field_config = potential_field_config or {}
        self.gamma: float = self.potential_field_config.get("gamma", 0.0)
        self.temperature: Optional[float] = self.potential_field_config.get("temperature", None)
        self.mass: float = self.potential_field_config.get("mass", 1.0)
        self.noise_sigma: float = self.potential_field_config.get("noise_sigma", 0.0)
        self.noise_seed: Optional[int] = self.potential_field_config.get("noise_seed", None)
        self.injection_func: Optional[Callable] = self.potential_field_config.get("injection_func", None)
        
        # Phase A 설정
        self.enable_phase_a = self.potential_field_config.get("enable_phase_a", False)
        self.phase_a_mode: str = self.potential_field_config.get("phase_a_mode", "minimal")
        self.phase_a_omega: float = self.potential_field_config.get("phase_a_omega", 0.0)
        self.phase_a_pole_position = self.potential_field_config.get("phase_a_pole_position")
        self.phase_a_strength = self.potential_field_config.get("phase_a_strength", 1.0)
        self.phase_a_rotation_direction = self.potential_field_config.get("phase_a_rotation_direction", 1)
        
        # CerebellumEngine 설정 저장
        self.cerebellum_config = cerebellum_config or {}
        self.cerebellum_memory_dim = self.cerebellum_config.get("memory_dim", 5)
        self.cerebellum_dt = self.cerebellum_config.get("dt", 0.001)
        self.cerebellum_correction_scale = self.cerebellum_config.get("correction_scale", 0.01)
        
        self.enable_logging = enable_logging
        if enable_logging:
            self.logger = logging.getLogger("CookiieBrainEngine")
        else:
            self.logger = None
        
        # 엔진 초기화
        self.well_formation_engine = None
        self.potential_field_engine = None
        self.hippo_memory_engine = None
        self.cerebellum_engine = None
        
        # WellFormationEngine 초기화
        if enable_well_formation:
            if not WELL_FORMATION_AVAILABLE:
                raise ImportError("WellFormationEngine을 import할 수 없습니다.")
            try:
                wf_config = well_formation_config or {}
                self.well_formation_engine = WellFormationEngine(
                    hebbian_config=wf_config.get("hebbian_config"),
                    stability_constraints=wf_config.get("stability_constraints"),
                    bias_config=wf_config.get("bias_config"),
                )
                if self.logger:
                    self.logger.info("WellFormationEngine 초기화 완료")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"WellFormationEngine 초기화 실패: {e}")
                raise
        
        # CerebellumEngine 초기화
        if enable_cerebellum:
            if not CEREBELLUM_AVAILABLE:
                if self.logger:
                    self.logger.warning("CerebellumEngine을 import할 수 없습니다. 비활성화합니다.")
                self.enable_cerebellum = False
            else:
                try:
                    cerebellum_engine_config = CerebellumConfig()
                    self.cerebellum_engine = CerebellumEngine(
                        memory_dim=self.cerebellum_memory_dim,
                        config=cerebellum_engine_config,
                    )
                    if self.logger:
                        self.logger.info("CerebellumEngine 초기화 완료")
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"CerebellumEngine 초기화 실패: {e}")
                    self.enable_cerebellum = False
        
        # HippoMemoryEngine 초기화
        self.hippo_memory_engine = None
        if enable_hippo_memory:
            if not HIPPO_MEMORY_AVAILABLE:
                if self.logger:
                    self.logger.warning("HippoMemoryEngine import 실패. 비활성화.")
                self.enable_hippo_memory = False
            else:
                try:
                    hippo_cfg = HippoConfig(**(hippo_memory_config or {}))
                    dim = len(self.potential_field_config.get("initial_state", [0, 0])) // 2 or 1
                    self.hippo_memory_engine = HippoMemoryEngine(
                        config=hippo_cfg,
                        dim=dim,
                        rng_seed=self.noise_seed,
                    )
                    if self.logger:
                        self.logger.info("HippoMemoryEngine 초기화 완료")
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"HippoMemoryEngine 초기화 실패: {e}")
                    self.enable_hippo_memory = False
        
        # Phase B 브릿지: WellRegistry (우물 누적 저장소)
        self.well_registry = None
        self._registry_version: int = 0
        if PHASE_B_AVAILABLE:
            wtg_cfg = WellToGaussianConfig(**(well_to_gaussian_config or {}))
            self.well_registry = WellRegistry(config=wtg_cfg)
        
        # TidalField 초기화 (3계층 중력: 태양+달+조석)
        self.tidal_field: Optional[TidalField] = None
        if enable_tidal:
            if not TIDAL_AVAILABLE:
                if self.logger:
                    self.logger.warning("TidalField import 실패. 비활성화.")
                self.enable_tidal = False
            else:
                self.tidal_field = self._build_tidal_field(tidal_config or {})
                if self.logger:
                    info = self.tidal_field.info()
                    self.logger.info(
                        f"TidalField 초기화 완료: "
                        f"central={'있음' if info['has_central'] else '없음'}, "
                        f"moons={info['n_moons']}개"
                    )

        # 내부 상태
        self.current_well_result: Optional[WellFormationResult] = None
        self.current_potential_func: Optional[Callable] = None
        self.current_field_func: Optional[Callable] = None
    
    def update(self, state: GlobalState) -> GlobalState:
        """통합 엔진 업데이트
        
        엔진 연결 순서:
        1. WellFormationEngine → W, b 생성
        2. PotentialFieldEngine → 퍼텐셜 필드 변환 및 상태 업데이트
        3. HippoMemoryEngine → 장기 기억 시스템 (선택적)
        4. CerebellumEngine → 운동 조율 및 학습 (선택적)
        
        Args:
            state: 현재 상태
            
        Returns:
            업데이트된 상태
        """
        # 상태 복사 (불변성 유지)
        # deep=True로 완전한 복제 (extension 내부 dict, numpy 배열도 복제)
        new_state = state.copy(deep=True)
        
        try:
            # 1. WellFormationEngine 실행
            if self.enable_well_formation:
                well_result = self._run_well_formation(new_state)
                if well_result:
                    if self.current_well_result is None:
                        well_changed = True
                    else:
                        well_changed = (
                            not np.array_equal(well_result.W, self.current_well_result.W) or
                            not np.array_equal(well_result.b, self.current_well_result.b)
                        )
                    
                    self.current_well_result = well_result
                    
                    # Registry 누적 (Phase B 브릿지)
                    if self.well_registry is not None:
                        episodes_data = new_state.get_extension("episodes", [])
                        self.well_registry.add(well_result, episodes_data)
                    
                    # Potential/field 재구성
                    if self.enable_potential_field and POTENTIAL_FIELD_AVAILABLE:
                        if (self.well_registry is not None
                                and self.well_registry.ready_for_orbit
                                and self._registry_version != self.well_registry.version):
                            mwp = self.well_registry.export_potential()
                            self.current_potential_func = mwp.potential
                            self.current_field_func = mwp.field
                            self.potential_field_engine = None
                            self._registry_version = self.well_registry.version
                            if self.logger:
                                self.logger.info(
                                    f"Gaussian mode activated: "
                                    f"{self.well_registry.count} wells"
                                )
                        elif well_changed:
                            self.current_potential_func = create_potential_from_wells(well_result)
                            self.current_field_func = create_field_from_wells(well_result)
                            self.potential_field_engine = None
                    
                    # WellFormationEngine 결과를 extensions에 저장
                    new_state.set_extension("well_formation", {
                        "W": well_result.W.copy(),
                        "b": well_result.b.copy(),
                        "well_result": well_result,
                    })
                    if self.well_registry is not None:
                        new_state.set_extension(
                            "well_registry", self.well_registry.info()
                        )
            
            # 2. PotentialFieldEngine 실행
            if self.enable_potential_field and self.current_well_result:
                if not self.potential_field_engine:
                    omega_coriolis = None
                    rotational_func = None
                    if self.enable_phase_a and PHASE_A_AVAILABLE:
                        dim = len(self.current_well_result.b)
                        if self.phase_a_mode == "minimal":
                            omega_coriolis = float(self.phase_a_omega)
                        elif self.phase_a_mode == "pole" and Pole is not None and create_rotational_field is not None:
                            pole_position = self.phase_a_pole_position
                            if pole_position is None:
                                pole_position = np.zeros(dim)
                            else:
                                pole_position = np.array(pole_position)
                            if len(pole_position) != dim:
                                pole_position = np.zeros(dim)
                            pole = Pole(
                                position=pole_position,
                                rotation_direction=int(self.phase_a_rotation_direction),
                                strength=float(self.phase_a_strength),
                            )
                            rotational_func = create_rotational_field(pole, use_simple_form=True)
                    combined_injection = self._build_combined_injection()
                    self.potential_field_engine = PotentialFieldEngine(
                        potential_func=self.current_potential_func,
                        field_func=self.current_field_func,
                        rotational_func=rotational_func,
                        omega_coriolis=omega_coriolis,
                        gamma=self.gamma,
                        injection_func=combined_injection,
                        noise_sigma=self.noise_sigma,
                        temperature=self.temperature,
                        mass=self.mass,
                        noise_seed=self.noise_seed,
                    )
                
                # PotentialFieldEngine 업데이트
                new_state = self.potential_field_engine.update(new_state)
            
            # 2.5. TidalField 상태 기록
            if self.enable_tidal and self.tidal_field is not None:
                sv = new_state.state_vector
                n_dim = len(sv) // 2
                x = sv[:n_dim]
                pf_ext = new_state.get_extension("potential_field", {})
                t = pf_ext.get("time", 0.0)
                new_state.set_extension("tidal", {
                    "info": self.tidal_field.info(),
                    "tidal_potential": self.tidal_field.potential(x, t),
                    "time": t,
                })
            
            # 3. HippoMemoryEngine 실행
            if self.enable_hippo_memory and self.hippo_memory_engine:
                sv = new_state.state_vector
                n_dim = len(sv) // 2
                x = sv[:n_dim]
                v = sv[n_dim:]
                dt = self.potential_field_config.get("dt", 0.01)

                injection, pot_changed = self.hippo_memory_engine.step(x, v, dt)

                if pot_changed and self.hippo_memory_engine.store.count > 0:
                    mwp = self.hippo_memory_engine.export_potential()
                    if mwp is not None:
                        self.current_potential_func = mwp.potential
                        self.current_field_func = mwp.field
                        self.potential_field_engine = None

                new_state.set_extension("hippo_injection", injection)
                new_state.set_extension("hippo_info", self.hippo_memory_engine.info())
            
            # 4. CerebellumEngine 실행 (선택적)
            if self.enable_cerebellum and self.cerebellum_engine:
                # CerebellumEngine은 compute_correction() 메서드를 사용
                # GlobalState에서 필요한 정보 추출
                state_vector = new_state.state_vector
                n_dim = len(state_vector) // 2
                
                # 위치와 속도 분리
                position = state_vector[:n_dim]
                velocity = state_vector[n_dim:]
                
                # 목표 상태 (extensions에서 가져오거나 기본값 사용)
                target_state = new_state.get_extension("target_state", position)
                context = new_state.get_extension("context", {})
                
                # CerebellumEngine 보정값 계산
                try:
                    correction = self.cerebellum_engine.compute_correction(
                        current_state=position,
                        target_state=target_state,
                        velocity=velocity,
                        context=context,
                        dt=self.cerebellum_dt,
                    )
                    
                    # 보정값을 상태에 반영
                    # 보정값을 속도에 추가하거나 위치에 직접 반영
                    new_position = position + correction * self.cerebellum_correction_scale
                    new_state.state_vector = np.concatenate([new_position, velocity])
                    
                    # CerebellumEngine 결과를 extensions에 저장
                    new_state.set_extension("cerebellum", {
                        "correction": correction,
                        "target_state": target_state,
                    })
                    
                    if self.logger:
                        self.logger.info("CerebellumEngine 실행 완료")
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"CerebellumEngine 실행 실패: {e}")
            
            if self.logger:
                self.logger.info("CookiieBrainEngine 업데이트 완료")
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"CookiieBrainEngine 업데이트 실패: {e}")
            # 에러 격리 모드: 엔진 실패 시에도 계속 진행 (부분 결과 반환)
            if self.error_isolation:
                if self.logger:
                    self.logger.warning(f"에러 격리 모드: 엔진 실패를 무시하고 계속 진행합니다.")
                # 부분 결과라도 반환
                return new_state
            else:
                # 기본 모드: 엔진 실패 시 전체 실패
                raise
        
        return new_state
    
    # ──────────────────────────────────────────────────────────
    #  통합 실행: 시뮬레이션 → 자동 분석
    # ──────────────────────────────────────────────────────────

    def run_and_analyze(
        self,
        state: GlobalState,
        n_steps: int = 5000,
        analyze: bool = True,
    ) -> Dict[str, Any]:
        """시뮬레이션을 돌리고 궤적을 Layer 1~6으로 자동 분석.

        이것이 CookiieBrain의 핵심 통합 흐름이다:
            WellFormation → PFE(Phase A+B+C) → 궤적 수집 → Layer 1~6 분석

        Parameters
        ----------
        state : GlobalState
            초기 상태
        n_steps : int
            시뮬레이션 스텝 수
        analyze : bool
            True면 궤적 수집 후 BrainAnalyzer 자동 실행

        Returns
        -------
        dict with keys:
            final_state : GlobalState
            positions : np.ndarray (n_steps, dim)
            velocities : np.ndarray (n_steps, dim)
            energies : np.ndarray (n_steps,)
            analysis : dict (BrainAnalyzer 결과, analyze=True일 때)
        """
        current = state
        dim = len(current.state_vector) // 2

        positions = np.zeros((n_steps, dim))
        velocities = np.zeros((n_steps, dim))
        energies = np.zeros(n_steps)
        dt = self.potential_field_config.get("dt", 0.01)

        for i in range(n_steps):
            current = self.update(current)
            sv = current.state_vector
            positions[i] = sv[:dim]
            velocities[i] = sv[dim:]
            energies[i] = current.energy

        result = {
            "final_state": current,
            "positions": positions,
            "velocities": velocities,
            "energies": energies,
            "dt": dt,
            "n_steps": n_steps,
        }

        if analyze and BRAIN_ANALYZER_AVAILABLE and self.well_registry is not None:
            mwp = self.well_registry.export_potential()
            analyzer = BrainAnalyzer(
                mwp=mwp,
                gamma=self.gamma,
                temperature=self.temperature or 1.0,
                mass=self.mass,
            )
            report = analyzer.run(positions, velocities, dt)
            result["analysis"] = report

            if self.logger:
                s = report["summary"]
                self.logger.info(
                    f"분석 완료: wells={s['n_wells']}, "
                    f"eq={s['is_equilibrium']}, "
                    f"Ṡ={s['entropy_production_rate']:.4f}"
                )

        return result

    # ──────────────────────────────────────────────────────────
    #  3계층 중력 (TidalField) 구성
    # ──────────────────────────────────────────────────────────

    def _build_tidal_field(self, cfg: Dict[str, Any]) -> "TidalField":
        """tidal_config로부터 CentralBody + OrbitalMoon + TidalField 생성.

        tidal_config 예시::

            {
                "central": {"position": [0,0], "mass": 10.0, "G": 1.0},
                "moons": [
                    {"host_center": [5,0], "semi_major_axis": 1.5,
                     "orbit_frequency": 2.0, "mass": 0.3, "eccentricity": 0.2},
                ],
            }

        central이 없으면 태양 없이 달만 운용.
        moons가 없으면 태양만 운용.
        """
        central = None
        central_cfg = cfg.get("central")
        if central_cfg is not None:
            pos = np.asarray(central_cfg.get("position", [0.0, 0.0]), dtype=float)
            central = CentralBody(
                position=pos,
                mass=central_cfg.get("mass", 10.0),
                G=central_cfg.get("G", 1.0),
                softening=central_cfg.get("softening", 1e-4),
            )

        moons = []
        for m_cfg in cfg.get("moons", []):
            hc = np.asarray(m_cfg.get("host_center", [0.0, 0.0]), dtype=float)
            moon = OrbitalMoon(
                host_center=hc,
                semi_major_axis=m_cfg.get("semi_major_axis", m_cfg.get("orbit_radius", 1.5)),
                eccentricity=m_cfg.get("eccentricity", 0.0),
                orbit_frequency=m_cfg.get("orbit_frequency", 2.0),
                mass=m_cfg.get("mass", 0.3),
                G=m_cfg.get("G", 1.0),
                softening=m_cfg.get("softening", 1e-4),
                initial_phase=m_cfg.get("initial_phase", 0.0),
                periapsis_angle=m_cfg.get("periapsis_angle", 0.0),
                spin_frequency=m_cfg.get("spin_frequency", 0.0),
                tidal_locking=m_cfg.get("tidal_locking", True),
                quadrupole_moment=m_cfg.get("quadrupole_moment", 0.0),
            )
            moons.append(moon)

        return TidalField(central=central, moons=moons)

    def _build_combined_injection(self) -> Optional[Callable]:
        """사용자 injection_func + TidalField 힘을 합성한 injection 함수 반환.

        둘 다 없으면 None.
        """
        user_inj = self.injection_func
        tidal_inj = None
        if self.enable_tidal and self.tidal_field is not None:
            tidal_inj = self.tidal_field.create_injection_func()

        if user_inj is None and tidal_inj is None:
            return None
        if user_inj is not None and tidal_inj is None:
            return user_inj
        if user_inj is None and tidal_inj is not None:
            return tidal_inj

        def combined(x: np.ndarray, v: np.ndarray, t: float) -> np.ndarray:
            return user_inj(x, v, t) + tidal_inj(x, v, t)
        return combined

    # ──────────────────────────────────────────────────────────
    #  WellFormation
    # ──────────────────────────────────────────────────────────

    def _run_well_formation(self, state: GlobalState) -> Optional[WellFormationResult]:
        """WellFormationEngine 실행
        
        Args:
            state: 현재 상태
            
        Returns:
            WellFormationResult 또는 None
        """
        if not self.well_formation_engine:
            if self.logger:
                self.logger.warning("WellFormationEngine이 초기화되지 않았습니다.")
            return None
        
        # state에서 episodes 추출
        episodes_data = state.get_extension("episodes", [])
        if not episodes_data:
            if self.logger:
                self.logger.warning("episodes가 없어 WellFormationEngine을 실행할 수 없습니다.")
            return None
        
        # episodes 데이터를 Episode 객체로 변환
        # episodes_data가 이미 Episode 객체 리스트인 경우 그대로 사용
        # 그렇지 않은 경우 변환 필요
        episodes = []
        for idx, ep_data in enumerate(episodes_data):
            if isinstance(ep_data, Episode):
                episodes.append(ep_data)
            elif isinstance(ep_data, dict):
                # 딕셔너리에서 Episode 객체 생성
                try:
                    episode = Episode(
                        pre_activity=ep_data.get("pre_activity", []),
                        post_activity=ep_data.get("post_activity", []),
                        timestamp=ep_data.get("timestamp", float(idx)),
                        episode_id=ep_data.get("episode_id", idx),
                        context=ep_data.get("context", {}),
                    )
                    episodes.append(episode)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Episode 변환 실패: {e}")
                    continue
            else:
                if self.logger:
                    self.logger.warning(f"알 수 없는 episodes 데이터 형식: {type(ep_data)}")
                continue
        
        if not episodes:
            if self.logger:
                self.logger.warning("유효한 episodes가 없습니다.")
            return None
        
        # WellFormationEngine 실행
        if self.logger:
            self.logger.info(f"WellFormationEngine 실행 중... (episodes: {len(episodes)})")
        
        try:
            well_result = self.well_formation_engine.generate_well(episodes)
            if self.logger:
                self.logger.info("WellFormationEngine 실행 완료")
            return well_result
        except Exception as e:
            if self.logger:
                self.logger.error(f"WellFormationEngine 실행 실패: {e}")
            raise
    
    def get_energy(self, state: GlobalState) -> float:
        """에너지 반환
        
        Args:
            state: 현재 상태
            
        Returns:
            에너지 값
        """
        # PotentialFieldEngine의 에너지 반환
        if self.potential_field_engine:
            return self.potential_field_engine.get_energy(state)
        return state.energy
    
    def get_state(self) -> Dict[str, Any]:
        """엔진 내부 상태 반환
        
        Returns:
            엔진 내부 상태 딕셔너리
        """
        state_dict = {
            "enable_well_formation": self.enable_well_formation,
            "enable_potential_field": self.enable_potential_field,
            "enable_hippo_memory": self.enable_hippo_memory,
            "enable_tidal": self.enable_tidal,
            "enable_cerebellum": self.enable_cerebellum,
            "current_well_result": self.current_well_result is not None,
            "current_potential_func": self.current_potential_func is not None,
            "current_field_func": self.current_field_func is not None,
        }
        if self.well_registry is not None:
            state_dict["well_registry"] = self.well_registry.info()
        if self.tidal_field is not None:
            state_dict["tidal"] = self.tidal_field.info()
        return state_dict
    
    def reset(self):
        """엔진 상태 리셋"""
        self.current_well_result = None
        self.current_potential_func = None
        self.current_field_func = None
        self.potential_field_engine = None
        if self.well_registry is not None:
            self.well_registry.clear()
            self._registry_version = 0
        
        if self.logger:
            self.logger.info("CookiieBrainEngine 리셋 완료")

