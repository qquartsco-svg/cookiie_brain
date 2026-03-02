# underworld 레이어 정의 (불가침)

**목적**: 수정·보완 시 레이어가 꼬이지 않도록 **의존성 방향**을 고정한다.  
아래 순서만 유효. 위 레이어는 아래 레이어를 참조할 수 있으나, **아래 레이어는 위 레이어를 절대 참조하지 않는다.**

---

## 1. 레이어 순서 (아래 → 위)

```
  ┌─────────────────────────────────────────────────────────────┐
  │  진입점 (패키지 경계)  __init__.py — 조합만, 비즈니스 로직 없음  │
  └─────────────────────────────────────────────────────────────┘
                                    │
  ┌─────────────────────────────────────────────────────────────┐
  │  L2 전파 (Propagate/Transform only)                          │
  │  wave_bus.py, siren.py                                       │
  │  허용: consciousness, propagation  /  금지: hades, deep_monitor, rules, eden │
  └─────────────────────────────────────────────────────────────┘
                                    │
  ┌─────────────────────────────────────────────────────────────┐
  │  L1.5 전파 DTO (Propagation DTO)                            │
  │  propagation.py                                              │
  │  허용: (타입만 consciousness 참조, 런타임 의존 없음)          │
  │  금지: hades, wave_bus, siren, deep_monitor, rules, eden     │
  └─────────────────────────────────────────────────────────────┘
                                    │
  ┌─────────────────────────────────────────────────────────────┐
  │  L1 측정 (Measure only)                                      │
  │  hades.py                                                    │
  │  허용: consciousness, deep_monitor, rules                   │
  │  금지: propagation, wave_bus, siren, eden                   │
  └─────────────────────────────────────────────────────────────┘
                                    │
  ┌─────────────────────────────────────────────────────────────┐
  │  L0' 물리 어댑터 (선택 외부)                                 │
  │  deep_monitor.py                                             │
  │  허용: 표준 라이브러리, 선택 solar.day4.core                  │
  │  금지: consciousness, rules, hades, propagation, wave_bus, siren, eden │
  └─────────────────────────────────────────────────────────────┘
                                    │
  ┌─────────────────────────────────────────────────────────────┐
  │  L0 기반 (Foundation)                                        │
  │  consciousness.py, rules.py                                  │
  │  허용: 표준 라이브러리만                                      │
  │  금지: deep_monitor, hades, propagation, wave_bus, siren, eden │
  └─────────────────────────────────────────────────────────────┘
```

---

## 2. 파일별 허용/금지 의존성

| 파일 | 레이어 | 허용 import | 금지 import |
|------|--------|-------------|-------------|
| `consciousness.py` | L0 | 표준 라이브러리 | `deep_monitor`, `hades`, `rules`, `propagation`, `wave_bus`, `siren`, `solar.eden` |
| `rules.py` | L0 | 표준 라이브러리 | `consciousness`, `deep_monitor`, `hades`, `propagation`, `wave_bus`, `siren`, `solar.eden` |
| `deep_monitor.py` | L0' | 표준 라이브러리, (선택) `solar.day4.core` | `consciousness`, `rules`, `hades`, `propagation`, `wave_bus`, `siren`, `solar.eden` |
| `hades.py` | L1 | `consciousness`, `deep_monitor`, `rules` | `propagation`, `wave_bus`, `siren`, `solar.eden` |
| `propagation.py` | L1.5 | TYPE_CHECKING 시에만 `consciousness` (런타임 없음) | `hades`, `wave_bus`, `siren`, `deep_monitor`, `rules`, `solar.eden` |
| `wave_bus.py` | L2 | `consciousness`, `propagation` | `hades`, `siren`, `deep_monitor`, `rules`, `solar.eden` |
| `siren.py` | L2 | `propagation` | `consciousness`, `hades`, `wave_bus`, `deep_monitor`, `rules`, `solar.eden` |
| `__init__.py` | 진입점 | 위 모듈 전부 (re-export용) | 비즈니스 로직·분기 없이 re-export만 |

---

## 3. 외부 경계 (불가침)

- **underworld → solar.eden**: **절대 금지**. 어떤 모듈도 `solar.eden`, `eden_os`, `adam`, `homeostasis`, `integrity_fsm` 등을 import 하지 않는다.
- **데이터 흐름**: 호출은 항상 **지상(Runner)** → `hades.listen()` 또는 `wave_bus.propagate()` → … → 지상이 반환값을 observe/homeostasis/fsm에 주입. underworld는 "호출당하는" 쪽만 한다.

---

## 4. 수정 시 체크리스트

- 새 파일 추가 시: 이 표에 레이어·허용/금지를 추가하고, 상단 docstring에 `# Layer N. Allowed: ... Forbidden: ...` 명시.
- 기존 파일 수정 시: 새로 import 하는 모듈이 "허용"에만 있는지 확인. "금지"에 있으면 레이어 꼬임 → 리팩터로 분리하거나 상위 레이어로 로직 이동.
