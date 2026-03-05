"""Solar System Data — NASA/JPL 기반 실측 상수
===============================================

단위계: AU, yr, M_sun  →  G = 4π²

데이터 출처:
  - NASA Planetary Fact Sheet (https://nssdc.gsfc.nasa.gov/planetary/factsheet/)
  - JPL Horizons System (https://ssd.jpl.nasa.gov/horizons/)
  - IAU 2015 Nominal Values

이 모듈은 순수 데이터만 제공한다.
EvolutionEngine과의 연결은 build_solar_system() 팩토리 함수를 통해 수행.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class PlanetData:
    """행성 물리 상수 (불변 데이터)."""
    name: str
    mass_solar: float           # M_sun 단위
    semi_major_au: float        # AU
    eccentricity: float
    inclination_deg: float      # 황도면 기준 (°)
    obliquity_deg: float        # 자전축 기울기 (°)
    J2: float                   # 편평도 (무차원)
    radius_au: float            # 적도 반지름 (AU)
    spin_period_days: float     # 항성 자전 주기 (일); 음수 = 역행
    C_MR2: float                # 관성모멘트 비 C/(MR²)
    retrograde_spin: bool = False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  실측 데이터
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUN_DATA = PlanetData(
    name="Sun",
    mass_solar=1.0,
    semi_major_au=0.0,
    eccentricity=0.0,
    inclination_deg=0.0,
    obliquity_deg=7.25,
    J2=2.2e-7,
    radius_au=4.6524726e-3,     # 696,000 km
    spin_period_days=25.05,
    C_MR2=0.070,
)

MERCURY = PlanetData(
    name="Mercury",
    mass_solar=1.6601e-7,
    semi_major_au=0.38710,
    eccentricity=0.20563,
    inclination_deg=7.005,
    obliquity_deg=0.034,
    J2=5.03e-5,
    radius_au=1.6308e-5,        # 2,439.7 km
    spin_period_days=58.646,
    C_MR2=0.346,
)

VENUS = PlanetData(
    name="Venus",
    mass_solar=2.4478e-6,
    semi_major_au=0.72333,
    eccentricity=0.00677,
    inclination_deg=3.395,
    obliquity_deg=177.36,
    J2=4.458e-6,
    radius_au=4.0454e-5,        # 6,051.8 km
    spin_period_days=243.025,
    C_MR2=0.33,
    retrograde_spin=True,
)

EARTH = PlanetData(
    name="Earth",
    mass_solar=3.0035e-6,
    semi_major_au=1.00000,
    eccentricity=0.01671,
    inclination_deg=0.000,
    obliquity_deg=23.44,
    J2=1.08263e-3,
    radius_au=4.2635e-5,        # 6,378.1 km
    spin_period_days=0.99727,
    C_MR2=0.3307,
)

MARS = PlanetData(
    name="Mars",
    mass_solar=3.2271e-7,
    semi_major_au=1.52368,
    eccentricity=0.09341,
    inclination_deg=1.850,
    obliquity_deg=25.19,
    J2=1.9605e-3,
    radius_au=2.2660e-5,        # 3,389.5 km
    spin_period_days=1.02596,
    C_MR2=0.3644,
)

JUPITER = PlanetData(
    name="Jupiter",
    mass_solar=9.5460e-4,
    semi_major_au=5.20260,
    eccentricity=0.04839,
    inclination_deg=1.303,
    obliquity_deg=3.13,
    J2=1.4736e-2,
    radius_au=4.7783e-4,        # 71,492 km
    spin_period_days=0.41354,
    C_MR2=0.254,
)

SATURN = PlanetData(
    name="Saturn",
    mass_solar=2.8580e-4,
    semi_major_au=9.55491,
    eccentricity=0.05386,
    inclination_deg=2.489,
    obliquity_deg=26.73,
    J2=1.6298e-2,
    radius_au=4.0280e-4,        # 60,268 km
    spin_period_days=0.44401,
    C_MR2=0.210,
)

URANUS = PlanetData(
    name="Uranus",
    mass_solar=4.3660e-5,
    semi_major_au=19.2184,
    eccentricity=0.04726,
    inclination_deg=0.773,
    obliquity_deg=97.77,
    J2=3.343e-3,
    radius_au=1.7085e-4,        # 25,559 km
    spin_period_days=0.71833,
    C_MR2=0.225,
    retrograde_spin=True,
)

NEPTUNE = PlanetData(
    name="Neptune",
    mass_solar=5.1510e-5,
    semi_major_au=30.1104,
    eccentricity=0.00859,
    inclination_deg=1.770,
    obliquity_deg=28.32,
    J2=3.411e-3,
    radius_au=1.6554e-4,        # 24,764 km
    spin_period_days=0.67125,
    C_MR2=0.23,
)

PLANETS: Dict[str, PlanetData] = {
    "Mercury": MERCURY,
    "Venus":   VENUS,
    "Earth":   EARTH,
    "Mars":    MARS,
    "Jupiter": JUPITER,
    "Saturn":  SATURN,
    "Uranus":  URANUS,
    "Neptune": NEPTUNE,
}

MOON_DATA = {
    "mass_frac": 0.01230,       # M_moon / M_earth
    "distance_au": 0.00257,     # 384,400 km in AU
    "radius_frac": 0.2724,      # R_moon / R_earth
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  팩토리: 데이터 → Body3D 변환
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _circular_velocity(G: float, M_central: float, a: float) -> float:
    """원형 궤도 속도 v = sqrt(GM/a)."""
    return np.sqrt(G * M_central / a)


def _initial_state(
    data: PlanetData,
    G: float,
    M_central: float,
) -> dict:
    """PlanetData → 초기 위치/속도/스핀 딕셔너리.

    모든 행성을 J2000 기준 x축 양의 방향에 배치.
    실제 위상각은 시뮬레이션 시작 후 자연 분리된다.
    """
    a = data.semi_major_au
    v = _circular_velocity(G, M_central, a) if a > 0 else 0.0

    incl = np.radians(data.inclination_deg)
    pos = np.array([a * np.cos(incl), 0.0, a * np.sin(incl)])
    vel = np.array([0.0, v * np.cos(incl), v * np.sin(incl)])

    obl = np.radians(data.obliquity_deg)
    if data.retrograde_spin:
        spin_axis = np.array([np.sin(obl), 0.0, -np.cos(obl)])
    else:
        spin_axis = np.array([np.sin(obl), 0.0, np.cos(obl)])
    norm = np.linalg.norm(spin_axis)
    if norm > 1e-30:
        spin_axis /= norm

    spin_rate = 2 * np.pi * 365.25 / abs(data.spin_period_days)

    return {
        "name": data.name,
        "mass": data.mass_solar,
        "pos": pos,
        "vel": vel,
        "spin_axis": spin_axis,
        "spin_rate": spin_rate,
        "obliquity": obl,
        "J2": data.J2,
        "radius": data.radius_au,
        "C_MR2": data.C_MR2,
    }


def build_solar_system(
    include: Optional[List[str]] = None,
    with_moon: bool = True,
    G: float = 4 * np.pi**2,
) -> List[dict]:
    """태양계 Body3D 생성용 딕셔너리 리스트 반환.

    Parameters
    ----------
    include : list of str or None
        포함할 행성 이름. None이면 8행성 전부.
    with_moon : bool
        True면 달 데이터도 포함 (Earth가 include에 있을 때).
    G : float
        중력 상수. 기본값 = 4π² (AU, yr, M_sun).

    Returns
    -------
    list of dict
        각 dict는 Body3D(**d)로 변환 가능.
        달은 별도 키 "_moon_config"로 giant_impact 파라미터 제공.
    """
    if include is None:
        include = list(PLANETS.keys())

    M_sun = SUN_DATA.mass_solar
    result = [_initial_state(SUN_DATA, G, M_sun)]

    for name in include:
        if name not in PLANETS:
            raise ValueError(f"Unknown planet: {name}. Available: {list(PLANETS.keys())}")
        result.append(_initial_state(PLANETS[name], G, M_sun))

    if with_moon and "Earth" in include:
        earth_data = PLANETS["Earth"]
        result.append({
            "_moon_config": {
                "target": "Earth",
                "obliquity_deg": earth_data.obliquity_deg,
                "spin_period_days": earth_data.spin_period_days,
                "moon_mass_frac": MOON_DATA["mass_frac"],
                "moon_distance_au": MOON_DATA["distance_au"],
                "J2": earth_data.J2,
                "C_MR2": earth_data.C_MR2,
            }
        })

    return result
