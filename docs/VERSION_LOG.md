# solar/ 버전 로그 / Version Log

## v1.2.2 — EM 레이어 개념 문서화

**날짜**: 2026-02-25
**작업**: README에 전자기 레이어 물리 개념 해설 추가

| 파일 | 설명 |
|------|------|
| `solar/README.md` | "전자기 레이어 개념 / EM Layer Concepts" 섹션 추가 |

추가 내용:
- Phase 2 (자기쌍극자): 물리 개념, B ∝ 1/r³ 수식, 세차 연동 원리, 코드 흐름
- Phase 3 (태양풍): 동압·플럭스·복사압·IMF 각각의 역할, 1/r² 감쇠 이유
- Phase 4 (자기권): Chapman-Ferraro 균형, 1/6 지수 유도, 자기권 구조 다이어그램
- 3개 Phase 체인 연결 흐름도
- 1/r³ vs 1/r² 감쇠 법칙 차이와 마그네토포즈 생성 원리

---

## v1.2.1 — 문서 정비 + EPS 중앙 관리

**날짜**: 2026-02-25
**작업**: 피드백 기반 README 강화 + em/ 코드 정비

| 파일 | 설명 |
|------|------|
| `solar/README.md` | 통합 단위 체계(Unit System) 섹션 추가 |
| `solar/README.md` | 파라미터 정책(Parameter Policy) 섹션 추가 |
| `solar/em/_constants.py` | EPS_ZERO, EPS_GEOM 중앙 상수 파일 신설 |
| `solar/em/magnetic_dipole.py` | 매직 넘버 → EPS_ZERO/EPS_GEOM 교체 (13개소) |
| `solar/em/solar_wind.py` | 매직 넘버 → EPS_ZERO 교체 (3개소) |
| `solar/em/magnetosphere.py` | 매직 넘버 → EPS_ZERO 교체 (3개소) |

검증: 기존 em_layer_demo.py 동일 결과 확인 (값 변동 없음)

---

## v1.2.0 — 전자기 레이어 완비 (Phase 2+3+4)

**날짜**: 2026-02-25
**작업**: 자기쌍극자 + 태양풍 + 자기권

| 파일 | 설명 |
|------|------|
| `solar/em/magnetic_dipole.py` | 자기쌍극자장 B(x,t) ∝ 1/r³, 11.5° 기울기 |
| `solar/em/solar_wind.py` | 태양풍 동압+복사압+IMF ∝ 1/r² |
| `solar/em/magnetosphere.py` | Chapman-Ferraro 자기권: r_mp, 보우쇼크, 차폐 |
| `examples/em_layer_demo.py` | Phase 2+3+4 통합 검증 (ALL PASS) |
| `docs/EM_LAYER_LOG.txt` | 통합 검증 출력 로그 |

검증:
- 표면 자기장 정확도: 0.00%
- 1/r³ 감쇠: 0.00%
- 태양풍 1/r²: 5행성 0.00%
- 마그네토포즈: 7.58 R_E
- 차폐: 0.78
- 세차-자기권 연동: PASS
- 에너지 보존: dE/E = 8.20e-11

---

## v1.1.0 — 자기쌍극자장 (Phase 2)

**날짜**: 2026-02-25
**작업**: em/ 레이어 신설, 자기쌍극자

| 파일 | 설명 |
|------|------|
| `solar/em/__init__.py` | 전자기 레이어 공개 API |
| `solar/em/magnetic_dipole.py` | 쌍극자 B필드, DipoleFieldPoint |
| `examples/magnetic_dipole_demo.py` | Phase 2 단독 검증 (ALL PASS) |
| `docs/MAGNETIC_DIPOLE_LOG.txt` | Phase 2 검증 출력 로그 |

---

## v1.0.0 — 전체 태양계 N-body (Phase 1) + 기어 분리

**날짜**: 2026-02-25
**작업**: 8행성 NASA 데이터 + core/data/cognitive/ 폴더 구조화

| 파일 | 설명 |
|------|------|
| `solar/data/solar_system_data.py` | NASA/JPL 8행성+태양+달 실측 상수 |
| `solar/core/` | 물리 코어 분리 (evolution_engine 등) |
| `solar/cognitive/` | 인지 레이어 분리 (ring_attractor 등) |
| `examples/full_solar_system_demo.py` | 10-body 100년 검증 (ALL PASS) |
| `docs/FULL_SOLAR_SYSTEM_LOG.txt` | 10-body 검증 출력 로그 |

검증:
- 에너지 보존: dE/E = 3.20e-10
- 각운동량 보존: dL/L = 3.04e-14
- 세차 주기: 24,763년 (NASA 25,772년, 3.9%)
- 전 행성 궤도 편차: < 1%

---

## v0.9.0 — Ring Attractor 결합

**날짜**: 2026-02-25
**작업**: 관성 기억 엔진 + 커플링 레이어

| 파일 | 설명 |
|------|------|
| `solar/ring_attractor.py` | Mexican-hat bump attractor |
| `solar/spin_ring_coupling.py` | 물리↔인지 필드 연결 |
| `examples/spin_ring_coupling_demo.py` | 커플링 검증 (ALL PASS) |
| `docs/SPIN_RING_COUPLING_LOG.txt` | 커플링 검증 출력 로그 |

---

## v0.8.0 — 3체 세차운동

**날짜**: 2026-02-25
**작업**: EvolutionEngine 신설, 세차운동 첫 재현

| 파일 | 설명 |
|------|------|
| `solar/evolution_engine.py` | N-body + 스핀-궤도 + 해양 |
| `examples/planet_evolution_demo.py` | 6단계 전과정 데모 |
| `docs/PRECESSION_VERIFICATION_LOG.txt` | 세차 검증 출력 로그 |

검증:
- 세차 주기: 24,575년 (NASA 25,772년, 4.6%)
- 에너지 보존: dE/E = 2.06e-15
