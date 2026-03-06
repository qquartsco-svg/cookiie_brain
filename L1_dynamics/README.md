# L1_dynamics — Layer 1~2 : 동역학 엔진

CookiieBrain의 **물리 기반.**  
행성이 자전하고, 에너지 지형이 생기고, 열적 요동이 주입되는 레이어.  
`L0_solar`(서사)가 이 위에서 돌아가고, `L3_memory`(기억)가 여기서 만든 지형을 제어한다.

---

## 이 레이어가 하는 일

- 행성 자전·조석·코리올리 힘 계산 (Phase_A)
- 우물→가우시안 에너지 지형 생성 (Phase_B)
- 열적 요동·FDT 주입 (Phase_C)

시스템의 "땅"을 만든다. 서사는 이 땅 위에서 펼쳐진다.

---

## 폴더 구조

```
L1_dynamics/
├── Phase_A/              ← Layer 1 : 필드 회전
│   ├── rotational_field.py   자전·코리올리 장(field) 생성
│   ├── tidal.py              조석력 계산
│   ├── moon.py               달 궤도·조석 영향
│   └── docs/                 Phase_A 설계 문서
├── Phase_B/              ← Layer 2a : 에너지 지형
│   ├── well_to_gaussian.py   우물 → 가우시안 변환
│   └── multi_well_potential.py  다중 우물 포텐셜
└── Phase_C/              ← Layer 2b : 요동
    ├── (fluctuation files)   열적 요동·FDT·확률적 진동
    └── README.md
```

---

## Phase별 역할

| Phase | 레이어 번호 | 이름 | 하는 일 |
|-------|-----------|------|---------|
| Phase_A | Layer 1 | 필드 회전 | 자전·조석·코리올리. 행성이 회전하는 기반 장 생성 |
| Phase_B | Layer 2a | 에너지 지형 | 우물→가우시안. 입자가 굴러다닐 포텐셜 지형 |
| Phase_C | Layer 2b | 요동 | 열적 요동·FDT. 확률적 진동을 시스템에 주입 |

---

## 다른 레이어와의 관계

| 방향 | 대상 | 내용 |
|------|------|------|
| 제공 | `L0_solar` | 서사가 돌아갈 물리 기반 (장·지형·요동) 공급 |
| 제공 | `L3_memory` | 우물 포텐셜 지형을 memory가 읽고 제어 |
| 측정됨 | `L4_analysis` | Phase_A~C 결과를 분석 레이어가 측정 |
