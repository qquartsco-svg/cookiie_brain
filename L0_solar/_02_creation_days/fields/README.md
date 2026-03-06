# `_02_creation_days/fields/` — 장(Field) 초기화

**L0_solar > _02_creation_days 서브폴더**

---

## 서사 위치 및 역할

```
_02_creation_days/ (Day 1~7 환경 구축)
      │
      ├── day1~7/        각 창조일 물리 도메인
      ├── engines/       에너지 우물 서브엔진
      ├── fields/   ←  여기. 장(field) 초기화
      │   └── firmament/ 창공 장 초기 상태 설정
      └── physics/       루시퍼 코어 물리
```

**서사**: Day 2에서 궁창(창공)이 물을 분리하며 장이 형성된다.
이 폴더는 그 창공 장(Firmament Field)의 **초기 상태값을 설정**한다.
`_03_eden_os_underworld/eden/firmament.py`가 런타임에 이 초기값을 사용한다.

---

## 폴더 구조

```
fields/
├── firmament/           창공 장 초기화
│   ├── __init__.py
│   └── README.md
└── __init__.py
```

---

## 엔지니어링 역할

`fields/firmament/`은 창공 장의 **정적 초기 파라미터**를 정의한다.
런타임 동적 계산은 `_03_eden_os_underworld/eden/firmament.py`가 담당.

```python
# fields/firmament/ → FirmamentLayer 초기값 제공
from L0_solar._02_creation_days.fields.firmament import FIRMAMENT_INIT
firmament = FirmamentLayer(initial_conditions=FIRMAMENT_INIT)
```

---

## 블록체인 서명

```bash
cd blockchain
python3 pham_sign_v4.py ../L0_solar/_02_creation_days/fields/firmament/__init__.py \
    --author "GNJz" --desc "창공 장 초기화"
```
