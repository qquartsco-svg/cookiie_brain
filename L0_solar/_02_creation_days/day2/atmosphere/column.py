"""AtmosphereColumn — single-column radiative atmosphere with thermal inertia.

Phase 6a: 궁창 (Firmament)
바다(SurfaceOcean)와 하늘을 가르는 압력-온도 경계.

State variables:
  T_surface [K]           — evolves via energy balance ODE
  composition             — dynamic (modifiable by outgassing, chemistry, etc.)

Physics:
  Energy balance with thermal inertia:
    C · dT_s/dt = F_absorbed - F_radiated

    F_absorbed = F_solar · (1-A) / f
    F_radiated = σ · T_s⁴ · (1 - ε_a/2)

    온실 효과의 본질:
      단순 온도 상승이 아니라 복사 플럭스 재분배 + 시간 지연 + 열용량.
      낮/밤 온도차 감소, 계절 완충, 열 저장/방출 지연.

  Optical depth from composition:
    ε_a = 1 - exp(-τ)
    τ = f(CO₂, H₂O, CH₄) via greenhouse module

  Thermal timescale:
    τ_th = C / (4σT³(1 - ε_a/2))
    Earth (ocean-dominated): ~2 years

  Surface pressure:
    P = M_col · g

  Water phase:
    Liquid if T > 273.16 K and P > 611.73 Pa

Dependencies:
  Reads from: em/solar_luminosity (F), core/ (mass, radius, spin)
  Modifies: nothing in core/ or em/ (observer mode)

Units: SI internally (K, Pa, W/m², seconds)
       dt accepted in years (consistent with EvolutionEngine)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Dict

from ._constants import (
    SIGMA_SB, K_BOLTZ, G_SI, M_SUN_KG, AU_M, YR_S,
    WATER_TRIPLE_T, WATER_TRIPLE_P, MU_AIR, N_AVOGADRO, EPS,
)
from .greenhouse import (
    optical_depth, effective_emissivity, equilibrium_surface_temp,
    bare_equilibrium_temp, GreenhouseParams,
)
from .water_cycle import (
    saturation_mixing_ratio,
    evaporation_rate,
    latent_heat_flux,
)


@dataclass
class AtmosphereComposition:
    """Atmospheric gas mixing ratios [mol/mol].

    Dynamic state variables — modifiable by outgassing,
    photodissociation, biology, etc.
    """
    N2: float = 0.78
    O2: float = 0.0              # zero before Great Oxidation Event
    CO2: float = 400e-6          # 400 ppm (current Earth)
    H2O: float = 0.01            # 1% global average
    CH4: float = 1.8e-6          # 1.8 ppm
    Ar: float = 0.0093
    O3: float = 0.0              # ozone, depends on O₂ + UV

    column_mass: float = 1.0332e4   # total atmospheric column [kg/m²]
    mean_molecular_mass: float = MU_AIR  # [kg/mol]


@dataclass
class AtmosphereState:
    """Observable atmospheric state snapshot."""
    body_name: str
    time_yr: float

    # Temperatures
    T_surface: float              # [K]
    T_eq: float                   # [K] bare (no atmosphere)
    T_atm: float                  # [K] effective atmospheric layer
    greenhouse_dT: float          # [K] warming from greenhouse

    # Radiative
    optical_depth: float          # τ_IR
    emissivity_atm: float         # ε_a
    F_absorbed: float             # [W/m²] absorbed solar (global avg)
    F_radiated: float             # [W/m²] outgoing longwave
    net_flux: float               # [W/m²] imbalance driving dT/dt

    # Thermal dynamics
    heat_capacity: float          # C [J/(m²·K)]
    thermal_timescale_yr: float   # τ_th [yr]

    # Pressure & composition
    P_surface: float              # [Pa]
    composition: AtmosphereComposition
    albedo: float

    # Habitability
    water_phase: str              # "solid" / "liquid" / "gas"
    habitable: bool

    # Water cycle (Phase 6b, when enabled)
    evaporation_kg_ms2: float = 0.0    # E [kg/(m²·s)]
    latent_heat_flux_wm2: float = 0.0  # L_v × E [W/m²]


class AtmosphereColumn:
    """Single-column radiative atmosphere with thermal inertia.

    Parameters
    ----------
    body_name : str
        Planet name.
    surface_gravity : float
        Surface gravity [m/s²]. Earth = 9.81.
    albedo : float
        Bond albedo. Earth = 0.306.
    redistribution : float
        Heat redistribution factor.
        4.0 = uniform sphere (fast rotator).
        1.0 = substellar point only (tidally locked).
    composition : AtmosphereComposition or None
        Initial atmospheric composition. None → current Earth defaults.
    heat_capacity : float
        Surface+ocean heat capacity [J/(m²·K)].
        Earth ocean-dominated: ~2.1e8 (70m mixed layer × 4.2e6 J/(m³·K)).
        Earth land-only: ~1e6.
    greenhouse_params : GreenhouseParams or None
        Radiative transfer coefficients. None → Earth-calibrated.
    T_surface_init : float or None
        Initial surface temperature [K].
        None → start at 250 K and let it relax to equilibrium.
    tau_init : float or None
        Initial optical depth (Eden IC 연동 시). None → composition에서 계산.
    eps_a_init : float or None
        Initial effective emissivity (Eden IC 연동 시). None → tau에서 계산.
        tau_init, eps_a_init 이 둘 다 넘어오면 step()에서 τ/ε 재계산하지 않음 (더블카운트 방지).
    use_water_cycle : bool
        Enable latent heat and water vapor feedback (Phase 6b).
    h2o_relax_yr : float
        H₂O relaxation time toward saturation [yr]. ~0.1 = fast.
    """

    def __init__(
        self,
        body_name: str = "Earth",
        surface_gravity: float = 9.81,
        albedo: float = 0.306,
        redistribution: float = 4.0,
        composition: Optional[AtmosphereComposition] = None,
        heat_capacity: float = 2.1e8,
        greenhouse_params: Optional[GreenhouseParams] = None,
        T_surface_init: Optional[float] = None,
        tau_init: Optional[float] = None,
        eps_a_init: Optional[float] = None,
        use_water_cycle: bool = False,
        h2o_relax_yr: float = 0.1,
    ):
        self.body_name = body_name
        self.g = surface_gravity
        self.albedo = albedo
        self.redistribution = redistribution
        self.composition = (
            composition if composition is not None
            else AtmosphereComposition()
        )
        self.heat_capacity = heat_capacity
        self.gh_params = (
            greenhouse_params if greenhouse_params is not None
            else GreenhouseParams()
        )
        self.use_water_cycle = use_water_cycle
        self.h2o_relax_yr = h2o_relax_yr

        self.time_yr = 0.0
        self._F_solar_si = 1361.0
        self._E_evap = 0.0
        self._Q_latent = 0.0

        # Eden IC 연동: tau/eps_a 넘어오면 사용하고 재계산하지 않음 (더블카운트 방지)
        self._eden_locked_tau_eps = (
            tau_init is not None and eps_a_init is not None
        )
        if self._eden_locked_tau_eps:
            self._tau = float(tau_init)
            self._eps_a = float(eps_a_init)
        else:
            self._tau = self._compute_tau()
            self._eps_a = effective_emissivity(self._tau)

        self.T_surface = T_surface_init if T_surface_init is not None else 250.0

    # ── internal ──────────────────────────────────────

    def _compute_tau(self) -> float:
        return optical_depth(
            CO2=self.composition.CO2,
            H2O=self.composition.H2O,
            CH4=self.composition.CH4,
            params=self.gh_params,
        )

    # ── observables ───────────────────────────────────

    def surface_pressure(self) -> float:
        """Surface atmospheric pressure P = M_col × g  [Pa]."""
        return self.composition.column_mass * self.g

    def thermal_timescale_s(self) -> float:
        """Thermal relaxation timescale [seconds].

        τ_th = C / (4σT³(1 - ε_a/2))
        """
        if self.T_surface < 1.0:
            return float('inf')
        denom_factor = max(1.0 - self._eps_a / 2.0, EPS)
        return self.heat_capacity / (
            4.0 * SIGMA_SB * self.T_surface ** 3 * denom_factor
        )

    def water_phase(self) -> str:
        """Water phase from (T, P) relative to phase diagram."""
        P = self.surface_pressure()
        T = self.T_surface
        if T < WATER_TRIPLE_T:
            return "solid"
        if P < WATER_TRIPLE_P:
            return "gas"
        return "liquid"

    def habitable(self) -> bool:
        """Can liquid water exist stably at the surface?"""
        return self.water_phase() == "liquid"

    def equilibrium_temp(self, F_solar_si: float) -> float:
        """Equilibrium T_surface for given flux (with current ε_a)."""
        return equilibrium_surface_temp(
            F_solar_si, self.albedo, self.redistribution, self._eps_a,
        )

    def bare_eq_temp(self, F_solar_si: float) -> float:
        """Bare T_eq (no atmosphere) for reference."""
        return bare_equilibrium_temp(
            F_solar_si, self.albedo, self.redistribution,
        )

    def surface_heat_flux(self) -> float:
        """Net heat flux at surface [W/m²].

        Positive = surface warming, negative = cooling.
        Includes latent heat when use_water_cycle is True.
        Output port for SurfaceOcean coupling (Phase 6b).
        """
        denom_factor = max(1.0 - self._eps_a / 2.0, EPS)
        F_in = self._F_solar_si * (1.0 - self.albedo) / self.redistribution
        F_out = SIGMA_SB * self.T_surface ** 4 * denom_factor
        return F_in - F_out - self._Q_latent

    # ── time evolution ────────────────────────────────

    def step(self, F_solar_si: float, dt_yr: float, extra_latent_heat_Wm2: Optional[float] = None):
        """Advance surface temperature by dt.

        Solves:  C · dT_s/dt = F_absorbed - F_radiated - Q_latent

        Uses linearized implicit integration for numerical stability.
        When use_water_cycle: adds latent heat and H₂O feedback.
        Optional extra_latent_heat_Wm2: biosphere/other source [W/m²] added to F_out.

        Parameters
        ----------
        F_solar_si : float
            Incoming stellar flux at planet distance [W/m²].
            Get from solar_luminosity.irradiance_si(r).
        dt_yr : float
            Time step [years].
        extra_latent_heat_Wm2 : float
            Additional latent heat flux [W/m²] (e.g. from biosphere transpiration).
        """
        self._F_solar_si = F_solar_si
        dt_s = dt_yr * YR_S

        # Eden IC 연동 시 τ/ε 재계산하지 않음 (더블카운트 방지)
        if not getattr(self, '_eden_locked_tau_eps', False):
            self._tau = self._compute_tau()
            self._eps_a = effective_emissivity(self._tau)

        denom_factor = max(1.0 - self._eps_a / 2.0, EPS)

        F_in = F_solar_si * (1.0 - self.albedo) / self.redistribution
        F_out = SIGMA_SB * self.T_surface ** 4 * denom_factor

        self._E_evap = 0.0
        self._Q_latent = 0.0

        if self.use_water_cycle and self.water_phase() == "liquid":
            P = self.surface_pressure()
            q_actual = 0.622 * self.composition.H2O  # kg/kg from mol/mol approx
            self._E_evap = evaporation_rate(
                self.T_surface, P, q_actual,
            )
            self._Q_latent = latent_heat_flux(self._E_evap, self.T_surface)
            F_out = F_out + self._Q_latent

            # H₂O relaxation toward saturation
            q_sat = saturation_mixing_ratio(self.T_surface, P)
            w_sat = q_sat / 0.622
            tau_h2o_s = self.h2o_relax_yr * YR_S
            dH2O = (w_sat - self.composition.H2O) * (dt_s / tau_h2o_s)
            self.composition.H2O = np.clip(
                self.composition.H2O + dH2O, 1e-6, 0.5,
            )

        # Biosphere or other extra latent heat (e.g. transpiration)
        if extra_latent_heat_Wm2 is not None:
            F_out = F_out + float(extra_latent_heat_Wm2)

        # Linearized implicit
        dF_dT = 4.0 * SIGMA_SB * self.T_surface ** 3 * denom_factor
        net = F_in - F_out

        if self.heat_capacity > EPS:
            ratio = dt_s / self.heat_capacity
            dT = ratio * net / (1.0 + ratio * dF_dT)
            self.T_surface = max(self.T_surface + dT, 2.7)

        self.time_yr += dt_yr

    # ── snapshot ──────────────────────────────────────

    def state(self, F_solar_si: Optional[float] = None) -> AtmosphereState:
        """Full atmospheric state snapshot.

        Parameters
        ----------
        F_solar_si : float or None
            Solar flux for reference. None → last value from step().
        """
        F = F_solar_si if F_solar_si is not None else self._F_solar_si

        T_eq = self.bare_eq_temp(F)
        T_atm = self.T_surface / 2.0 ** 0.25 if self._eps_a > 0.01 else 0.0

        denom_factor = max(1.0 - self._eps_a / 2.0, EPS)
        F_in = F * (1.0 - self.albedo) / self.redistribution
        F_out = SIGMA_SB * self.T_surface ** 4 * denom_factor

        tau_th_yr = self.thermal_timescale_s() / YR_S

        F_rad = SIGMA_SB * self.T_surface ** 4 * denom_factor
        net = F_in - F_rad - self._Q_latent

        return AtmosphereState(
            body_name=self.body_name,
            time_yr=self.time_yr,
            T_surface=self.T_surface,
            T_eq=T_eq,
            T_atm=T_atm,
            greenhouse_dT=self.T_surface - T_eq,
            optical_depth=self._tau,
            emissivity_atm=self._eps_a,
            F_absorbed=F_in,
            F_radiated=F_rad,
            net_flux=net,
            heat_capacity=self.heat_capacity,
            thermal_timescale_yr=tau_th_yr,
            P_surface=self.surface_pressure(),
            composition=self.composition,
            albedo=self.albedo,
            water_phase=self.water_phase(),
            habitable=self.habitable(),
            evaporation_kg_ms2=self._E_evap,
            latent_heat_flux_wm2=self._Q_latent,
        )
