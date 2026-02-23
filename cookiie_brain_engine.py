"""Cookiie Brain 통합 엔진

모든 개별 엔진들을 연결하는 통합 시스템.

핵심 기능:
- 개별 엔진 초기화 및 연결
- 엔진 간 데이터 흐름 자동 관리
- 상태 자동 동기화
- 전체 시스템으로 작동

통합 엔진:
1. WellFormationEngine → W, b 생성 (Hopfield 에너지)
2. PotentialFieldEngine → 에너지 지형 → 퍼텐셜 필드 변환
3. HippoMemoryEngine → 장기 기억 시스템
4. CerebellumEngine → 운동 조율 및 학습
5. 기타 엔진들...

Author: GNJz (Qquarts)
Version: 0.2.0
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
    from Phase_A import Pole, create_rotational_field
    PHASE_A_AVAILABLE = True
except ImportError:
    PHASE_A_AVAILABLE = False
    Pole = None
    create_rotational_field = None

# Phase_B (Multi-well potential, Gaussian bridge) import
try:
    from Phase_B.well_to_gaussian import WellRegistry, WellToGaussianConfig
    PHASE_B_AVAILABLE = True
except ImportError:
    PHASE_B_AVAILABLE = False
    WellRegistry = None
    WellToGaussianConfig = None

# HippoMemoryEngine import (선택적)
try:
    # 메인 폴더 기준: CookiieBrain/ -> Archive/Integrated/4.Hippo_Memory_Engine/
    hippo_path = Path(__file__).parent.parent / "Archive" / "Integrated" / "4.Hippo_Memory_Engine"
    sys.path.insert(0, str(hippo_path))
    # HippoMemoryEngine의 실제 import 경로는 구조에 따라 조정 필요
    HIPPO_MEMORY_AVAILABLE = False  # 일단 False로 설정, 나중에 구현
except ImportError:
    HIPPO_MEMORY_AVAILABLE = False

__version__ = "0.2.0"


class CookiieBrainEngine(SelfOrganizingEngine):
    """Cookiie Brain 통합 엔진
    
    엔진 오케스트레이션 레이어: 개별 엔진들을 연결하는 통합 시스템.
    
    엔진 연결 순서:
    1. WellFormationEngine → W, b 생성 (Hopfield 에너지)
    2. PotentialFieldEngine → 퍼텐셜 필드 변환
    3. HippoMemoryEngine → 장기 기억 시스템 (선택적)
    4. CerebellumEngine → 운동 조율 및 학습 (선택적)
    
    설계 원칙:
    - 불변성 유지: state를 직접 수정하지 않고 copy-and-return (deep=True)
    - 엔진 간 자동 연결: 데이터 흐름 자동 관리
    - 상태 자동 동기화: GlobalState가 전체 시스템에서 공유
    - 모듈화: 각 엔진은 독립적으로 작동 가능
    - Well 변경 감지: Well 결과 변경 시 potential 함수 및 엔진 재생성
    - 에러 격리: error_isolation=True 시 엔진 실패해도 계속 진행
    """
    
    def __init__(
        self,
        enable_well_formation: bool = True,
        enable_potential_field: bool = True,
        enable_hippo_memory: bool = False,
        enable_cerebellum: bool = False,
        well_formation_config: Optional[Dict[str, Any]] = None,
        potential_field_config: Optional[Dict[str, Any]] = None,
        cerebellum_config: Optional[Dict[str, Any]] = None,
        well_to_gaussian_config: Optional[Dict[str, Any]] = None,
        error_isolation: bool = False,
        enable_logging: bool = True,
    ):
        """CookiieBrainEngine 초기화
        
        Args:
            enable_well_formation: WellFormationEngine 활성화 여부
            enable_potential_field: PotentialFieldEngine 활성화 여부
            enable_hippo_memory: HippoMemoryEngine 활성화 여부 (선택적)
            enable_cerebellum: CerebellumEngine 활성화 여부 (선택적)
            well_formation_config: WellFormationEngine 설정 (None이면 {}로 처리)
            potential_field_config: PotentialFieldEngine 설정 (enable_phase_a, phase_a_pole_position 등)
            cerebellum_config: CerebellumEngine 설정 (None이면 기본값 사용)
            well_to_gaussian_config: WellToGaussianConfig 설정 (Phase B 브릿지)
                - center_mode: "pattern" | "solve"
                - min_wells_for_orbit: int (기본 3)
                - dedup_distance: float (기본 0.5)
            error_isolation: True면 엔진 실패 시 격리하고 계속 진행, False면 전체 실패
            enable_logging: 로깅 활성화 여부
        """
        self.enable_well_formation = enable_well_formation
        self.enable_potential_field = enable_potential_field
        self.enable_hippo_memory = enable_hippo_memory
        self.enable_cerebellum = enable_cerebellum
        self.error_isolation = error_isolation
        
        if enable_potential_field and not POTENTIAL_FIELD_AVAILABLE:
            raise ImportError(
                "PotentialFieldEngine을 import할 수 없습니다. "
                "PotentialFieldEngine을 설치하거나 PYTHONPATH에 추가하세요."
            )

        # PotentialFieldEngine / Phase A 설정 저장
        self.potential_field_config = potential_field_config or {}
        self.enable_phase_a = self.potential_field_config.get("enable_phase_a", False)
        self.phase_a_mode = self.potential_field_config.get("phase_a_mode", "minimal")  # "minimal" | "pole"
        self.phase_a_omega = self.potential_field_config.get("phase_a_omega", 1.0)
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
                # WellFormationEngine 초기화 (설정은 well_formation_config에서 가져옴)
                config = well_formation_config or {}
                self.well_formation_engine = WellFormationEngine(
                    hebbian_config=config.get("hebbian_config"),
                    stability_constraints=config.get("stability_constraints"),
                    bias_config=config.get("bias_config"),
                )
                if self.logger:
                    self.logger.info("WellFormationEngine 초기화 완료")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"WellFormationEngine 초기화 실패: {e}")
                raise
        
        # PotentialFieldEngine은 WellFormationEngine 결과를 받아서 초기화
        # 따라서 여기서는 초기화하지 않고, update()에서 동적으로 생성
        
        # CerebellumEngine 초기화
        if enable_cerebellum:
            if not CEREBELLUM_AVAILABLE:
                if self.logger:
                    self.logger.warning("CerebellumEngine을 import할 수 없습니다. CerebellumEngine을 비활성화합니다.")
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
        
        # HippoMemoryEngine 초기화 (선택적, 나중에 구현)
        if enable_hippo_memory:
            if not HIPPO_MEMORY_AVAILABLE:
                if self.logger:
                    self.logger.warning("HippoMemoryEngine을 import할 수 없습니다. HippoMemoryEngine을 비활성화합니다.")
                self.enable_hippo_memory = False
            else:
                # TODO: HippoMemoryEngine 초기화 구현
                if self.logger:
                    self.logger.info("HippoMemoryEngine 초기화 (구현 예정)")
        
        # Phase B 브릿지: WellRegistry (우물 누적 저장소)
        self.well_registry = None
        self._registry_version: int = 0
        if PHASE_B_AVAILABLE:
            wtg_cfg = WellToGaussianConfig(**(well_to_gaussian_config or {}))
            self.well_registry = WellRegistry(config=wtg_cfg)
        
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
                            # Gaussian 모드: 다중 우물 퍼텐셜
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
                            # Hopfield 모드: 단일 우물
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
                # PotentialFieldEngine 생성/재생성 (Well 변경 시 재생성됨)
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
                    self.potential_field_engine = PotentialFieldEngine(
                        potential_func=self.current_potential_func,
                        field_func=self.current_field_func,
                        rotational_func=rotational_func,
                        omega_coriolis=omega_coriolis,
                    )
                
                # PotentialFieldEngine 업데이트
                new_state = self.potential_field_engine.update(new_state)
            
            # 3. HippoMemoryEngine 실행 (선택적)
            if self.enable_hippo_memory and self.hippo_memory_engine:
                # TODO: HippoMemoryEngine 통합 구현
                if self.logger:
                    self.logger.info("HippoMemoryEngine 실행 (구현 예정)")
                # new_state = self.hippo_memory_engine.update(new_state)
            
            # 4. CerebellumEngine 실행 (선택적)
            if self.enable_cerebellum and self.cerebellum_engine:
                state_vector = new_state.state_vector
                if len(state_vector) % 2 != 0:
                    raise ValueError(
                        f"state_vector must have even length for Cerebellum "
                        f"(got {len(state_vector)}). "
                        f"Expected format: [x1,...,xN, v1,...,vN]"
                    )
                n_dim = len(state_vector) // 2
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
            "enable_cerebellum": self.enable_cerebellum,
            "current_well_result": self.current_well_result is not None,
            "current_potential_func": self.current_potential_func is not None,
            "current_field_func": self.current_field_func is not None,
        }
        if self.well_registry is not None:
            state_dict["well_registry"] = self.well_registry.info()
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

