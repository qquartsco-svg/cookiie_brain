"""Rotational Field Generator

Phase A: 위상 생성 (Rotational Field)

회전 성분을 생성하여 순환 운동(자전)을 가능하게 만듭니다.

수식:
- 최소 형태 (코리올리형, 에너지 보존):
    R(x, v) = ω J v
    v · R = v · (ωJv) = ω(v'Jv) = 0  (J 반대칭 → 항상 0 → 에너지 보존)

- Pole 기반 형태 (위치 의존, 에너지 비보존):
    R(x) = ω J (x - x_pole)
    v · R(x) ≠ 0 일반적 → 에너지 비보존

- Combined field: a = -∇V(x) + R

왜 R(x)=ωJx가 아닌 R(v)=ωJv 인가:
    에너지 보존 조건: 힘이 속도에 수직 (v·F=0).
    R(x)=ωJx → x·R(x)=0 (위치에 직교) 이지만 v·R(x)≠0 (속도에 직교 아님).
    R(v)=ωJv → v·R(v)=0 (속도에 직교, 항상) → 에너지 보존 보장.

Author: GNJz (Qquarts)
Version: 0.2.0
"""

import numpy as np
from typing import Callable, Optional, Union
from dataclasses import dataclass


def create_skew_symmetric_matrix(n: int, axis: list = [0, 1]) -> np.ndarray:
    """반대칭(skew-symmetric) 행렬 생성

    수식:
        J = [0  -1]  (2D)
            [1   0]

    n차원에서는 지정된 축에 대해 반대칭 행렬 생성

    Args:
        n: 차원
        axis: 회전 축 (기본값: [0, 1] = xy 평면)

    Returns:
        반대칭 행렬 J (n×n)
    """
    J = np.zeros((n, n))
    if len(axis) == 2:
        i, j = axis[0], axis[1]
        J[i, j] = -1
        J[j, i] = 1
    return J


@dataclass
class Pole:
    """회전의 중심점 (폴)

    Attributes:
        position: 폴 위치 (회전 중심)
        rotation_direction: 회전 방향 (+1: 반시계, -1: 시계)
        strength: 회전 강도 (ω)
    """
    position: np.ndarray
    rotation_direction: int = 1  # +1: 반시계, -1: 시계
    strength: float = 1.0  # ω (회전 세기)

    def __post_init__(self):
        self.position = np.array(self.position)
        if self.rotation_direction not in [1, -1]:
            raise ValueError("rotation_direction must be +1 or -1")


def create_minimal_rotational_field(
    omega: float = 1.0,
    n_dim: int = 2,
    axis: list = [0, 1],
) -> Callable:
    """최소 회전 성분 — 코리올리형 (Phase A 자전, 에너지 보존)

    수식:
        R(x, v) = ω J v

    에너지 보존 증명:
        P = v · R = v · (ωJv) = ω(v'Jv) = 0
        J 반대칭 → v'Jv = 0 항상 성립 → 회전항이 일을 하지 않음.

    Args:
        omega: 회전 각속도 (양수=반시계, 음수=시계)
        n_dim: 공간 차원
        axis: 회전 평면 축 (기본값: [0,1] = xy)

    Returns:
        R(x, v) -> np.ndarray  (시그니처: 두 인자, v 사용)
    """
    J = create_skew_symmetric_matrix(n_dim, axis=axis)

    def R(x: np.ndarray, v: np.ndarray) -> np.ndarray:
        v = np.asarray(v, dtype=float)
        if len(v) < 2:
            raise ValueError("Rotational field requires at least 2D space")
        return omega * (J @ v)

    return R


