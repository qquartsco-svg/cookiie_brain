# 독립 모듈 → GitHub 단독 레포 분리 가능 여부 점검

**목적**: 현재 CookiieBrain 내 모듈 중 **깃허브 레포에 완전히 따로 올려도 되는 수준**인지 점검한다.  
(qquartsco-svg 쪽에 이미 cookiie_brain, GaiaFire_Engine, WellFormation_Engine 등이 별도 레포로 있는 구조를 전제로, **추가로 분리 가능한 것**을 정리)

---

## 1. “단독 레포 가능” 판정 기준

| 항목 | 설명 |
|------|------|
| **의존성** | 해당 폴더만 clone 했을 때 `solar.*`, `cookiie_brain` 등 부모 레포 import 없이 동작 (또는 선택적 의존만 있고 없을 때 graceful fallback). |
| **진입점** | `pip install -e .` 또는 `python -m 패키지.데모` 로 설치·실행 가능한 구조. |
| **패키지 메타** | `pyproject.toml` 또는 `setup.py` + `requirements` 명시. |
| **문서** | README에 설치 방법, 최소 사용 예시, 의존성(numpy 등) 명시. |
| **경로 가정** | 데모/테스트가 `sys.path.insert(0, '상위레포')` 에만 의존하지 않음 — 패키지 설치로 해결 가능. |

---

## 2. 후보별 점검 결과

### 2.1 solar/eden (에덴 시스템)

| 항목 | 상태 | 비고 |
|------|------|------|
| **의존성** | ✅ 코어는 numpy만. Day2/Day7 없이 동작. | eden_demo 1곳만 `solar.day2.greenhouse` 사용(데모용 T 추정). |
| **진입점** | ⚠️ 부족 | `python -m solar.eden.eden_demo` 는 **solar** 가 상위에 있을 때만 동작. 단독 레포면 `eden` 이 루트 패키지여야 함. |
| **패키지 메타** | ❌ 없음 | `pyproject.toml` / `setup.py` / `requirements.txt` 없음. |
| **문서** | ✅ 있음 | solar/eden __init__ docstring, docs/EDEN_CONCEPT.md, EDEN_STANDALONE_CHECK.md. |
| **경로 가정** | ⚠️ 있음 | eden_demo: `sys.path.insert(0, '..', '..')` → 단독 레포에선 패키지 설치로 대체 필요. |

**결론**: **거의 가능. 손보면 단독 레포 가능.**

- **필요 작업**  
  1. **pyproject.toml** 추가: `name = "eden-system"` (또는 `solar-eden`), `dependencies = ["numpy"]`, 패키지 디렉터리 `eden` 또는 `solar_eden`.  
  2. **단독 레포 구조**: 루트에 `eden/` (현재 solar/eden 내용) + `pyproject.toml`. clone 후 `pip install -e .` → `from eden import make_firmament, make_flood_engine`.  
  3. **eden_demo**  
     - 옵션 A: `solar.day2.greenhouse` 제거 → initial_conditions 내부 T 계산만 사용 (완전 독립).  
     - 옵션 B: greenhouse 사용 부분을 try/except ImportError로 감싸서, 없으면 “T 추정 생략” 등으로 표시.  
  4. **데모 실행**: `python -m eden.eden_demo` 가 패키지 루트 기준으로 동작하도록 (sys.path 수정 제거 또는 상대 경로 제거).

---

### 2.2 solar/engines — 전체 vs 개별 Well

| 대상 | 의존성 | 단독 레포 가능 여부 |
|------|--------|----------------------|
| **engines/ 전체** (현재 구조) | ❌ `solar.engines.__init__` 이 `..day2`, `..day3`, … re-export | **불가** — solar 없으면 동작 안 함. |
| **개별 Well 폴더** (01~12) | ✅ 각 well 내부는 stdlib(+numpy 일부)만 사용하는 복사본 | **가능** — 폴더만 복사하면 동작하도록 설계됨. |

**개별 Well 예: 08_orbit_well**

