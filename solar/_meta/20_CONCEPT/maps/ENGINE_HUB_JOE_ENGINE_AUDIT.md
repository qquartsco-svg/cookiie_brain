# ENGINE_HUB Joe_Engine 전체 로직 점검 결과

**대상**: `00_BRAIN/ENGINE_HUB/00_PLANET_LAYER/Joe_Engine/`  
**점검일**: 문서 기준 반영

---

## 1. 점검 요약

| 항목 | 점검 전 | 점검 후 |
|------|--------|--------|
| **CONFIG 주입** | 계수 하드코딩만 존재 | `_core.DEFAULT_CONFIG` 도입, `assess_planet(..., config=...)` 로 오버라이드 가능 |
| **재현 가능성** | 결과에 사용 계수 미기록 | `PlanetAssessment.config_used` 필드로 실제 사용 계수 기록 |
| **저수준 API** | ref_min/ref_max 만 지원 | `compute_planet_stress_and_instability_from_snapshot(..., config=...)` 지원 |
| **CLI** | config_used 미표시 | `config_used keys` 출력 추가 |
| **README** | CONFIG·config_used 미언급 | CONFIG 예제, config_used, 재현 가능성 섹션 추가 |

---

## 2. 파일별 로직 확인

### 2.1 `_core.py`

- **PANGEA §4**: `planet_stress_raw` = a1·σ_plate + a2·(P_w/p_ref) + a3·S_rot + a4·(W_surface/W_total) + a5·dW_norm.  
  `instability_raw` = b1·stress + b2·(W_surface/W_total) + b3·dW_norm.  
  `normalize`, `saturate` 로 [0,1] 클램프.
- **스냅샷 키**: sigma_plate, P_w, S_rot, W_surface, W_total, dW_surface_dt_norm. 없으면 `_get_float`로 0 또는 default.
- **DEFAULT_CONFIG**: ref_min, ref_max, a1~a5, b1~b3, p_ref 포함. 계수는 이 dict 기준으로만 사용되며, 호출 측에서 config로 덮을 수 있음.

### 2.2 `explore.py`

- **PlanetAssessment**: planet_stress, instability, habitability_label, summary, **config_used** (dict, default_factory=dict).
- **assess_planet(snapshot, config=None, ref_min=..., ref_max=...)**:  
  cfg = DEFAULT_CONFIG + config 병합 → planet_stress_raw(..., a1=cfg["a1"], ...), normalize(..., cfg["ref_min"], cfg["ref_max"]), instability_raw(..., b1=cfg["b1"], ...), saturate → _label_habit → PlanetAssessment(..., config_used=cfg).
- **habitability_label**: stress 또는 inst ≥ 0.7 → extreme; ≥ 0.4 → low; ≥ 0.2 → moderate; else high.

### 2.3 `__init__.py`

- **export**: assess_planet, PlanetAssessment, compute_planet_stress_and_instability_from_snapshot, **DEFAULT_CONFIG**, __version__.
- **compute_planet_stress_and_instability_from_snapshot(snapshot, config=None, ref_min=..., ref_max=...)**:  
  내부에서 assess_planet 호출 후 (planet_stress, instability) 반환.

### 2.4 `__main__.py`

- 인자 없음 → DEFAULT_SNAPSHOT 사용; 인자 1개 → 해당 경로 JSON 로드(실패 시 DEFAULT_SNAPSHOT).
- assess_planet(snap) 호출 후 planet_stress, instability, habitability_label, summary 출력 + **config_used keys** 출력.

### 2.5 `README.md`

- 입출력, 폴더 구조, 설치, 사용 예(assess_planet, config 예제, 저수준 API), CLI, 스냅샷 키, **재현 가능성(config_used)** 설명.

### 2.6 `requirements.txt`

- 주석만으로 “외부 의존 없음” 명시. 유지.

---

## 3. 검증 실행 결과

```text
$ python -m Joe_Engine
  planet_stress: 0.154  instability: 0.235  habitability: moderate
  config_used keys: ['ref_min', 'ref_max', 'a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2', 'b3', 'p_ref']

$ python -c "from Joe_Engine import assess_planet, DEFAULT_CONFIG; r = assess_planet({}); ..."
  stress=0.000 inst=0.000 label=high, config_used: [...], OK
```

- CLI 및 API 동작 정상. config_used 기록 확인.

---

## 4. 정리

- **역할**: 조(JOE) PANGEA §4 기반 “거시 스냅샷 → planet_stress, instability, habitability_label” **평가기**. 독립 패키지, CookiieBrain/solar 무의존.
- **계약**: 입력 = 스냅샷 dict(표준 키 6개), 출력 = PlanetAssessment(스트레스·불안정도·라벨·요약·**config_used**).  
  CONFIG로 계수 오버라이드 가능하며, config_used로 재현·감사 가능.
- **Feature Layer(물리→스냅샷)**: ENGINE_HUB Joe_Engine에는 없음. 스냅샷은 호출 측에서 채우거나, CookiieBrain `solar._01_beginnings.joe.feature_layers` 규약을 참고해 구성.

이상으로 ENGINE_HUB Joe_Engine 전체 로직이 설계(CONFIG 주입, config_used, 재현 가능성)에 맞게 구현된 것으로 확인됨.
