# 에덴 독립 모듈 확인 (solar/eden)

**목적**: solar/eden 이 **독립 모듈**로 동작하는지, 외부(solar.day*) 의존을 어디서 쓰는지 정리한다.

---

## 1. 독립 모듈 판정 기준 (STANDALONE_ENGINES_POLICY 기준)

- 입력 포트가 명확 (params / env dict)
- 상태(state) 캡슐화
- 다른 레이어는 **읽기/쓰기 포트**로만 연결 (내부에서 `from solar.dayX` 없거나 최소·선택적)

---

## 2. solar/eden 내부 → 외부 의존

| 파일 | 외부 의존 | 용도 | 독립 여부 |
|------|-----------|------|-----------|
| **firmament.py** | 없음 | 궁창 상태·전이 | ✅ 완전 독립 (stdlib만) |
| **flood.py** | 없음 | 대홍수 엔진 | ✅ 완전 독립 (stdlib만) |
| **initial_conditions.py** | `numpy` | IC·밴드 동역학 | ✅ 독립 (numpy만) |
| **geography.py** | 없음 | 지형·자기장·노출 지역 | ✅ 완전 독립 (stdlib만) |
| **biology.py** | `.initial_conditions` (eden 내부) | 수명·체형·생물 인자 | ✅ eden 내부만 의존 |
| **search.py** | `..day7.runner` (선택적) | `deep_validate()` 안에서만, try/except ImportError | ⚠️ **선택적** — Day7 없어도 search/스크리닝 동작 |
| **eden_demo.py** | `solar.day2.atmosphere.greenhouse` | 데모에서 "추정 T_surface" 출력용 1곳 | ⚠️ **데모 전용** — 코어와 무관 |

요약:

- **코어 에덴** (firmament, flood, initial_conditions, geography, biology): **solar.day* 전혀 안 씀.** numpy만 (initial_conditions). → **독립 모듈**.
- **search**: Day7은 `deep_validate()` 안에서만 사용하고, **import 실패 시 스킵**하므로 Day7 없이도 탐색·스크리닝·에덴 점수는 그대로 동작. → **실질적으로 독립**.
- **eden_demo**: day2 greenhouse는 **데모 스크립트 한 곳**뿐. 코어 에덴만 쓰는 사용처는 독립.

---

## 3. 외부 → solar/eden 의존 (누가 eden을 쓰는가)

| 호출처 | 사용 내용 |
|--------|-----------|
| **solar/day7/runner.py** | `eden.geography.magnetic_protection_factor`, `eden.initial_conditions.make_antediluvian` (옵션) |
| docs, 예제 | `from solar.eden import ...` |

→ **에덴은 “제공자”**, Day7이 “소비자”. 에덴 쪽이 Day1~6를 import하지 않으므로 **에덴을 별도 패키지로 분리해도 되고**, Day7만 eden을 의존하도록 두면 됨.

---

## 4. 모듈별 독립성 요약

| 모듈 | 외부 의존 | 독립 모듈 여부 |
|------|-----------|----------------|
| FirmamentLayer / FloodEngine | 없음 | ✅ 독립 |
| InitialConditions / make_antediluvian 등 | numpy | ✅ 독립 (numpy만) |
| EdenGeography / magnetic_protection_factor | 없음 | ✅ 독립 |
| EdenSearchEngine / compute_eden_score | Day7은 deep_validate 시 선택적 | ✅ 독립 (Day7 없어도 동작) |
| BiologyFactors / compute_biology | eden 내부만 | ✅ 독립 |
| eden_demo.py | day2 greenhouse (데모 1곳) | ⚠️ 데모만 비독립 — 코어는 독립 |

---

## 5. 결론

- **에덴(solar/eden)은 독립 모듈로 쓸 수 있다.**
  - Day1~6를 전혀 import하지 않음.
  - Day7은 **search의 deep_validate**에서만 선택적으로 사용하고, 없으면 스킵.
  - 유일한 비독립 사용처는 **eden_demo.py**의 day2 greenhouse 한 줄(데모용 T 추정)뿐.

- **완전 독립으로 쓰려면 (선택 사항)**  
  - eden_demo에서 `solar.day2.atmosphere.greenhouse` 대신, initial_conditions에 이미 있는 `_optical_depth`·T 계산을 쓰거나,  
  - 데모 전용 플래그로 “T 추정 표시 안 함”으로 두면 **solar 전부 없이** 에덴만으로도 실행 가능.

이 문서는 점검용 스냅샷이다. 코드 변경 시 의존성만 다시 확인하면 된다.
