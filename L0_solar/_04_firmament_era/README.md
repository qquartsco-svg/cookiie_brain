# `_04_firmament_era` — 창공 환경시대

> L0_solar 서사 레이어 4번째 챕터
> 수증기 캐노피(궁창)가 지구를 감싸며 에덴 시대 온실 환경을 유지하는 단계.

---

## 서사적 위치

```
_01_beginnings → _02_creation_days (Day1~7) → _03_eden_os_underworld
                                                        ↓
                                              _04_firmament_era ← 여기
                                                        ↓
                                              _05_noah_flood (상전이 트리거)
```

창공은 단순한 물리 레이어가 아니다.
에덴OS가 안정적으로 운영될 수 있는 **환경 전제 조건**이다.
창공이 있는 한:
- 전지구 온도 균일 (극지방도 0°C 근처)
- UV 차폐
- 고압·고습 대기
- 생물 수명 연장 (저엔트로피 환경)

창공이 붕괴하면 이 모든 조건이 동시에 무너진다.

---

## 엔지니어링 구조

### 핵심 구현 파일

| 파일 | 위치 | 역할 |
|---|---|---|
| `FirmamentLayer` | `L0_solar/_03_eden_os_underworld/eden/firmament.py` | 창공 1스텝 실행, 붕괴 감지 |
| `Layer0Snapshot` | `L0_solar/_03_eden_os_underworld/eden/firmament.py` | 상태 스냅샷 |
| `make_antediluvian()` | `L0_solar/_03_eden_os_underworld/eden/initial_conditions.py` | 에덴 시대 초기 조건 |
| `engine.py` | `L0_solar/_04_firmament_era/engine.py` | `run_firmament_era_step()` 진입점 |

### 상태 벡터 인터페이스

```python
# FirmamentLayer.step(dt_yr, instability=...) 출력
{
    "T_global_K":          float,   # 전지구 평균 기온 [K]
    "H2O_canopy_kg":       float,   # 수증기 캐노피 잔량 [kg]
    "instability":         float,   # 0.0~1.0 (0.85 이상 → 붕괴 트리거)
    "collapse_triggered":  bool,    # 붕괴 여부
    "albedo":              float,   # 알베도
    "UV_surface":          float,   # 지표 UV 강도
}
```

### 붕괴 임계

```python
if instability >= 0.85:
    # FirmamentLayer._do_collapse() 호출
    # → FloodEvent 생성
    # → _05_noah_flood 로 상태 전달
```

`instability`는 `_01_beginnings/joe`의 JOE 관찰자가 계산한
`planet_stress`와 `_05_noah_flood`의 외부 충격(lucifer_impulse)의 합산값이다.

---

## 물리 모델

```
T_global = T_eq × (1 + α_H2O × f_canopy)
         = 복사 평형 기온 × 수증기 온실 증폭 계수

f_canopy : 캐노피 완전도 (1.0 → 창공 완전, 0.0 → 붕괴)
α_H2O   : 수증기 온실 증폭 (기본 ~0.33, T_global ≈ 297K = 24°C)
```

---

## 빠른 사용

```python
from L0_solar._04_firmament_era import run_firmament_era_step
from L0_solar._03_eden_os_underworld.eden.initial_conditions import make_antediluvian

ic = make_antediluvian()
state = run_firmament_era_step(ic, dt_yr=1.0, instability=0.3)
print(state["T_global_K"], state["collapse_triggered"])
```

---

## 다음 단계

창공이 붕괴(`collapse_triggered=True`)되면
→ `_05_noah_flood/engine.py`의 `run_noah_scenario()`가 호출된다.
