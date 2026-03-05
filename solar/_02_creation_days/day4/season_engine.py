"""SeasonEngine — 계절 위상·진폭 엔진 (Day 4 helper)

역할:
    - 1년 주기의 계절 리듬을 독립 상태공간으로 표현한다.
    - 각 위도(lat)에 대해:
        * 계절 위상(season_phase)
        * 온도 편차 ΔT_seasonal
        * 건기 진폭 dry_season_modifier
        * (확장용) 강수/토양수분 패턴
      을 계산해 다른 레이어(atmosphere/biosphere/fire)가 읽어가도록 한다.

디자인 원칙:
    - EvolutionEngine / Milankovitch 로부터 오는 "연평균" 및 "season_amplitude"
      정보를 받아, 1년 안에서의 리듬(phase)을 재구성하는 helper로만 동작한다.
    - 자체적으로 복잡한 기후 모델을 구현하지 않고,
      "간단한 사인파 패턴 + 위도·경사·amplitude 스케일" 수준에서 표현한다.

사용 예시:

    from solar._02_creation_days.day4.season_engine import SeasonEngine

    season = SeasonEngine(obliquity_deg=23.44)
    dt_yr = 1.0 / 12.0   # 한 달
    for _ in range(12):
        season.step(dt_yr)
        st = season.state(lat_deg=45.0)
        print(st.phase, st.delta_T, st.dry_season_modifier)

"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class SeasonState:
    """위도별 계절 상태.

    Attributes
    ----------
    phase : float
        계절 위상 [rad], 0=봄분점, π/2=여름, π=가을, 3π/2=겨울.
    delta_T : float
        계절 온도 편차 [K]. 양수 = 평년보다 따뜻함, 음수 = 평년보다 차가움.
    dry_season_modifier : float
        건기 강도 계수 [0, +∞). 1.0 = 기준, >1 = 더 건조, <1 = 덜 건조.
    """

    phase: float
    delta_T: float
    dry_season_modifier: float


class SeasonEngine:
    """간단한 계절 리듬 엔진.

    Notes
    -----
    - 내부 시간은 `t_in_year` (0~1) 로 관리된다.
    - 위상은 `phase = 2π * t_in_year`.
    - amplitude_* 파라미터와 위도·경사(obliquity)에 따라
      ΔT 및 dry_season_modifier를 계산한다.
    """

    def __init__(
        self,
        obliquity_deg: float = 23.44,
        year_length_yr: float = 1.0,
        temp_amplitude_equator_K: float = 5.0,
        temp_amplitude_pole_K: float = 25.0,
        dry_amplitude_equator: float = 0.6,
        dry_amplitude_pole: float = 0.2,
    ) -> None:
        self.obliquity_deg = obliquity_deg
        self.year_length_yr = year_length_yr

        self.temp_amp_eq = temp_amplitude_equator_K
        self.temp_amp_pole = temp_amplitude_pole_K
        self.dry_amp_eq = dry_amplitude_equator
        self.dry_amp_pole = dry_amplitude_pole

        self.t_in_year = 0.0  # [0, 1)

        # 기준 경사각 (현 지구값) 대비 season amplitude 스케일
        self._obliquity_ref_deg = 23.44

    @property
    def phase(self) -> float:
        """현재 계절 위상 [rad], 0~2π."""
        return 2.0 * math.pi * self.t_in_year

    def step(self, dt_yr: float) -> None:
        """내부 season_phase를 dt 만큼 전진."""
        if self.year_length_yr <= 0:
            raise ValueError("year_length_yr must be positive")
        self.t_in_year = (self.t_in_year + dt_yr / self.year_length_yr) % 1.0

    def _latitude_weight(self, lat_deg: float) -> float:
        """위도에 따른 0~1 가중치 (0=적도, 1=극지).

        선형보다는 기하학에 가까운 형태를 위해 sin(|lat|) 기반으로 사용한다.
        """
        lat_rad = math.radians(abs(lat_deg))
        return min(max(math.sin(lat_rad), 0.0), 1.0)

    @property
    def obliquity_scale(self) -> float:
        """경사각에 따른 계절 진폭 스케일.

        기본 아이디어: 계절성 진폭 ∝ sin(obliquity).
        경사각이 0이면 계절성이 0, 경사각이 커질수록 진폭이 커진다.
        """
        ref = math.sin(math.radians(self._obliquity_ref_deg))
        cur = math.sin(math.radians(self.obliquity_deg))
        if ref <= 0:
            return 1.0
        return max(0.0, cur / ref)

    def _temp_amplitude(self, lat_deg: float) -> float:
        """위도별 온도 진폭 [K]."""
        w = self._latitude_weight(lat_deg)
        base = (1.0 - w) * self.temp_amp_eq + w * self.temp_amp_pole
        return base * self.obliquity_scale

    def _dry_amplitude(self, lat_deg: float) -> float:
        """위도별 건기 진폭 계수."""
        w = self._latitude_weight(lat_deg)
        base = (1.0 - w) * self.dry_amp_eq + w * self.dry_amp_pole
        return base * self.obliquity_scale

    def state(self, lat_deg: float) -> SeasonState:
        """해당 위도의 계절 상태를 계산."""
        # 북반구: phase 그대로, 남반구: 위상 반전 (반년 차이)
        global_phase = self.phase
        if lat_deg >= 0:
            phase = global_phase
        else:
            phase = (global_phase + math.pi) % (2.0 * math.pi)

        # 간단한 사인파 계절 온도 편차: 여름(phase ≈ π/2)에서 최대
        temp_amp = self._temp_amplitude(lat_deg)
        delta_T = temp_amp * math.sin(phase)

        # 건기 강도: 예시로 "여름 후반~초가을"에 건기가 최대가 되도록 설계
        dry_amp = self._dry_amplitude(lat_deg)
        # 위상 이동: π/2 (여름 중심) + π/4 → 여름 후반
        dry_phase = phase - (math.pi * 3.0 / 4.0)
        dry_season = 1.0 + dry_amp * max(0.0, math.sin(dry_phase))

        return SeasonState(
            phase=phase,
            delta_T=delta_T,
            dry_season_modifier=dry_season,
        )

