# 에덴 탐색 모듈만 독립 엔진화 — 가능 여부 및 방법

**질문**: 현재 solar 구조는 그대로 두고, **에덴 탐색 모듈만** 따로 독립 엔진(EdenSearch_Engine 같은 별도 레포)으로 만들 수 있는가?

**답**: **가능하다.**  
solar/eden 폴더는 **현 구조 그대로** 두고 깃허브 업데이트하고, **탐색 로직만** 별도 패키지로 분리하면 된다.

---

## 1. 현재 의존 관계

에덴 탐색(search.py)이 쓰는 것:

| 사용처 | 소스 | solar.day* 의존 |
|--------|------|------------------|
| InitialConditions, make_antediluvian, make_postdiluvian | solar/eden/initial_conditions.py | 없음 (numpy만) |
| EdenGeography, make_eden_geography, magnetic_protection_factor | solar/eden/geography.py | 없음 (stdlib만) |
| deep_validate() 안에서 PlanetRunner | solar/day7/runner | 있음 → try/except로 **선택적** (없으면 스킵) |

→ **탐색 코어**는 이미 **solar.day*에 전혀 안 묶여 있음.**  
IC·Geography는 둘 다 eden 안에 있고, 그 안에는 numpy·stdlib만 씀.

---

## 2. 독립 엔진 레포에 넣을 것

**EdenSearch_Engine** (또는 `eden-search-engine`) 같은 **별도 레포**에 아래만 넣으면 된다.

1. **탐색 로직**  
   - EdenCriteria, EdenCandidate, SearchSpace, SearchResult  
   - EdenSearchEngine, compute_eden_score, compute_band_eden_scores  
   - make_eden_search, make_antediluvian_space, make_postdiluvian_space, make_exoplanet_space  

2. **IC 생성**  
   - InitialConditions, EarthBandState  
   - initial_conditions.py의 동역학 함수들  
     (_optical_depth, _T_surface, _pole_eq_delta, _band_temperatures, _soil_moisture, _gpp_per_band, _mutation_factor)  
   - make_antediluvian, make_postdiluvian  
   - 의존성: **numpy**만 필요.

3. **Geography 쪽**  
   - 탐색에서 쓰는 건 `geo.band_protection()` / `magnetic_protection_factor(lat)` 뿐.  
   - 독립 엔진에서는 **geo=None**일 때 이미  
     `magnetic_protection_factor(lat)` 로 대체하고 있음.  
   - 그때만 쓰면 되므로, **magnetic_protection_factor 하나만** 독립 엔진에 복사해 두면 됨 (geography.py 전체 불필요).  
   - 수식은 math만 쓰는 순수 함수.

4. **deep_validate**  
   - PlanetRunner는 **선택 기능**으로 유지.  
   - 독립 엔진에서는 `try: from ..day7.runner ... except ImportError: return []` 같은 식으로 두고,  
     **레포만 단독**이면 그냥 스킵되게 하면 됨.

정리하면:  
- **독립 엔진** = search 로직 + IC(동역학 포함) + magnetic_protection_factor.  
- 의존성: **numpy**.  
- solar/ 폴더는 전혀 필요 없음.

---

## 3. solar/eden 쪽은 어떻게 두는가

**현 구조 유지** 전제면 두 가지다 가능하다.

- **방식 A — 코드 두 군데**  
  - 독립 엔진 레포에 위 내용으로 새 패키지 구현.  
  - solar/eden/search.py는 **지금처럼 그대로** 두고,  
    계속 `from .initial_conditions import ...`, `from .geography import ...` 로 동작.  
  - CookiieBrain에서는 기존처럼 `from solar.eden import make_eden_search` 등 그대로 사용.  
  - 단점: search 로직이 두 레포에 있어서, 나중에 수정 시 동기화 필요.

- **방식 B — 단일 소스**  
  - 독립 엔진 레포에 위 내용으로 패키지 구현 후,  
    예: `pip install eden-search-engine`  
  - solar/eden/search.py 를 **얇은 래퍼**로만 둠:  
    - `from eden_search_engine import EdenSearchEngine, EdenCriteria, ...`  
    - InitialConditions / EdenGeography 는 **solar.eden** 에서만 가져와서,  
      엔진 생성 시 `EdenSearchEngine(..., geo=make_eden_geography())` 처럼 넘김.  
  - 이렇게 하면 “탐색 로직”은 독립 엔진 한 곳만 두고,  
    solar/eden은 **그걸 쓰는 쪽** + IC/Geography 제공만 담당.  
  - CookiieBrain 쪽 사용법은 그대로 `from solar.eden import make_eden_search` 유지 가능.

원하면 **방식 B**로 가면,  
- 지구 시스템(solar)은 그대로 두고 깃허브 업데이트하고,  
- **에덴 탐색만** 독립 엔진 레포로 분리해서 사용·배포할 수 있다.

---

## 4. 요약

| 질문 | 답 |
|------|----|
| solar/eden 구조 유지한 채 가능한가? | **가능.** solar/eden 은 그대로 두고, 탐색만 분리하면 됨. |
| 탐색만 독립 엔진으로 만들 수 있나? | **가능.** search + IC(동역학) + magnetic_protection_factor 만 넣으면 됨. |
| solar.day* / cookiie_brain 필수인가? | **아니오.** 독립 엔진은 numpy만 있으면 동작. |
| deep_validate(PlanetRunner)는? | **선택.** 독립 레포에서는 import 실패 시 스킵하면 됨. |

즉, **“현재 solar 구조에서 그대로 쓰면서, 에덴 탐색 모듈만 따로 독립 엔진화 할 수 있냐”**에 대한 답은 **예, 할 수 있다**이고,  
위와 같이 **독립 엔진 레포에 넣을 범위**와 **solar/eden 유지 방식(A/B)**만 정해주면 된다.
