"""mobility_engine — Day5 생물 이동 에이전트 (Bird/Fish)

이 모듈은 Day5 레이어의 "움직이는 생물"을
아주 단순한 형태로 표현한다.

역할:
    - 위도 밴드별로 정의된 biosphere 상태(B_seed 등)에 대해
      이동률(migration rate)을 계산하는 helper.
    - 실제 mass transport는 seed_transport.SeedTransport 가 담당하고,
      여기서는 "어느 밴드가 어느 이웃으로 얼마나 자주 이동하려 하는가"
      를 rate [1/yr] 로 제공한다.

Loop 연결:
    Loop F: BirdAgent 씨드 분산 → pioneer 원거리 확산
    Loop G: 구아노 N → nitrogen.N_soil
    Loop H: FishAgent 포식 → phyto 감소 → CO₂ 호흡 변화

수식:
    rate_i = base_rate * max(0, 1 + o2_sensitivity * (O2_i - O2_ref))
    구아노 플럭스: r_guano * base_rate  [g N/m²/yr per band]
    씨드 플럭스:   r_seed * migration_rates[i]  [/yr]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import math

from ._constants import (
    R_SEED_DISPERSAL,
    R_GUANO_N,
    R_PREDATION,
    R_RESP_CO2,
)


# ── 유틸리티 ───────────────────────────────────────────────────────────────────

def _ring_neighbors(n_bands: int) -> List[List[int]]:
    """위도 밴드 이웃 목록 생성.

    물리적 위도 구조:
        밴드 0        = 남극 (−90°) → 오른쪽(1)만 이웃
        밴드 1~n-2   = 중위도      → 양쪽(i-1, i+1) 이웃
        밴드 n-1     = 북극 (+90°) → 왼쪽(n-2)만 이웃

    위도 경계에서 wrap-around 하지 않는다.
    """
    neighbors: List[List[int]] = []
    for i in range(n_bands):
        nb: List[int] = []
        if i > 0:
            nb.append(i - 1)        # 남쪽 이웃
        if i < n_bands - 1:
            nb.append(i + 1)        # 북쪽 이웃
        neighbors.append(nb)
    return neighbors


def long_range_neighbors(n_bands: int, max_jump: int = 2) -> List[List[int]]:
    """장거리 이동 이웃: 인접뿐 아니라 ±max_jump 밴드까지 연결.

    "전 지구적 네트워킹" 확장용. 철새 등이 한 번에 여러 위도 밴드를 넘나드는
    비인접 연결을 허용한다. 극→적도 도달 스텝 수를 줄인다.

    Parameters
    ----------
    n_bands : int
        위도 밴드 수.
    max_jump : int
        최대 점프 거리 (밴드 단위). 1이면 인접만 (= _ring_neighbors).

    Returns
    -------
    List[List[int]]
        각 밴드 i에 대해 [i-max_jump, ..., i-1, i+1, ..., i+max_jump] (범위 내만).
    """
    if max_jump < 1:
        return _ring_neighbors(n_bands)
    neighbors: List[List[int]] = []
    for i in range(n_bands):
        nb: List[int] = []
        for d in range(-max_jump, max_jump + 1):
            if d == 0:
                continue
            j = i + d
            if 0 <= j < n_bands:
                nb.append(j)
        neighbors.append(nb)
    return neighbors


# ── BirdAgent ─────────────────────────────────────────────────────────────────

@dataclass
class BirdAgent:
    """새 무리(BirdAgent)의 이동 특성.

    확장 포인트 (개념 완성도 90%):
        - biomass_by_band: 밴드별 새 바이오매스 [무차원]. 주면 씨드/구아노 플럭스가 이에 비례.
        - land_fraction_by_band: 육지 비율. 주면 육상 밴드에서만 활동 (해양 밴드에서 0).
        - long_range_max_jump: 2 이상이면 인접이 아닌 장거리 이웃 사용 (철새형).

    Attributes
    ----------
    n_bands : int
        위도 밴드 수 (latitude_bands.BAND_COUNT 와 일치 권장).
    base_rate : float
        기본 이동률 [1/yr]. dt_yr * base_rate << 1 권장.
    o2_sensitivity : float
        대기 O2 에 따른 이동률 스케일링 계수.
        rate_i = base_rate * (1 + o2_sensitivity * (O2_i - O2_ref)).
    o2_ref : float
        기준 O2 몰분율 (예: 0.21).
    r_seed : float
        씨드 분산 계수 (Loop F).
    r_guano : float
        구아노 N 기여 계수 (Loop G).
    long_range_max_jump : Optional[int]
        None 이면 인접만(i±1). 2면 ±2 밴드까지 이웃 (장거리 분산).
    """

    n_bands: int
    base_rate: float = 0.05
    o2_sensitivity: float = 1.0
    o2_ref: float = 0.21
    r_seed: float = R_SEED_DISPERSAL
    r_guano: float = R_GUANO_N
    long_range_max_jump: Optional[int] = None

    def __post_init__(self) -> None:
        if self.long_range_max_jump is not None and self.long_range_max_jump >= 2:
            self._neighbors = long_range_neighbors(self.n_bands, self.long_range_max_jump)
        else:
            self._neighbors = _ring_neighbors(self.n_bands)

    @property
    def neighbors(self) -> List[List[int]]:
        """위도 밴드 링 구조의 이웃 인덱스."""
        return self._neighbors

    def migration_rates(
        self,
        o2_by_band: Optional[List[float]] = None,
        land_fraction_by_band: Optional[List[float]] = None,
    ) -> List[float]:
        """각 밴드의 effective migration rate [1/yr] 를 반환.

        land_fraction_by_band 가 주어지면: 육상 밴드에서만 활동 (rate_i *= land_fraction_i).
        해양만 있는 밴드는 0이 되어 "하늘·바다 도메인 분리"를 만족한다.
        """
        if o2_by_band is None:
            base = [self.base_rate] * self.n_bands
        else:
            scaled: List[float] = []
            for o2 in o2_by_band:
                delta = o2 - self.o2_ref
                scale = max(0.0, 1.0 + self.o2_sensitivity * delta)
                scaled.append(self.base_rate * scale)
            base = scaled
        if land_fraction_by_band is None or len(land_fraction_by_band) != self.n_bands:
            return base
        return [base[i] * max(0.0, min(1.0, land_fraction_by_band[i])) for i in range(self.n_bands)]

    def seed_flux(
        self,
        pioneer: List[float],
        o2_by_band: Optional[List[float]] = None,
        land_fraction_by_band: Optional[List[float]] = None,
        biomass_by_band: Optional[List[float]] = None,
    ) -> List[float]:
        """Loop F: 씨드 유입 플럭스율 [pioneer_unit / yr].

        biomass_by_band 가 주어지면: 플럭스가 "에이전트 바이오매스"에 비례 (out_i ∝ pioneer[i] * rate_i * B_bird[i]).
        land_fraction_by_band 가 주어지면: 육상 밴드에서만 방출 (도메인 분리).

        역할 (사용 경로):
            이 메서드는 **SeedTransport.step() 과 함께 쓰는 것이 아니라**,
            SeedTransport 없이 "얼마나 많은 씨드가 이웃에서 유입되는가"를
            빠르게 추정하고 싶을 때 사용하는 보조 helper이다.

            실제 보존형 transport(pioneer 총합 보존)가 필요하면
            migration_rates() → SeedTransport.step(B_pioneer, dt_yr) 경로를 사용한다.

        수식:
            out_i  = R_SEED_DISPERSAL * rate_i * pioneer[i] * (B_bird[i] or 1)
            in_j  += out_i / len(neighbors_i)
        """
        rates = self.migration_rates(o2_by_band, land_fraction_by_band)
        if biomass_by_band is not None and len(biomass_by_band) == self.n_bands:
            scale = [max(0.0, b) for b in biomass_by_band]
        else:
            scale = [1.0] * self.n_bands
        flux_in = [0.0] * self.n_bands
        for i in range(self.n_bands):
            out = self.r_seed * rates[i] * pioneer[i] * scale[i]
            for j in self._neighbors[i]:
                flux_in[j] += out / len(self._neighbors[i])
        return flux_in

    def guano_flux(
        self,
        o2_by_band: Optional[List[float]] = None,
        land_fraction_by_band: Optional[List[float]] = None,
        biomass_by_band: Optional[List[float]] = None,
    ) -> List[float]:
        """Loop G: 구아노 N 기여 [g N/m²/yr].

        guano[i] = r_guano * rate_i * (B_bird[i] or 1).
        land_fraction_by_band 적용 시 육상 밴드에서만 방출.
        """
        rates = self.migration_rates(o2_by_band, land_fraction_by_band)
        if biomass_by_band is not None and len(biomass_by_band) == self.n_bands:
            scale = [max(0.0, b) for b in biomass_by_band]
        else:
            scale = [1.0] * self.n_bands
        return [self.r_guano * rates[i] * scale[i] for i in range(self.n_bands)]


# ── FishAgent ─────────────────────────────────────────────────────────────────

@dataclass
class FishAgent:
    """해양 어류/플랑크톤 무리의 단순 이동 특성.

    확장 포인트:
        - land_fraction_by_band: 주면 해양 밴드에서만 활동 (rate_i *= (1 - land_fraction_i)).
        - biomass_by_band: 주면 포식/CO₂ 플럭스가 물고기 바이오매스에 비례.

    Loop H (먹이사슬):
        phyto[i] × B_fish → 포식 → CO₂ 호흡
    """

    n_bands: int
    base_rate: float = 0.02
    r_pred: float = R_PREDATION
    r_co2: float = R_RESP_CO2

    def __post_init__(self) -> None:
        self._neighbors = _ring_neighbors(self.n_bands)

    @property
    def neighbors(self) -> List[List[int]]:
        return self._neighbors

    def migration_rates(
        self,
        land_fraction_by_band: Optional[List[float]] = None,
    ) -> List[float]:
        """각 밴드의 effective migration rate [1/yr].
        land_fraction_by_band 가 주어지면: 해양 밴드에서만 활동 (rate_i *= (1 - land_i)).
        """
        base = [self.base_rate] * self.n_bands
        if land_fraction_by_band is None or len(land_fraction_by_band) != self.n_bands:
            return base
        return [base[i] * max(0.0, min(1.0, 1.0 - land_fraction_by_band[i])) for i in range(self.n_bands)]

    def predation_flux(
        self,
        phyto: List[float],
        biomass_by_band: Optional[List[float]] = None,
        land_fraction_by_band: Optional[List[float]] = None,
    ) -> List[float]:
        """Loop H: phyto 포식량 [/yr].
        pred[i] = r_pred * base_rate * phyto[i] * (B_fish[i] or 1).
        land_fraction_by_band 적용 시 해양 밴드에서만 포식.
        """
        rates = self.migration_rates(land_fraction_by_band)
        if biomass_by_band is not None and len(biomass_by_band) == self.n_bands:
            scale = [max(0.0, b) for b in biomass_by_band]
        else:
            scale = [1.0] * self.n_bands
        return [self.r_pred * rates[i] * p * scale[i] for i, p in enumerate(phyto)]

    def co2_resp_flux(
        self,
        phyto: List[float],
        biomass_by_band: Optional[List[float]] = None,
        land_fraction_by_band: Optional[List[float]] = None,
    ) -> List[float]:
        """FishAgent 경로 CO₂ 호흡 플럭스 [상대값/yr].
        land_fraction_by_band / biomass_by_band 는 predation_flux 와 동일하게 적용.

        ⚠️  이중 계산 주의:
            FoodWeb.step() 에 env["fish_predation"]을 주입하면,
            FoodWeb 내부에서 fish_pred 를 co2_resp_yr 에 이미 포함시킨다.
            따라서 이 메서드와 FoodWeb.step() 을 동시에 사용하면
            동일한 포식량이 CO₂에 두 번 반영된다.
        """
        pred = self.predation_flux(phyto, biomass_by_band, land_fraction_by_band)
        return [self.r_co2 * p for p in pred]


# ── 팩토리 ────────────────────────────────────────────────────────────────────

def make_bird_agent(n_bands: int = 12) -> BirdAgent:
    """기본 BirdAgent 생성 helper."""
    return BirdAgent(n_bands=n_bands)


def make_fish_agent(n_bands: int = 12) -> FishAgent:
    """기본 FishAgent 생성 helper."""
    return FishAgent(n_bands=n_bands)


__all__ = [
    "BirdAgent",
    "FishAgent",
    "make_bird_agent",
    "make_fish_agent",
    "long_range_neighbors",
    "R_SEED_DISPERSAL",
    "R_GUANO_N",
    "R_PREDATION",
    "R_RESP_CO2",
]
