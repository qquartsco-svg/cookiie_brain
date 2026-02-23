"""Moon/Satellite Gravity Field

달/위성의 중력장을 생성합니다.

물리적 의미:
- 달은 자전을 안정화/조절하는 역할
- 자전 자체를 만드는 필수 요소는 아님
- 하지만 자전을 더 안정적으로 만듦

수식:
- 중력장: G_moon(x) = -G * M_moon * (x - x_moon) / ||x - x_moon||^3
- 합성 필드: g(x) = -∇E(x) + R(x) + G_moon(x)

Author: GNJz (Qquarts)
Version: 0.1.4
"""

import numpy as np
from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class Moon:
    """달/위성 객체
    
    Attributes:
        position: 달 위치
        mass: 달의 질량
        G: 중력 상수
        softening: 수치 안정성을 위한 작은 값
    """
    position: np.ndarray
    mass: float = 1.0
    G: float = 1.0
    softening: float = 1e-6
    
    def __post_init__(self):
        """초기화 후 검증"""
        self.position = np.array(self.position)
        if self.mass <= 0:
            raise ValueError("Moon mass must be positive")
        if self.G <= 0:
            raise ValueError("Gravity constant must be positive")


def create_moon_gravity_field(moon: Moon) -> Callable[[np.ndarray], np.ndarray]:
    """달의 중력장 생성 함수
    
    수식:
        G_moon(x) = -G * M_moon * (x - x_moon) / ||x - x_moon||^3
    
    Args:
        moon: 달 객체
    
    Returns:
        달의 중력장 함수 G_moon(x) -> np.ndarray
    """
    def G_moon(x: np.ndarray) -> np.ndarray:
        """달의 중력장 계산"""
        x = np.array(x)
        r = x - moon.position
        
        # 거리 계산 (수치 안정성)
        r_norm = np.linalg.norm(r) + moon.softening
        
        # 중력장 계산
        return -moon.G * moon.mass * r / (r_norm**3)
    
    return G_moon


def create_field_with_moon(
    gradient_func: Callable[[np.ndarray], np.ndarray],
    rotational_func: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    moon_gravity_func: Optional[Callable[[np.ndarray], np.ndarray]] = None
) -> Callable[[np.ndarray], np.ndarray]:
    """Gradient + Rotational + Moon 합성 필드
    
    수식:
        g(x) = -∇E(x) + R(x) + G_moon(x)
    
    Args:
        gradient_func: Gradient field 함수 (-∇E)
        rotational_func: Rotational field 함수 (R), 선택적
        moon_gravity_func: 달의 중력장 함수 (G_moon), 선택적
    
    Returns:
        합성 필드 함수 g(x) -> np.ndarray
    """
    def combined_field(x: np.ndarray) -> np.ndarray:
        """합성 필드 계산"""
        field = gradient_func(x)
        
        if rotational_func is not None:
            rotational = rotational_func(x)
            if len(field) != len(rotational):
                raise ValueError("Field dimensions must match")
            field = field + rotational
        
        if moon_gravity_func is not None:
            moon_gravity = moon_gravity_func(x)
            if len(field) != len(moon_gravity):
                raise ValueError("Field dimensions must match")
            field = field + moon_gravity
        
        return field
    
    return combined_field


def analyze_moon_effect(
    field_without_moon: Callable[[np.ndarray], np.ndarray],
    field_with_moon: Callable[[np.ndarray], np.ndarray],
    test_points: list
) -> dict:
    """달의 효과 분석
    
    달이 추가되었을 때 필드의 변화를 분석
    
    Args:
        field_without_moon: 달 없이 필드
        field_with_moon: 달 포함 필드
        test_points: 테스트할 점들의 리스트
    
    Returns:
        분석 결과 딕셔너리
    """
    results = {
        "field_difference": [],
        "max_difference": 0.0,
        "avg_difference": 0.0,
    }
    
    differences = []
    for point in test_points:
        field_wo = field_without_moon(point)
        field_w = field_with_moon(point)
        diff = np.linalg.norm(field_w - field_wo)
        differences.append(diff)
        results["field_difference"].append({
            "point": point.tolist(),
            "difference": float(diff)
        })
    
    if differences:
        results["max_difference"] = float(max(differences))
        results["avg_difference"] = float(np.mean(differences))
    
    return results


