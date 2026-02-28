# day6/ — 여섯째날: Evolutionary Interaction · Reproductive OS Layer

**역할**  
Day5 로 **연결된** biosphere 위에서, **종(species)** 단위 **경쟁·공생·포식·돌연변이**가 일어나고, **재생산 프로토콜이 안정화**되는 레이어.  
핵심 사건: **이중 유전자 재조합(binary pair)** 의 표준화 → 진화가 안정적 정보 프로세스로 전환.

- **물리적 의미**: 땅 위를 기어다니는 온갖 생물·세균·유기물이 **원시적 혼란** 속에서 뒤섞이고, **돌연변이·선택**을 거쳐 상상 못 할 다양성이 나오는 단계.  
  그 결과 **정보가 안정적으로 다음 세대로 복제되는 규칙**(이중 재조합 OS)이 수렴.
- **엔지니어링 의미**: **single replication** → 불안정한 탐색; **dual recombination** → 안정적 진화 엔진.  
  Genome_child = recombine(Genome_A, Genome_B) + mutation.  
  남·녀 = Exploration(♂) + Exploitation(♀) = 진화를 가능하게 만든 **정보 구조(API)**.

`day6/` 는 이 레이어의 **모듈을 한곳에서 re-export 하는 인덱스 패키지**이며,  
실제 구현은 `solar/day6/*.py` 에 있다.

> ⚠️ **재현성**  
> - Day6 는 **re-export 전용**이며, 구현은 `species_engine`, `mutation_engine`, `reproduction_engine`, `genome_state`, `selection_engine`, `interaction_graph`, `niche_model` 등에 있다.  
> - 상세 개념·수식: [`docs/DAY6_ENGINEERING_ANALYSIS.md`](../docs/DAY6_ENGINEERING_ANALYSIS.md).

---

## 1. 한 줄 정의

**Day 6 = Evolutionary Interaction Layer + Reproductive Operating System Layer**

> 이동으로 연결된 biosphere 위에서, **경쟁·공생·포식·돌연변이**로 종 다양성과 선택 압력이 발생하고,  
> **이중 유전자 재조합(남·녀)** 이 표준화되어 **진화가 안정적 정보 프로세스**로 전환되는 단계.

- **Day 5**: 행성 네트워크 생성 (transport).  
- **Day 6**: **진화 혼란 → 재생산 OS 확립 → 질서 탄생.**

---

## 2. 핵심 수식

**개체군**  
\[
\frac{\mathrm{d}N_s}{\mathrm{d}t}
= \mathrm{growth} - \mathrm{competition} + \mathrm{mutation} + \mathrm{selection}
\]

**단순 복제 (Day5 이전)**  
\(\mathrm{Genome}_{t+1} = \mathrm{mutate}(\mathrm{Genome}_t)\) → 탐색은 되지만 수렴 느림.

**이중 재조합 (Day6 핵심)**  
\[
\mathrm{Genome}_{\mathrm{child}}
= \mathrm{recombine}(\mathrm{Genome}_A,\, \mathrm{Genome}_B) + \mathrm{mutation}
\]  
→ 다양성 ↑, 적응 속도 ↑, 오류 수정 능력 ↑.

**조우 확률** (ContactEngine):  
\(P_{\mathrm{contact}}(i,j) = \rho_i\, \rho_j\, k_{\mathrm{encounter}}\, V_{\mathrm{cell}}^{-1}\).

**돌연변이** (MutationEngine, optional **binary_convergence_pressure**):  
\(\mathrm{d}N_{\mathrm{new}}/\mathrm{d}t = \mu\, P_{\mathrm{contact}}(A,B)\, \mathrm{fitness\_pressure}(\mathrm{env})\).

---

## 3. Day 5 vs Day 6

| 구분 | Day 5 | Day 6 |
|------|--------|--------|
| **중심** | 이동 | **상호작용 + 재생산 프로토콜** |
| **주체** | 생물체(agent) | **종(species)** |
| **수학** | transport | **competition + mutation + recombination** |
| **상태** | 연결 | **진화** |
| **정보** | 분산·운반 | **안정적 복제 규칙 수렴** |

---

## 4. 구성 모듈 (스켈레톤)

| 모듈 | 역할 |
|------|------|
| **contact_engine** | 조우 확률 P_contact(i,j) = ρ_i ρ_j k/V (혼돈 핵심) |
| **species_engine** | 개체군 동역학 (N_s, growth − competition) |
| **mutation_engine** | 변이·종분화 (μ_eff = μ·P_contact·fitness_pressure) |
| **reproduction_engine** | 이중 재조합 (crossover, recombine) |
| **genome_state** | 상속 가능 정보 (Genome, recombine, mutate) |
| **selection_engine** | Exploitation(♀) + Exploration(♂) 선택 |
| **interaction_graph** | 포식·경쟁 네트워크 |
| **niche_model** | 서식지 분할·자원 경쟁 |

---

## 5. Day 1–5 와의 연결

- **Day 3**: land_fraction, GPP, N_soil → Day6 무대·자원.  
- **Day 4**: 질소·계절 → 시간 리듬·영양.  
- **Day 5**: 새·물고기 transport; Day6 는 **땅** 위 **기어다니는** 정보체·다종 상호작용.  
- **Gaia**: Loop I/J/K 후보 (다양성 → 먹이사슬·대기·transport 피드백).

상세: [`docs/DAY6_ENGINEERING_ANALYSIS.md`](../docs/DAY6_ENGINEERING_ANALYSIS.md).
