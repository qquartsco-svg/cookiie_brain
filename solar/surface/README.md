# solar/surface/ — 땅과 바다의 분리 (셋째날 / Phase 7)

> *"하나님이 물을 한 곳으로 모으고 땅이 드러나게 하시니라"* (창 1:9)

이 레이어는 **지표면의 물리적 이질성**(땅 vs 바다)을 정의하고, 행성 전체 **복사 평형(Radiative Equilibrium)**에 쓰이는 **유효 알베도**를 제공한다.  
단순 지형 구분이 아니라, "알베도 기어"로서 대기 column의 지표 온도 계산에 직접 기여한다.

---

## 1. 개념

- **궁창(둘째날)** = 바다와 하늘(기체)의 분리 → `atmosphere/` 레이어.
- **셋째날** = 바다와 **땅(육지)** 의 분리 → 이 레이어 `surface/`.

| 용어 | 의미 |
|------|------|
| **땅 (land)** | 물이 모여 드러난 육지. 반사율이 해양보다 높음. |
| **바다 (ocean)** | 물이 모인 곳. 반사율이 낮음. |
| **대륙 비율** | 전 표면 중 육지 비율. 코드 변수명: `land_fraction`. 지구 근사: 0.29. |

---

## 2. 물리 — 유효 알베도

전지구 복사 평형에서 쓰는 **단일 반사율**은 육지와 해양의 면적 가중 평균으로 둔다.

**수식**

\[
A_{\mathrm{eff}}
= f_{\mathrm{land}}\, A_{\mathrm{land}}
+ (1 - f_{\mathrm{land}})\, A_{\mathrm{ocean}}
\]

(ASCII: `A_eff = f_land * A_land + (1 - f_land) * A_ocean`)

- \(A_{\mathrm{eff}}\): 유효 알베도 (무차원, 0~1)
- \(f_{\mathrm{land}}\): 육지 면적 비율 (코드: `land_fraction`)
- \(A_{\mathrm{land}}\): 육지 평균 알베도 (코드: `albedo_land`)
- \(A_{\mathrm{ocean}}\): 해양 평균 알베도 (코드: `albedo_ocean`)

**지구 근사 (코드 기본값)**

| 파라미터 | 기호 | 값 | 설명 |
|----------|------|-----|------|
| 대륙 비율 | \(f_{\mathrm{land}}\) | 0.29 | `F_LAND_EARTH` |
| 육지 알베도 | \(A_{\mathrm{land}}\) | 0.30 | 숲·사막·빙하 혼합, `A_LAND_DEFAULT` |
| 해양 알베도 | \(A_{\mathrm{ocean}}\) | 0.08 | `A_OCEAN_DEFAULT` |

→ 지구 조건에서 \(A_{\mathrm{eff}} \approx 0.12\) 전후 (해양 우세).

---

## 3. 모듈 — 파일 구성

| 파일 | 역할 |
|------|------|
| **surface_schema.py** | `SurfaceSchema` dataclass, `effective_albedo()` 함수, 상수 `F_LAND_EARTH`, `A_LAND_DEFAULT`, `A_OCEAN_DEFAULT` |
| **__init__.py** | 패키지 API: `SurfaceSchema`, `effective_albedo` export |

**의존성 (레이어 규칙)**

- `surface/`는 **core/, em/, atmosphere/를 import 하지 않음.**  
  순수 계산 모듈(상수 + 식)만 보유.
