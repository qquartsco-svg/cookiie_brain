"""Biosphere physical constants and defaults.

Units: biomass [kg C/m²], time [yr], flux [W/m²], composition [mol/mol].
"""

# —— Pioneer (harsh-environment) —————————————————————————————
T_MID_PIONEER = 283.0          # [K] broad optimum center
SIGMA_T_PIONEER = 40.0        # [K] wide tolerance
R_PIONEER = 0.02              # [kg C/m²/yr] max pioneer NPP rate
M_PIONEER = 0.1               # [1/yr] pioneer mortality
ETA_ORGANIC = 0.3             # fraction of dead pioneer → organic_layer
LAMBDA_DECAY = 0.05           # [1/yr] organic layer decay
ORGANIC_THRESHOLD = 0.1       # [kg C/m²] min organic for photosynthesis
PIONEER_THRESHOLD = 0.05      # [kg C/m²] alternative threshold

# —— Photosynthesis (light–CO2–T–water) ——————————————————————
P_MAX = 2.0                   # [kg C/m²/yr] max GPP
F_HALF = 100.0                # [W/m²] light saturation
K_C = 40e-6                   # [mol/mol] CO2 half-saturation (~40 ppm scale)
T_OPT = 298.0                 # [K] optimum T
SIGMA_T_PHOTO = 15.0          # [K] temperature tolerance
K_RESP_LEAF = 0.5             # [1/yr]
K_RESP_ROOT = 0.3
K_RESP_WOOD = 0.05
A_LEAF = 0.4                  # NPP allocation
A_ROOT = 0.3
A_WOOD = 0.2
A_SEED = 0.1
M_LEAF = 0.8
M_ROOT = 0.2
M_WOOD = 0.02
B_THRESHOLD_SEED = 0.2        # [kg C/m²] biomass above which seed production
K_SEED = 0.1                  # seed production rate
M_SEED = 0.2                  # seed loss / germination rate
K_GERM = 0.3                  # germination rate when conditions OK

# —— O2-dependent (respiration / successional) ———————————————————
K_O2 = 0.01                   # [mol/mol] O2 half-saturation for f_O2
O2_THRESHOLD = 0.005          # [mol/mol] ~0.5% O2 for “respiration plants”

# —— Transpiration / latent heat ——————————————————————————————
K_TRANS = 0.5e-6              # [kg H2O/(W·m⁻²·yr)] scaling leaf → transpiration
L_V_REF = 2.5e6               # [J/kg] latent heat vaporization (match atmosphere)
YR_S = 3.15576e7              # [s] Julian year

# —— Albedo feedback (simplified) ———————————————————————————————
ALBEDO_BARE_LAND = 0.30
ALBEDO_VEG_MIN = 0.12         # full vegetation
VEG_COVER_SCALE = 2.0         # how fast albedo drops with biomass

EPS = 1e-30
