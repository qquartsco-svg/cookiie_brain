# 궁창시대 → 에덴 탐색 → 아담/이브 계승 → 4대강·생명나무 체루빔 — 엔지니어링 분석

**목적**: 현재 상황 정리 후, “남북극이 얼음지대가 아닌 궁창시대 스페이스 세차운동 상태로 돌아가서, 에덴 탐색과 그 에덴의 지구 환경 OS 내부 시스템 관리자(아담·이브 → 네오) 명맥, 그리고 에덴 4대강·생명나무 체루빔”까지를 **엔지니어링 관점에서 철저히 분석**하고 작업 진행 순서를 제안한다.

---

## 1. 현재 상황 정리

### 1.1 구현 완료된 것

| 영역 | 내용 | 위치 |
|------|------|------|
| **Creation Days 1~7** | 물리·대기·표면·생물·이동·진화·완성·안식 | solar/day1~7 |
| **Eden 환경** | 궁창(firmament), 대홍수(flood), 초기조건(initial_conditions), 지리(geography) | solar/eden/ |
| **에덴 탐색** | EdenSearchEngine, SearchSpace, EdenCriteria, EdenExplorationGrid, Grid 연동(2D~7D) | solar/eden/search.py, exploration.py |
| **극지 빙하 없음** | antediluvian IC: pole_eq_delta_K=15K, albedo=0.20 → band_T 극지 > -10°C → ice_mask 전부 0 | initial_conditions.py, EarthBandState.ice_mask |
| **세차운동** | EvolutionEngine 스핀 세차, MilankovitchCycle 해석적 세차, geography PRECESSION_PERIOD_YR, precession_frame | day4/core/evolution_engine.py, day4/cycles/milankovitch.py, eden/geography.py |
| **문서** | 아담·이브 개념(Observer/Controller), 계승(ReproductionEngine·SelectionEngine), 12시스템 관리자 | docs/EDEN_CONCEPT.md, ADAM_EVE_SYSTEM.md |

### 1.2 아직 구현되지 않은 것

| 영역 | 내용 | 비고 |
|------|------|------|
| **Eden IC → Day7 Runner 연동** | τ/albedo/ΔT 더블카운트 방지, Runner/AtmosphereColumn에서 Eden override 시 재계산 금지 | docs/EDEN_ENGINEERING_FINAL.md 규칙 |
| **Adam / Eve / Lineage** | adam.py, eve.py, lineage.py — 12밴드 관리자·탐색자·계승 로직 | ADAM_EVE_SYSTEM.md “예정” |
| **4대강** | 에덴에서 흘러나와 네 갈래로 나뉜 강(비손·기혼·히데겔·유브라데) — 데이터/엔진 없음 | 창세기 2:10-14 |
| **생명나무·체루빔** | 생명나무 접근 경로 수호, 체루빔·불칼 — 코드/문서 없음 | 창세기 3:24 |

### 1.3 “네오(Neo)” 대응

- **영화 매트릭스의 네오**: 시스템을 바꿀 수 있는 “선택된 자”, 기존 시스템 관리 구조를 이어받는 존재.
- **본 프로젝트 대응**: 에덴의 **다음 세대 시스템 관리자** = Adam × Eve → ReproductionEngine으로 생성된 자녀 → SelectionEngine으로 **적합도 기반 선택**된 계승자.  
  즉 **“네오” = lineage에서 선택된 successor(다음 관리자)** 로 정의하면 된다.

---

## 2. “남북극이 얼음지대가 아닌 궁창시대 스페이스 세차운동 상태”로 돌아가는 것

### 2.1 물리적 정의

- **궁창시대(antediluvian)**  
  - `make_antediluvian()`: H2O_canopy=0.05, pole_eq_delta_K=15K, albedo=0.20, f_land=0.40, precip_mode='mist'.  
  - 결과: T_surface ≈ 35°C, 극지 band_T도 -10°C 이상 → **ice_mask[i]=0 for all i** (이미 initial_conditions.py에서 동역학으로 계산됨).
- **세차운동**  
  - **우주(스페이스) 세차**: EvolutionEngine의 N-body·토크 → 자전축 역행 세차(~25,772 yr).  
  - **궁창시대와의 관계**: 궁창 자체가 세차를 끄는 것이 아님. “궁창시대 상태” = **동일한 물리(세차 포함)** 위에 **Eden IC(극지 균온화·빙하 없음)** 를 올린 것.
