# Solar System Architecture

이 프로젝트는 **행성 형성 → 창조 → 생명 → 통제** 흐름을 기반으로 구성된  
행성 시뮬레이션 및 탐색 엔진이다.

---

## 전체 흐름

1. **Planet Exploration** — 태초 이전의 탐색 (JOE)
2. **Planet Construction** — 천지창조 환경 구축 (Day1~7)
3. **Creation (Genesis)** — 에덴 조성 및 통제 (Eden · Underworld)
4. **Eden System** — 에덴·인지·하데스·사이렌
5. **Underworld Monitoring** — 궁창 시대 → 홍수 Era

---

## 시스템 단계 (solar/)

| 단계 | 폴더 | 의미 |
|------|------|------|
| 1 | **_01_beginnings** | 행성 탐사 (조 JOE 엔진) |
| 2 | **_02_creation_days** | 천지창조 Day1~7, physics, fields, bridge, engines |
| 3 | **_03_eden_os_underworld** | 에덴·생물권·인지·통치·언더월드·모니터링 |
| 4 | **_04_firmament_era** | 궁창 환경시대 (firmament layer, 대기 안정) |
| 5 | **_05_noah_flood** | 노아 대홍수 이벤트 (붕괴·홍수 동역학) |

탐사 → 창조 → 에덴 → 궁창 → 홍수 순서가 번호로 고정되어 데이터 파이프라인의 직관성을 보장한다.

---

## Verification

구조 검증은 **프로젝트 루트(CookiieBrain)** 에서 실행한다.

```bash
cd /path/to/CookiieBrain
python solar/verify_imports.py
```

**검증 항목**

- 모듈 별칭 (solar.day1, solar.eden, solar.surface 등)
- import 경로 (_02_creation_days.day6, day3.surface 등)
- 엔진 심볼 (SurfaceSchema, EvolutionEngine, GaiaBridge, run_pipeline, BiosphereColumn 등)
- planet_dynamics = joe, surface = day3.surface

---

## Quick Test

**Pipeline (1단계)**

```bash
python -c "import solar; s=solar.run_pipeline(steps_per_stage={'beginnings':1,'creation':0,'eden':0,'firmament':0,'flood':0}); print('OK', s.joe_result)"
```

**Day7 runner 한 스텝**

```bash
python -c "
import solar
from solar._03_eden_os_underworld.eden.initial_conditions import make_antediluvian
from solar._02_creation_days.day7.runner import make_planet_runner
ic = make_antediluvian()
runner = make_planet_runner(initial_conditions=ic.to_runner_kwargs())
print('OK', type(runner.step(dt_yr=0.01)).__name__)
"
```

**Milankovitch 데모**

```bash
python -m solar._02_creation_days.day4.cycles.milankovitch_demo
```

---

## 관련 문서

| 문서 | 역할 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 시스템 개요 (이 문서) |
| [LAYER_FLOW.md](LAYER_FLOW.md) | 시간 흐름 |
| [FOLDER_MAP.md](FOLDER_MAP.md) | 실제 폴더 구조 |

---

## 다음 단계 제안

- **서사적 문서화**: 각 Phase 폴더(_01~_05) README에 “이 단계가 이전 단계의 물리 결과를 어떻게 인지 상태로 넘기는지” 서사 추가.
- **통합 테스트**: verify_imports 외에, 단계별 물리 수치가 정상 전달되는지 확인하는 integration_test 스위트 구성.