- `orbit_engine.py`: stdlib만 (math, dataclasses, typing). **solar 미참조.**  
- README: `sys.path.insert(0, '.')` 후 `from orbit_engine import MilankovitchCycle`.  
- **부족한 것**:  
  - `pyproject.toml` (또는 setup.py) 없음.  
  - `pip install -e .` 후 `from orbit_well import MilankovitchCycle` 같은 공식 진입점 없음.  
  - 의존성 명시(requirements) 없음.

**결론**:  
- **engines/ 통째로**는 현재 구조로는 **단독 레포 불가**.  
- **01~12 각 Well 폴더**는 **코드는 단독 가능**. 각 Well을 별도 레포로 올리려면:  
  - 해당 Well 폴더를 레포 루트로 두고,  
  - `pyproject.toml` + README 설치/사용법 추가하면 **“완전히 따로 레포에 올려도 되는” 수준**까지 갈 수 있음.

---

### 2.3 solar 전체 / Day7

| 대상 | 의존성 | 단독 레포 가능 여부 |
|------|--------|----------------------|
| **solar 전체** | day1~7, eden, bridge, cognitive 내부 상호 참조 | **통합 패키지**로만 의미 있음. 이미 **cookiie_brain** 레포가 이 통합을 담는 구조로 보임. |
| **Day7 단독** | eden, day2~day6 전부 사용 | Day7만 따로 레포로 올리면 **solar(또는 eden+day*) 의존**을 반드시 명시해야 하고, 그 의존 레포들도 함께 배포/설치 가능해야 함. 단독 “완전 독립” 레포는 아님. |

---

## 3. 요약 표 — “지금 바로 단독 레포 가능?” 여부

| 모듈 | 지금 바로 단독 레포 가능? | 필요한 작업 (최소) |
|------|--------------------------|---------------------|
| **solar/eden** | ⚠️ 거의 됨 | pyproject.toml, 패키지 루트를 `eden`으로 하는 구조, eden_demo의 day2 1곳 제거/옵션, sys.path 정리 |
| **solar/engines/01~12 개별 Well** | ⚠️ 코드는 됨 | 각 Well별 pyproject.toml + README 설치/의존성, 진입점 정리 |
| **solar/engines 전체** | ❌ | 현재는 solar re-export → 구조 변경 없이는 단독 레포 불가 |
| **solar 전체** | — | 통합 패키지(cookiie_brain)로 이미 레포 존재 가능성 → “단독”이 아니라 통합 레포로 유지 |
| **Day7 단독** | ❌ | eden·day2~6 의존 필수 → 의존 패키지 함께 배포해야 함 |

---

## 4. 권장 순서 (단독 레포로 올리려면)

1. **에덴 (solar/eden)**  
   - 위 “필요 작업” 반영 후 **Eden_Engine** 또는 **Eden_System** 같은 이름으로 새 레포 생성.  
   - 의존성: `numpy` 만 명시하면 됨.  
   - 기존 qquartsco-svg의 `GaiaFire_Engine`, `WellFormation_Engine` 패턴과 맞추기 좋음.

2. **12 Well 개별**  
   - 원하면 `Orbit_Engine`(08), `Stress_Engine`(06) 등 **이미 독립 복사본인 Well**부터 pyproject.toml + README 추가해 하나씩 단독 레포로 올리기.  
   - 12개 전부 동일 패턴으로 정리 가능.

3. **solar/engines 통합**  
   - 단독 레포로 쓰려면 “solar re-export”를 제거하고, 각 Well을 서브패키지로 넣은 **새 통합 패키지**로 재구성해야 함. 현재 구조 그대로는 “완전히 따로” 레포 불가.

---

## 5. 최종 답

- **“완전히 따로 깃허브 레포에 올려도 되는 수준”**인 것은:  
  - **solar/eden** → **거의 됨.** pyproject.toml + 진입점 + eden_demo 1곳 정리하면 **단독 레포 가능.**  
  - **solar/engines 아래 01~12 개별 Well** → **코드는 단독 가능.** 각 Well마다 패키지 메타·README만 보강하면 **단독 레포 가능.**  
- **그대로는 안 되는 것**:  
  - **solar/engines 전체** (현재 re-export 구조), **Day7 단독** (상위 의존 필수).

이 문서는 점검 시점 스냅샷이다. 패키지 메타 추가·경로 정리 후 다시 한 번 위 기준으로 검증하면 된다.