- **정리**: “남극·북극이 얼음지대가 아닌 궁창시대의 스페이스 세차운동 상태로 돌아간다” =  
  **PlanetRunner(및 Day2/Day4 드라이버)에 Eden antediluvian 초기조건을 넣어서 돌리면, 극지가 빙하가 아닌 상태로 나오고, 세차는 그대로 우주(evolution_engine + Milankovitch)에서 계산된다** 로 해석하면 된다.

### 2.2 구현 관점에서 “돌아간다”에 필요한 것

1. **Runner에 Eden IC 주입**  
   - `to_runner_kwargs()`로 T_surface_K_init, pole_eq_delta_K, albedo_init, pressure_atm 등 전달.  
   - Runner/AtmosphereColumn 측: **Eden에서 온 값이 있으면 τ/ε/T를 재계산하지 않음** (더블카운트 방지).
2. **빙하 밴드 수 강제(선택)**  
   - Eden 모드일 때 Day4 MilankovitchDriver의 `is_glacial`을 “사용하지 않음” 또는 “Eden override 시 항상 False”로 두어, 빙하 알베도/ice_fraction이 0으로 유지되게 할 수 있음.  
   - 현재는 **Eden IC만 써도** band_T가 -10°C 이상이면 `ice_mask`가 0이므로, Runner가 Eden IC의 band 상태를 그대로 쓰면 “극지 빙하 없음”이 자동 만족된다.
3. **세차 프레임**  
   - geography: 에덴은 `precession_frame='magnetic'`, 홍수 후는 `precession_frame='rotation'`.  
   - “궁창시대 스페이스 세차운동 상태”에서는 **evolution_engine + cycles** 의 세차는 그대로 두고, **지리/자기장 해석**만 Eden geography(magnetic frame)를 쓰면 된다.

따라서 “극지 비빙하 + 궁창시대 세차 상태”는 **Eden IC를 Runner에 연결하고 더블카운트만 제거**하면, 기존 코드만으로 달성 가능하다.

---

## 3. 에덴 탐색 → 그 에덴의 지구 환경 OS → 아담·이브 → 명맥(네오)

### 3.1 흐름 한 줄 요약

```
에덴 탐색(Search) → 후보 EdenCandidate 선택 → 그 후보로 PlanetRunner(OS) 구성
→ 그 OS의 “관리자” = Adam(Observer) + Eve(Controller)
→ Adam × Eve → Lineage(ReproductionEngine + SelectionEngine) → 다음 관리자 선택 = “네오”
```

### 3.2 단계별 매핑

| 단계 | 시스템 역할 | 구현 위치(현재/예정) |
|------|-------------|------------------------|
| 에덴 탐색 | 파라미터 공간 스캔 → EdenCriteria 통과 후보, ExplorationGrid·grid_agent | search.py, exploration.py ✅ |
| “그 에덴” 결정 | SearchResult.best 또는 사용자 지정 EdenCandidate → InitialConditions | search.py → initial_conditions |
| 지구 환경 OS | 해당 IC로 PlanetRunner 생성, 12밴드·12엔진 구동 | day7/runner.py + Eden IC 연동 (예정) |
| 시스템 관리자 | Adam: 12밴드 감독·이름 붙이기·임계 관리 / Eve: 탐색·이상 탐지·피드백 | eden/adam.py, eve.py (예정) |
| 명맥 이어감 | Adam × Eve → 자녀(ReproductionEngine) → SelectionEngine → 다음 관리자 | eden/lineage.py (예정) |
| “네오” | lineage에서 선택된 **successor** = 다음 세대의 12시스템 관리자 | lineage.select_successor() 등 |

### 3.3 작업 순서 제안

1. **Eden IC → PlanetRunner 연동**  
   - Runner(또는 day7 통합 진입점)가 `eden_ic: Optional[InitialConditions] = None` 등을 받아 `to_runner_kwargs()` 반영.  
   - Day2/AtmosphereColumn: Eden에서 온 τ/T/albedo/pole_eq_delta가 있으면 **재계산하지 않고** 그대로 사용.
