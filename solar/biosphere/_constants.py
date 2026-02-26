"""Biosphere physical constants and defaults.

Units: biomass [kg C/m²], time [yr], flux [W/m²], composition [mol/mol].

Pioneer 파라미터 현실 근거 (지구 전체 스케일):
  - 이끼·지의류 실제 NPP: ~0.001~0.005 kg C/m²/yr (척박 암석 환경)
    현재 R_PIONEER = 0.001 (암반 위 지의류 수준)
  - 사망률: 지의류 수명 수백년 → M_PIONEER = 0.005 /yr (200년 수명 근사)
  - 유기물 전환: 사체 일부만 humus로 → ETA_ORGANIC = 0.05 (5%)
  - 분해 속도: 한냉·건조 환경에서 느림, 그러나 열대는 빠름
    LAMBDA_DECAY = 0.02 (평균 50년 반감기 수준)
  - 토양 임계값: 식물이 착근하려면 humus층 수 cm 이상 필요
    지구 평균 1m²당 ~1~3 kg C/m² (표층 토양 유기탄소 밀도 참고)
    여기선 0D 글로벌 모델이므로 ORGANIC_THRESHOLD = 1.5 kg C/m²
  - PIONEER_THRESHOLD 제거(0으로) — organic_layer 만으로 판정
    (pioneer 자체가 식물 착근 조건이 되면 물리적으로 부정확)
"""

# —— Pioneer (harsh-environment) — 물리 기반 파라미터 ——————————
# 설계 목표: 지구 전체 0D 모델에서 ~500~2,000년 내 토양 임계 도달
# (용암지대 300~500년, 고위도 암반 1,000~3,000년 관측값의 중간)

T_MID_PIONEER   = 283.0   # [K] 지의류 최적 온도 (10°C)
SIGMA_T_PIONEER = 40.0    # [K] 광범위 온도 허용 (지의류 특성)

# 로지스틱 성장 파라미터
R_PIONEER       = 0.08    # [1/yr] 내재 성장률. 지의류 실측 ~0.05~0.1/yr
M_PIONEER       = 0.005   # [1/yr] 사망률 (수명 ~200년)
K0_CARRYING     = 0.05    # [kg C/m²] 돌땅에서 최소 수용 용량
K_SOIL_FEEDBACK = 8.0     # 토양 피드백 계수: K = K0 + K_soil * organic
                           # organic=0.1 → K=0.85, organic=0.5 → K=4.05

# 풍화 (Weathering) — pioneer가 암석을 깎는 속도
W_WEATHERING    = 0.002   # [kg mineral / (kg C · yr)] 풍화 속도
                           # 현실: 지의류 연간 암석 풍화 ~0.001~0.005 mm/yr 근사

# 광물 → humus 안정화 기여율
W_MINERAL_HUMUS = 0.0003  # [kg C / (kg mineral · yr)]
                           # 광물 입자가 유기물 분해를 늦추는 효과

# Humus 전환·분해
ETA_ORGANIC     = 0.08    # 사체 → humus 전환율 (8%. 대부분은 CO2로 호흡)
LAMBDA_DECAY    = 0.003   # [1/yr] humus 기본 분해속도 (반감기 ~330년, 한냉 암반)
LAMBDA_T_SCALE  = 2.0     # Q10 계수 (온도 10K → 분해속도 2배)

# 토양 임계값
ORGANIC_THRESHOLD = 0.5   # [kg C/m²] 식물 착근 가능 원시 토양
                           # (엄밀한 1.5보다 낮춤 — 0D 글로벌 모델 스케일 보정)
PIONEER_THRESHOLD = 999.0 # 사실상 비활성 — organic 만으로 판정

# —— Photosynthesis (light–CO2–T–water) ——————————————————————
P_MAX = 2.0                   # [kg C/m²/yr] max GPP
F_HALF = 100.0                # [W/m²] light saturation
K_C = 40e-6                   # [mol/mol] CO2 half-saturation (~40 ppm scale)
T_OPT = 298.0                 # [K] optimum T
SIGMA_T_PHOTO = 15.0          # [K] temperature tolerance
K_RESP_LEAF = 0.5             # [1/yr]
K_RESP_ROOT = 0.3
K_RESP_WOOD = 0.05
# —— 기준 NPP 분배 비율 (Base allocation logits — softmax로 정규화됨) ————
# 설계: alloc = softmax(base + delta(O2, soil))
# 합이 1이 되지 않아도 됨 — softmax가 정규화
A_LEAF_BASE = 2.0             # 잎: 초기 초본 단계에서 높음
A_ROOT_BASE = 1.5             # 뿌리: 항상 일정 비중
A_WOOD_BASE = 0.5             # 줄기/목본: 초기엔 낮음, O₂↑ 로 증가
A_STEM_BASE = 1.0             # 줄기(초본): 싹→줄기 단계
A_FRUIT_BASE = 0.2            # 열매: 성숙 후 증가

