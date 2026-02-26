# v1.4.0 atmosphere(궁창) 레이어 구성/일관성 점검 결과

**점검 기준**: README·VERSION_LOG·코드 정합성  
**경로**: `/mnt/data/` (업로드본) vs `/Users/jazzin/Desktop/00_BRAIN/CookiieBrain` (로컬)

---

## 1) 패키지 상태 — _constants.py

| 요구사항 | README/VERSION_LOG | `/mnt/data/` 업로드본 | 로컬 CookiieBrain |
|----------|-------------------|------------------------|---------------------|
| SIGMA_SB, K_BOLTZ, AU_M, YR_S … | atmosphere/_constants.py | ❌ EPS만 있음 | ✅ 전부 존재 |
| EPS_ZERO, EPS_GEOM | em/_constants.py | — | ✅ em/ 전용 |

**결론 (업로드본 기준)**  
업로드된 `_constants.py`는 **em/_constants.py** 용도(EPS 상수)로 보이며, atmosphere 전용 대기 상수가 없음.  
→ greenhouse.py/column.py 실행 시 atmosphere/_constants.py 상수 누락으로 **ImportError 확정**.

---

## 2) 패키지 __init__.py

| 요구사항 | README 사용예시 | `/mnt/data/` 업로드본 | 로컬 CookiieBrain |
|----------|----------------|------------------------|---------------------|
| `from solar import AtmosphereColumn, ...` | solar 루트 export | ❌ geometric_phase 등 다른 모듈 | ✅ solar/__init__.py에 atmosphere export |
| atmosphere/__init__.py | AtmosphereColumn, Composition 등 | ❌ atmosphere API 아님 | ✅ 정상 |

**역할 정리**  
- **solar/__init__.py**는 최상위 public API(README import 경로)를 보장한다.  
- **solar/atmosphere/__init__.py**는 atmosphere 레이어의 public API만 노출한다.

**결론 (업로드본 기준)**  
업로드된 `__init__.py`가 README에 적힌 import 경로와 맞지 않음.  
→ README 예시대로 import 시 **ImportError/AttributeError 가능**.

---

## 3) greenhouse.py, column.py — 설계 일치 여부

README 핵심 관계:
- τ → ε_a = 1 - exp(-τ)
- T_s = [F(1-A)/(f·σ·(1-ε_a/2))]^(1/4)
- C·dT/dt = F_in - F_out (열적 관성)

**결론**: greenhouse/column의 수식·구조는 README 설계와 **정합**.  
다만 **1) 상수 import**가 해결되어야 실제로 실행 가능.

---

## 4) water_cycle.py — Phase 6b 스타일

- README: Phase 6b = latent heat(증발·응결) 추가
- water_cycle.py: Clausius-Clapeyron, evaporation, latent_heat_flux 방향 일치

**갭**:
- 물리상수(잠열 등)가 atmosphere/_constants.py 또는 CONFIG로 **중앙화되지 않고** 파일 내부에 산재
- column.py `surface_heat_flux()`와 water_cycle 연동의 **시그니처·규약**이 문서/코드에 아직 완전히 고정되지 않음

**결론**: 6b는 "초안은 있으나, 정책·상수·결합 규약 정리 진행 중" 상태.

---

## 즉시 수정 필요 (실제 오류급)

### 1. atmosphere/_constants.py 복구

**(A) v1.4.0 실행 필수** (greenhouse/column이 직접 참조):

- SIGMA_SB, K_BOLTZ (또는 R_GAS)
- AU_M, YR_S
- WATER_TRIPLE_T, WATER_TRIPLE_P (water_phase 판정)
- (압력 계산에 쓰면) G_SI — 또는 g를 입력으로 받는 구조면 불필요

**(B) v1.4.0에서는 미사용 / 확장용** (6b~에서 필요):

- N_AVOGADRO, EPS
- MU_* (분자량들)
- M_SUN_KG 등 항성/궤도 단위용

EPS 상수(EPS_ZERO, EPS_GEOM)는 **em/_constants.py**에 유지.  
atmosphere/_constants.py는 위 대기 물리 상수 전용.

### 2. __init__.py 정리

**solar/__init__.py**:
```python
from .atmosphere import AtmosphereColumn, AtmosphereState, AtmosphereComposition, ...
```

**solar/atmosphere/__init__.py**:
```python
from .column import AtmosphereColumn, AtmosphereState, AtmosphereComposition
from .greenhouse import optical_depth, effective_emissivity, ...
from .water_cycle import saturation_vapor_pressure, evaporation_rate, ...
```

README 예시 `from solar import SolarLuminosity, AtmosphereColumn, AtmosphereComposition` 가 동작하려면 solar 루트에서 위 항목들을 export해야 함.

---

## 로컬 워크스페이스 상태 (참고)

`/Users/jazzin/Desktop/00_BRAIN/CookiieBrain` 기준:
- solar/atmosphere/_constants.py: ✅ 대기 상수 전부 존재
- solar/atmosphere/__init__.py: ✅ atmosphere API 정상
- solar/__init__.py: ✅ SolarLuminosity, AtmosphereColumn, AtmosphereComposition export
- solar/em/_constants.py: ✅ EPS_ZERO, EPS_GEOM만 보유

→ **로컬은 정합 상태**.  
업로드 과정에서 동일 파일명(_constants.py, __init__.py)이 서로 다른 레이어(em/ vs atmosphere/ vs solar/)에서 섞여 업로드된 것으로 보임. (경로 혼입/파일명 충돌)

---

## 다음 단계 (요청 시)

- **먼저** `/mnt/data` 업로드본을 로컬 패키지 구조(폴더 경로 포함) 그대로 다시 업로드/동기화해야 테스트가 의미가 있다. 깨진 패키지 대상 테스트는 "검증"이 아니라 "환경 오류 확인"이 되어버림.
- README 검증값(254K→288K, τ=1.56, ε_a=0.79, P≈101,357 Pa)이 실제 실행으로 재현되는지 **최소 단위 테스트 스크립트** 작성
- water_cycle 상수·규약 정리 및 surface_heat_flux 시그니처 문서화