2. **탐색 결과 → Runner 생성**  
   - `make_planet_runner(eden_candidate: EdenCandidate)` 또는 `make_planet_runner(eden_ic=result.best.ic)` 형태로 “그 에덴” OS 생성.
3. **adam.py**  
   - Adam(runner, judge): `watch(dt_yr)` → runner.step, judge.push, 진단(labels, violations).  
   - 12밴드 이름 부여, 임계(선악과 경계) 관리.
4. **eve.py**  
   - Eve(adam): Adam.genome(또는 runner 상태)에서 파생, `explore(snap)` → 이상 탐지, Adam에게 ControlSignal 피드백.
5. **lineage.py**  
   - ReproductionEngine으로 자녀 생성, SelectionEngine으로 적합도(예: SabbathJudge 기반 안정도) 평가 → **successor 선택** = “네오”.
6. **데모**  
   - eden_search_demo → best candidate → make_planet_runner(ic) → Adam·Eve 생성 → step 반복 → lineage 한 세대 → successor 출력.

---

## 4. 에덴에서 보이는 4대강 — 엔지니어링 설계

### 4.1 서사 근거

- 창세기 2:10-14: 한 강이 에덴에서 흘러 나와 네 갈래로 나뉜다 — 비손(Pishon), 기혼(Gihon), 히데겔(Tigris), 유브라데(Euphrates).

### 4.2 시스템 해석

- **한 강이 에덴에서 나옴** → 단일 수원(에덴 “원천”)에서 유출.  
- **네 갈래** → 4개의 유역/흐름 축.

### 4.3 데이터·API 제안

- **FourRivers**  
  - 4개 강 각각: 이름, 원천(에덴 내) 밴드 또는 좌표, 경로(밴드 인덱스 리스트 또는 경로 그래프), 목적지(바다/호수 밴드 또는 지리 영역).
- **12밴드와의 연결**  
  - 옵션 A: 밴드를 4구역으로 묶어 각 구역 대표 강 하나. 예: band 0–2 → Pishon, 3–5 → Gihon, 6–8 → Tigris, 9–11 → Euphrates.  
  - 옵션 B: geography의 ExposedRegion(베링, 순다, 북해, 동시베리아, 사훌, 남극 해안) 중 4개를 강 유역과 매핑.  
  - 옵션 C: 수문학적 “유역 그래프”를 나중에 도입하고, 4대강을 그 그래프의 4개 주요 흐름으로 정의.
- **최소 구현**  
  - `solar/eden/four_rivers.py`:  
    - 상수 또는 설정: `EDEN_FOUR_RIVERS = [("Pishon", bands_or_region), ("Gihon", ...), ("Tigris", ...), ("Euphrates", ...)]`.  
    - 함수: `get_river_bands(name)` → 해당 강이 지나는 밴드 인덱스 리스트, `get_river_for_band(band_id)` → 그 밴드가 속한 강 이름.  
  - EdenGeography 또는 EdenCandidate와 결합: “이 에덴의 4대강 구성”을 IC/지리와 함께 넘길 수 있게 함.

### 4.4 작업 순서

- Phase 1: 4대강 이름·밴드 매핑만 정의(상수/설정 + `get_river_bands` / `get_river_for_band`).  
- Phase 2: 필요 시 geography(ExposedRegion)·수계와 연결하거나, 수문 그래프가 생기면 4대강을 그 위에 정의.

---

## 5. 생명나무·체루빔 — 엔지니어링 설계

### 5.1 서사 근거

- 창세기 3:24: 선악과 사건 후, 에덴 동쪽에 생명나무로 가는 길을 체루빔과 불붙은 칼로 지키게 하심.

### 5.2 시스템 해석

- **생명나무**  
  - “접근 시 시스템이 최대 안정/불멸에 가까운 상태” 또는 “특정 제약이 만족되는 영역”.  
  - 코드: `TreeOfLifeState` = (region/band_id, condition).  
    - 예: `stability > threshold` 이고 `mutation_factor < 0.01` 인 (band 또는 region).
- **체루빔**  
  - “생명나무로의 무단 접근을 막는 수호자”.  
  - 코드: **CherubimGuard** — 규칙: `if not permitted(actor) and approach(tree_region): block or apply penalty`.  
  - “선악과” 위반(임계 위반) 시 `permitted(actor)=False` 로 두면, 체루빔이 생명나무 접근을 차단하는 구조.
