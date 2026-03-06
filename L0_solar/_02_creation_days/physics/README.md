# `_02_creation_days/physics/` — 물리 코어 진입점

**L0_solar > _02_creation_days 서브폴더**

---

## 서사 위치 및 역할

```
_02_creation_days/ (Day 1~7 환경 구축)
      │
      ├── day1~7/        각 창조일 물리 도메인
      ├── engines/       에너지 우물 서브엔진
      ├── fields/        장(field) 초기화
      └── physics/  ←  여기. 행성 심층 물리 코어
          └── lucifer_core/  내핵·외핵·맨틀, 심층 모니터 진입점
```

**서사**: 창조 Day 1~7 전반에 걸쳐 행성 내부(내핵·외핵·맨틀) 상태가
지표 환경과 결합된다. `lucifer_core`는 그 심층 물리의 진입점이다.
이 모듈은 훗날 `_06_lucifer_impact`의 충돌 에너지가 내부 구조에 미치는 영향과도 연결된다.

---

## 폴더 구조

```
physics/
├── lucifer_core/          내핵·외핵·맨틀 심층 모니터 진입점
│   ├── __init__.py        run() 래퍼
│   └── README.md
└── __init__.py
```

---

## 엔지니어링 역할

`lucifer_core/`는 런처(wrapper)다. 실제 구현은 언더월드에 있다.

```python
# physics/lucifer_core/__init__.py → run() 래퍼
# 실제 구현:
from L0_solar._03_eden_os_underworld.underworld.deep_monitor import (
    read_deep_snapshot, DeepSnapshot
)

# DeepSnapshot: 내핵 온도, 외핵 유동, 맨틀 대류 상태
snapshot = read_deep_snapshot(planet_state)
```

**설계 이유**: `_02_creation_days` 레이어는 `_03` 이하를 직접 import하지 않는다.
`physics/lucifer_core/run()`이 중간 래퍼 역할을 해서 레이어 간 의존성을 단방향으로 유지.

---

## _06_lucifer_impact 와의 연결

`_06_lucifer_impact`가 계산하는 충돌 에너지(E_eff_MT)는
이 `lucifer_core`가 모니터링하는 내부 구조에 충격을 전달한다.

```
_06 lucifer_strike() → E_eff_MT
  → lucifer_core가 감지 → DeepSnapshot 갱신
  → _07_polar_ice 기후 강제에 반영
```

---

## 블록체인 서명

```bash
cd blockchain
python3 pham_sign_v4.py ../L0_solar/_02_creation_days/physics/lucifer_core/__init__.py \
    --author "GNJz" --desc "루시퍼 코어 물리 진입점"
```
