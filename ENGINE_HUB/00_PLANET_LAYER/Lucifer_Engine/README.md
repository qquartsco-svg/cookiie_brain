# Lucifer Engine — 혜성/소행성 충돌 예상·탐색 독립 엔진

**Comet/Asteroid Impact Estimator · 완전 독립 모듈**

루시퍼 엔진은 **혜성·소행성 충돌 파라미터**를 받아, 전지구 평균 에너지 밀도와 행성 환경 델타(대기·수권·극-적도 온도차 등)를 **오더 수준**으로 추정하는 독립 엔진입니다.  
CookiieBrain·solar·기타 프로젝트에 **의존하지 않으며**, 행성 방어·시뮬레이션·연구용으로 그대로 쓸 수 있는 **상용화 가능한 단일 패키지**입니다.

---

## 서사적 위치 (Narrative)

- **역할**: 충돌 탐색기(Impact Explorer) — 직경·밀도·속도·입사각·수심·위치만으로 에너지와 환경 델타를 산출.
- **출처**: CookiieBrain solar/_06_lucifer_impact 레이어에서 유래했으나, **이 리포지터리는 독립 배포용**이며 서사·설계만 공유합니다.

---

## 완전 독립 모델

| 항목 | 내용 |
|------|------|
| **의존성** | 표준 라이브러리만 사용. `requirements.txt` 없음(또는 빈 파일). |
| **패키지** | `pip install -e .` 후 `python -m lucifer_engine` 또는 `from lucifer_engine import estimate_impact` 사용 가능. |
| **상용화** | 별도 라이선스로 재배포·상용 제품에 삽입 가능. |

---

## 설치

리포지터리 루트에서:

```bash
cd Lucifer_Engine
pip install -e .
```

---

## 사용 — API

```python
from lucifer_engine import ImpactParams, estimate_impact

params = ImpactParams(
    D_km=10.0,
    rho_gcm3=3.0,
    v_kms=20.0,
    theta_deg=45.0,
    h_km=4.0,
    lat_deg=-30.0,
    lon_deg=120.0,
)
result = estimate_impact(params)
# result.E_total_J, result.E_eff_J, result.shock_strength, result.delta_* ...
```

---

## CLI

```bash
# 기본 파라미터로 실행
python -m lucifer_engine

# JSON 파일로 파라미터 전달
python -m lucifer_engine /path/to/params.json
```

**params.json 예시**:

```json
{
  "D_km": 10.0,
  "rho_gcm3": 3.0,
  "v_kms": 20.0,
  "theta_deg": 45.0,
  "h_km": 4.0,
  "lat_deg": -30.0,
  "lon_deg": 120.0
}
```

---

## 폴더 구조

```
Lucifer_Engine/
├── README.md
├── SIGNATURE.md
├── pyproject.toml
├── requirements.txt   # 비어 있거나 없음
└── lucifer_engine/
    ├── __init__.py
    ├── impact_estimator.py
    └── __main__.py
```

---

## 블록체인·서명 및 검증

공식 릴리스는 서명된 Git 태그로 배포할 수 있습니다.  
배포 아티팩트에 대한 체크섬·서명 정보는 **[SIGNATURE.md](./SIGNATURE.md)** 에 기재됩니다.

검증 방법 (리포 루트에서):

```bash
git hash-object lucifer_engine/__init__.py
git hash-object lucifer_engine/impact_estimator.py
git hash-object lucifer_engine/__main__.py
```

출력 SHA1 이 `SIGNATURE.md` 와 일치하면 코드 무결성이 확인됩니다.

---

## CookiieBrain과의 관계

- **본 패키지**: 충돌 추정 코어만 포함. (ImpactParams → ImpactResult.)
- **solar/_06_lucifer_impact**: 이 엔진을 설치해 쓰거나, 동일 API를 solar 내부에서 재구현해 사용할 수 있음. 의존 방향은 `_06 → Lucifer_Engine` (읽기만).
