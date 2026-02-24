"""Moon/Satellite Gravity Field

고정된 외부 중력원(달/위성)을 생성하여 기본 퍼텐셜 필드에 합성합니다.

현재 상태:
- 달의 위치는 고정 (공전 미구현, Phase B 영역)
- 공전이 되려면 달의 위치가 매 스텝 GlobalState로 업데이트되어야 함

수식:
    G_moon(x) = -G * M_moon * (x - x_moon) / ||x - x_moon||^3

합성:
    g(x) = -∇V(x) + R(x) + G_moon(x)

주의 — rotational_func 시그니처:
    create_field_with_moon의 rotational_func는 위치 의존형 R(x)만 받음.
    코리올리형 R(x,v)=ωJv 는 PotentialFieldEngine 내부(omega_coriolis)에서
    Strang splitting으로 처리되므로 여기서 합성하지 않음.

Author: GNJz (Qquarts)
Version: 0.2.0
"""

import numpy as np
from typing import Callable, Optional
from dataclasses import dataclass


@dataclass
class Moon:
    """고정된 외부 중력원 (달/위성)

    현재는 위치가 고정됨 (공전은 Phase B에서 구현 예정).
    공전 구현 시 position을 매 스텝 갱신하거나,
    Moon을 GlobalState의 extension으로 관리해야 함.

    Attributes:
        position: 달 위치 (고정)
        mass: 달의 질량
        G: 중력 상수
        softening: 수치 안정성용 (r=0 근처 발산 방지)
    """
    position: np.ndarray
    mass: float = 1.0
    G: float = 1.0
    softening: float = 1e-6

    def __post_init__(self):
        self.position = np.array(self.position)
        if self.mass <= 0:
            raise ValueError("Moon mass must be positive")
        if self.G <= 0:
            raise ValueError("Gravity constant must be positive")


def create_moon_gravity_field(moon: Moon) -> Callable[[np.ndarray], np.ndarray]:
    """달의 중력장 생성

    수식:
        G_moon(x) = -G * M_moon * (x - x_moon) / (||x - x_moon|| + ε)^3

    softening은 ||r|| + ε 방식 (Plummer softening과 다름).
    r → 0 근처 발산을 막되, 먼 거리에서는 역제곱 법칙 유지.

    Args:
        moon: 달 객체

    Returns:
        G_moon(x) -> np.ndarray (위치 의존 중력 벡터)
    """
    def G_moon(x: np.ndarray) -> np.ndarray:
        x = np.array(x)
        r = x - moon.position
        r_norm = np.linalg.norm(r) + moon.softening
        return -moon.G * moon.mass * r / (r_norm ** 3)

    return G_moon


def create_field_with_moon(
    gradient_func: Callable[[np.ndarray], np.ndarray],
    rotational_func: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    moon_gravity_func: Optional[Callable[[np.ndarray], np.ndarray]] = None
) -> Callable[[np.ndarray], np.ndarray]:
    """위치 의존 필드 합성: gradient + rotation(pole형) + moon

    수식:
        g(x) = -∇V(x) + R(x) + G_moon(x)

    주의:
        rotational_func는 R(x) 시그니처만 호환.
        코리올리형 R(x,v)=ωJv 는 여기가 아니라 PotentialFieldEngine 내부
        (omega_coriolis + Strang splitting)에서 처리됨.

    Args:
        gradient_func: -∇V(x) -> np.ndarray
        rotational_func: R(x) -> np.ndarray (pole형만, 선택적)
        moon_gravity_func: G_moon(x) -> np.ndarray (선택적)

    Returns:
        합성 필드 g(x) -> np.ndarray
    """
    def combined_field(x: np.ndarray) -> np.ndarray:
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
    """달 추가 전후 필드 변화 분석

    Args:
        field_without_moon: 달 없는 필드
        field_with_moon: 달 포함 필드
        test_points: 비교할 위치 리스트

    Returns:
        {"field_difference": [...], "max_difference": float, "avg_difference": float}
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
