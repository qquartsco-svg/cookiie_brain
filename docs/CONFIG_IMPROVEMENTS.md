# 설정 개선 사항 (v0.1.1 → v0.1.2)

**작성일**: 2026-02-21  
**버전**: 0.1.2

---

## 하드코딩 제거

### 개선 전 (v0.1.1)

```python
# 하드코딩된 매직 넘버
self.cerebellum_engine = CerebellumEngine(
    memory_dim=5,  # 하드코딩
    config=cerebellum_config,
)

correction = self.cerebellum_engine.compute_correction(
    ...
    dt=0.001,  # 하드코딩
)

new_position = position + correction * 0.01  # 하드코딩
```

### 개선 후 (v0.1.2)

```python
# 설정으로 관리
cerebellum_config = {
    "memory_dim": 5,
    "dt": 0.001,
    "correction_scale": 0.01,
}

brain = CookiieBrainEngine(
    ...
    cerebellum_config=cerebellum_config,
)

# 내부에서 설정값 사용
self.cerebellum_memory_dim = self.cerebellum_config.get("memory_dim", 5)
self.cerebellum_dt = self.cerebellum_config.get("dt", 0.001)
self.cerebellum_correction_scale = self.cerebellum_config.get("correction_scale", 0.01)
```

---

## 설정 파라미터

### CerebellumEngine 설정

```python
cerebellum_config = {
    "memory_dim": int,        # 기본값: 5
    "dt": float,              # 기본값: 0.001
    "correction_scale": float, # 기본값: 0.01
}
```

**설명**:
- `memory_dim`: CerebellumEngine의 메모리 차원
- `dt`: 시간 스텝 크기
- `correction_scale`: 보정값 스케일링 계수

---

## 사용 예제

```python
from cookiie_brain_engine import CookiieBrainEngine

# CerebellumEngine 설정 커스터마이징
brain = CookiieBrainEngine(
    enable_well_formation=True,
    enable_potential_field=True,
    enable_cerebellum=True,
    cerebellum_config={
        "memory_dim": 10,        # 메모리 차원 증가
        "dt": 0.002,             # 시간 스텝 증가
        "correction_scale": 0.02, # 보정값 스케일 증가
    },
)
```

---

## 변경 사항 요약

1. ✅ `memory_dim=5` → `cerebellum_config.get("memory_dim", 5)`
2. ✅ `dt=0.001` → `cerebellum_config.get("dt", 0.001)`
3. ✅ `correction * 0.01` → `correction * self.cerebellum_correction_scale`

---

**작성자**: GNJz (Qquarts)  
**버전**: 0.1.2

