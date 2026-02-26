# 자가순환 시스템 보편 템플릿 — 뉴런 · 지구 · 우주선

**목적**: 뉴런 → 지구 환경 → 우주선 생명유지장치까지 **동일한 5블록 구조**로 설계·매핑하여, 엔지니어링 관점에서 하나의 순환 형식으로 다룬다.

---

## 1. 보편 5블록 (Standard Template)

비평형 구동 하에서 **한 호흡 사이클**을 이루는 구성은 다음으로 고정한다.

| 블록 | 역할 | 물리적 의미 |
|------|------|-------------|
| **Drive** | 외부 입력 | 연료·복사·외력 — 비평형 구동 |
| **Reservoir** | 저장 | 에너지·물질 완충 풀 |
| **Work** | 작업/변환 | 저장된 것을 사용해 패턴·구조·흐름 생성 |
| **Sink** | 손실/배출 | 열·복사·마찰·분해 — 엔트로피 배출 |
| **Phase/Controller** | 위상/조절 | 리듬·주기·지연 — 작업의 시간 조직화 |

**보존 규칙**:  
- 에너지 수지: Drive = Reservoir 증감 + Work 소비 + Sink  
- 물질 수지: 도메인별 플럭스 ↔ mixing ratio 규약 고정  
- 시간척도: 도메인마다 dt, τ 분리 (ms / yr / mission duration)

---

## 2. 인스턴스 매핑

### 2.1 뉴런 (bio_neurons_lego)

| 블록 | 구현 |
|------|------|
| Drive | Glu, O₂ 공급 |
| Reservoir | E_buf, ATP (`mitochon_atp.py`) |
| Work | HH 막전위·펌프·스파이크 (`hh_soma.py`) |
| Sink | Heat, CO₂, J_use |
| Phase | DTG (E, φ) (`dtg_system.py`) |

### 2.2 지구 환경 (solar + atmosphere + biosphere)

| 블록 | 구현 |
|------|------|
| Drive | Solar Luminosity F(r) |
| Reservoir | 대기·해양 열용량, 수증기, organic_layer, B_* |
| Work | 수순환, 광합성 GPP/NPP, 증산, 성장(leaf/wood/seed) |
| Sink | OLR, 잠열, 호흡/분해, 복사 냉각 |
| Phase | 계절/세차(궤도·자전), 생장 단계(페노로지) |

### 2.3 우주선 생명유지 (Life Support — 동일 템플릿)

| 블록 | 구현 (설계 목표) |
|------|------------------|
| Drive | 태양광/전력, 보급(물·식량·O₂), 재생 루프 |
| Reservoir | 열용량, O₂/CO₂/H₂O 탱크, 식생/미생물 풀 |
| Work | 광합성·재생산, 온도·습도 제어, 공기 정화 |
| Sink | 우주 방출(열·폐기물), 재활용 손실 |
| Phase | 주/년 주기, 재보급·유지보수 이벤트 |

**정리**: 지구 환경 모델 = 우주선 내부 환경 설정의 **동일 구조 인스턴스**. 변수·단위·스케일만 바꾸고 5블록과 보존 규칙을 유지하면 된다.

---

## 3. 코드 레벨 대응 (현재 구현)

| 레이어 | Drive | Reservoir | Work | Sink | Phase |
|--------|-------|-----------|------|------|-------|
| solar/em | F_solar_si | — | — | — | — |
| atmosphere/column | F_in | C·T_surface, H2O | water_cycle | F_out, _Q_latent | τ_th |
| surface | — | — | A_eff | — | — |
| biosphere/column | F, CO2, H2O | B_*, organic | GPP/NPP, 증산 | Resp, delta_CO2/O2 | B_seed 발아/휴면 |

브릿지에서 biosphere ↔ atmosphere/surface 피드백을 연결하면 지구 루프가 닫힌다.  
동일 포트(에너지·조성·알베도)를 우주선 모드에서 재정의하면 우주선 자가순환이 된다.

---

## 4. 파일 위치

- 이 설계: `docs/CIRCULATION_TEMPLATE.md`  
- 지구 인스턴스 배선: `solar/brain_core_bridge.py`  
- 식생 Work 레이어: `solar/biosphere/column.py`  
- 뉴런 인스턴스: `New_Run.py/bio_neurons_lego/` (외부)