- **불칼**  
  - “접근 시도에 대한 비용/금지”.  
  - 전이 비용 무한대, 또는 “해당 전이 금지” 플래그로 구현 가능.

### 5.3 데이터·API 제안

- **TreeOfLifeRegion**  
  - `band_id: Optional[int]`, 또는 `region_id: str`, `condition: Callable[[PlanetSnapshot], bool]`.  
  - 예: “band 5이고, snapshot.band_T[5] in [295,305] and snapshot.band_GPP[5] > threshold”.
- **CherubimGuard**  
  - `tree: TreeOfLifeRegion`, `permitted: Callable[[Actor], bool]` (Actor = Adam/Eve 또는 successor).  
  - `allow_approach(actor, snapshot) -> bool`: permitted(actor)이고 condition(snapshot)이면 True, 아니면 False.  
  - `blocked_message`: 접근 거부 시 로그/메시지.
- **Adam/Eve와 연동**  
  - Adam: “선악과” = 임계(threshold) 관리. 위반 시 `actor.permitted_for_tree_of_life = False` 로 설정.  
  - Eve 또는 Controller가 “생명나무 영역 접근” 행동을 시도할 때 CherubimGuard.allow_approach(actor)를 호출 → False면 접근 불가(불칼 = 비용 무한대 또는 전이 금지).

### 5.4 작업 순서

- Phase 1: `solar/eden/tree_and_cherubim.py` (또는 eden/ 내 별도 모듈)  
  - TreeOfLifeRegion(condition만 우선), CherubimGuard(permitted, allow_approach).  
  - Adam 쪽에서 “임계 위반 = permitted False” 설정만 연결.  
- Phase 2: 생명나무 조건을 band_T, GPP, stability 등으로 구체화하고, 불칼을 “전이 비용/금지”로 명시.

---

## 6. 전체 작업 로드맵 (의존성 순)

```
[Phase A] Eden IC ↔ Day7 Runner 연동 (더블카운트 방지)
    ↓
[Phase B] 탐색 결과 → make_planet_runner(eden_ic) → “그 에덴” OS 생성
    ↓
[Phase C] Adam(Observer) + Eve(Controller) 구현 (adam.py, eve.py)
    ↓
[Phase D] Lineage 구현 (lineage.py) — ReproductionEngine + SelectionEngine → successor(“네오”)
    ↓
[Phase E] 4대강 데이터/API (four_rivers.py) — 밴드/지역 매핑
    ↓
[Phase F] 생명나무·체루빔 (tree_and_cherubim.py) — 조건·수호·Adam 임계 위반 연동
```

- **궁창시대 극지 비빙하 + 세차**: Phase A 완료 시, Eden IC를 쓰는 Runner가 “남북극 얼음지대가 아닌 궁창시대 스페이스 세차운동 상태”를 그대로 반영한다.  
- **에덴 탐색 → OS → 아담·이브 → 네오**: Phase A→B→C→D 순서로 진행하면 “에덴 탐색과 그 에덴의 지구 환경 OS 내부 시스템 관리자 명맥”이 코드로 이어진다.  
- **4대강·생명나무 체루빔**: Phase E·F는 Phase C(D) 이후에 붙여도 되고, 4대강은 탐색/지리와만 연결해도 되어서 Phase B 직후부터 시작 가능.

---

## 7. 요약 표

| 주제 | “돌아간다”/연결 방식 | 구현 포인트 |
|------|----------------------|-------------|
| 남북극 비빙하 + 궁창시대 | Eden IC 사용 시 ice_mask=0, pole_eq_delta=15K, albedo=0.20 | Runner에 Eden IC 주입 + 더블카운트 방지 |
| 스페이스 세차운동 | evolution_engine + Milankovitch 그대로, 지리만 Eden geography(magnetic) | 변경 없음 / geography만 Eden용 |
| 에덴 탐색 → 그 에덴 OS | SearchResult.best → make_planet_runner(ic) | Phase A, B |
| 아담·이브 → 네오 | Adam, Eve, Lineage → successor 선택 | Phase C, D |
| 4대강 | 4강 이름·밴드(또는 지역) 매핑 | Phase E, four_rivers.py |
| 생명나무·체루빔 | TreeOfLifeRegion + CherubimGuard + Adam 임계 위반 → 접근 차단 | Phase F, tree_and_cherubim.py |

