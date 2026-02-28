# 10 Net Well — 연결 엔진 (SeedTransport)

> *"새들이 땅 위 하늘 궁창에 날으라" — 창세기 1:20*

## 역할
보존형 확산 커널 — 밴드 간 씨드(바이오매스) 수송.
새/물고기 이동이 씨드를 확산시키는 과정.
**질량 보존**을 보장하는 수치 안정 확산기.

## 독립성
- 의존: stdlib(`dataclasses`) 만
- 완전 독립 — 복사만 해도 즉시 실행

## 주요 클래스
| 클래스 | 역할 |
|--------|------|
| `SeedTransport` | 보존형 확산 — `step(B, dt_yr)` |
| `TransportKernel` | 이웃·이동률 정의 dataclass |

## 빠른 시작
```python
import sys; sys.path.insert(0, '.')
from net_engine import SeedTransport, TransportKernel

kernel = TransportKernel(n_bands=4, neighbors=[[1],[0,2],[1,3],[2]], rates=[0.05]*4)
transport = SeedTransport(kernel)
B = [1.0, 0.5, 0.3, 0.1]
B2 = transport.step(B, dt_yr=1.0)
print(f"before={B}  after={[round(x,3) for x in B2]}")
print(f"보존 확인: sum_before={sum(B):.3f}  sum_after={sum(B2):.3f}")
```

## 시스템 위치
```
12 Well 시스템
└── 10_net_well  ← 연결 (밴드 간 확산·수송)
```