- **atmosphere/** 가 이 레이어의 `effective_albedo()` 결과를 **읽기만** 한다.  
  즉, 데이터 흐름은 `surface → atmosphere` 단방향.

---

## 4. 사용 예시

**단독 사용**

```python
from solar.surface import SurfaceSchema, effective_albedo

# 지구 기본 (land_fraction=0.29)
sfc = SurfaceSchema(land_fraction=0.29)
A = sfc.effective_albedo()   # ~0.12 (ocean-dominated)

# 화성 (거의 전 육지)
sfc_mars = SurfaceSchema(land_fraction=1.0, albedo_land=0.25)
A_mars = sfc_mars.effective_albedo()
```

**atmosphere/ 와 연동**

```python
from solar.surface import SurfaceSchema
from solar.atmosphere import AtmosphereColumn

sfc = SurfaceSchema(land_fraction=0.29)
atm = AtmosphereColumn(
    body_name="Earth",
    albedo=sfc.effective_albedo(),   # surface에서 A_eff 사용
    T_surface_init=288.0,
)
# column은 이 albedo로 복사 평형·T_surface 계산
```

---

## 5. 환경설정이 어디까지 됐나 (코드 기준)

아래는 **코드/실행 기준**으로 “완료·진행 중·미구현”을 나눈 정리다.  
이 레이어(surface/)는 **D**에 해당한다.

| 구간 | 내용 | 상태 |
|------|------|------|
| **A. 행성 상태공간(코어)** | 중력/궤도/스핀/세차, SurfaceOcean(우물·조석·코리올리·와도) | ✅ 완료 |
| **B. 외부 환경(관측자 레이어)** | 빛(광도→조도), 태양풍/IMF, 자기쌍극자/자기권 | ✅ 완료 |
| **C. 궁창(대기권, Phase 6a)** | 온실(τ→ε_a), 열적 관성 ODE, P·T·물상 판정 | ✅ 완료 (패키징 점검 별도) |
| **D. 셋째날(땅/바다 분리, Phase 7)** | \(A_{\mathrm{eff}}\) 구현, surface→atmosphere 연동, surface_day3_demo 검증 | ✅ 완료 |
| **E. 수순환(Phase 6b)** | water_cycle, 잠열, surface_heat_flux 연동 | ⚠️ 진행 중 (상수/규약 정리 필요) |

**지금 시스템이 의미하는 것 (한 줄)**  
행성 상태공간 위에 “환경 출력층”(빛·바람·자기권·대기·표면 알베도)을 기어처럼 얹어,  
**비평형 입력(태양 복사) + 보호(자기권) + 저장/지연(대기 열관성) + 경계조건(땅/바다 알베도)**까지 갖춘  
**창발 실험용 월드 샌드박스**가 된 상태이다.  
→ 물리 법칙을 하나씩 대입/연결했을 때, 상태공간이 혼돈으로 가는지·안정 루프가 생기는지·임계조건이 어디인지 계측할 수 있는 구조.

---

## 6. 검증 (surface_day3_demo)

| 항목 | 내용 |
|------|------|
| **P7-1** | 지구 \(f_{\mathrm{land}}=0.29\) 일 때 \(A_{\mathrm{eff}} \approx 0.12{\sim}0.15\) (해양 지배) |
| **P7-2** | 전 바다 vs 전 육지 시 \(A_{\mathrm{ocean}} < A_{\mathrm{land}}\) |
| **P7-3** | surface 알베도 → AtmosphereColumn 연동 시 \(T_{\mathrm{eq}}\) 변화 |
| **P7-4** | 땅 비율 증가 → 알베도 상승 → 행성 냉각 (수치 확인) |

실행: `examples/surface_day3_demo.py`.

---

## 7. 다음으로 올 수 있는 기어 (환경설정 순서)

1. **Phase 6b 정리** — 수순환/잠열, 에너지·질량 교환 루프, surface_heat_flux 규약.
2. **Phase 6c** — 지각/가스 공급(Outgassing), 조성 τ의 시간 변화.
3. **대기 탈출/광화학** — 자기권·자외선 차폐가 수치적으로 의미 있게 쓰이기.
4. **Phase 8** — 반응-확산 + 경계 + 비평형 구동 → “자가순환 객체” 창발 가능성.

현재 surface/ 는 **전역 평균 \(f_{\mathrm{land}}\) 모델**만 제공한다.  
공간 격자·동적 land_fraction·식생 피드백 등은 미구현이며, 필요 시 이후 기어로 추가한다.

---

## 8. 참고 문서

- 개념·날짜 매핑: `docs/CREATION_DAYS_AND_PHASES.md`
- 코드 위치·연결: `docs/DAY3_ENVIRONMENT_WHERE_AND_WHAT.md`
- 개념 레이어: `solar/concept/03_surface/README.md`
