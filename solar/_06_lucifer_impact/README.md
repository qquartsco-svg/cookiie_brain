# _06_lucifer_impact — 루시퍼 임팩트 레이어 (혜성/소행성 충돌 탐색)

**역할**  
- 혜성/소행성 충돌 파라미터를 받아, 전지구 평균 에너지 밀도(J/m²)를 추정하고  
  궁창 캐노피, 대기압, 해수면, 극-적도 온도차에 대한 **오더 수준 델타**를 계산하는
  **독립 레이어형 모듈**이다.
- `_05_noah_flood` 뿐 아니라, 다른 레이어/엔진에서도 그대로 가져다 쓸 수 있는
  **재사용 가능한 "충돌 탐색기"**를 목표로 한다.

---

## 1. 패키지 구성

```text
_06_lucifer_impact/
├── __init__.py          # 공개 API: ImpactParams, ImpactResult, estimate_impact
├── impact_estimator.py  # 충돌 파라미터 → 에너지/환경 델타 추정 코어
└── SIGNATURE.md         # 이 레이어 내 파일들에 대한 Git 블록체인 서명 정보
```

- 상위에서 사용할 때:

```python
from solar._06_lucifer_impact import ImpactParams, estimate_impact

params = ImpactParams(
    D_km=10.0,
    rho_gcm3=3.0,
    v_kms=20.0,
    theta_deg=45.0,
    h_km=4.0,
    lat_deg=-30.0,
    lon_deg=120.0,
)
impact = estimate_impact(params)
```

이렇게 얻은 `impact.shock_strength`, `delta_*` 값은
Noah Flood, EdenOS, JOE/MOE 등 어디에서든 소비할 수 있다.

---

## 2. 노아 플러드 레이어와의 관계

- `_05_noah_flood/scenarios.py` 의
  `run_scenario_lucifer_impact_mid_ocean()` 은 이 레이어를 읽기만(import) 한다.
- 의존 방향:

```text
_06_lucifer_impact  →  (숫자/델타 제공)
_05_noah_flood      →  이 값을 읽어 effective_instability spike 등에 사용
```

즉, **충돌 추정기(_06)** 는 완전히 독립 레이어로 남고,  
노아 플러드 쪽이 소비자 역할만 수행한다.

---

## 3. 블록체인 서명 / 무결성 확인

이 레이어의 파일들은 Git 객체 해시를 통해 서명되며,
`SIGNATURE.md` 에 현재 커밋 기준 해시가 기록되어 있다.

검증 방법 (CookiieBrain 루트에서):

```bash
cd CookiieBrain
git hash-object solar/_06_lucifer_impact/__init__.py
git hash-object solar/_06_lucifer_impact/impact_estimator.py
```

출력되는 SHA1 값이 `SIGNATURE.md` 에 기록된 값과 일치하면,  
이 레이어의 코드가 변조되지 않았음을 확인할 수 있다.

