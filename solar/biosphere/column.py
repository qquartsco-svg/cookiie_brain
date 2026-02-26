"""BiosphereColumn — pioneer + photosynthetic + Phase Gate 생애주기 (Phase 7b/7c/7d).

설계 철학 (세차운동·토양 ODE와 동일):
  "물리 법칙/관측값을 율(d/dt)로 정의하면, 장주기 패턴이 자연스럽게 나온다"

생애주기 흐름:
  [돌땅]
    → pioneer ODE (2739년) → organic >= 0.5
    → photo_ready ON
    → GPP/NPP 시작 → B_leaf, B_root 성장
    → 씨(B_seed) 생산
    → 발아 게이트 → B_sprout (싹)
    → B_sprout → B_stem (줄기)  [sigmoid Phase Gate]
    → B_stem   → B_wood (나무)  [sigmoid Phase Gate]
    → B_wood   → B_fruit (열매) [O₂ + 성숙 조건]
    → B_fruit  → B_seed (씨)    [순환 닫힘]

Gaia Attractor 루프 (Phase 7d — 행성 항상성):
  [루프 A] 사체 분해 → CO₂ 대기 방출
    사망한 biomass(잎·줄기·나무) × (1-ETA_LITTER) → delta_CO2 (탄소 순환 닫힘)

  [루프 B] 사체 일부 → organic_layer 환류
    사망한 biomass × ETA_LITTER → organic_layer (토양 갱신/유지)

  [루프 C] 대기 CO₂/O₂/T → 생물권 env 실시간 반영
    env["CO2"], env["O2"] → GPP, f_O2 계산에 즉시 사용 (양방향 루프)
    → 높은 CO₂에서 GPP↑ → O₂ 방출↑ → CO₂ 낮아짐 (음성 피드백 attractor)
    → 낮은 O₂에서 f_O2↓ → 목본·결실 억제 (초기 지구 재현)

ODE 적분 규약:
  - 모든 변화량은 d*/dt [단위/yr] 로 정의 (율)
  - dt는 state += d* * dt_yr 에서 딱 한 번만 곱함
  - to_seed, germ 등 중간값도 [단위/yr] 율로 유지

Inputs : F_solar_si, T_surface, P_surface, CO2, H2O, O2, water_phase, land_fraction
Outputs: delta_CO2, delta_O2, transpiration_kg_per_m2_yr, latent_heat_biosphere_W,
         delta_albedo_land, GPP, Resp, NPP, photo_active,
         co2_from_decomp  [Gaia 루프 A: 분해 CO₂]
         organic_to_soil  [Gaia 루프 B: 토양 환류]
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Any

from .state import BiosphereState
from . import pioneer
from . import photo
from ._constants import (
    # 기관 사망률
    M_LEAF, M_ROOT, M_WOOD, M_STEM, M_FRUIT, M_SEED,
    # 기준 분배 로짓
    A_LEAF_BASE, A_ROOT_BASE, A_WOOD_BASE, A_STEM_BASE, A_FRUIT_BASE,
    A_WOOD_O2, A_FRUIT_O2, A_LEAF_O2,
    # Phase Gate
    K_GERM, GERM_SOIL_HALF, GERM_T_MIN, GERM_T_OPT, GERM_T_MAX,
    K_SPROUT_TO_STEM, B_SPROUT_HALF,
    K_STEM_TO_WOOD, B_STEM_HALF,
    K_FRUIT, B_WOOD_FRUIT_TH,
    K_FRUIT_TO_SEED,
    # Gaia Attractor (Phase 7d) — 사체 분해 → CO₂ + 토양 환류
    ETA_LITTER, ETA_WOOD_DECAY,
    # 알베도
    ALBEDO_BARE_LAND, ALBEDO_VEG_MIN, VEG_COVER_SCALE,
    EPS,
)


# ── 헬퍼 함수 ─────────────────────────────────────────────────────────────────

def _sigmoid(x: float, half: float, sharpness: float = 10.0) -> float:
    """연속 Phase Gate: x/(x+half) 형태 (Michaelis-Menten).
    x가 half일 때 0.5, x→∞ 이면 1.0.
    no if-else, 연속 미분 가능.
    """
    return x / (x + half + EPS)


def _softmax_alloc(logits: Dict[str, float]) -> Dict[str, float]:
    """logit dict → 합이 1인 분배 비율 (softmax).
    탄소 회계 정합: sum(alloc) = 1 보장.
    """
    exp_vals = {k: math.exp(min(v, 20.0)) for k, v in logits.items()}
    total = sum(exp_vals.values()) + EPS
    return {k: v / total for k, v in exp_vals.items()}


def _germ_gate(T: float, organic: float, f_W: float) -> float:
    """발아 게이트 g_germ ∈ [0,1].
    g_soil: 토양 준비도 (Michaelis-Menten)
    g_T   : 온도 적합도 (삼각형 함수 — 연속)
    g_W   : 수분 (f_W 그대로)
    """
    g_soil = _sigmoid(organic, GERM_SOIL_HALF)

    # 온도 삼각형 게이트 (연속)
    if T <= GERM_T_MIN or T >= GERM_T_MAX:
        g_T = 0.0
    elif T <= GERM_T_OPT:
        g_T = (T - GERM_T_MIN) / (GERM_T_OPT - GERM_T_MIN + EPS)
    else:
        g_T = (GERM_T_MAX - T) / (GERM_T_MAX - GERM_T_OPT + EPS)
    g_T = max(0.0, g_T)

    return g_soil * g_T * max(0.0, f_W)


# ── BiosphereColumn ────────────────────────────────────────────────────────────

@dataclass
class BiosphereColumn:
    """Single-column biosphere (0D global land average).

    State:
      Pioneer  : pioneer_biomass, organic_layer, mineral_layer
      광합성   : B_leaf, B_root
      Phase Gate: B_sprout → B_stem → B_wood → B_fruit → B_seed

    step(env, dt_yr) → feedback dict for atmosphere/surface.
    """

    body_name: str = "Earth"
    land_fraction: float = 0.29

    # 초기값
    pioneer_biomass_init: float = 0.001
    organic_layer_init: float = 0.0
    mineral_layer_init: float = 0.0
    B_leaf_init: float = 0.0
    B_root_init: float = 0.0
    B_sprout_init: float = 0.0
    B_stem_init: float = 0.0
    B_wood_init: float = 0.0
    B_fruit_init: float = 0.0
    B_seed_init: float = 0.0

    # 진화 상태
    pioneer_biomass: float = field(default=0.001)
    organic_layer: float = field(default=0.0)
    mineral_layer: float = field(default=0.0)
    B_leaf: float = field(default=0.0)
    B_root: float = field(default=0.0)
    B_sprout: float = field(default=0.0)
    B_stem: float = field(default=0.0)
    B_wood: float = field(default=0.0)
    B_fruit: float = field(default=0.0)
    B_seed: float = field(default=0.0)

    time_yr: float = field(default=0.0)

    def __post_init__(self) -> None:
        self.pioneer_biomass = self.pioneer_biomass_init
        self.organic_layer   = self.organic_layer_init
        self.mineral_layer   = self.mineral_layer_init
        self.B_leaf   = self.B_leaf_init
        self.B_root   = self.B_root_init
        self.B_sprout = self.B_sprout_init
        self.B_stem   = self.B_stem_init
        self.B_wood   = self.B_wood_init
        self.B_fruit  = self.B_fruit_init
        self.B_seed   = self.B_seed_init

    # ── step ──────────────────────────────────────────────────────────────────

    def step(self, env: Dict[str, Any], dt_yr: float) -> Dict[str, Any]:
        """1스텝 전진. 모든 ODE는 율(d/dt)로 계산 후 dt_yr 한 번만 적용."""
        F          = env.get("F_solar_si", 0.0)
        T          = env.get("T_surface", 273.0)
        CO2        = env.get("CO2", 400e-6)
        H2O        = env.get("H2O", 0.01)
        O2         = env.get("O2", 0.0)
        water_phase = env.get("water_phase", "gas")
        f_W        = env.get("soil_moisture",
                              1.0 if water_phase == "liquid" else 0.2)

        # ── 1. Pioneer ODE (항상 활성) ────────────────────────────────────────
        d_pioneer, d_organic, d_mineral = pioneer.d_pioneer_dt(
            self.pioneer_biomass, self.organic_layer, self.mineral_layer,
            T, water_phase, H2O,
        )
        self.pioneer_biomass = max(0.0, self.pioneer_biomass + d_pioneer * dt_yr)
        self.organic_layer   = max(0.0, self.organic_layer   + d_organic * dt_yr)
        self.mineral_layer   = max(0.0, self.mineral_layer   + d_mineral * dt_yr)

        GPP = 0.0; Resp = 0.0; delta_CO2 = 0.0; delta_O2 = 0.0; trans_rate = 0.0
        co2_from_decomp = 0.0  # [kg C/m²/yr] Gaia 루프 A: 사체 분해 → CO₂
        organic_to_soil  = 0.0  # [kg C/m²/yr] Gaia 루프 B: 사체 → 토양 환류

        # ── Gaia 루프 A+B: 사체 분해 (biomass 사망률 × 각 pool) ───────────────
        # 잎·싹·줄기 낙엽 분해
        litter_rate = (M_LEAF  * self.B_leaf
                       + M_STEM * self.B_sprout
                       + M_STEM * self.B_stem)
        # 고사목(나무·열매) 분해
        wood_rate   = (M_WOOD  * self.B_wood
                       + M_FRUIT * self.B_fruit)

        # [루프 A] 분해 → CO₂ 대기 방출 [kg C/m²/yr]
        co2_from_decomp = (litter_rate * (1.0 - ETA_LITTER)
                           + wood_rate  * (1.0 - ETA_WOOD_DECAY))

        # [루프 B] 분해 → humus(organic_layer) 환류 [kg C/m²/yr]
        organic_to_soil = (litter_rate * ETA_LITTER
                           + wood_rate  * ETA_WOOD_DECAY)
        self.organic_layer = max(0.0, self.organic_layer + organic_to_soil * dt_yr)

        # ── 2. 광합성 활성화 조건 ─────────────────────────────────────────────
        # [루프 C] CO₂/O₂/T는 env에서 직접 읽힘 → GPP·f_O2 계산에 즉시 반영
        #   env["CO2"] ↑ → GPP ↑ → delta_O2 ↑ → 대기 CO₂ 감소 (음성 피드백)
        if photo.photo_ready(self.organic_layer, self.pioneer_biomass, water_phase):

            GPP  = photo.gpp(F, CO2, T, f_W)
            Resp = photo.respiration(self.B_leaf, self.B_root, self.B_wood)
            NPP  = GPP - Resp
            o2_fac = photo.f_O2(O2)

            # ── 3. NPP 분배 (softmax — 탄소 회계 정합) ───────────────────────
            logits = {
                "leaf"  : A_LEAF_BASE  + A_LEAF_O2  * o2_fac,
                "root"  : A_ROOT_BASE,
                "stem"  : A_STEM_BASE  * (1.0 - o2_fac),   # 초기 단계 편향
                "wood"  : A_WOOD_BASE  + A_WOOD_O2  * o2_fac,
                "fruit" : A_FRUIT_BASE + A_FRUIT_O2 * o2_fac,
            }
            alloc = _softmax_alloc(logits)

            # 기관 성장 율 [kg C/m²/yr]
            d_B_leaf = alloc["leaf"]  * max(0.0, NPP) - M_LEAF * self.B_leaf
            d_B_root = alloc["root"]  * max(0.0, NPP) - M_ROOT * self.B_root

            # ── 4. Phase Gate ODE: 씨 → 싹 → 줄기 → 나무 → 열매 → 씨 ────────

            # (a) 씨 → 싹: 발아 게이트
            g_germ = _germ_gate(T, self.organic_layer, f_W)
            germ_rate = K_GERM * g_germ * self.B_seed          # [kg C/m²/yr]

            # (b) 싹 → 줄기: Michaelis-Menten Phase Gate
            gate_sprout = _sigmoid(self.B_sprout, B_SPROUT_HALF)
            sprout_to_stem_rate = K_SPROUT_TO_STEM * gate_sprout * self.B_sprout

            # (c) 줄기 → 목본: Michaelis-Menten Phase Gate
            gate_stem = _sigmoid(self.B_stem, B_STEM_HALF)
            stem_to_wood_rate = K_STEM_TO_WOOD * gate_stem * self.B_stem

            # (d) 나무 → 열매: 목본 성숙도 × O₂ 조건
            wood_maturity = _sigmoid(self.B_wood, B_WOOD_FRUIT_TH)
            fruit_rate = K_FRUIT * wood_maturity * o2_fac * self.B_wood

            # (e) 열매 → 씨: 결실 성숙
            fruit_to_seed_rate = K_FRUIT_TO_SEED * self.B_fruit

            # 씨 생산: NPP 분배 중 fruit alloc + 열매에서 전환
            seed_from_npp  = alloc["fruit"] * max(0.0, NPP)   # 직접 씨 분배
            seed_from_fruit = fruit_to_seed_rate               # 열매 성숙 → 씨

            # Phase Gate 상태변수 율 [kg C/m²/yr]
            d_B_sprout = (germ_rate
                          + alloc["stem"] * max(0.0, NPP)      # NPP 중 싹 분배
                          - sprout_to_stem_rate
                          - M_STEM * self.B_sprout)

            d_B_stem   = (sprout_to_stem_rate
                          - stem_to_wood_rate
                          - M_STEM * self.B_stem)

            d_B_wood   = (alloc["wood"] * max(0.0, NPP)
                          + stem_to_wood_rate
                          - fruit_rate
                          - M_WOOD * self.B_wood)

            d_B_fruit  = (fruit_rate
                          - fruit_to_seed_rate
                          - M_FRUIT * self.B_fruit)

            d_B_seed   = (seed_from_npp
                          + seed_from_fruit
                          - germ_rate                           # 발아로 소비
                          - M_SEED * self.B_seed)

            # ── 5. 적분: dt_yr 한 번만 곱함 ──────────────────────────────────
            self.B_leaf   = max(0.0, self.B_leaf   + d_B_leaf   * dt_yr)
            self.B_root   = max(0.0, self.B_root   + d_B_root   * dt_yr)
            self.B_sprout = max(0.0, self.B_sprout + d_B_sprout * dt_yr)
            self.B_stem   = max(0.0, self.B_stem   + d_B_stem   * dt_yr)
            self.B_wood   = max(0.0, self.B_wood   + d_B_wood   * dt_yr)
            self.B_fruit  = max(0.0, self.B_fruit  + d_B_fruit  * dt_yr)
            self.B_seed   = max(0.0, self.B_seed   + d_B_seed   * dt_yr)

            # ── 6. 대기 피드백 플럭스 [단위/yr, 면적당] ───────────────────────
            area_land = max(EPS, self.land_fraction)
            # [루프 A 통합] 순 탄소 플럭스 = 광합성 고정 - 호흡 - 분해 CO₂
            # 부호 규약: delta_CO2 < 0 → 대기 CO₂ 감소 (생물권이 흡수)
            #            delta_CO2 > 0 → 대기 CO₂ 증가 (생물권이 방출)
            net_C_flux = (GPP - Resp) - co2_from_decomp  # [kg C/m²/yr, land area]
            delta_CO2  = -net_C_flux / area_land
            delta_O2   =  (GPP - Resp) * (32.0 / 12.0) / area_land
            trans_rate = photo.transpiration_flux(self.B_leaf, F, f_W)

        # ── 광합성 비활성 시에도 분해 CO₂는 대기로 방출 ──────────────────────
        # (photo 블록 진입 못한 경우: delta_CO2=0 이지만 분해는 계속)
        if delta_CO2 == 0.0 and co2_from_decomp > 0.0:
            area_land = max(EPS, self.land_fraction)
            delta_CO2 = co2_from_decomp / area_land   # 분해만 있는 경우 양수(방출)

        latent_W = photo.latent_heat_W(trans_rate)

        # ── 7. 알베도 피드백 ──────────────────────────────────────────────────
        veg = 1.0 - math.exp(-VEG_COVER_SCALE * max(0.0,
                              self.B_leaf + self.B_stem + self.B_wood))
        A_land_new = ALBEDO_VEG_MIN + (ALBEDO_BARE_LAND - ALBEDO_VEG_MIN) * (1.0 - veg)
        delta_albedo_land = A_land_new - ALBEDO_BARE_LAND

        self.time_yr += dt_yr

        return {
            "delta_CO2":                 delta_CO2,
            "delta_O2":                  delta_O2,
            "transpiration_kg_per_m2_yr": trans_rate,
            "latent_heat_biosphere_W":   latent_W,
            "delta_albedo_land":         delta_albedo_land,
            "GPP":  GPP,
            "Resp": Resp,
            "NPP":  GPP - Resp,
            "photo_active": GPP > 0,
            # Gaia Attractor 루프 출력 (Phase 7d)
            "co2_from_decomp":  co2_from_decomp,   # [kg C/m²/yr] 사체 분해 → CO₂
            "organic_to_soil":  organic_to_soil,    # [kg C/m²/yr] 사체 → 토양 환류
            # edge AI 요약 출력
            "B_sprout": self.B_sprout,
            "B_stem":   self.B_stem,
            "B_wood":   self.B_wood,
            "B_fruit":  self.B_fruit,
            "B_seed":   self.B_seed,
        }

    # ── state snapshot ────────────────────────────────────────────────────────

    def state(self) -> BiosphereState:
        """현재 상태 스냅샷."""
        # succession_phase: 연속 스칼라 (0=pioneer ~ 4=fruit)
        phase = 0.0
        if self.organic_layer >= 0.5:
            phase = 1.0 + _sigmoid(self.B_sprout, B_SPROUT_HALF)
        if self.B_stem > 0.01:
            phase = 2.0 + _sigmoid(self.B_stem, B_STEM_HALF)
        if self.B_wood > 0.1:
            phase = 3.0 + _sigmoid(self.B_wood, B_WOOD_FRUIT_TH)
        if self.B_fruit > 0.01:
            phase = 4.0

        return BiosphereState(
            pioneer_biomass=self.pioneer_biomass,
            organic_layer=self.organic_layer,
            mineral_layer=self.mineral_layer,
            B_leaf=self.B_leaf,
            B_root=self.B_root,
            B_sprout=self.B_sprout,
            B_stem=self.B_stem,
            B_wood=self.B_wood,
            B_fruit=self.B_fruit,
            B_seed=self.B_seed,
            GPP=0.0, Resp=0.0, NPP=0.0,
            transpiration_flux=0.0,
            latent_heat_biosphere=0.0,
            photo_active=False,
            f_O2=photo.f_O2(0.0),
            succession_phase=phase,
        )