이 문서를 기준으로 Phase A부터 순차 진행하면, 요청하신 스토리라인이 엔지니어링적으로 일관되게 구현 가능하다.

---

## 8. 피드백 반영 — 확정 설계안

아래는 동일 목표에 대한 **피드백 정리본**을 반영한 확정 설계다.  
조건: **하드코딩 금지 / 파라미터(CONFIG) 주입 / 레이어 분리 / 직관적 임포트**.

### 8.1 임포트·패키지 구조

```
solar.day7           — 행성 OS (PlanetRunner, SabbathJudge)
solar.eden           — 에덴 환경·탐색 (firmament, flood, initial_conditions, geography, search, exploration)
solar.eden_os        — 에덴 내부 운영·오브젝트·계승 (EdenWorld, rivers, tree, cherubim, Adam/Eve, lineage)
```

- **eden_os** 는 “에덴 위에서 돌아가는 운영 레이어” 전용. 서사 오브젝트(강/나무/체루빔)와 시스템 관리자(Adam/Eve)·계승(lineage)을 한 곳에서 관리.

### 8.2 작업 진행 순서 (실제 구현 로드맵)

| Step | 목표 | 입·출력·합격 조건 |
|------|------|-------------------|
| **Step 1** | 궁창시대(극지 비빙하/균온)를 **환경 스냅샷으로 확정** | **입력**: EdenCandidate 또는 antediluvian preset. **출력**: EdenWorldEnv (T, CO2, UV_shield, pressure, band temps, ice=0 등). **합격**: ice_bands==0, hab_bands>=10, mutation_factor<=0.10, (선택) SabbathJudge drift 과도하지 않음. **서사 오브젝트(강/나무/체루빔) 금지** — 물리만. |
| **Step 2** | 4대강을 **좌표가 아닌 네트워크(그래프) 오브젝트**로 구현 | **이유**: “에덴은 좌표가 아니다” — 강은 한 점이 아니라 흐름/분기/연결. **rivers.py 최소**: RiverNode(name, kind, meta), RiverEdge(src, dst, flow_rate, seasonality). 4대강 = 근원 노드 1개 → 4분기. **합격**: 4강 이름/속성이 CONFIG로 주입, 월드 스텝에 따라 유량/계절성만 변하고 네트워크는 보존. |
| **Step 3** | 생명나무를 **리소스/상태 머신**으로 구현 | **tree_of_life.py**: TreeOfLife(state: locked \| available \| consumed \| removed), grant(effect)는 biology 모델과 연결(예: lifespan multiplier). 접근 조건·접근 시 효과·체루빔 가드 대상. **합격**: Tree 상태 변화가 EdenWorld 로그에 남고 재현 가능. |
| **Step 4** | 체루빔 = **Guard/Access Control + Scanner** | **cherubim_guard.py**: 입력 EdenWorldState, AgentIntent → 출력 GuardDecision(allow/deny, reason, risk_score). **규칙은 반드시 CONFIG 기반(하드코딩 금지)**. **합격**: Adam/Eve가 생명나무 접근 시도 시 정책 조건 충족 전 DENY, 충족 시 ALLOW. deny/allow는 조건식·점수·로그로만 기록. |
| **Step 5** | Adam/Eve = **운영자·계승** 에이전트 레이어 | **Adam**: observe(world)→Observation, decide(obs)→Intent, act(intent, world)→world. **Eve**: 정책 변형/분기, 다음 세대 생성 규칙(계승 트리거). **lineage.py**: LineageGraph(parent→child), inherit(policy, mutation). **합격**: 스텝이 지나며 운영자 인스턴스가 이어지고, 세대별 정책 파라미터가 로그로 재현 가능. |

### 8.3 12시스템과 EdenOS 연결

| 12의 의미 | EdenOS에서의 역할 |
|-----------|-------------------|
| **12밴드(공간)** | EdenWorld의 “지역/지파” |
| **12엔진(기능)** | EdenOSRunner의 “서브시스템 순서” |
| **window=12(시간)** | 운영자 계승/판정 주기(계약 갱신·안정 판정) |

**EdenOSRunner.step() 고정 순서**:

1. env 업데이트(궁창/계절)
2. rivers 업데이트
3. tree 상태 업데이트
4. cherubim_guard 판정
5. agents(Adam/Eve) 의사결정·행동
6. lineage 갱신
7. 로그·판정