def create_rotational_field(
    pole: Pole,
    epsilon: float = 1e-6,
    use_simple_form: bool = True
) -> Callable[[np.ndarray], np.ndarray]:
    """Pole 기반 회전 성분 생성 함수 (curl ≠ 0, 에너지 비보존)

    주의: 이 함수는 위치 의존 회전 R(x) = ωJ(x-pole) 을 생성.
    v·R(x) ≠ 0 이므로 에너지가 보존되지 않음.
    에너지 보존이 필요하면 create_minimal_rotational_field (코리올리형) 사용.

    Args:
        pole: 회전 중심점 (폴)
        epsilon: 수치 안정성을 위한 작은 값
        use_simple_form: True면 단순 형태, False면 거리 의존 형태

    Returns:
        Rotational field 함수 R(x) -> np.ndarray
    """
    if use_simple_form:
        def R(x: np.ndarray) -> np.ndarray:
            """R = ω J (x - x_pole)"""
            x = np.asarray(x, dtype=float)
            r = x - pole.position
            n = len(r)
            if n < 2:
                raise ValueError("Rotational field requires at least 2D space")
            J = create_skew_symmetric_matrix(n, axis=[0, 1])
            return pole.rotation_direction * pole.strength * (J @ r)
        return R
    else:
        def R(x: np.ndarray) -> np.ndarray:
            """R = ω [-r_y, r_x] / (||r||² + ε)"""
            x = np.asarray(x, dtype=float)
            r = x - pole.position
            if len(r) < 2:
                raise ValueError("Rotational field requires at least 2D space")
            r_norm_sq = np.dot(r, r) + epsilon
            if len(r) == 2:
                R_vec = np.array([-r[1], r[0]])
            else:
                R_vec = np.zeros_like(r)
                R_vec[0] = -r[1]
                R_vec[1] = r[0]
            return pole.rotation_direction * pole.strength * R_vec / r_norm_sq
        return R


def create_combined_field(
    gradient_func: Callable[[np.ndarray], np.ndarray],
    rotational_func: Optional[Callable[[np.ndarray], np.ndarray]] = None
) -> Callable[[np.ndarray], np.ndarray]:
    """Gradient + Rotational 합성 필드

    수식:
        g(x) = -∇E(x) + R(x)

    Args:
        gradient_func: Gradient field 함수 (-∇E)
        rotational_func: Rotational field 함수 (R), 선택적

    Returns:
        합성 필드 함수 g(x) -> np.ndarray
    """
    def combined_field(x: np.ndarray) -> np.ndarray:
        gradient = gradient_func(x)
        if rotational_func is not None:
            rotational = rotational_func(x)
            if len(gradient) != len(rotational):
                raise ValueError("Gradient and rotational fields must have same dimension")
            return gradient + rotational
        return gradient
    return combined_field


def compute_curl_2d(
    field_func: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    epsilon: float = 1e-6
) -> float:
    """2D 필드의 curl 계산

    수식:
        curl = ∂F_y/∂x - ∂F_x/∂y

    Args:
        field_func: 필드 함수
        x: 계산 위치
        epsilon: 수치 미분용 작은 값

    Returns:
        curl 값 (스칼라, 2D)
    """
    x = np.array(x)
    if len(x) != 2:
        raise ValueError("compute_curl_2d requires 2D space")

    F = field_func(x)

    x_plus = x.copy()
    x_plus[0] += epsilon
    F_plus_x = field_func(x_plus)
    dFy_dx = (F_plus_x[1] - F[1]) / epsilon

    y_plus = x.copy()
    y_plus[1] += epsilon
    F_plus_y = field_func(y_plus)
    dFx_dy = (F_plus_y[0] - F[0]) / epsilon

    curl = dFy_dx - dFx_dy
    return curl


def verify_rotational_component(
    field_func: Callable[[np.ndarray], np.ndarray],
    test_points: list,
    threshold: float = 1e-3
) -> bool:
    """Rotational component 존재 확인

    curl ≠ 0인지 확인하여 회전 성분이 있는지 검증

    Args:
        field_func: 필드 함수
        test_points: 테스트할 점들의 리스트
        threshold: curl이 0이 아닌 것으로 판단하는 임계값

    Returns:
        회전 성분이 있으면 True
    """
    for point in test_points:
        curl = compute_curl_2d(field_func, point)
        if abs(curl) > threshold:
            return True
    return False
