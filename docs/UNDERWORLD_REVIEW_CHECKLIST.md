# 언더월드(Underworld) 로직 검토·피드백용 체크리스트

**목적**: 언더월드 로직이 제대로 구현됐는지 확인·피드백 받을 때 **어떤 파일·문서를 보면 되는지** 정리.

---

## 1. 반드시 볼 파일 (언더월드 구현체)

| 순서 | 경로 | 내용 |
|------|------|------|
| 1 | `solar/underworld/__init__.py` | 패키지 공개 (ConsciousnessSignal, HadesObserver, make_hades_observer) |
| 2 | `solar/underworld/consciousness.py` | ConsciousnessSignal(frozen), SignalType(Enum). 목소리 데이터 구조. |
| 3 | `solar/underworld/deep_monitor.py` | DeepSnapshot, read_deep_snapshot(). day4/core 선택 의존, 없으면 스텁. |
| 4 | `solar/underworld/hades.py` | HadesObserver, listen(...) → ConsciousnessSignal. **룰 평가는 rules.evaluate_rules(deep) 호출.** |
| 5 | `solar/underworld/rules.py` | RuleSpec, DEFAULT_RULES, evaluate_rules(). 룰 목록·severity·메시지 정책 (데이터). |

---

## 2. 연동 확인용 파일 (지상에서 언더월드 쓰는 부분)

| 순서 | 경로 | 확인 포인트 |
|------|------|-------------|
| 6 | `solar/eden/eden_os/eden_os_runner.py` | (1) `solar.underworld` import·`_UNDERWORLD_AVAILABLE` (2) `self._hades = make_hades_observer(0)` (3) Step 5 전 `hades_signal = self._hades.listen(...)` (4) `observe(..., hades_signal=hades_signal)` (5) `homeostasis.update(..., hades_signal, stress_injection)` |
| 7 | `solar/eden/eden_os/adam.py` | `observe(..., hades_signal=None)`. hades_signal이 있으면 notes에 `[지하] message`, severity>0.5면 anomaly. |

---

## 3. 참고할 문서 (개념·설계)

| 순서 | 경로 | 내용 |
|------|------|------|
| 8 | `docs/EDENOS_DYNAMICS_AND_UNDERWORLD.md` | 지하(Hades) 역할, ConsciousnessSignal·listen() 설계, 폴더 구조. |
| 9 | `docs/WORK_SUMMARY_EDENOS_AND_FILES.md` | 전체 작업 요약. 섹션 2·3에서 underworld 폴더·파일 위치. |
| 10 | `docs/UNDERWORLD_EXTENSIBILITY.md` | 확장성 분석, 병목, 룰 CONFIG 분리 반영. |

---

## 4. 반드시 유지할 설계 규칙 (검토 시 확인)

- **Hades ONLY measures. Hades NEVER acts.**
- Hades는 관측·신호(ConsciousnessSignal) 생성만 함. decide / punish / want 없음.
- 행동·전이는 항상 Dynamics(IntegrityFSM, lineage) 쪽에서만 발생. 이 규칙이 깨지면 physics layer 붕괴.

---

## 5. 피드백 받을 때 넘기면 좋은 질문 예시

- ConsciousnessSignal·SignalType 설계가 목적(의식의 목소리 전달)에 맞는가?
- deep_monitor가 day4/core 없을 때 스텁만 반환하는 방식이 괜찮은가? 실제 core 연동 시 어떤 필드를 읽어야 하는가?
- HadesObserver.listen()의 거시 룰 판단(magnetic_ok, thermal_ok, gravity_ok)을 실제 물리값으로 채우려면 어떻게 확장할 것인가?
- 지상 연동(runner → listen → observe / homeostasis) 흐름이 빠진 구간은 없는가?

---

**요약**: 구현체는 **1~5번 파일**, 연동은 **6~7번 파일**, 개념·설계는 **8~10번 문서**를 보면 언더월드 로직 검토·피드백에 필요한 범위를 다룰 수 있음. 설계 규칙 **Hades ONLY measures, NEVER acts** 는 섹션 4와 hades.py docstring에 고정.