# O₂ 조건에 따른 분배 조정 계수
A_WOOD_O2   = 3.0             # O₂ 높을수록 목본 비중↑
A_FRUIT_O2  = 2.0             # O₂ 높을수록 결실 비중↑
A_LEAF_O2   = -1.5            # O₂ 높을수록 잎 비중↓ (성숙 신호)

# 사망률 [1/yr] — 순수 율(rate), dt는 적분에서만 1회 적용
M_LEAF  = 0.5                 # 잎: ~2년 수명
M_ROOT  = 0.15                # 뿌리: ~7년
M_WOOD  = 0.02                # 목본: ~50년 수명
M_STEM  = 0.3                 # 초본 줄기: ~3년
M_FRUIT = 1.5                 # 열매: ~0.7년 (계절성)
M_SEED  = 0.15                # 씨: 장기 저장 가능

# —— Phase Gate: 씨 → 싹 → 줄기 → 나무 → 열매 ————————————————
# 발아 게이트
K_GERM          = 0.5         # [1/yr] 발아율 (~2년)
GERM_SOIL_HALF  = 0.4         # [kg C/m²] 발아 토양 반포화
GERM_T_MIN      = 275.0       # [K] 발아 최저 온도 (2°C)
GERM_T_OPT      = 295.0       # [K] 발아 최적 온도 (22°C)
GERM_T_MAX      = 313.0       # [K] 발아 최고 온도 (40°C)

# 싹(sprout) → 줄기(stem) 전환
# 관측 근거: 유묘 → 초본 줄기 ~1~5년
K_SPROUT_TO_STEM = 0.25       # [1/yr] (~4년)
B_SPROUT_HALF    = 0.15       # [kg C/m²] 전환 반포화

# 줄기(stem) → 목본(wood) 전환
# 관측 근거: 초본 → 목질화 ~5~20년
K_STEM_TO_WOOD  = 0.08        # [1/yr] (~12년)
B_STEM_HALF     = 0.3         # [kg C/m²] 전환 반포화

# 결실(fruiting): 목본 성숙 후 열매 생산
# 관측 근거: 성목 → 첫 결실 ~5~20년 (수종별)
K_FRUIT         = 0.15        # [1/yr] (~7년 성숙 후)
B_WOOD_FRUIT_TH = 1.0         # [kg C/m²] 열매 생산 시작 목본 임계
# 열매 → 씨 전환
K_FRUIT_TO_SEED = 0.8         # [1/yr] (1계절 내 성숙)

# —— 하위 호환 alias (photo.py 등 기존 코드 호환) ———————————————————
A_LEAF = A_LEAF_BASE
A_ROOT = A_ROOT_BASE
A_WOOD = A_WOOD_BASE
A_SEED = A_FRUIT_BASE
B_THRESHOLD_SEED = 0.2
K_SEED = 0.1

# —— Gaia Attractor: 사체 분해 → CO₂ 방출 + 토양 환류 ————————————
# 설계 목표: 죽은 biomass(잎·줄기·나무)가 분해되어
#   → CO₂ 대기 방출 (탄소 순환 닫힘)
#   → 일부는 humus로 전환 (토양 갱신)
# 관측 근거:
#   - 열대 낙엽 분해: ~1년, 한냉 목본: ~50~200년
#   - humus 전환율: 사체의 ~5~15%가 안정 humus 됨

# 분해 시 humus 전환 비율 (나머지는 CO₂로 방출)
ETA_LITTER       = 0.08       # 잎·줄기 낙엽 → humus 8%
ETA_WOOD_DECAY   = 0.12       # 고사목 → humus 12% (느린 분해, 고품질 humus)

# CO₂ 방출 비율 (1 - ETA_LITTER 등은 암묵적으로 CO₂)
# 명시적 상수로 관리 (설계 의도 문서화)
CO2_FROM_LITTER  = 1.0 - ETA_LITTER    # ≈ 0.92 (잎 사체의 92%가 CO₂)
CO2_FROM_WOOD    = 1.0 - ETA_WOOD_DECAY # ≈ 0.88 (목본 사체의 88%가 CO₂)

# —— O2-dependent (respiration / successional) ———————————————————
K_O2 = 0.01                   # [mol/mol] O2 half-saturation for f_O2
O2_THRESHOLD = 0.005          # [mol/mol] ~0.5% O2 for "respiration plants"

# —— Transpiration / latent heat ——————————————————————————————
K_TRANS = 0.5e-6              # [kg H2O/(W·m⁻²·yr)] scaling leaf → transpiration
L_V_REF = 2.5e6               # [J/kg] latent heat vaporization (match atmosphere)
YR_S = 3.15576e7              # [s] Julian year

# —— Albedo feedback (simplified) ———————————————————————————————
ALBEDO_BARE_LAND = 0.30
ALBEDO_VEG_MIN = 0.12         # full vegetation
VEG_COVER_SCALE = 2.0         # how fast albedo drops with biomass

EPS = 1e-30
