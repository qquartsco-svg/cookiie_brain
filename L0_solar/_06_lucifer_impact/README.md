# _06_lucifer_impact — 루시퍼 임팩트 레이어

**역할**
혜성/소행성 충돌 파라미터를 받아 에너지·크레이터·쓰나미·환경 델타를 계산하는 독립 레이어.  
출력값은 `_05_noah_flood`(impulse_shock 주입) 및 `_07_polar_ice`(결빙 시뮬레이션 입력)로 흘러간다.

---

## 패키지 구성

```text
_06_lucifer_impact/
├── __init__.py          공개 API: lucifer_strike(), LUCIFER_MODE (3-tier fallback)
├── impact_estimator.py  로컬 폴백 충돌 추정기 (LuciferEngine 미설치 시)
├── README.md
└── SIGNATURE.md         Git blob 해시 서명
```

## LuciferEngine 3-tier fallback

| 우선순위 | 조건 | 모드 | 제공 |
|---------|------|------|------|
| 1 | `lucifer_engine` 설치됨 | `full_pipeline` | 궤도 → MOID → 확률 → 에너지/크레이터/쓰나미 |
| 2 | 미설치, effects만 | `effects_only` | 에너지 + 크레이터 + 쓰나미 |
| 3 | 완전 폴백 | `impact_only` | 에너지만 (레거시) |

## 서사 연결

```
_05_noah_flood   ← impulse_shock 주입
_06_lucifer_impact → E_eff_MT, delta_H2O, delta_T_pole
_07_polar_ice    ← 위 값을 받아 결빙 시뮬레이션
```

## 빠른 사용

```python
from L0_solar._06_lucifer_impact import lucifer_strike
ir, cr, ts = lucifer_strike(D_km=5.0, is_ocean=True, v_kms=25.0)
# ir.E_eff_MT, ir.delta_H2O_canopy, ir.delta_pole_eq_K → _07_polar_ice 입력
```

## 관련 독립 엔진

- **위치**: `ENGINE_HUB/00_PLANET_LAYER/Lucifer_Engine/`
- **설치**: `pip install -e ENGINE_HUB/00_PLANET_LAYER/Lucifer_Engine`
- 상세 사양: `ENGINE_HUB/00_PLANET_LAYER/Lucifer_Engine/README.md`
