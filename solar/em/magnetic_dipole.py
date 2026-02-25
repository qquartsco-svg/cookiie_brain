"""Magnetic Dipole — 행성 자기쌍극자장
======================================

자전축(spin_axis)과 연동되는 자기쌍극자 필드.
core/의 Body3D 상태를 읽어서 공간상의 B(x,t)를 계산한다.

물리:
  자기 쌍극자 모멘트 벡터:
    m̂ = R(α_tilt) · ŝ  (자전축에서 자기축으로 기울기 적용)

  쌍극자 필드 (SI 단위 정규화 후 무차원):
    B(r) = (μ₀/4π) · [3(m̂·r̂)r̂ − m̂] / r³

  지구 참값:
    - 자기 모멘트: 7.94 × 10²² A·m²
    - 자기축 기울기: 자전축에서 약 11.5° 기울어짐
    - 적도 표면 자기장: ~31 μT (0.31 Gauss)
    - 극 표면 자기장: ~62 μT (0.62 Gauss)

  이 모듈의 단위계:
    거리: AU,  자기장: B₀ 단위 (표면 적도 자기장 = 1.0)
    → 실제 환산: B_real = B * B_surface_equator

의존: numpy + solar.core.Body3D (읽기 전용)
이 모듈은 core/를 수정하지 않는다. 관측자 레이어.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class DipoleFieldPoint:
    """특정 위치에서의 자기장 관측값."""
    position: np.ndarray        # 관측 위치 [AU]
    B_vector: np.ndarray        # 자기장 벡터 [B₀ 단위]
    B_magnitude: float          # |B| [B₀ 단위]
    r_from_center: float        # 행성 중심에서의 거리 [AU]
    latitude_deg: float         # 자기 위도 [°]
    L_shell: float              # L-shell 파라미터 (r/R_eq / cos²λ)


class MagneticDipole:
    """행성 자기쌍극자장.

    자전축(spin_axis)에서 자기축(magnetic axis)을 유도하고,
    공간 임의 지점에서 쌍극자 자기장 B(x)를 계산한다.

    Parameters
    ----------
    body_name : str
        추적할 천체 이름 (EvolutionEngine에서 find()로 검색).
    magnetic_moment : float
        무차원 자기 모멘트 크기. 기본값 1.0 (정규화).
        실제 스케일이 필요하면 B₀ 단위로 환산.
    tilt_deg : float
        자전축 대비 자기축 기울기 [°]. 지구 = 11.5°.
    tilt_azimuth_deg : float
        자기축 기울기의 방위각 [°]. 자전축 주위 회전 위상.
    """

    def __init__(
        self,
        body_name: str = "Earth",
        magnetic_moment: float = 1.0,
        tilt_deg: float = 11.5,
        tilt_azimuth_deg: float = 0.0,
    ):
        self.body_name = body_name
        self.magnetic_moment = magnetic_moment
        self.tilt_deg = tilt_deg
        self.tilt_azimuth_deg = tilt_azimuth_deg

        self._tilt_rad = np.radians(tilt_deg)
        self._tilt_az_rad = np.radians(tilt_azimuth_deg)

    def magnetic_axis(self, spin_axis: np.ndarray) -> np.ndarray:
        """자전축 → 자기축 변환.

        자전축(ŝ)에서 tilt_deg만큼 기울어진 자기축(m̂)을 계산.
        tilt_azimuth_deg는 ŝ 주위 회전 위상.

        Parameters
        ----------
        spin_axis : ndarray, shape (3,)
            자전축 단위 벡터.

        Returns
        -------
        ndarray, shape (3,)
            자기축 단위 벡터.
        """
        s = spin_axis / (np.linalg.norm(spin_axis) + 1e-30)

        if abs(self._tilt_rad) < 1e-10:
            return s.copy()

        if abs(s[2]) < 0.999:
            perp1 = np.cross(s, np.array([0.0, 0.0, 1.0]))
        else:
            perp1 = np.cross(s, np.array([1.0, 0.0, 0.0]))
        perp1 /= np.linalg.norm(perp1) + 1e-30

        perp2 = np.cross(s, perp1)
        perp2 /= np.linalg.norm(perp2) + 1e-30

        cos_t = np.cos(self._tilt_rad)
        sin_t = np.sin(self._tilt_rad)
        cos_az = np.cos(self._tilt_az_rad)
        sin_az = np.sin(self._tilt_az_rad)

        m_hat = cos_t * s + sin_t * (cos_az * perp1 + sin_az * perp2)
        m_hat /= np.linalg.norm(m_hat) + 1e-30

        return m_hat

    def B_field(
        self,
        position: np.ndarray,
        body_pos: np.ndarray,
        spin_axis: np.ndarray,
        body_radius: float,
    ) -> np.ndarray:
        """공간 임의 지점에서의 쌍극자 자기장 벡터.

        B(r) = B₀ · (R/r)³ · [3(m̂·r̂)r̂ − m̂]

        Parameters
        ----------
        position : ndarray, shape (3,)
            관측 지점 [AU].
        body_pos : ndarray, shape (3,)
            행성 중심 위치 [AU].
        spin_axis : ndarray, shape (3,)
            자전축 단위 벡터.
        body_radius : float
            행성 적도 반지름 [AU].

        Returns
        -------
        ndarray, shape (3,)
            자기장 벡터 [B₀ 단위]. B₀ = 표면 적도 자기장.
        """
        r_vec = position - body_pos
        r = np.linalg.norm(r_vec)

        if r < 1e-30 or body_radius < 1e-30:
            return np.zeros(3)

        r_hat = r_vec / r
        m_hat = self.magnetic_axis(spin_axis)

        r_norm = r / body_radius
        scale = self.magnetic_moment / (r_norm ** 3)

        m_dot_r = np.dot(m_hat, r_hat)
        B = scale * (3.0 * m_dot_r * r_hat - m_hat)

        return B

    def field_at(
        self,
        position: np.ndarray,
        body_pos: np.ndarray,
        spin_axis: np.ndarray,
        body_radius: float,
    ) -> DipoleFieldPoint:
        """관측 지점에서의 자기장 + 메타데이터.

        Parameters
        ----------
        position, body_pos, spin_axis, body_radius :
            B_field()와 동일.

        Returns
        -------
        DipoleFieldPoint
        """
        B = self.B_field(position, body_pos, spin_axis, body_radius)
        B_mag = np.linalg.norm(B)

        r_vec = position - body_pos
        r = np.linalg.norm(r_vec)

        m_hat = self.magnetic_axis(spin_axis)
        if r > 1e-30:
            r_hat = r_vec / r
            sin_lat = np.dot(r_hat, m_hat)
            sin_lat = np.clip(sin_lat, -1.0, 1.0)
            lat_deg = np.degrees(np.arcsin(sin_lat))
        else:
            lat_deg = 0.0
            sin_lat = 0.0

        cos_lat = np.cos(np.arcsin(sin_lat))
        if body_radius > 1e-30 and cos_lat > 1e-10:
            L_shell = (r / body_radius) / (cos_lat ** 2)
        else:
            L_shell = 0.0

        return DipoleFieldPoint(
            position=position.copy(),
            B_vector=B,
            B_magnitude=B_mag,
            r_from_center=r,
            latitude_deg=lat_deg,
            L_shell=L_shell,
        )

    def surface_field_strength(self, latitude_deg: float) -> float:
        """표면 자기장 세기 (위도 함수).

        |B(λ)| = B₀ · √(1 + 3sin²λ)

        Parameters
        ----------
        latitude_deg : float
            자기 위도 [°].

        Returns
        -------
        float
            자기장 세기 [B₀ 단위].
        """
        sin_lat = np.sin(np.radians(latitude_deg))
        return self.magnetic_moment * np.sqrt(1.0 + 3.0 * sin_lat ** 2)

    def field_line_r(
        self, L: float, latitude_deg: float,
    ) -> float:
        """자기력선 반지름 (L-shell 파라미터).

        r(λ) = L · R_eq · cos²λ

        Parameters
        ----------
        L : float
            L-shell 값 (적도에서의 반지름/R_eq).
        latitude_deg : float
            자기 위도 [°].

        Returns
        -------
        float
            자기력선 위의 반지름 [R_eq 단위].
        """
        cos_lat = np.cos(np.radians(latitude_deg))
        return L * cos_lat ** 2

    def subsolar_standoff(
        self,
        body_radius: float,
        solar_wind_pressure: float,
        mu0_over_4pi: float = 1.0,
    ) -> float:
        """마그네토포즈 하부태양점 거리 (Chapman-Ferraro).

        r_mp = R_eq · (B₀² / (2μ₀ · P_sw))^(1/6)

        이 메서드는 Phase 4(자기권)의 사전 인터페이스.
        현재는 추정값만 반환.

        Parameters
        ----------
        body_radius : float
            행성 적도 반지름 [AU].
        solar_wind_pressure : float
            태양풍 동압 [정규화 단위].
        mu0_over_4pi : float
            자기 상수 (정규화).

        Returns
        -------
        float
            마그네토포즈 거리 [AU].
        """
        if solar_wind_pressure < 1e-30:
            return float('inf')

        B0_sq = self.magnetic_moment ** 2
        ratio = B0_sq / (2.0 * mu0_over_4pi * solar_wind_pressure)
        r_mp = body_radius * (ratio ** (1.0 / 6.0))
        return r_mp

    def sample_field_grid(
        self,
        body_pos: np.ndarray,
        spin_axis: np.ndarray,
        body_radius: float,
        n_r: int = 20,
        n_theta: int = 36,
        r_min_mult: float = 1.0,
        r_max_mult: float = 10.0,
    ) -> dict:
        """2D 단면(자기적도면)의 B필드 그리드 샘플링.

        Parameters
        ----------
        body_pos, spin_axis, body_radius : 행성 상태.
        n_r, n_theta : 방사/각도 해상도.
        r_min_mult, r_max_mult : 반지름 범위 (R_eq 배수).

        Returns
        -------
        dict with keys:
            'r_grid', 'theta_grid' : ndarray (n_r, n_theta)
            'Br', 'Btheta', 'Bmag' : ndarray (n_r, n_theta)
        """
        m_hat = self.magnetic_axis(spin_axis)

        if abs(m_hat[2]) < 0.999:
            eq1 = np.cross(m_hat, np.array([0.0, 0.0, 1.0]))
        else:
            eq1 = np.cross(m_hat, np.array([1.0, 0.0, 0.0]))
        eq1 /= np.linalg.norm(eq1) + 1e-30
        eq2 = np.cross(m_hat, eq1)
        eq2 /= np.linalg.norm(eq2) + 1e-30

        r_vals = np.linspace(r_min_mult, r_max_mult, n_r) * body_radius
        theta_vals = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)

        r_grid = np.zeros((n_r, n_theta))
        theta_grid = np.zeros((n_r, n_theta))
        Br = np.zeros((n_r, n_theta))
        Btheta = np.zeros((n_r, n_theta))
        Bmag = np.zeros((n_r, n_theta))

        for i, rv in enumerate(r_vals):
            for j, th in enumerate(theta_vals):
                point = body_pos + rv * (np.cos(th) * eq1 + np.sin(th) * eq2)
                B = self.B_field(point, body_pos, spin_axis, body_radius)

                r_grid[i, j] = rv
                theta_grid[i, j] = th

                r_hat = (point - body_pos)
                r_hat /= np.linalg.norm(r_hat) + 1e-30
                th_hat = np.cross(m_hat, r_hat)
                th_norm = np.linalg.norm(th_hat)
                if th_norm > 1e-10:
                    th_hat /= th_norm

                Br[i, j] = np.dot(B, r_hat)
                Btheta[i, j] = np.dot(B, th_hat)
                Bmag[i, j] = np.linalg.norm(B)

        return {
            "r_grid": r_grid,
            "theta_grid": theta_grid,
            "Br": Br,
            "Btheta": Btheta,
            "Bmag": Bmag,
            "m_hat": m_hat.copy(),
            "eq1": eq1.copy(),
            "eq2": eq2.copy(),
        }
