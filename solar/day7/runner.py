"""runner.py — Day7 통합 스텝 드라이버 (PlanetRunner)

Day1~6의 엔진들을 12개 위도 밴드 위에서 순서대로 호출하는 통합 루프.

호출 순서 (한 스텝):
    1. RhythmEngine   → obliquity, insolation_scale (장주기 리듬)
    2. AtmosphereEngine → T_surface, CO2_ppm (대기)
    3. LatitudeBands  → 밴드별 T, F, W (생물권 공간)
    4. SeasonEngine   → 계절 위상·온도 편차 (밴드별)
    5. NitrogenEngine → N_soil (밴드별)
    6. OceanEngine    → upwelling, CO2_sink (전 지구)
    7. FoodWebEngine  → trophic 상태 (밴드별)
    8. TransportEngine → 씨드 확산 (밴드 간)
    9. MutationEngine  → 변이 이벤트 (밴드별)
   10. FeedbackEngine  → genome→env 수정 (전 지구)
   11. NicheEngine     → 자원 점유 (밴드별)
   12. StressEngine    → 스트레스 누적 (전 지구 요약)

12번째 스텝이 "안식 판정"으로 연결됨.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..day2.atmosphere.column import AtmosphereColumn
from ..day3.biosphere.latitude_bands import LatitudeBands, BAND_COUNT, BAND_CENTERS_DEG
from ..day3.fire.stress_accumulator import StressAccumulator, NeuronEvent
from ..day4.cycles.milankovitch import MilankovitchCycle
from ..day4.nitrogen.cycle import NitrogenCycle
from ..day4.gravity_tides.ocean_nutrients import OceanNutrients
from ..day4.season_engine import SeasonEngine
from ..day5.seed_transport import SeedTransport, TransportKernel
from ..day5.food_web import FoodWeb, TrophicState
from ..day6.mutation_engine import MutationEngine, make_mutation_engine
from ..day6.gaia_feedback import GaiaFeedbackEngine, make_gaia_feedback_engine
from ..day6.niche_model import NicheModel, NicheState, make_niche_model
from ..day6.genome_state import GenomeState


# ── 스냅샷 ────────────────────────────────────────────────────────────────────

@dataclass
class PlanetSnapshot:
    """한 스텝의 전 지구 상태 스냅샷.

    12개 밴드 × 독립 엔진의 교차 지점.
    각 band_env[i]가 "i번째 지파(tribe)의 환경 상태"에 해당.
    """
    time_yr: float

    # 전 지구 스칼라
    CO2_ppm: float
    T_surface_K: float
    obliquity_deg: float
    insolation_scale: float       # Milankovitch 스케일 (전 지구 평균)
    ocean_upwelling_uM: float
    planet_stress: float          # [0, 1]

    # 12개 밴드 벡터 (길이 = BAND_COUNT = 12)
    band_T: List[float]           # 밴드별 온도 [K]
    band_F: List[float]           # 밴드별 복사 조도 [W/m²]
    band_W: List[float]           # 밴드별 토양 수분 [0~1]
    band_N_soil: List[float]      # 밴드별 질소 [relative]
    band_seed: List[float]        # 밴드별 씨드 바이오매스
    band_trophic: List[Any]       # 밴드별 TrophicState
    band_niche: List[Any]         # 밴드별 NicheState
    mutation_events: int          # 이 스텝 총 변이 이벤트 수

    def summary(self) -> str:
        return (
            f"t={self.time_yr:.1f}yr | "
            f"CO2={self.CO2_ppm:.1f}ppm | "
            f"T={self.T_surface_K:.1f}K | "
            f"obl={self.obliquity_deg:.2f}° | "
            f"stress={self.planet_stress:.3f} | "
            f"mutations={self.mutation_events}"
        )


# ── PlanetRunner ──────────────────────────────────────────────────────────────

class PlanetRunner:
    """Day1~6 통합 스텝 드라이버.

    12개 위도 밴드(공간) × 12개 독립 엔진(기능)의 교차점.
    각 step(dt_yr) 호출이 창세기 "하루"에 해당하는 전 지구 시뮬레이션 한 스텝.

    Parameters
    ----------
    n_bands : int
        위도 밴드 수 (기본 12).
    n_species : int
        니치 모델의 종 수.
    seed : int
        난수 시드 (재현성).
    initial_conditions : dict, optional
        InitialConditions.to_runner_kwargs() 결과를 넘기면
        CO2, O2, albedo, f_land, mutation_factor 등이 동역학 계산값으로 초기화된다.
        None이면 대홍수 이후(postdiluvian) 기본값 사용.
    """

    def __init__(
        self,
        n_bands: int = BAND_COUNT,
        n_species: int = 4,
        seed: int = 42,
        initial_conditions: Optional[Dict] = None,
    ) -> None:
        self.n_bands = n_bands
        self.rng = random.Random(seed)
        self.time_yr = 0.0

        # ── 초기조건 파싱 ─────────────────────────────────────────────────────
        ic = initial_conditions or {}
        _CO2_ppm        = ic.get('CO2_ppm_init',       400.0)
        _O2_frac        = ic.get('O2_frac_init',        0.21)
        _albedo         = ic.get('albedo_init',         0.306)
        _f_land         = ic.get('f_land_init',         0.29)
        _mutation_factor= ic.get('mutation_factor',     1.0)
        _precip_mode    = ic.get('precip_mode',         'rain')
        _T_surface_init = ic.get('T_surface_K_init',    None)  # None → 대기 계산
        _pole_eq_delta  = ic.get('pole_eq_delta_K',     48.0)
        _pressure_atm   = ic.get('pressure_atm',        1.0)
        # 자기장 보호 강도 (밴드별, geography.py에서 주입 가능)
        # 기본: 위도 함수로 자동 계산 / IC에서 override 가능
        _mag_protection = ic.get('mag_protection_bands', None)

        # 초기조건 메타 저장 (스냅샷/문서화용)
        self._ic_phase   = ic.get('phase', 'postdiluvian') if ic else 'postdiluvian'
        self._ic_summary = ic  # 원본 보존

        # ── 1. 리듬 엔진 (Day4 Milankovitch) ────────────────────────────────
        self.rhythm = MilankovitchCycle()

        # ── 2. 대기 엔진 (Day2) ──────────────────────────────────────────────
        from ..day2.atmosphere.column import AtmosphereComposition
        comp = AtmosphereComposition(CO2=_CO2_ppm * 1e-6, O2=_O2_frac)
        atm_kwargs: Dict[str, Any] = dict(
            albedo      = _albedo,
            composition = comp,
        )
        if _T_surface_init is not None:
            atm_kwargs['T_surface_init'] = _T_surface_init
        self.atmosphere = AtmosphereColumn(**atm_kwargs)

        # ── 3. 생물권 밴드 (Day3) ────────────────────────────────────────────
        self.biosphere = LatitudeBands(CO2_ppm=_CO2_ppm, O2_frac=_O2_frac)

        # ── 4. 계절 엔진 (Day4) ──────────────────────────────────────────────
        self.season = SeasonEngine(obliquity_deg=23.44)

        # ── 5. 질소 엔진 (Day4) — 밴드별 인스턴스 ───────────────────────────
        self.nitrogen = [NitrogenCycle() for _ in range(n_bands)]

        # ── 6. 해양 엔진 (Day4) ──────────────────────────────────────────────
        self.ocean = OceanNutrients()

        # ── 7. 먹이사슬 엔진 (Day5) — 밴드별 ───────────────────────────────
        self.food_web_engines = [FoodWeb() for _ in range(n_bands)]
        self.food_web_states = [
            TrophicState(phyto=1.0, herbivore=0.5, carnivore=0.2, co2_resp_yr=0.0)
            for _ in range(n_bands)
        ]

        # ── 8. 수송 엔진 (Day5) ──────────────────────────────────────────────
        neighbors = self._make_linear_neighbors(n_bands)
        rates = [0.05] * n_bands
        kernel = TransportKernel(n_bands=n_bands, neighbors=neighbors, rates=rates)
        self.transport = SeedTransport(kernel)
        self.band_seed = [1.0] * n_bands

        # ── 9. 변이 엔진 (Day6) ──────────────────────────────────────────────
        # mutation = base × UV_factor × magnetic_protection[band]
        # UV_factor  : InitialConditions.mutation_factor (UV차폐 기반)
        # mag_protect: geography.band_protection() (자기장 기반)
        # 전 지구 평균 자기 보호값으로 base_rate 초기화
        from ..eden.geography import magnetic_protection_factor
        _BAND_LATS = [-82.5, -67.5, -52.5, -37.5, -22.5, -7.5,
                        7.5,  22.5,  37.5,  52.5,  67.5,  82.5]
        if _mag_protection is None:
            _mag_protection = [magnetic_protection_factor(lat) for lat in _BAND_LATS]
        self._mag_protection = list(_mag_protection[:n_bands])
        _avg_mag = sum(self._mag_protection) / len(self._mag_protection)
        # base_rate = 0.01 × UV_factor × avg_mag_protection
        _base_mut = 0.01 * _mutation_factor * _avg_mag
        self.mutation = make_mutation_engine(base_mutation_rate=_base_mut)
        self._mutation_factor = _mutation_factor   # 스냅샷 기록용

        # ── 10. 피드백 엔진 (Day6) ───────────────────────────────────────────
        self.feedback = make_gaia_feedback_engine()
        self._genomes = [
            GenomeState(traits=[0.5, 0.5, 0.5, 0.5])
            for _ in range(n_species)
        ]
        self._densities = [1.0] * n_species

        # ── 11. 니치 엔진 (Day6) — 밴드별 ──────────────────────────────────
        self.niche_engine = make_niche_model(n_bands=n_bands, n_species=n_species)
        # f_land: 에덴=0.40, 현재=0.29
        # resource_capacity: f_land에 비례 확장
        _cap = 100.0 * (_f_land / 0.29)
        self.niche_states = [
            NicheState(
                band_idx=i,
                land_fraction=_f_land,
                resource_capacity=_cap,
                occupancy=[1.0] * n_species,
            )
            for i in range(n_bands)
        ]

        # ── 12. 스트레스 엔진 (Day3) ─────────────────────────────────────────
        self.stress = StressAccumulator()

        # ── 스트레스 기준점 저장 (초기조건 기준) ────────────────────────────
        # 에덴에서 35°C, 250ppm은 "정상" → 기준점을 초기값으로
        self._stress_T_ref   = _T_surface_init if _T_surface_init else 288.0
        self._stress_CO2_ref = _CO2_ppm

    # ── 내부 헬퍼 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _make_linear_neighbors(n: int) -> List[List[int]]:
        """선형 체인 이웃 (밴드 i → i±1)."""
        neighbors = []
        for i in range(n):
            nb = []
            if i > 0:
                nb.append(i - 1)
            if i < n - 1:
                nb.append(i + 1)
            neighbors.append(nb)
        return neighbors

    # ── 메인 스텝 ─────────────────────────────────────────────────────────────

    def step(self, dt_yr: float = 1.0) -> PlanetSnapshot:
        """전 지구 한 스텝 적분.

        12개 엔진을 순서대로 호출하고 PlanetSnapshot을 반환한다.

        Parameters
        ----------
        dt_yr : float
            시간 스텝 [yr].

        Returns
        -------
        PlanetSnapshot
            이 스텝 완료 후 전 지구 상태 스냅샷.
        """
        t = self.time_yr

        # ── STEP 1: 리듬 (Milankovitch) ─────────────────────────────────────
        obliquity_deg = self.rhythm.obliquity(t_yr=t)
        insolation_scale = self.rhythm.insolation_scale(t_yr=t, phi_deg=0.0)  # 적도 기준

        # ── STEP 2: 대기 ─────────────────────────────────────────────────────
        F_solar = self.biosphere.F0 * insolation_scale
        self.atmosphere.step(F_solar_si=F_solar, dt_yr=dt_yr)
        T_surface = self.atmosphere.T_surface
        CO2_ppm = self.biosphere.CO2_ppm

        # ── STEP 3: 생물권 밴드 ──────────────────────────────────────────────
        self.biosphere.obliquity_rad = obliquity_deg * 3.14159265 / 180.0
        bio_result = self.biosphere.step(dt_yr=dt_yr)
        band_T = list(self.biosphere.band_T)
        band_F = list(self.biosphere.band_F)
        band_W = list(self.biosphere.band_W)
        CO2_ppm = bio_result.get("CO2_ppm", CO2_ppm)

        # ── STEP 4: 계절 ─────────────────────────────────────────────────────
        self.season.obliquity_deg = obliquity_deg
        self.season.step(dt_yr=dt_yr)
        # 밴드별 계절 보정 T (아래 질소/먹이사슬에서 사용)
        band_T_season = []
        for i, lat in enumerate(BAND_CENTERS_DEG[:self.n_bands]):
            s = self.season.state(lat_deg=lat)
            band_T_season.append(band_T[i] + s.delta_T)

        # ── STEP 5: 질소 (밴드별) ────────────────────────────────────────────
        band_N_soil = []
        for i in range(self.n_bands):
            T_K = max(200.0, band_T_season[i])
            W   = max(0.0, min(1.0, band_W[i]))
            gpp = max(0.0, band_F[i] / 1000.0)   # 간단 GPP 근사
            n_state = self.nitrogen[i].step(
                dt=dt_yr,
                B_pioneer=gpp,
                GPP_rate=gpp,
                O2_frac=self.biosphere.O2_frac if hasattr(self.biosphere, 'O2_frac') else 0.21,
                T_K=T_K,
                W_moisture=W,
            )
            band_N_soil.append(n_state.N_soil)

        # ── STEP 6: 해양 ─────────────────────────────────────────────────────
        ocean_state = self.ocean.step(
            dt=dt_yr,
            upwelling_uM=10.0 * insolation_scale,
            light_factor=min(1.0, insolation_scale),
        )
        upwelling = ocean_state.upwelling_uM

        # ── STEP 7: 먹이사슬 (밴드별) ───────────────────────────────────────
        new_fw_states = []
        for i in range(self.n_bands):
            gpp = max(0.0, band_F[i] / 500.0)
            env_fw = {"GPP": gpp, "fish_predation": 0.01}
            new_state = self.food_web_engines[i].step(
                self.food_web_states[i], env=env_fw, dt_yr=dt_yr
            )
            new_fw_states.append(new_state)
        self.food_web_states = new_fw_states

        # ── STEP 8: 씨드 수송 (밴드 간) ─────────────────────────────────────
        self.band_seed = self.transport.step(self.band_seed, dt_yr=dt_yr)

        # ── STEP 9: 변이 (전 지구 대표 스텝) ────────────────────────────────
        env_mut = {"T_surface": T_surface, "CO2_ppm": CO2_ppm}
        mut_events = self.mutation.step(
            p_contact=0.1,
            env=env_mut,
            dt_yr=dt_yr,
            band_idx=0,
            n_traits=4,
            rng=self.rng,
        )
        total_mutations = len(mut_events)

        # ── STEP 10: Gaia 피드백 (genome→env) ────────────────────────────────
        env_global = {"albedo": 0.3, "CO2_ppm": CO2_ppm, "T_surface": T_surface}
        genome_traits = [g.traits for g in self._genomes]  # List[List[float]]
        fb_result = self.feedback.step(
            env_global,
            genomes=genome_traits,
            densities=self._densities,
            dt_yr=dt_yr,
        )
        CO2_ppm = fb_result.env_new.get("CO2_ppm", CO2_ppm)

        # ── STEP 11: 니치 (전체 밴드 일괄) ──────────────────────────────────
        env_by_band = [
            {"GPP_scale": min(1.0, max(0.0, band_F[i] / 500.0))}
            for i in range(self.n_bands)
        ]
        self.niche_states = self.niche_engine.step(
            self.niche_states, env_by_band, dt_yr=dt_yr
        )

        # ── STEP 12: 스트레스 누적 ───────────────────────────────────────────
        # CO2 이상·온도 이상: 초기조건 기준점에서의 편차로 계산
        # (에덴: 기준=250ppm/308K, 현재: 기준=400ppm/288K)
        stress_magnitude = max(0.0,
            (CO2_ppm - self._stress_CO2_ref) / max(self._stress_CO2_ref, 1.0) +
            (T_surface - self._stress_T_ref) / 50.0
        )
        if stress_magnitude > 0.01:
            _atp = min(1.0, stress_magnitude)
            event = NeuronEvent(
                time_ms=self.time_yr * 365.25 * 24.0 * 3600.0 * 1000.0,
                co2_umol_s=max(0.0, (CO2_ppm - self._stress_CO2_ref) * 0.1),
                heat_mw=max(0.0, (T_surface - self._stress_T_ref) * 0.5),
                atp_consumed=_atp,
                neuron_id=0,
            )
            self.stress.push_neuron_event(event)
        stress_summary = self.stress.summary()
        planet_stress = stress_summary.get("planet_stress_ema", 0.0)

        # ── 시간 전진 ─────────────────────────────────────────────────────────
        self.time_yr += dt_yr

        # ── 스냅샷 반환 ───────────────────────────────────────────────────────
        return PlanetSnapshot(
            time_yr=self.time_yr,
            CO2_ppm=CO2_ppm,
            T_surface_K=T_surface,
            obliquity_deg=obliquity_deg,
            insolation_scale=insolation_scale,
            ocean_upwelling_uM=upwelling,
            planet_stress=planet_stress,
            band_T=band_T_season,
            band_F=band_F,
            band_W=band_W,
            band_N_soil=band_N_soil,
            band_seed=list(self.band_seed),
            band_trophic=list(self.food_web_states),
            band_niche=list(self.niche_states),
            mutation_events=total_mutations,
        )


# ── 팩토리 ────────────────────────────────────────────────────────────────────

def make_planet_runner(
    n_bands: int = BAND_COUNT,
    n_species: int = 4,
    seed: int = 42,
    initial_conditions: Optional[Dict] = None,
) -> PlanetRunner:
    """PlanetRunner 생성 helper.

    Parameters
    ----------
    initial_conditions : dict, optional
        InitialConditions.to_runner_kwargs() 결과.
        None이면 대홍수 이후(postdiluvian) 기본값.

    Examples
    --------
    # 에덴 환경으로 시작:
    from solar.eden.initial_conditions import make_antediluvian
    ic = make_antediluvian()
    runner = make_planet_runner(initial_conditions=ic.to_runner_kwargs())

    # 현재 지구(기본):
    runner = make_planet_runner()
    """
    return PlanetRunner(
        n_bands=n_bands,
        n_species=n_species,
        seed=seed,
        initial_conditions=initial_conditions,
    )


__all__ = ["PlanetRunner", "PlanetSnapshot", "make_planet_runner"]