→ “천지창조 → 12시스템 → 에덴 운영”이 임포트와 러너 구조로 일관되게 이어진다.

### 8.4 테스트 기준 (완료 판정)

**최소 통과 세트(스모크 테스트)**:

1. **EdenCandidate(best)** 를 로드해 EdenWorld 생성.
2. **EdenOSRunner.step()** 24회 실행.
3. 아래 모두 만족:
   - **재현성**: seed 동일하면 로그 동일.
   - **생태/환경**: ice_bands == 0 유지(antediluvian 설정).
   - **Guard**: 생명나무 접근은 정책 충족 전 DENY.
   - **계승**: 특정 이벤트 이후 Eve가 계승을 트리거하고 lineage 그래프가 1단 이상 생성.
   - **4대강**: 네트워크 유지 + 유량 변화 로그 출력.

### 8.5 궁창시대·극지 비빙하·스페이스 세차 — 레이어 위치

이것은 **물리 강제가 아니라 시나리오의 좌표계/시간keeping(lore) 레이어**로 둔다.

| 항목 | EdenOS에서의 처리 |
|------|-------------------|
| **얼음 없음** | initial_conditions의 albedo / pole_eq_delta / ice_threshold로 **환경 결과(극지 균온)**만 반영. 엔진은 이 결과만 사용. |
| **남극이 위쪽** | 지도 렌더/표현 좌표계(geography/visualization)에서만 처리. |
| **스페이스 세차 관점** | calendar/timekeeping을 **lore 변수**로만 유지. **물리 강제 금지**. |

→ 엔진은 “환경 결과(극지 균온)”만 사용하고, 이야기적 해석은 좌표계·라벨링·표현에만 붙인다.

### 8.6 개념 대응 요약 (피드백 용어)

| 피드백 용어 | 설계 대응 |
|-------------|-----------|
| 아담/이브 = 슈퍼유저(Neo 프로토콜) | Adam: observe/decide/act, GPP/파라미터 조작 권한, 동물 명명 = 데이터 인덱싱. Eve: 보조 프로세서·분산 병렬·계승 트리거. |
| 4대강 = 글로벌 리소스 라우팅 네트워크 | rivers.py 그래프(RiverNode, RiverEdge), 근원 1 → 4분기, CONFIG 주입. |
| 생명나무 = 코어 커널 / 선악과 = 금지 API | tree_of_life.py 상태 머신, grant(effect), 선악과 = Root 전용 API 호출 시 권한 상실·엔트로피 주입. |
| 체루빔·불칼 = 방화벽 | cherubim_guard.py GuardDecision(allow/deny, reason, risk_score), CONFIG 기반. 불칼 = 다형성 암호화/접근 원천 차단. |

---

## 9. 변경·보완 요약 (기존 분석 대비)

| 항목 | 기존 문서 | 피드백 반영 후 |
|------|------------|----------------|
| 패키지 | eden/ 내 adam, eve, lineage, four_rivers, tree_and_cherubim | **eden_os/** 로 분리 — 에덴 “내부 운영” 전용. |
| 4대강 | 밴드 매핑·get_river_bands 등 | **그래프 오브젝트**(RiverNode, RiverEdge), 유량/계절성, CONFIG 주입. |
| 생명나무 | TreeOfLifeRegion + condition | **상태 머신**(locked/available/consumed/removed) + grant(effect), 로그 재현. |
| 체루빔 | allow_approach(actor, snapshot) | **GuardDecision(allow/deny, reason, risk_score)**, 규칙 **CONFIG 기반(하드코딩 금지)**. |
| Adam/Eve | observe/watch, explore, control | **observe→decide→act** 3단계, Eve = 계승 트리거·정책 변형. lineage = LineageGraph + inherit(policy, mutation). |
| 러너 | PlanetRunner 중심 | **EdenOSRunner** step 순서 7단계 고정(env→rivers→tree→cherubim→agents→lineage→log). |
| 극지/세차 | 물리·geography에 반영 | **lore/좌표계 레이어**로만 유지, 물리 강제 금지. |

이 섹션 8·9를 반영한 상태가 **현재 확정 설계**이며, 구현은 Step 1부터 순서대로 진행하면 된다.
